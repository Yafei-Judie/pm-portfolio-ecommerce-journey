-- Does a late FIRST order actually cost repeat business, not just a review
-- score? Uses customer_unique_id (persists across orders for the same real
-- person, unlike customer_id which is one-per-order in this dataset).
-- Dataset: Olist Brazilian E-Commerce (loaded via SETUP.md into SQLite)

WITH customer_orders AS (
  SELECT
    c.customer_unique_id,
    o.order_id,
    o.order_purchase_timestamp,
    ROW_NUMBER() OVER (PARTITION BY c.customer_unique_id ORDER BY o.order_purchase_timestamp) AS order_rank,
    COUNT(*) OVER (PARTITION BY c.customer_unique_id) AS total_orders_by_customer,
    CAST(julianday(o.order_delivered_customer_date) - julianday(o.order_estimated_delivery_date) AS INTEGER) AS days_late
  FROM orders o
  JOIN customers c ON c.customer_id = o.customer_id
  WHERE o.order_status = 'delivered'
    AND o.order_delivered_customer_date IS NOT NULL AND o.order_delivered_customer_date != ''
),
first_orders AS (
  SELECT
    customer_unique_id,
    CASE WHEN days_late > 0 THEN 'first order was late' ELSE 'first order on-time/early' END AS first_order_status,
    CASE WHEN total_orders_by_customer > 1 THEN 1 ELSE 0 END AS became_repeat_customer
  FROM customer_orders
  WHERE order_rank = 1
)
SELECT
  first_order_status,
  COUNT(*) AS customers,
  SUM(became_repeat_customer) AS became_repeat,
  ROUND(100.0 * SUM(became_repeat_customer) / COUNT(*), 2) AS pct_became_repeat
FROM first_orders
GROUP BY first_order_status;
