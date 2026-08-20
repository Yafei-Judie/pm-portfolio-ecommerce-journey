-- Channel performance: which acquisition source/medium actually converts, not just drives traffic
-- Dataset: bigquery-public-data.ga4_obfuscated_sample_ecommerce
-- Question this answers: if we had a marketing budget to reallocate, which channel earns it?

WITH sessions AS (
  SELECT
    user_pseudo_id,
    (SELECT value.string_value FROM UNNEST(event_params) WHERE key = 'ga_session_id') AS session_id,
    traffic_source.source AS source,
    traffic_source.medium AS medium,
    event_name,
    ecommerce.purchase_revenue_in_usd AS purchase_revenue
  FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
  WHERE event_name IN ('session_start', 'purchase')
)

SELECT
  COALESCE(source, '(direct)') AS source,
  COALESCE(medium, '(none)') AS medium,
  COUNT(DISTINCT IF(event_name = 'session_start', CONCAT(user_pseudo_id, session_id), NULL)) AS sessions,
  COUNT(DISTINCT IF(event_name = 'purchase', user_pseudo_id, NULL)) AS purchasers,
  ROUND(SUM(IF(event_name = 'purchase', purchase_revenue, 0)), 2) AS revenue,
  ROUND(SAFE_DIVIDE(
    COUNT(DISTINCT IF(event_name = 'purchase', user_pseudo_id, NULL)),
    COUNT(DISTINCT IF(event_name = 'session_start', CONCAT(user_pseudo_id, session_id), NULL))
  ) * 100, 2) AS conversion_rate_pct
FROM sessions
GROUP BY source, medium
HAVING sessions > 50
ORDER BY revenue DESC;
