from sqlalchemy import DateTime, Integer, Numeric, String, text

from db import get_engine
from generate_data import generate_tables


TABLE_TYPES = {
    'customers': {
        'customer_id': String(20),
        'customer_name': String(100),
        'segment': String(30),
        'country': String(50),
        'created_at': DateTime(timezone=False),
        'ingestion_batch_id': String(50),
        'ingested_at': DateTime(timezone=True),
    },
    'products': {
        'product_id': String(20),
        'product_name': String(100),
        'category': String(50),
        'unit_price': Numeric(12, 2),
        'ingestion_batch_id': String(50),
        'ingested_at': DateTime(timezone=True),
    },
    'orders': {
        'order_id': String(20),
        'customer_id': String(20),
        'order_ts': DateTime(timezone=False),
        'status': String(20),
        'order_total': Numeric(14, 2),
        'ingestion_batch_id': String(50),
        'ingested_at': DateTime(timezone=True),
    },
    'order_items': {
        'order_item_id': String(20),
        'order_id': String(20),
        'product_id': String(20),
        'quantity': Integer(),
        'unit_price': Numeric(12, 2),
        'ingestion_batch_id': String(50),
        'ingested_at': DateTime(timezone=True),
    },
}


def main():
    tables = generate_tables()
    engine = get_engine()

    with engine.begin() as connection:
        connection.execute(text('CREATE SCHEMA IF NOT EXISTS bronze'))
        connection.execute(text('CREATE SCHEMA IF NOT EXISTS silver'))
        connection.execute(text('CREATE SCHEMA IF NOT EXISTS gold'))

        for table_name in ('customers', 'products', 'orders', 'order_items'):
            tables[table_name].to_sql(
                name=table_name,
                schema='bronze',
                con=connection,
                if_exists='replace',
                index=False,
                chunksize=1_000,
                method='multi',
                dtype=TABLE_TYPES[table_name],
            )

        connection.execute(text(
            'ALTER TABLE bronze.customers ADD PRIMARY KEY (customer_id)'
        ))
        connection.execute(text(
            'ALTER TABLE bronze.products ADD PRIMARY KEY (product_id)'
        ))
        connection.execute(text(
            'ALTER TABLE bronze.orders ADD PRIMARY KEY (order_id)'
        ))
        connection.execute(text(
            'CREATE INDEX ix_bronze_order_items_item '
            'ON bronze.order_items (order_item_id)'
        ))
        connection.execute(text(
            'CREATE INDEX ix_bronze_order_items_order '
            'ON bronze.order_items (order_id)'
        ))

    counts = ', '.join(
        f'{name}={len(frame):,}' for name, frame in tables.items()
    )
    print(f'Bronze seed loaded successfully: {counts}')


if __name__ == '__main__':
    main()
