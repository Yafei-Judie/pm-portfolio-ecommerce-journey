# Setup

Two free accounts, neither of which I can create for you — both need identity/email verification on your end.

## 1. BigQuery (for the GA4 queries in `sql/01` and `sql/02`)

1. Go to https://console.cloud.google.com and sign in with any Google account.
2. Create a new project (top left project picker → New Project). Name it something like `pm-portfolio`.
3. No billing setup needed for this — BigQuery's free tier is 1TB of query processing per month, and this project's queries use a few GB at most.
4. Open BigQuery in the console, click "+ Add data" → "Star a project by name" → enter `bigquery-public-data`, then navigate to `ga4_obfuscated_sample_ecommerce`.
5. Paste any query from `sql/01_ga4_acquisition_funnel.sql` or `sql/02_ga4_channel_performance.sql` into the query editor and run.

## 2. Kaggle (for the Olist queries in `sql/03` and `sql/04`)

1. Go to https://www.kaggle.com and create a free account.
2. Go to https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce and click Download (or use the Kaggle API — Account → Create New Token — if you want it scriptable).
3. Unzip into a local folder, e.g. `analysis/olist-data/`.
4. Load the CSVs into DuckDB or SQLite so the SQL in `sql/03` and `sql/04` runs unmodified:

```bash
# DuckDB is the fastest path — no server, reads CSV directly
brew install duckdb   # or download from duckdb.org if brew isn't set up yet
cd "analysis/olist-data"
duckdb olist.duckdb
```

Then inside the duckdb shell:

```sql
CREATE TABLE orders AS SELECT * FROM read_csv_auto('olist_orders_dataset.csv');
CREATE TABLE order_reviews AS SELECT * FROM read_csv_auto('olist_order_reviews_dataset.csv');
CREATE TABLE order_items AS SELECT * FROM read_csv_auto('olist_order_items_dataset.csv');
CREATE TABLE customers AS SELECT * FROM read_csv_auto('olist_customers_dataset.csv');
```

Once loaded, run the queries in `sql/03_olist_delivery_performance.sql` and `sql/04_olist_delay_vs_reviews.sql` directly in the duckdb shell.

## Once data is flowing

Tell me and I'll take the real query output and write up `analysis/findings.md` with actual charts — nothing in this repo states a number that didn't come out of a query you ran.
