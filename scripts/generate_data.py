import random
from datetime import datetime, timedelta
from decimal import Decimal

import pandas as pd


RANDOM_SEED = 20260815
CUSTOMER_COUNT = 1_000
PRODUCT_COUNT = 200
ORDER_COUNT = 5_000
LOGICAL_ITEM_COUNT = 12_000
SECOND_BATCH_ROW_COUNT = 36
START_DATE = datetime(2026, 8, 1)
SECOND_BATCH_DATE = datetime(2026, 8, 15).date()
PRIMARY_BATCH_ID = 'load-20260901-primary'
SECOND_BATCH_ID = 'load-20260902-replay'
PRIMARY_INGESTED_AT = pd.Timestamp('2026-09-01T02:00:00Z')
SECONDARY_INGESTED_AT = pd.Timestamp('2026-09-02T02:00:00Z')


def money_from_cents(cents):
    return (Decimal(cents) / Decimal(100)).quantize(Decimal('0.01'))


def generate_tables():
    rng = random.Random(RANDOM_SEED)

    segments = ('consumer', 'small_business', 'enterprise')
    countries = ('Indonesia', 'Singapore', 'Malaysia', 'Thailand', 'Vietnam')
    categories = ('electronics', 'home', 'office', 'sports', 'beauty')

    customer_rows = []
    for number in range(1, CUSTOMER_COUNT + 1):
        customer_rows.append({
            'customer_id': f'C{number:05d}',
            'customer_name': f'Customer {number:04d}',
            'segment': segments[(number - 1) % len(segments)],
            'country': countries[(number - 1) % len(countries)],
            'created_at': pd.Timestamp(
                START_DATE - timedelta(days=rng.randrange(30, 730))
            ),
            'ingestion_batch_id': PRIMARY_BATCH_ID,
            'ingested_at': PRIMARY_INGESTED_AT,
        })

    product_rows = []
    product_prices = {}
    for number in range(1, PRODUCT_COUNT + 1):
        product_id = f'P{number:04d}'
        price = money_from_cents(rng.randrange(500, 50_001))
        product_prices[product_id] = price
        product_rows.append({
            'product_id': product_id,
            'product_name': f'Product {number:03d}',
            'category': categories[(number - 1) % len(categories)],
            'unit_price': price,
            'ingestion_batch_id': PRIMARY_BATCH_ID,
            'ingested_at': PRIMARY_INGESTED_AT,
        })

    order_rows = []
    item_rows = []
    order_context = {}
    item_number = 1

    for number in range(1, ORDER_COUNT + 1):
        order_id = f'O{number:06d}'
        order_day = START_DATE + timedelta(days=(number - 1) % 30)
        order_ts = order_day + timedelta(
            hours=rng.randrange(8, 22),
            minutes=rng.randrange(0, 60),
            seconds=rng.randrange(0, 60),
        )
        if number % 20 == 0:
            status = 'cancelled'
        elif number % 20 == 1:
            status = 'refunded'
        else:
            status = 'completed'

        customer_id = f'C{rng.randrange(1, CUSTOMER_COUNT + 1):05d}'
        item_count = 3 if number <= 2_000 else 2
        order_total = Decimal('0.00')

        for _ in range(item_count):
            product_id = f'P{rng.randrange(1, PRODUCT_COUNT + 1):04d}'
            quantity = rng.randrange(1, 5)
            unit_price = product_prices[product_id]
            order_total += unit_price * quantity
            item_rows.append({
                'order_item_id': f'OI{item_number:07d}',
                'order_id': order_id,
                'product_id': product_id,
                'quantity': quantity,
                'unit_price': unit_price,
                'ingestion_batch_id': PRIMARY_BATCH_ID,
                'ingested_at': PRIMARY_INGESTED_AT,
            })
            item_number += 1

        order_context[order_id] = {
            'order_date': order_ts.date(),
            'status': status,
        }
        order_rows.append({
            'order_id': order_id,
            'customer_id': customer_id,
            'order_ts': pd.Timestamp(order_ts),
            'status': status,
            'order_total': order_total.quantize(Decimal('0.01')),
            'ingestion_batch_id': PRIMARY_BATCH_ID,
            'ingested_at': PRIMARY_INGESTED_AT,
        })

    if len(item_rows) != LOGICAL_ITEM_COUNT:
        raise RuntimeError(f'Expected {LOGICAL_ITEM_COUNT} logical item rows.')

    eligible_rows = [
        row for row in item_rows
        if order_context[row['order_id']]['order_date'] == SECOND_BATCH_DATE
        and order_context[row['order_id']]['status'] == 'completed'
    ]
    eligible_total = sum(
        row['unit_price'] * row['quantity'] for row in eligible_rows
    )
    target_row_value = eligible_total * Decimal('0.09') / SECOND_BATCH_ROW_COUNT
    selected_rows = sorted(
        eligible_rows,
        key=lambda row: (
            abs((row['unit_price'] * row['quantity']) - target_row_value),
            row['order_item_id'],
        ),
    )[:SECOND_BATCH_ROW_COUNT]

    second_batch_rows = []
    for row in selected_rows:
        replayed = dict(row)
        replayed['ingestion_batch_id'] = SECOND_BATCH_ID
        replayed['ingested_at'] = SECONDARY_INGESTED_AT
        second_batch_rows.append(replayed)
    item_rows.extend(second_batch_rows)

    return {
        'customers': pd.DataFrame(customer_rows),
        'products': pd.DataFrame(product_rows),
        'orders': pd.DataFrame(order_rows),
        'order_items': pd.DataFrame(item_rows),
    }


if __name__ == '__main__':
    tables = generate_tables()
    for table_name, frame in tables.items():
        print(f'{table_name}: {len(frame):,} rows')
