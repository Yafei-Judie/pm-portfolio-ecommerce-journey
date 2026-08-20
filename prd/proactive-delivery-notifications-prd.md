# PRD: Proactive Delivery Delay Notifications

**Owner:** Judie (Associate PM case study)
**Status:** Problem checked against real data (Olist Brazilian E-Commerce dataset, ~100k orders, 2016–2018) and pressure-tested by an independent critique pass — see `analysis/limitations-and-alternative-views.md`
**Last updated:** 2026-08-19/20, after running `sql/03`, `sql/04`, and a follow-up measurement-quality check (`sql/08`)

## 1. Problem

Customers currently find out a delivery is going to miss its promised window only when it's already late — no proactive signal beforehand. `sql/04_olist_delay_vs_reviews.sql` shows a strong association in real order and review data:

- A delivery that lands **7+ days late** drops the average review score from ~4.3 (typical for on-time/early) to **1.70**, and pushes the share of 1-2 star reviews from ~9% to **79.2%**.
- Even a modest **1-7 day** delay roughly halves the average score (2.71) and pushes **49.4%** of reviews into 1-2 stars.
- Being early costs almost nothing — early-by-8+-days and early-by-1-7-days score nearly identically to on-time delivery.

Two things temper how that association should be read, both found by pressure-testing the finding rather than just reporting it (full detail in `analysis/limitations-and-alternative-views.md`):

- **It's an association, not a proven cause.** The query has no seller, category, or distance control, so it can't separate "customers punish waiting" from "bad sellers produce both slow shipping and bad reviews." The 1-2 star share (79.2% vs. ~9%) is the more defensible number than the mean-score gap, since a 1-5 star scale isn't a linear unit and "costs 2.6 points" implies precision the data doesn't support.
- **97.3% of the 7+ days late bucket rated before the package arrived** (`sql/08_review_timing_vs_delivery.sql`, independently verified against the live database). Olist's review survey triggers off the *estimated* delivery date, not actual receipt, so for the bucket this PRD is built on, the review mostly isn't "I got it late and was upset" — it's "it still hasn't arrived and is overdue." That doesn't kill the case for a notification; if anything it strengthens a different version of it (the pain is the open-ended silent wait, which a notification addresses regardless of when the package eventually lands). But it means the success metric in section 5 needed a fix — see below.

And `sql/03_olist_delivery_performance.sql` shows this isn't evenly distributed: lateness ranges from 2.8% of deliveries (Amazonas) to 21.4% (Alagoas) by state, with the highest-volume state (São Paulo, 42% of all delivered orders) sitting at a relatively good 4.5% late. `sql/05_distance_vs_delay.sql` adds a mechanism: physical seller-customer distance itself predicts lateness (4.4% late under 50km, 11.7% late at 1500km+), so this is a real logistics-coverage problem, not just a state-level artifact — which matters for scope: a notification should trigger off the actual per-order delay signal, not an assumed average.

Across the full dataset, 6,409 of 96,353 delivered-and-reviewed orders (6.7%) were late. That reach number is what `roadmap/roadmap.md`'s RICE score is built on.

## 2. Goal

Reduce the share of 1-2 star reviews attributable to delivery timing by giving customers an honest, early heads-up when a delay is detected, instead of silence followed by a late package. The 1-2 star **share** is the number this goal is actually measured against (79.2% in the worst bucket vs. ~9% for on-time), not the mean score — a rate is something a cost model (refund rate, CX ticket volume) can be built on; an average of an ordinal 1-5 scale isn't. Given the measurement-quality finding above, "review score" here should be understood as largely measuring wait-anxiety in the worst bucket, not post-delivery regret — which is a *better* argument for a notification, not a weaker one, since the wait itself is exactly what a proactive message addresses.

One more honest limit, from `analysis/limitations-and-alternative-views.md`'s business-strategy lens: repeat-purchase rate for customers whose first order was late is 2.55% vs. 3.03% for on-time — real, same direction, but a much smaller effect than the review-score swing, against a baseline repeat rate of only ~3% overall (Olist is a structurally low-repeat marketplace). This is a review-experience fix, not a proven retention/revenue play — don't oversell it as the latter.

## 3. Non-goals

- Not attempting to fix the underlying carrier/logistics delay itself — this is a communication feature, not a logistics fix.
- Not building a full order-tracking page redesign — scoped to the notification only.

