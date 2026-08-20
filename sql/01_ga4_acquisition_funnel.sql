-- Acquisition and on-site funnel: view_item -> add_to_cart -> begin_checkout -> purchase
-- Dataset: bigquery-public-data.ga4_obfuscated_sample_ecommerce
-- Question this answers: where in the funnel do we lose the most users, and is that
-- consistent across the three months in the sample?

WITH events AS (
  SELECT
    user_pseudo_id,
    event_name,
    PARSE_DATE('%Y%m%d', event_date) AS event_date
  FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
  WHERE event_name IN ('view_item', 'add_to_cart', 'begin_checkout', 'purchase')
),

funnel_users AS (
  SELECT
    DATE_TRUNC(event_date, MONTH) AS month,
    COUNT(DISTINCT IF(event_name = 'view_item', user_pseudo_id, NULL)) AS viewed_item,
    COUNT(DISTINCT IF(event_name = 'add_to_cart', user_pseudo_id, NULL)) AS added_to_cart,
    COUNT(DISTINCT IF(event_name = 'begin_checkout', user_pseudo_id, NULL)) AS began_checkout,
    COUNT(DISTINCT IF(event_name = 'purchase', user_pseudo_id, NULL)) AS purchased
  FROM events
  GROUP BY month
)

SELECT
  month,
  viewed_item,
  added_to_cart,
  began_checkout,
  purchased,
  ROUND(SAFE_DIVIDE(added_to_cart, viewed_item) * 100, 1)   AS pct_view_to_cart,
  ROUND(SAFE_DIVIDE(began_checkout, added_to_cart) * 100, 1) AS pct_cart_to_checkout,
  ROUND(SAFE_DIVIDE(purchased, began_checkout) * 100, 1)     AS pct_checkout_to_purchase,
  ROUND(SAFE_DIVIDE(purchased, viewed_item) * 100, 1)        AS pct_overall_conversion
FROM funnel_users
ORDER BY month;
