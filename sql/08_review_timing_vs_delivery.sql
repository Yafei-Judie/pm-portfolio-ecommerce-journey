-- Do customers usually review AFTER they receive the package, or before?
-- This matters because sql/04's whole premise assumes reviews reflect a
-- completed delivery experience. If most reviews in the "7+ days late"
-- bucket were submitted before the package arrived, the review is really
-- measuring "still waiting, overdue" rather than "received it late, upset
-- about it" — a different (and arguably stronger) case for a proactive
-- notification, but a different metric design for measuring whether the
-- notification works.
-- Dataset: Olist Brazilian E-Commerce (loaded via SETUP.md into SQLite)

WITH delivered_orders AS (
  SELECT
    o.order_id,
    o.order_delivered_customer_date,
    CAST(julianday(o.order_delivered_customer_date) - julianday(o.order_estimated_delivery_date) AS INTEGER) AS days_late
  FROM orders o
  WHERE o.order_status = 'delivered'
    AND o.order_delivered_customer_date IS NOT NULL AND o.order_delivered_customer_date != ''
),
bucketed AS (
  SELECT
    order_id, order_delivered_customer_date,
    CASE
      WHEN days_late > 7 THEN '7+ days late'
      WHEN days_late > 0 THEN '1-7 days late'
      WHEN days_late = 0 THEN 'on the estimated day'
      WHEN days_late >= -7 THEN 'early (1-7 days)'
      ELSE 'early (8+ days)'
    END AS delivery_bucket,
    CASE
      WHEN days_late > 7 THEN 1 WHEN days_late > 0 THEN 2 WHEN days_late = 0 THEN 3
      WHEN days_late >= -7 THEN 4 ELSE 5
    END AS sort_order
  FROM delivered_orders
)
SELECT
  b.delivery_bucket,
  COUNT(*) AS orders,
  SUM(CASE WHEN r.review_answer_timestamp < b.order_delivered_customer_date THEN 1 ELSE 0 END) AS answered_before_delivery,
  ROUND(100.0 * SUM(CASE WHEN r.review_answer_timestamp < b.order_delivered_customer_date THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_before_delivery
FROM bucketed b
JOIN order_reviews r ON r.order_id = b.order_id
GROUP BY b.delivery_bucket, b.sort_order
ORDER BY b.sort_order;
