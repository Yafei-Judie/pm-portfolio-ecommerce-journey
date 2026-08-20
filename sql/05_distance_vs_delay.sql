-- Does physical distance between seller and customer explain lateness better
-- than state alone? Real haversine distance (km) from averaged zip-prefix
-- lat/lng in the geolocation table, bucketed, against on-time performance.
-- Dataset: Olist Brazilian E-Commerce (loaded via SETUP.md into SQLite)
--
-- Takes the first order_item per order as a single representative seller —
-- most orders in this dataset are single-item, and multi-seller orders would
-- need a different distance definition (nearest seller? furthest? average?)
-- that the PRD doesn't need resolved for this question.

WITH zip_geo AS (
  SELECT geolocation_zip_code_prefix AS zip, AVG(geolocation_lat) AS lat, AVG(geolocation_lng) AS lng
  FROM geolocation
  GROUP BY geolocation_zip_code_prefix
),
first_item AS (
  SELECT order_id, seller_id
  FROM order_items
  WHERE order_item_id = 1
),
order_geo AS (
  SELECT
    o.order_id,
    CAST(julianday(o.order_delivered_customer_date) - julianday(o.order_estimated_delivery_date) AS INTEGER) AS days_late,
    cg.lat AS c_lat, cg.lng AS c_lng,
    sg.lat AS s_lat, sg.lng AS s_lng
  FROM orders o
  JOIN customers c ON c.customer_id = o.customer_id
  JOIN zip_geo cg ON cg.zip = c.customer_zip_code_prefix
  JOIN first_item fi ON fi.order_id = o.order_id
  JOIN sellers s ON s.seller_id = fi.seller_id
  JOIN zip_geo sg ON sg.zip = s.seller_zip_code_prefix
  WHERE o.order_status = 'delivered'
    AND o.order_delivered_customer_date IS NOT NULL AND o.order_delivered_customer_date != ''
),
with_distance AS (
  SELECT
    order_id, days_late,
    -- Haversine formula, clamped to [-1, 1] before acos to avoid a domain
    -- error from floating-point drift when a seller ships to their own zip.
    6371 * acos(
      MIN(1.0, MAX(-1.0,
        cos(radians(c_lat)) * cos(radians(s_lat)) * cos(radians(s_lng) - radians(c_lng))
        + sin(radians(c_lat)) * sin(radians(s_lat))
      ))
    ) AS distance_km
  FROM order_geo
)
SELECT
  CASE
    WHEN distance_km < 50 THEN '1. Under 50km (same metro)'
    WHEN distance_km < 300 THEN '2. 50-300km'
    WHEN distance_km < 800 THEN '3. 300-800km'
    WHEN distance_km < 1500 THEN '4. 800-1500km'
    ELSE '5. 1500km+'
  END AS distance_bucket,
  COUNT(*) AS orders,
  ROUND(AVG(distance_km), 0) AS avg_km_in_bucket,
  ROUND(AVG(days_late), 2) AS avg_days_late,
  ROUND(100.0 * SUM(CASE WHEN days_late > 0 THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_late
FROM with_distance
GROUP BY distance_bucket
ORDER BY distance_bucket;
