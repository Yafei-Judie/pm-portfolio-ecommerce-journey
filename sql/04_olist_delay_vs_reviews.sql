-- Does a late delivery actually cost review score? And by how much?
-- Dataset: Olist Brazilian E-Commerce (loaded via SETUP.md into DuckDB/SQLite)
-- Question this answers: is delivery timing a real driver of customer satisfaction here,
-- or is it noise next to product quality? This is the number the PRD leans on.

WITH delivered_orders AS (
  SELECT
    o.order_id,
    DATE_DIFF(
      CAST(o.order_delivered_customer_date AS DATE),
      CAST(o.order_estimated_delivery_date AS DATE),
      DAY
    ) AS days_late
  FROM orders o
  WHERE o.order_status = 'delivered'
    AND o.order_delivered_customer_date IS NOT NULL
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
    END AS delivery_bucket
  FROM delivered_orders
)

SELECT
  b.delivery_bucket,
  COUNT(*) AS orders,
  ROUND(AVG(r.review_score), 2) AS avg_review_score,
  ROUND(100.0 * SUM(CASE WHEN r.review_score <= 2 THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_1_or_2_star
FROM bucketed b
JOIN order_reviews r ON r.order_id = b.order_id
GROUP BY b.delivery_bucket
ORDER BY
  CASE b.delivery_bucket
    WHEN '7+ days late' THEN 1
    WHEN '1-7 days late' THEN 2
    WHEN 'on the estimated day' THEN 3
    WHEN 'early (1-7 days)' THEN 4
    ELSE 5
  END;
