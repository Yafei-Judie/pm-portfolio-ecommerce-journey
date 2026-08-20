# Roadmap: Delivery Delay Notifications

RICE scoring for the notification feature's rollout phases. Scores are placeholders structured to be filled in with real reach numbers once `sql/03` shows actual order volume by state — the framework is real, the inputs get replaced.

## RICE scoring

| Phase | Reach | Impact | Confidence | Effort | RICE score | Priority |
|---|---|---|---|---|---|---|
| Email notification (v1) | orders/month affected by delay (from `sql/03`) | high — direct review-score lever per `sql/04` | medium — rules-based trigger, proven pattern | 2 (small: template + trigger logic) | reach × impact × confidence / effort | P0 |
| In-account status banner (v2) | same as v1 | medium — reinforces email, doesn't add new reach | high — trivial once v1 trigger exists | 1 | — | P1 |
| SMS notification (v2) | subset who opt into SMS | medium — faster to see than email | medium — needs SMS provider integration | 3 | — | P2 |
| CX proactive-compensation flag (v2) | orders 5+ days late (subset of v1 reach) | high — targets the worst-experience tail | medium — needs a real cost/benefit threshold, not a guess | 2 | — | P1 |
| Predictive ETA model (v3) | all orders | high, if accurate | low — no training data yet | 8 (large) | — | P3, revisit after v1 data exists |

## Release plan

- **v1 (email only):** owns the release date. Ships once trigger logic is validated against a sample of real delayed orders (using `sql/03`'s output to sanity-check that the 48h-no-movement rule actually correlates with real lateness, not noise).
- **v2 (banner + SMS + CX flag):** sequenced after v1 has at least one full month of live delay data to check the guardrail metric (false-positive rate) before adding more channels.
- **v3 (predictive model):** explicitly deferred — flagged as needing v1/v2's real delay data as training data first. Not scoped further until that data exists.

## Risks tracked

- Carrier feed might not expose a clean "delayed" signal at the granularity this needs — if so, v1's trigger logic gets rebuilt around whatever signal actually exists (dependency on `prd/`'s open question #1).
- False-positive delay warnings erode trust faster than no warning at all — this is the reason the guardrail metric exists, not an afterthought.
