# Airflow with Pyspark inside

- build docker using docker `docker build -t airflow-spark .`
- run docker compose using `docker compose -f airflow.yaml up -d`

# Running the python script on Airflow
- From the project root inside an Airflow container, run `python scripts/extract.py`.
- The ETL DAG runs the scripts with the same project-relative paths.

## Configuration

Copy `.env.example` to `.env` and set the external PostgreSQL values used by
`scripts/load.py`: `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, and
`DB_PORT`. Never commit `.env` or real credentials.

## Project layout

```text
.
├── dags/       # Airflow DAG definitions
├── scripts/    # ETL scripts
├── data/       # Mounted pipeline input/output data
└── logs/       # Airflow runtime logs
```

The container keeps Airflow's internal home at `/opt/airflow`, but pipeline
commands and data references are intentionally relative to the project root.
