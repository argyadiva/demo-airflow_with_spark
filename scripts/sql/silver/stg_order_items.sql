DROP TABLE IF EXISTS silver.stg_order_items;

CREATE TABLE silver.stg_order_items AS
SELECT
    order_item_id,
    order_id,
    product_id,
    quantity::INTEGER AS quantity,
    unit_price::NUMERIC(12, 2) AS unit_price,
    ingestion_batch_id,
    ingested_at
FROM bronze.order_items;

CREATE INDEX ix_stg_order_items_order_item_id
    ON silver.stg_order_items (order_item_id);

CREATE INDEX ix_stg_order_items_order_id
    ON silver.stg_order_items (order_id);
