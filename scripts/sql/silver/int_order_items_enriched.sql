DROP TABLE IF EXISTS silver.int_order_items_enriched;

CREATE TABLE silver.int_order_items_enriched AS
SELECT
    item.order_item_id,
    item.order_id,
    orders.customer_id,
    orders.order_date,
    orders.status,
    item.product_id,
    products.product_name,
    products.category,
    item.quantity,
    item.unit_price,
    (item.quantity * item.unit_price)::NUMERIC(14, 2) AS line_revenue,
    item.ingestion_batch_id,
    item.ingested_at
FROM silver.stg_order_items AS item
INNER JOIN silver.stg_orders AS orders
    ON item.order_id = orders.order_id
INNER JOIN silver.stg_products AS products
    ON item.product_id = products.product_id;

CREATE INDEX ix_int_order_items_enriched_order_id
    ON silver.int_order_items_enriched (order_id);

CREATE INDEX ix_int_order_items_enriched_product_id
    ON silver.int_order_items_enriched (product_id);
