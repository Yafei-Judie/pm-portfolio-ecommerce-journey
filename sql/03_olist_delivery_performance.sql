-- On-time delivery rate: does the actual delivery date beat the estimated delivery date?
-- Dataset: Olist Brazilian E-Commerce (loaded via SETUP.md into DuckDB/SQLite)
-- Question this answers: what % of orders miss their promised delivery window, and does
-- that vary by customer state (proxy for carrier/region performance)?

WITH delivered_orders AS (
  SELECT
    o.order_id,
    c.customer_state,
    o.order_purchase_timestamp,
    o.order_estimated_delivery_date,
    o.order_delivered_customer_date,
    DATE_DIFF(
      CAST(o.order_delivered_customer_date AS DATE),
      CAST(o.order_estimated_delivery_date AS DATE),
      DAY
    ) AS days_late  -- positive = late, negative = early, 0 = on the day
  FROM orders o
  JOIN customers c ON c.customer_id = o.customer_id
  WHERE o.order_status = 'delivered'
    AND o.order_delivered_customer_date IS NOT NULL
)

SELECT
  customer_state,
  COUNT(*) AS delivered_orders,
  ROUND(AVG(days_late), 2) AS avg_days_late,
  ROUND(100.0 * SUM(CASE WHEN days_late > 0 THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_late,
  ROUND(100.0 * SUM(CASE WHEN days_late <= 0 THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_on_time_or_early
FROM delivered_orders
GROUP BY customer_state
HAVING COUNT(*) >= 30
ORDER BY pct_late DESC;