## 4. Proposed solution

When an order's delivery status feed shows it's likely to miss the estimated delivery date (e.g. a "in transit, delayed" scan event, or no movement for 48+ hours past the last expected checkpoint), trigger:

1. An email/SMS to the customer with a revised estimate and a plain-language reason if available.
2. An in-account order-status banner showing the same revised estimate.
3. An internal flag so CX can proactively route a discount/apology if the delay crosses a threshold (e.g. 5+ days).

## 5. Success metrics

- Primary: **1-2 star share** (not mean score) for delayed-but-notified orders vs. delayed-and-not-notified orders, compared against **review-submission timing relative to the notification**, not against final delivery date. This fix matters: since 97.3% of the worst bucket rates before the package even arrives, comparing against delivery date could show zero movement even if the notification genuinely helps — the review is often already in by the time delivery-date-based analysis would look for an effect.
- Secondary: reduction in "where is my order" support contact volume.
- Guardrail: notification false-positive rate (told customer it'd be late, arrived on time) stays under a set threshold. This isn't symmetric with a false negative, though: today's baseline is a guaranteed false negative on every late order (silence, every time), which is the worst cell in the data (1.70 avg, 79.2% 1-2 star). v1 should tolerate a fairly generous false-positive rate in exchange for catching more of the 7+ day bucket, then tighten as signal quality improves — "stay under a threshold" without a stated direction to err isn't a complete guardrail.

## 6. Scope for v1

- Email notification only (SMS and in-account banner are v2 — sequencing lives in `roadmap/roadmap.md`).
- Trigger logic: rules-based (no movement for 48h past expected checkpoint), not a predictive model — ML-based ETA prediction is a later iteration once we have enough labeled delay data.
- **Message confidence, not just timing and channel.** The trigger is a weak heuristic (48h no-scan), so the revised estimate it produces is low-confidence dressed up as a specific date. If a customer gets a second promise (the revised ETA) and that one slips too, that's a "double deviation" — a worse outcome than the silent 2.71-average experience this PRD is trying to improve on. v1 copy should show a range, not a precise-sounding single date, and set expectations that the estimate may move again. This is a real scope addition, not a copy nice-to-have — see `analysis/limitations-and-alternative-views.md`'s customer-behavior section for the full argument.

## 7. Open questions

- What delay signal is actually available from the carrier feed at trigger time? (Depends on real fulfillment infra — flagged as a build-team question, not assumed.)
- Where's the threshold for "flag to CX for proactive compensation"? Needs a real cost-per-discount vs. review-score-value tradeoff, not a guess.
- **DEF-02, found by `qa/trigger_simulator.py`:** the v1 trigger rule (no scan movement for 48h past the expected checkpoint) never fires for an order with zero scan events ever — a fully lost package before its first scan. The rule needs a prior scan to measure staleness against, so the worst-case order (never scanned at all) is exactly the one the current rule misses. This needs a second, independent trigger condition — something like "no first scan within N hours of the order being marked shipped" — not a tweak to the existing threshold. Scoped here rather than quietly folded into section 4, since it changes what v1 actually needs to build, not just its copy.

## 8. Validation outcome

This PRD was originally scoped before the queries were run, deliberately — the point was to let `sql/04` confirm or kill the premise rather than write the problem statement first and go looking for numbers to back it. It found a strong, real association: late delivery correlates with a steep jump in 1-2 star reviews (79.2% of 7+-days-late orders, vs. ~9% for on-time/early). Section 1 above now reflects that more precisely than the original draft did — the first version of this line said the query "confirmed the premise cleanly," which overstated what a two-variable crosstab can show. It was corrected after an independent four-lens critique (`analysis/limitations-and-alternative-views.md`) checked the finding for confounders, measurement error, and whether the proposed fix was even the right one.

That critique changed the PRD's language and two pieces of scope (the section 5 success metric, the section 6 message-confidence requirement), but not the underlying call to ship a rules-based v1 notification — every lens converged on the same practical read: the pain in the worst bucket is largely an unexplained, ongoing wait, and a notification addresses that regardless of the exact causal mechanism. If a future iteration's data doesn't support a change like this, the right move is the same one this PRD modeled twice now: rewrite the problem around what the data actually shows, not what the roadmap already committed to — and don't let your own PRD's language get ahead of what the query actually proved.
