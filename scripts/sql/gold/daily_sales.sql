DROP TABLE IF EXISTS gold.daily_sales;

CREATE TABLE gold.daily_sales AS
SELECT
    order_date,
    COUNT(*)::INTEGER AS completed_order_count,
    SUM(total_units)::INTEGER AS total_units,
    SUM(order_revenue)::NUMERIC(14, 2) AS revenue,
    ROUND(AVG(order_revenue), 2)::NUMERIC(14, 2) AS average_order_value,
    CURRENT_TIMESTAMP AS computed_at
FROM silver.int_order_totals
GROUP BY order_date;

CREATE UNIQUE INDEX ux_daily_sales_order_date
    ON gold.daily_sales (order_date);
