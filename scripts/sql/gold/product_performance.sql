DROP TABLE IF EXISTS gold.product_performance;

CREATE TABLE gold.product_performance AS
SELECT
    product_id,
    product_name,
    category,
    COUNT(DISTINCT order_id)::INTEGER AS completed_order_count,
    SUM(quantity)::INTEGER AS units_sold,
    SUM(line_revenue)::NUMERIC(14, 2) AS revenue,
    CURRENT_TIMESTAMP AS computed_at
FROM silver.int_order_items_enriched
WHERE status = 'completed'
GROUP BY
    product_id,
    product_name,
    category;

CREATE UNIQUE INDEX ux_product_performance_product_id
    ON gold.product_performance (product_id);
