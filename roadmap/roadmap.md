# Roadmap: Delivery Delay Notifications

RICE scoring for the notification feature's rollout phases, using real reach numbers from `sql/03` and `sql/04` run against the Olist dataset (2016-09-04 to 2018-10-17, ~25.4 months of order history).

## RICE scoring

Reach is monthly, derived from the dataset span: 6,409 late orders ÷ 25.4 months ≈ **250/month** affected by any delay; 4,211 orders 5+ days late ÷ 25.4 ≈ **166/month**; 99,441 total orders ÷ 25.4 ≈ **3,915/month** placed. Impact and Confidence use the standard RICE scale (Impact: 3=massive, 2=high, 1=medium, 0.5=low; Confidence: 1.0/0.8/0.5/0.2).

| Phase | Reach/mo | Impact | Confidence | Effort (mo) | RICE score | Priority |
|---|---|---|---|---|---|---|
| Email notification (v1) | 250 | 2 — direct review-score lever; `sql/04` shows a 7+ day delay drops avg review from ~4.3 to 1.70 | 0.8 — rules-based trigger, proven pattern | 2 | (250×2×0.8)/2 = **200** | P0 |
| CX proactive-compensation flag (v2) | 166 | 2 — targets exactly the "7+ days late" bucket where 79.2% of reviews are 1-2 star | 0.8 | 2 | (166×2×0.8)/2 = **133** | P1 |
| In-account status banner (v2) | 250 | 1 — reinforces email, doesn't add new reach | 0.8 — trivial once v1 trigger exists | 1 | (250×1×0.8)/1 = **200** | P1 |
| SMS notification (v2) | 75 — **assumption**: ~30% SMS opt-in; no real opt-in data exists, flagged rather than invented | 1 — faster to see than email | 0.5 — unproven opt-in assumption drags confidence down | 3 — needs SMS provider integration | (75×1×0.5)/3 = **12.5** | P2 |
| Predictive ETA model (v3) | 3,915 — all orders | 2 — high if accurate | 0.2 — no training data yet | 8 (large) | (3915×2×0.2)/8 = **196** | P3, revisit after v1/v2 data exists |

**Worth flagging on its own:** the predictive model's raw RICE score (196) actually beats the CX flag (133) and roughly ties the email notification (200) — pure reach outweighs its low confidence. That's a real RICE artifact, not an error, and it's exactly why RICE informs sequencing rather than dictating it: v3 has a hard dependency on v1/v2 generating labeled delay data to train on, so it stays P3 regardless of score. A framework score that contradicts an obvious dependency is a signal to state the override explicitly, not to quietly re-sort the table until the numbers agree with the plan.

## Release plan

- **v1 (email only):** owns the release date. Ships once trigger logic is validated against a sample of real delayed orders (using `sql/03`'s output to sanity-check that the 48h-no-movement rule actually correlates with real lateness, not noise).
- **v2 (banner + SMS + CX flag):** sequenced after v1 has at least one full month of live delay data to check the guardrail metric (false-positive rate) before adding more channels.
- **v3 (predictive model):** explicitly deferred — flagged as needing v1/v2's real delay data as training data first. Not scoped further until that data exists.

## Risks tracked

- Carrier feed might not expose a clean "delayed" signal at the granularity this needs — if so, v1's trigger logic gets rebuilt around whatever signal actually exists (dependency on `prd/`'s open question #1).
- False-positive delay warnings erode trust faster than no warning at all — this is the reason the guardrail metric exists, not an afterthought.
