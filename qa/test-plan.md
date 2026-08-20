# QA Test Plan: Delivery Delay Notification (v1, email)

## Scope

Covers the trigger logic, email send, and the revised-estimate content. Does not cover carrier-feed accuracy itself (out of scope — that's the input, not the feature).

## Test cases

| ID | Case | Steps | Expected result | Priority |
|---|---|---|---|---|
| TC-01 | Order with genuine 48h+ no-movement delay | Simulate a carrier feed with no scan event for 48h past expected checkpoint | Notification triggers within 1h of the 48h threshold being crossed | P0 |
| TC-02 | Order delivered on time, no delay signal | Normal delivery, no gap in scan events | No notification sent | P0 |
| TC-03 | Order with a brief feed outage but no real delay | Scan gap under 48h, then resumes normally | No false-positive notification | P0 |
| TC-04 | Customer with no email on file | Trigger fires for an order missing a valid email | Falls back gracefully (no crash, logs the miss, doesn't silently drop) | P1 |
| TC-05 | Duplicate trigger on the same order | Delay condition re-evaluated multiple times before resolution | Customer gets exactly one notification per delay event, not one per re-check | P0 |
| TC-06 | Revised estimate accuracy | Compare the notification's revised delivery estimate against actual delivery date | Revised estimate is within an agreed tolerance (needs a real number from `sql/03`'s avg_days_late once data exists) | P1 |
| TC-07 | Notification content renders correctly | Check email across common clients | No broken template, correct order number/items, no placeholder text left in | P1 |
| TC-08 | Order resolves before notification would fire | Delay condition clears before the 48h threshold | No notification sent (don't warn about a problem that self-resolved) | P0 |

## Defect log

Empty until v1 build starts — this is where real defects get tracked, prioritized (P0/P1/P2), and marked resolved as the prototype in `prototype/` gets tested against these cases. Kept empty here deliberately rather than filled with invented bugs.

## Sign-off criteria for v1 ship

- All P0 cases pass.
- Guardrail metric from `prd/proactive-delivery-notifications-prd.md` (false-positive rate) measured on a sample and under threshold before wider rollout.
