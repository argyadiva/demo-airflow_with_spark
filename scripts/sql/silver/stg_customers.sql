DROP TABLE IF EXISTS silver.stg_customers;

CREATE TABLE silver.stg_customers AS
SELECT
    customer_id,
    INITCAP(TRIM(customer_name)) AS customer_name,
    LOWER(TRIM(segment)) AS segment,
    INITCAP(TRIM(country)) AS country,
    created_at,
    ingestion_batch_id,
    ingested_at
FROM bronze.customers;

CREATE UNIQUE INDEX ux_stg_customers_customer_id
    ON silver.stg_customers (customer_id);
