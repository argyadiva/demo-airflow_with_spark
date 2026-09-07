import os
from datetime import timedelta

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import URL


def required_env(name):
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f'Missing required environment variable: {name}')
    return value


def get_engine():
    return create_engine(
        URL.create(
            drivername='postgresql+psycopg2',
            username=required_env('DB_USER'),
            password=required_env('DB_PASSWORD'),
            host=required_env('DB_HOST'),
            port=int(os.getenv('DB_PORT', '5432')),
            database=required_env('DB_NAME'),
        ),
        connect_args={'sslmode': 'require'},
    )


engine = get_engine()
silver = pd.read_sql('SELECT * FROM silver_coin_prices', engine)

if silver.empty:
    raise RuntimeError('No silver data found. Run scripts/silver.py first.')

silver['extracted_at'] = pd.to_datetime(silver['extracted_at'], utc=True)
as_of = silver['extracted_at'].max()
window_start = as_of - timedelta(hours=24)
window = silver[silver['extracted_at'].between(window_start, as_of)]

latest = (
    window.sort_values('extracted_at')
    .groupby('coin_id', as_index=False)
    .tail(1)[['coin_id', 'price_usd', 'price_idr', 'batch_id', 'extracted_at']]
    .rename(columns={
        'price_usd': 'latest_price_usd',
        'price_idr': 'latest_price_idr',
        'batch_id': 'latest_batch_id',
        'extracted_at': 'latest_observed_at',
    })
)

metrics = (
    window.groupby('coin_id', as_index=False)
    .agg(
        lowest_price_usd_24h=('price_usd', 'min'),
        highest_price_usd_24h=('price_usd', 'max'),
        lowest_price_idr_24h=('price_idr', 'min'),
        highest_price_idr_24h=('price_idr', 'max'),
        sample_count=('price_usd', 'count'),
    )
)

gold = latest.merge(metrics, on='coin_id')
gold['computed_at'] = pd.Timestamp.now(tz='UTC')
gold.to_sql(
    name='gold_latest_coin_stats',
    con=engine,
    if_exists='append',
    index=False,
)

print(f'Gold datamart stored for {len(gold)} coins.')
