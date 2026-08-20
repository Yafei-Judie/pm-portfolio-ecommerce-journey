# End-to-End E-Commerce Customer Journey: A PM Case Study

A self-directed product management case study covering the full customer journey in an e-commerce business: discovery, purchase, fulfillment, delivery, and post-purchase experience. Built to practice the exact skill set that shows up in Associate/entry-level technical PM postings: SQL, GA4-style analytics, prioritization, PRD writing, QA collaboration, and AI-assisted prototyping.

## Why this project

Most PM portfolio pieces are either pure case-study writeups (no data, no proof of technical fluency) or pure SQL/dashboard projects (no product thinking). This one does both: real queries against real public datasets, feeding a real product decision, documented the way a PM actually documents it.

## Datasets

- **[GA4 sample e-commerce dataset](https://developers.google.com/analytics/bigquery/web-ecommerce-demo-dataset)** (`bigquery-public-data.ga4_obfuscated_sample_ecommerce`) — real BigQuery event export from the Google Merchandise Store, Nov 2020–Jan 2021. Used for the acquisition and on-site funnel analysis. Free to query in BigQuery's 1TB/month free tier.
- **[Olist Brazilian E-Commerce dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)** (Kaggle) — ~100k real orders with purchase timestamps, estimated vs. actual delivery dates, and customer review scores. Used for the fulfillment/delivery and post-purchase analysis.

See `SETUP.md` for exactly how to get both connected (both need a free account — Google Cloud and Kaggle — that I can't create on your behalf).

## Structure

| Folder | What's in it |
|---|---|
| `sql/` | Funnel, channel-performance, delivery-performance, and delay-vs-review-score queries |
| `analysis/` | Findings and charts once the queries are run against live data |
| `prd/` | A full PRD for a feature the data justifies |
| `roadmap/` | RICE-prioritized roadmap and release timeline for that feature |
| `prototype/` | A small AI-assisted clickable prototype of the feature |
| `qa/` | Test plan and defect log for the prototype |
| `docs/` | Project charter and working docs (stand-in for Confluence) |

## The narrative this builds toward

The data (particularly Olist's estimated-vs-actual delivery gap) points at a specific, ownable problem: customers aren't proactively told when a delivery is going to miss its promised window, so the first signal they get is a late package and a bad review. `prd/proactive-delivery-notifications-prd.md` scopes a feature to fix that, `roadmap/` sequences it, `prototype/` shows what it looks like, and `qa/` shows how it'd be tested before ship. That's the full loop: data → decision → spec → build → verify.

## Status

Scaffold and query set are complete. Charts and findings in `analysis/` populate once the datasets are connected (see `SETUP.md`) — no fabricated numbers here.
