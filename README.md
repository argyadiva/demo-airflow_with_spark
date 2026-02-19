# Airflow with Pyspark inside

- build docker using docker `docker build -t airflow-spark .`
- run docker compose using `docker compose -f airflow.yaml up -d`

# Running the python script on Airflow
- run the script by `sudo -u airflow python /opt/airflow/scripts/script.py`