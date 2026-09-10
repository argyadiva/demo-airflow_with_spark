DROP TABLE IF EXISTS silver.int_customer_orders;

CREATE TABLE silver.int_customer_orders AS
SELECT
    customer_id,
    order_date,
    COUNT(*)::INTEGER AS completed_order_count,
    SUM(total_units)::INTEGER AS total_units,
    SUM(order_revenue)::NUMERIC(14, 2) AS revenue
FROM silver.int_order_totals
GROUP BY
    customer_id,
    order_date;

CREATE UNIQUE INDEX ux_int_customer_orders_customer_date
    ON silver.int_customer_orders (customer_id, order_date);
