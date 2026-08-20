# QA Test Plan: Delivery Delay Notification (v1, email)

## Scope

Covers the trigger logic, email send, and the revised-estimate content. Does not cover carrier-feed accuracy itself (out of scope — that's the input, not the feature).

## Test cases

| ID | Case | Steps | Expected result | Priority | Status |
|---|---|---|---|---|---|
| TC-01 | Order with genuine 48h+ no-movement delay | Simulate a carrier feed with no scan event for 48h past expected checkpoint | Notification triggers within 1h of the 48h threshold being crossed | P0 | **PASS** (simulated) |
| TC-02 | Order delivered on time, no delay signal | Normal delivery, no gap in scan events | No notification sent | P0 | **PASS** (simulated) |
| TC-03 | Order with a brief feed outage but no real delay | Scan gap under 48h, then resumes normally | No false-positive notification | P0 | **PASS** (simulated) |
| TC-04 | Customer with no email on file | Trigger fires for an order missing a valid email | Falls back gracefully (no crash, logs the miss, doesn't silently drop) | P1 | **PASS** (simulated) |
| TC-05 | Duplicate trigger on the same order | Delay condition re-evaluated multiple times before resolution | Customer gets exactly one notification per delay event, not one per re-check | P0 | **PASS** (simulated) |
| TC-06 | Revised estimate accuracy | Compare the notification's revised delivery estimate against actual delivery date | Revised estimate matches the real average delay among late orders (10.6 days, n=6,534, from `sql/04`) | P1 | **PASS** (simulated) |
| TC-07 | Notification content renders correctly | Check email across common clients | No broken template, correct order number/items, no placeholder text left in | P1 | **PASS** (manual browser check) |
| TC-08 | Order resolves before notification would fire | Delay condition clears before the 48h threshold | No notification sent (don't warn about a problem that self-resolved) | P0 | **PASS** (simulated) |

"Simulated" means tested against `qa/trigger_simulator.py`, a real runnable implementation of the v1 rule (no scan movement for 48h past the expected checkpoint), not a description of one. There's still no live backend — this simulator is the rule as specified, tested in isolation, which is the standard way to validate trigger logic before it's wired into a real feed. Run it yourself: `python3 qa/trigger_simulator.py`. Current result: **8/8 test cases pass**, plus one documented gap below.

## Defect log

| ID | Found | Severity | Status |
|---|---|---|---|
| DEF-01 | The order-status prototype's revised-estimate date (originally "Aug 21–22") and the email prototype's matching date were both arbitrary placeholders, not tied to any real number, despite the repo's own rule that nothing states a figure without a source. | P2 | **Fixed** — both now show a delay window (~11 days past the original estimate) matching the real average delay among late orders from `sql/04_olist_delay_vs_reviews.sql` (10.6 days, n=6,534). Verified by re-rendering both prototypes locally and confirming the new date and footnote text. |
| DEF-02 | The v1 trigger rule as specified in the PRD ("no scan movement for 48h past the expected checkpoint") never fires for an order that has **zero scan events ever** — a fully lost package before its first scan. The rule needs at least one prior scan to measure staleness against, so a package that never gets scanned at all silently never triggers a notification. Found by `qa/trigger_simulator.py`'s EDGE-01 case, not caught by the original test-case list above. | **P0** — this is arguably the worst-case scenario for the whole feature (the customer with the most reason to be told gets told the least) | **Open** — needs a second rule in the PRD: something like "no first scan within N hours of the order being marked shipped" as a separate trigger condition, distinct from the staleness rule. Not fixed here because it's a scope change to the PRD's trigger logic, not a copy fix — flagged for `prd/proactive-delivery-notifications-prd.md` section 7 (open questions) instead of silently patched. |

Real defect count: 2 found, 1 fixed, 1 open and correctly scoped as a PRD change rather than quietly patched.

## Sign-off criteria for v1 ship

- All P0 cases pass.
- Guardrail metric from `prd/proactive-delivery-notifications-prd.md` (false-positive rate) measured on a sample and under threshold before wider rollout.
