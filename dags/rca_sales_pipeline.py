import datetime as dt
import os

from airflow import DAG
from airflow.operators.bash import BashOperator


with DAG(
    dag_id='rca_sales_pipeline',
    description='Build the silver and gold models for the RCA workshop.',
    start_date=dt.datetime(2026, 8, 1),
    schedule_interval=None,
    catchup=False,
    tags=['rca-workshop', 'participant'],
) as dag:
    project_root = os.environ.get('AIRFLOW_HOME', '/opt/airflow')

    def model_task(layer, model_name):
        return BashOperator(
            task_id=model_name,
            bash_command=(
                'python scripts/run_sql.py '
                f'scripts/sql/{layer}/{model_name}.sql'
            ),
            cwd=project_root,
        )

    stg_customers = model_task('silver', 'stg_customers')
    stg_products = model_task('silver', 'stg_products')
    stg_orders = model_task('silver', 'stg_orders')
    stg_order_items = model_task('silver', 'stg_order_items')
    int_order_items_enriched = model_task(
        'silver', 'int_order_items_enriched'
    )
    int_order_totals = model_task('silver', 'int_order_totals')
    int_customer_orders = model_task('silver', 'int_customer_orders')
    daily_sales = model_task('gold', 'daily_sales')
    customer_sales = model_task('gold', 'customer_sales')
    product_performance = model_task('gold', 'product_performance')

    [stg_orders, stg_order_items, stg_products] >> int_order_items_enriched
    int_order_items_enriched >> [int_order_totals, product_performance]
    int_order_totals >> [int_customer_orders, daily_sales]
    [stg_customers, int_customer_orders] >> customer_sales
