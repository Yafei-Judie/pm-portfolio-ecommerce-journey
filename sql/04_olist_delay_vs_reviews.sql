-- Does a late delivery actually cost review score? And by how much?
-- Dataset: Olist Brazilian E-Commerce (loaded via SETUP.md into SQLite)
-- Question this answers: is delivery timing a real driver of customer satisfaction here,
-- or is it noise next to product quality? This is the number the PRD leans on.
--
-- review_score is imported as TEXT by sqlite3's CSV importer, so it's cast explicitly
-- before aggregating.

WITH delivered_orders AS (
  SELECT
    o.order_id,
    CAST(julianday(o.order_delivered_customer_date) - julianday(o.order_estimated_delivery_date) AS INTEGER) AS days_late
  FROM orders o
  WHERE o.order_status = 'delivered'
    AND o.order_delivered_customer_date IS NOT NULL AND o.order_delivered_customer_date != ''
),

bucketed AS (
  SELECT
    order_id,
    CASE
      WHEN days_late > 7 THEN '7+ days late'
      WHEN days_late > 0 THEN '1-7 days late'
      WHEN days_late = 0 THEN 'on the estimated day'
      WHEN days_late >= -7 THEN 'early (1-7 days)'
      ELSE 'early (8+ days)'
    END AS delivery_bucket,
    CASE
      WHEN days_late > 7 THEN 1
      WHEN days_late > 0 THEN 2
      WHEN days_late = 0 THEN 3
      WHEN days_late >= -7 THEN 4
      ELSE 5
    END AS sort_order
  FROM delivered_orders
)

SELECT
  b.delivery_bucket,
  COUNT(*) AS orders,
  ROUND(AVG(CAST(r.review_score AS REAL)), 2) AS avg_review_score,
  ROUND(100.0 * SUM(CASE WHEN CAST(r.review_score AS INTEGER) <= 2 THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_1_or_2_star
FROM bucketed b
JOIN order_reviews r ON r.order_id = b.order_id
GROUP BY b.delivery_bucket, b.sort_order
ORDER BY b.sort_order;
