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


with DAG('coin_scrapper2',
         default_args=default_args,
         schedule_interval='*/5 * * * *',
         catchup=False,
         ) as dag:

    project_root = os.environ.get('AIRFLOW_HOME', '/opt/airflow')

    echo_java = BashOperator(
        task_id='echo_java',
        bash_command='whoami',
        cwd=project_root,
    )
    echo_path = BashOperator(
        task_id='echo_path',
        bash_command='python -c "from pyspark.sql import SparkSession; spark = SparkSession.builder.getOrCreate()"',
        cwd=project_root,
    )
    

echo_java >> echo_path
