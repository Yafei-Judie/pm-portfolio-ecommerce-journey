-- Freight cost as a share of item price, by category. Not directly about
-- delivery timing, but relevant business context for the same PRD: if
-- freight already eats 20-30% of price in some categories, a fix that adds
-- cost (faster/pricier shipping) has a much tighter margin ceiling than one
-- that doesn't (a notification).
-- Dataset: Olist Brazilian E-Commerce (loaded via SETUP.md into SQLite)

SELECT
  ct.product_category_name_english AS category,
  COUNT(*) AS items,
  ROUND(AVG(oi.price), 2) AS avg_price,
  ROUND(AVG(oi.freight_value), 2) AS avg_freight,
  ROUND(100.0 * AVG(oi.freight_value) / AVG(oi.price), 1) AS freight_pct_of_price
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
JOIN category_translation ct ON ct.product_category_name = p.product_category_name
GROUP BY category
HAVING items >= 200
ORDER BY freight_pct_of_price DESC
LIMIT 15;
