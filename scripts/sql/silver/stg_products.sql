DROP TABLE IF EXISTS silver.stg_products;

CREATE TABLE silver.stg_products AS
SELECT
    product_id,
    INITCAP(TRIM(product_name)) AS product_name,
    LOWER(TRIM(category)) AS category,
    unit_price::NUMERIC(12, 2) AS current_unit_price,
    ingestion_batch_id,
    ingested_at
FROM bronze.products;

CREATE UNIQUE INDEX ux_stg_products_product_id
    ON silver.stg_products (product_id);
