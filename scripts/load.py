import os

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import URL


def required_env(name):
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f'Missing required environment variable: {name}')
    return value


db_url = URL.create(
    drivername='postgresql+psycopg2',
    username=required_env('DB_USER'),
    password=required_env('DB_PASSWORD'),
    host=required_env('DB_HOST'),
    port=int(os.getenv('DB_PORT', '5432')),
    database=required_env('DB_NAME'),
)
engine = create_engine(db_url, connect_args={'sslmode': 'require'})

df = pd.read_csv('data/transform_result_crypto_pipeline.csv')
df.to_sql(name='crypto_price', con=engine, if_exists="append", index=False)
