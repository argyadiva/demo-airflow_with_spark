import os
import uuid
from datetime import datetime, timezone

import pandas as pd
import requests
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.engine import URL


COINGECKO_URL = 'https://api.coingecko.com/api/v3/simple/price'
FRANKFURTER_URL = 'https://api.frankfurter.dev/v1/latest'
COIN_IDS = 'bitcoin,ethereum,ripple,solana,doge'


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


batch_id = str(uuid.uuid4())
extracted_at = pd.Timestamp(datetime.now(timezone.utc))

coin_response = requests.get(
    COINGECKO_URL,
    params={
        'ids': COIN_IDS,
        'vs_currencies': 'usd',
        'include_last_updated_at': 'true',
    },
    timeout=30,
)
coin_response.raise_for_status()

currency_response = requests.get(
    FRANKFURTER_URL,
    params={'base': 'USD', 'symbols': 'IDR'},
    timeout=30,
)
currency_response.raise_for_status()

coin_raw = pd.DataFrame([{
    'batch_id': batch_id,
    'extracted_at': extracted_at,
    'raw_payload': coin_response.json(),
}])

currency_raw = pd.DataFrame([{
    'batch_id': batch_id,
    'extracted_at': extracted_at,
    'raw_payload': currency_response.json(),
}])

engine = get_engine()
coin_raw.to_sql(
    name='bronze_coin_gecko',
    con=engine,
    if_exists='append',
    index=False,
    dtype={'raw_payload': JSONB},
)

currency_raw.to_sql(
    name='bronze_currency_rate',
    con=engine,
    if_exists='append',
    index=False,
    dtype={'raw_payload': JSONB},
)

print(f'Bronze batch {batch_id} stored successfully.')
