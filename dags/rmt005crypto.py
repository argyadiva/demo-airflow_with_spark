import datetime as dt
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

    project_root = '{{ task.dag.folder }}/..'

    python_extract = BashOperator(
        task_id='python_extract',
        bash_command='python scripts/extract.py',
        cwd=project_root,
    )
    python_transform = BashOperator(
        task_id='python_transform',
        bash_command='python scripts/transform.py',
        cwd=project_root,
    )
    python_load = BashOperator(
        task_id='python_load',
        bash_command='python scripts/load.py',
        cwd=project_root,
    )
    

python_extract >> python_transform >> python_load
