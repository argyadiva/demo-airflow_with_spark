import os

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
        pool_pre_ping=True,
    )
