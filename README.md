# Airflow with PySpark inside

## Airflow

Build and start the project:

```text
docker build -t airflow-spark .
docker compose -f airflow.yaml up -d
```

The Airflow DAG runs the three layers in order:

```text
scripts/bronze.py -> scripts/silver.py -> scripts/gold.py
```

The container keeps Airflow's internal home at `/opt/airflow`, but task
commands use project-relative paths.

## Configuration

Copy `.env.example` to `.env` and set the PostgreSQL values used by the
pipeline scripts:

```text
DB_HOST=...
DB_NAME=...
DB_USER=...
DB_PASSWORD=...
DB_PORT=5432
```

Never commit `.env` or real credentials.

## Layers

- `bronze.py` fetches CoinGecko and Frankfurter and stores the complete API responses in `bronze_coin_gecko` and `bronze_currency_rate` as JSONB.
- `silver.py` matches the two raw bronze tables by `batch_id`, calculates USD and IDR prices, and writes `silver_coin_prices`.
- `gold.py` calculates latest prices and observed 24-hour statistics in `gold_latest_coin_stats`.

## Walkthrough notebooks

The notebooks are educational mirrors of the production scripts and run
locally, outside Airflow.

Create a local environment from the repository root:

```text
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-notebook.txt
jupyter notebook
```

Run them in this order:

1. `notebooks/bronze_walkthrough.ipynb`
2. Inspect `bronze_coin_gecko` and `bronze_currency_rate`.
3. `notebooks/silver_walkthrough.ipynb`
4. Inspect `silver_coin_prices`.
5. `notebooks/gold_walkthrough.ipynb`
6. Inspect `gold_latest_coin_stats`.

The notebooks load database configuration from `.env` and never display
password values.

## Project layout

```text
.
├── dags/        # Airflow DAG definitions
├── scripts/     # Production bronze, silver, and gold scripts
├── notebooks/   # Local educational walkthroughs
├── data/        # Mounted local data directory
└── logs/        # Airflow runtime logs
```
