# PRD: Proactive Delivery Delay Notifications

**Owner:** Judie (Associate PM case study)
**Status:** Problem validated against real data (Olist Brazilian E-Commerce dataset, ~100k orders, 2016–2018)
**Last updated:** 2026-08-19, after running `sql/03` and `sql/04`

## 1. Problem

Customers currently find out a delivery is going to miss its promised window only when it's already late — no proactive signal beforehand. This isn't a hunch; it's confirmed by `sql/04_olist_delay_vs_reviews.sql` against real order and review data:

- A delivery that lands **7+ days late** drops the average review score from ~4.3 (typical for on-time/early) to **1.70**, and pushes the share of 1-2 star reviews from ~9% to **79.2%**.
- Even a modest **1-7 day** delay roughly halves the average score (2.71) and pushes **49.4%** of reviews into 1-2 stars.
- Being early costs almost nothing — early-by-8+-days and early-by-1-7-days score nearly identically to on-time delivery.

And `sql/03_olist_delivery_performance.sql` shows this isn't evenly distributed: lateness ranges from 2.8% of deliveries (Amazonas) to 21.4% (Alagoas) by state, with the highest-volume state (São Paulo, 42% of all delivered orders) sitting at a relatively good 4.5% late. This is a distance/logistics-coverage problem concentrated in specific regions, not a flat national delay rate — which matters directly for scope: a notification should trigger off the actual per-order delay signal, not an assumed average.

Across the full dataset, 6,409 of 96,353 delivered-and-reviewed orders (6.7%) were late. That reach number is what `roadmap/roadmap.md`'s RICE score is built on.

## 2. Goal

Reduce the share of 1-2 star reviews attributable to delivery timing by giving customers an honest, early heads-up when a delay is detected, instead of silence followed by a late package. Given the data above, even converting a fraction of the "7+ days late" bucket's reviews from the 1.70 average toward something closer to the "1-7 days late" bucket's 2.71 would be a meaningful move on overall review health, since that bucket alone drives a disproportionate share of 1-2 star reviews.

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

## 8. Validation outcome

This PRD was originally scoped before the queries were run, deliberately — the point was to let `sql/04` confirm or kill the premise rather than write the problem statement first and go looking for numbers to back it. It confirmed the premise cleanly: late delivery has a steep, specific cost (79.2% of 7+-days-late orders get 1-2 stars, vs. ~9% for on-time/early), not a marginal one. Section 1 above now reflects the real numbers. If a future iteration's data doesn't support a change like this, the right move is the same one this PRD modeled: rewrite the problem around what the data actually shows, not what the roadmap already committed to.
