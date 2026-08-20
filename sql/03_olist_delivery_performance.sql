-- On-time delivery rate: does the actual delivery date beat the estimated delivery date?
-- Dataset: Olist Brazilian E-Commerce (loaded via SETUP.md into SQLite)
-- Question this answers: what % of orders miss their promised delivery window, and does
-- that vary by customer state (proxy for carrier/region performance)?
--
-- SQLite has no DATE_DIFF or DATE type — dates are stored as ISO8601 text, so day
-- differences use julianday() subtraction instead.

WITH delivered_orders AS (
  SELECT
    o.order_id,
    c.customer_state,
    CAST(julianday(o.order_delivered_customer_date) - julianday(o.order_estimated_delivery_date) AS INTEGER) AS days_late
    -- positive = late, negative = early, 0 = on the day
  FROM orders o
  JOIN customers c ON c.customer_id = o.customer_id
  WHERE o.order_status = 'delivered'
    AND o.order_delivered_customer_date IS NOT NULL AND o.order_delivered_customer_date != ''
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
