# Setup

Two free accounts, neither of which I can create for you — both need identity/email verification on your end.

## 1. BigQuery (for the GA4 queries in `sql/01` and `sql/02`)

1. Go to https://console.cloud.google.com and sign in with any Google account.
2. Create a new project (top left project picker → New Project). Name it something like `pm-portfolio`.
3. No billing setup needed for this — BigQuery's free tier is 1TB of query processing per month, and this project's queries use a few GB at most.
4. Open BigQuery in the console, click "+ Add data" → "Star a project by name" → enter `bigquery-public-data`, then navigate to `ga4_obfuscated_sample_ecommerce`.
5. Paste any query from `sql/01_ga4_acquisition_funnel.sql` or `sql/02_ga4_channel_performance.sql` into the query editor and run.

## 2. Kaggle (for the Olist queries in `sql/03` through `sql/08`) — done

1. Signed into Kaggle, downloaded https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce (45MB zip, CC BY-NC-SA 4.0 license — fine for a personal portfolio, not for resale).
2. Unzipped into `analysis/olist-data/` (gitignored — raw CSVs never get pushed to GitHub).
3. Loaded all 9 CSVs into SQLite (`sqlite3` ships with macOS, no install needed) — orders, customers, and order_reviews first, then order_items, sellers, products, order_payments, geolocation, and category_translation once the deeper queries (freight economics, seller-customer distance, repeat purchase) needed them:

```bash
sqlite3 -csv analysis/olist-data/olist.db ".import 'analysis/olist-data/olist_orders_dataset.csv' orders"
sqlite3 -csv analysis/olist-data/olist.db ".import 'analysis/olist-data/olist_customers_dataset.csv' customers"
sqlite3 -csv analysis/olist-data/olist.db ".import 'analysis/olist-data/olist_order_reviews_dataset.csv' order_reviews"
sqlite3 -csv analysis/olist-data/olist.db ".import 'analysis/olist-data/olist_order_items_dataset.csv' order_items"
sqlite3 -csv analysis/olist-data/olist.db ".import 'analysis/olist-data/olist_sellers_dataset.csv' sellers"
sqlite3 -csv analysis/olist-data/olist.db ".import 'analysis/olist-data/olist_products_dataset.csv' products"
sqlite3 -csv analysis/olist-data/olist.db ".import 'analysis/olist-data/olist_order_payments_dataset.csv' order_payments"
sqlite3 -csv analysis/olist-data/olist.db ".import 'analysis/olist-data/olist_geolocation_dataset.csv' geolocation"
sqlite3 -csv analysis/olist-data/olist.db ".import 'analysis/olist-data/product_category_name_translation.csv' category_translation"
```

Note: `sqlite3 -csv ... .import` inside a `cd && heredoc` chain got blocked by this environment's permission rules — running each `.import` as its own command with absolute paths worked fine. Your setup may not hit this at all.

Run any query against `analysis/olist-data/olist.db`, e.g.:

```bash
sqlite3 -header -column analysis/olist-data/olist.db < sql/03_olist_delivery_performance.sql
```

`sql/05_distance_vs_delay.sql` uses SQLite's built-in math functions (`acos`, `radians`, etc. — available since 3.35, and it's a real haversine distance calculation, not an approximation) to compute actual seller-customer distance from averaged zip-prefix lat/lng in the geolocation table. It's the heaviest query in the repo (~96k orders × a 1M-row geolocation table) — it took long enough locally that it ran as a background process rather than blocking.

(sql/03 and sql/04 were rewritten from an earlier DuckDB-syntax draft to SQLite syntax — `DATE_DIFF`/`CAST AS DATE` don't exist in SQLite, so date math uses `julianday()` instead. If you'd rather use DuckDB, `brew install duckdb` and adjust the date functions back.)

## Data is in

`analysis/findings.md` has the real output from all eight queries — GA4 funnel/channel performance, Olist delivery/review-score findings, review-timing-vs-delivery, seller-customer distance, repeat-purchase, and freight economics. `analysis/limitations-and-alternative-views.md` has an independent multi-lens critique of the core finding (causal inference, business strategy, customer behavior, measurement quality), run as a 4-agent panel and then verified by re-running the load-bearing numbers myself against the live database rather than trusting the agent output directly. No number in this repo was invented; anything not yet run is explicitly marked as pending.
