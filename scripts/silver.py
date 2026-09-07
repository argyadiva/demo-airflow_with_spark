import json
import os

import pandas as pd
from sqlalchemy import create_engine, text
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


def payload_as_dict(payload):
    return payload if isinstance(payload, dict) else json.loads(payload)


engine = get_engine()
bronze = pd.read_sql(
    text(
        """
        SELECT batch_id, extracted_at, raw_payload
        FROM bronze_coin_gecko
        ORDER BY extracted_at DESC
        LIMIT 1
        """
    ),
    engine,
)

if bronze.empty:
    raise RuntimeError('No bronze data found. Run scripts/bronze.py first.')

batch_id = bronze['batch_id'].iloc[0]
extracted_at = bronze['extracted_at'].iloc[0]
coin_payload = payload_as_dict(bronze['raw_payload'].iloc[0])

currency = pd.read_sql(
    text(
        """
        SELECT batch_id, raw_payload
        FROM bronze_currency_rate
        WHERE batch_id = :batch_id
        ORDER BY extracted_at DESC
        LIMIT 1
        """
    ),
    engine,
    params={'batch_id': batch_id},
)

if currency.empty:
    raise RuntimeError(
        f'No currency bronze row found for CoinGecko batch {batch_id}.'
    )

currency_payload = payload_as_dict(currency['raw_payload'].iloc[0])

coin_rows = [
    {'coin_id': coin_id, 'price_usd': values['usd']}
    for coin_id, values in coin_payload.items()
]
coins = pd.DataFrame(coin_rows)
exchange_rate = currency_payload['rates']['IDR']

silver = coins.assign(
    batch_id=batch_id,
    extracted_at=extracted_at,
    exchange_rate=exchange_rate,
    price_idr=coins['price_usd'] * exchange_rate,
    provider_date=currency_payload.get('date'),
)[[
    'batch_id',
    'extracted_at',
    'coin_id',
    'price_usd',
    'exchange_rate',
    'price_idr',
    'provider_date',
]]

silver.to_sql(
    name='silver_coin_prices',
    con=engine,
    if_exists='append',
    index=False,
)

print(f'Silver batch {batch_id} stored with {len(silver)} coin rows.')
