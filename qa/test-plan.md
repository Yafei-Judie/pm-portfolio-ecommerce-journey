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

Most of the test cases above (TC-01 through TC-05, TC-08) test backend trigger logic that doesn't exist yet — there's no live system behind the two HTML prototypes, so those cases stay untested until v1 actually builds. What *can* be tested now is the prototype UI itself, so I did:

| ID | Found | Severity | Status |
|---|---|---|---|
| DEF-01 | The order-status prototype's revised-estimate date (originally "Aug 21–22") and the email prototype's matching date were both arbitrary placeholders, not tied to any real number, despite the repo's own rule that nothing states a figure without a source. | P2 | **Fixed** — both now show a delay window (~11 days past the original estimate) matching the real average delay among late orders from `sql/04_olist_delay_vs_reviews.sql` (10.6 days, n=6,534). Verified by re-rendering both prototypes locally and confirming the new date and footnote text. |

TC-07 (notification content renders correctly, no leftover placeholder text) passes for both prototypes as of this fix — verified via a local HTTP server (`python3 -m http.server`, since `file://` URLs don't work with the browser automation used here) and a visual check of both the normal and delayed states.

Real defect count so far: 1 found, 1 fixed. This log grows as v1 actually gets built and tested against the trigger-logic cases above.

## Sign-off criteria for v1 ship

- All P0 cases pass.
- Guardrail metric from `prd/proactive-delivery-notifications-prd.md` (false-positive rate) measured on a sample and under threshold before wider rollout.
