import datetime as dt
import os

from airflow import DAG
from airflow.operators.bash import BashOperator


with DAG(
    dag_id='rca_sales_seed',
    description='Create the deterministic bronze data for the RCA workshop.',
    start_date=dt.datetime(2026, 8, 1),
    schedule_interval=None,
    catchup=False,
    tags=['rca-workshop', 'setup'],
) as dag:
    project_root = os.environ.get('AIRFLOW_HOME', '/opt/airflow')

    load_bronze = BashOperator(
        task_id='load_bronze',
        bash_command='python scripts/load.py',
        cwd=project_root,
    )
