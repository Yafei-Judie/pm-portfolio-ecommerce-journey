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
| `analysis/` | `findings.md` (real numbers + charts) and `make_charts.py`, which regenerates every chart from the query output |
| `prd/` | A full PRD for a feature the data justifies |
| `roadmap/` | RICE-prioritized roadmap and release timeline for that feature |
| `prototype/` | A small AI-assisted clickable prototype of the feature |
| `qa/` | Test plan and defect log for the prototype |
| `docs/` | Project charter, an Amplitude event-taxonomy spec for the feature, and working docs (stand-in for Confluence) |

## Findings, in one chart

![Delivery timing vs average review score](analysis/charts/olist_delay_vs_review.png)

A delivery that lands 7+ days late drops the average review score from ~4.3 to 1.70, and pushes the share of 1-2 star reviews from ~9% to 79%. Being early costs almost nothing. Full findings, funnel/channel charts, and the SQL behind all of it are in `analysis/findings.md`.

## The narrative this builds toward

The data (particularly Olist's estimated-vs-actual delivery gap) points at a specific, ownable problem: customers aren't proactively told when a delivery is going to miss its promised window, so the first signal they get is a late package and a bad review. `prd/proactive-delivery-notifications-prd.md` scopes a feature to fix that, `roadmap/` sequences it, `prototype/` shows what it looks like, and `qa/` shows how it'd be tested before ship. That's the full loop: data → decision → spec → build → verify.

## Status

All four queries run, findings written up with charts, PRD and roadmap rewritten against the real numbers. What's still open: the QA test plan's defect log is a template with no executed defects yet (honest gap, not hidden), and the Amplitude taxonomy in `docs/` is a specification, not a live instance, since this feature hasn't shipped anywhere real. No fabricated numbers anywhere in this repo.
