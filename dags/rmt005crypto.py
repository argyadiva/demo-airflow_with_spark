import datetime as dt
import os
from datetime import timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator


default_args = {
    'owner': 'terry',
    'start_date': dt.datetime(2025, 1, 8),
    'retries': 1,
    'retry_delay': dt.timedelta(minutes=600),
}


with DAG('rmt_005_crypto_etl',
         default_args=default_args,
         schedule_interval='*/5 * * * *',
         catchup=False,
         ) as dag:

    project_root = os.environ.get('AIRFLOW_HOME', '/opt/airflow')

    bronze = BashOperator(
        task_id='bronze',
        bash_command='python scripts/bronze.py',
        cwd=project_root,
    )
    silver = BashOperator(
        task_id='silver',
        bash_command='python scripts/silver.py',
        cwd=project_root,
    )
    gold = BashOperator(
        task_id='gold',
        bash_command='python scripts/gold.py',
        cwd=project_root,
    )
    

bronze >> silver >> gold
