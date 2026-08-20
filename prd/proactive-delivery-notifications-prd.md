# PRD: Proactive Delivery Delay Notifications

**Owner:** Judie (Associate PM case study)
**Status:** Draft — pending real data from `sql/03` and `sql/04`
**Last updated:** placeholder, fill in once query results are in

## 1. Problem

Customers currently find out a delivery is going to miss its promised window only when it's already late — no delivery, no email, no proactive signal. The `04_olist_delay_vs_reviews.sql` analysis is built to test the hypothesis that late deliveries drive a disproportionate share of low review scores, and `03_olist_delivery_performance.sql` is built to show whether lateness is a systemic issue or concentrated in a few regions/carriers.

*(Once the real numbers come back from BigQuery/DuckDB, this section gets rewritten with the actual pct_late, avg_days_late, and review-score delta — no estimate stands in for a real query result.)*

## 2. Goal

Reduce the share of 1-2 star reviews attributable to delivery timing by giving customers an honest, early heads-up when a delay is detected, instead of silence followed by a late package.

## 3. Non-goals

- Not attempting to fix the underlying carrier/logistics delay itself — this is a communication feature, not a logistics fix.
- Not building a full order-tracking page redesign — scoped to the notification only.

## 4. Proposed solution

When an order's delivery status feed shows it's likely to miss the estimated delivery date (e.g. a "in transit, delayed" scan event, or no movement for 48+ hours past the last expected checkpoint), trigger:

1. An email/SMS to the customer with a revised estimate and a plain-language reason if available.
2. An in-account order-status banner showing the same revised estimate.
3. An internal flag so CX can proactively route a discount/apology if the delay crosses a threshold (e.g. 5+ days).

## 5. Success metrics

- Primary: review score delta for delayed-but-notified orders vs. delayed-and-not-notified orders (needs an A/B or phased rollout to measure cleanly).
- Secondary: reduction in "where is my order" support contact volume.
- Guardrail: notification false-positive rate (told customer it'd be late, arrived on time) stays under a set threshold — a wrong early warning has its own trust cost.

## 6. Scope for v1

- Email notification only (SMS and in-account banner are v2 — sequencing lives in `roadmap/roadmap.md`).
- Trigger logic: rules-based (no movement for 48h past expected checkpoint), not a predictive model — ML-based ETA prediction is a later iteration once we have enough labeled delay data.

## 7. Open questions

- What delay signal is actually available from the carrier feed at trigger time? (Depends on real fulfillment infra — flagged as a build-team question, not assumed.)
- Where's the threshold for "flag to CX for proactive compensation"? Needs a real cost-per-discount vs. review-score-value tradeoff, not a guess.

## 8. What the data needs to show before this ships

This PRD is written before the queries are run, deliberately — the whole point of the exercise is that `sql/04` either confirms or kills the premise. If delayed orders don't actually score meaningfully lower, this PRD gets rewritten around whatever problem the data does show.
