DROP TABLE IF EXISTS silver.stg_orders;

CREATE TABLE silver.stg_orders AS
SELECT
    order_id,
    customer_id,
    order_ts,
    order_ts::DATE AS order_date,
    LOWER(TRIM(status)) AS status,
    order_total::NUMERIC(14, 2) AS source_order_total,
    ingestion_batch_id,
    ingested_at
FROM bronze.orders;

CREATE UNIQUE INDEX ux_stg_orders_order_id
    ON silver.stg_orders (order_id);
