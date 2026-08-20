-- Channel performance: which acquisition source/medium actually converts, not just drives traffic
-- Dataset: bigquery-public-data.ga4_obfuscated_sample_ecommerce
-- Question this answers: if we had a marketing budget to reallocate, which channel earns it?
--
-- Note: metric is distinct users who triggered session_start, not a true session count.
-- An earlier version of this query joined on the ga_session_id event param to build a real
-- session ID and returned zero rows — that param isn't reliably populated for session_start
-- events in this obfuscated sample. Distinct users is the more robust substitute and still
-- answers the reach question honestly; it just slightly understates users with multiple
-- sessions in the window.

SELECT
  COALESCE(source, '(direct)') AS source,
  COALESCE(medium, '(none)') AS medium,
  COUNT(DISTINCT IF(event_name = 'session_start', user_pseudo_id, NULL)) AS users_started_session,
  COUNT(DISTINCT IF(event_name = 'purchase', user_pseudo_id, NULL)) AS purchasers,
  ROUND(SUM(IF(event_name = 'purchase', purchase_revenue, 0)), 2) AS revenue
FROM (
  SELECT
    user_pseudo_id,
    traffic_source.source AS source,
    traffic_source.medium AS medium,
    event_name,
    ecommerce.purchase_revenue_in_usd AS purchase_revenue
  FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
  WHERE event_name IN ('session_start', 'purchase')
)
GROUP BY source, medium
HAVING users_started_session > 50
ORDER BY revenue DESC;
