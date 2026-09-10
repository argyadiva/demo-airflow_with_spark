DROP TABLE IF EXISTS silver.int_order_totals;

CREATE TABLE silver.int_order_totals AS
SELECT
    order_id,
    customer_id,
    order_date,
    COUNT(*)::INTEGER AS item_row_count,
    SUM(quantity)::INTEGER AS total_units,
    SUM(line_revenue)::NUMERIC(14, 2) AS order_revenue
FROM silver.int_order_items_enriched
WHERE status = 'completed'
GROUP BY
    order_id,
    customer_id,
    order_date;

CREATE UNIQUE INDEX ux_int_order_totals_order_id
    ON silver.int_order_totals (order_id);
