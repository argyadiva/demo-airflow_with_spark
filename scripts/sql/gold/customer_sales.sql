DROP TABLE IF EXISTS gold.customer_sales;

CREATE TABLE gold.customer_sales AS
SELECT
    customers.customer_id,
    customers.customer_name,
    customers.segment,
    customers.country,
    COALESCE(SUM(metrics.completed_order_count), 0)::INTEGER
        AS completed_order_count,
    COALESCE(SUM(metrics.total_units), 0)::INTEGER AS total_units,
    COALESCE(SUM(metrics.revenue), 0)::NUMERIC(14, 2) AS revenue,
    CURRENT_TIMESTAMP AS computed_at
FROM silver.stg_customers AS customers
LEFT JOIN silver.int_customer_orders AS metrics
    ON customers.customer_id = metrics.customer_id
GROUP BY
    customers.customer_id,
    customers.customer_name,
    customers.segment,
    customers.country;

CREATE UNIQUE INDEX ux_customer_sales_customer_id
    ON gold.customer_sales (customer_id);
