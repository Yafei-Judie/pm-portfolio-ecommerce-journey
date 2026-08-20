# Amplitude event taxonomy: delivery delay notifications

This is a specification, not a live Amplitude instance. I don't have real Amplitude access to attach to this project, and I'm not going to fake screenshots of a tool I didn't use. What this shows instead is the actual PM skill behind "using Amplitude": deciding what to track, why, and how it ties back to a real decision — in this case, the guardrail and success metrics already defined in `prd/proactive-delivery-notifications-prd.md` section 5.

## Events

| Event | Fires when | Key properties |
|---|---|---|
| `order_delay_detected` | The rules-based trigger (48h no movement past expected checkpoint) fires internally | `order_id`, `customer_state`, `days_since_last_scan`, `original_eta`, `revised_eta` |
| `delay_notification_sent` | The email in `prd/` section 4 actually sends | `order_id`, `channel` (email/sms/banner), `hours_since_delay_detected` |
| `delay_notification_opened` | Customer opens the email or views the in-account banner | `order_id`, `channel`, `time_to_open_minutes` |
| `order_delivered` | Carrier confirms delivery | `order_id`, `actual_delivery_date`, `days_late` (negative if early), `was_notified` (boolean) |
| `review_submitted` | Customer leaves a review | `order_id`, `review_score`, `days_late`, `was_notified` |
| `cx_compensation_flagged` | The v2 CX flag in `roadmap/roadmap.md` fires for a 5+ day delay | `order_id`, `days_late`, `flagged_to_team` |

## User properties

- `sms_opt_in` (boolean) — needed to size the SMS phase honestly; `roadmap/roadmap.md` currently marks that reach number as an unverified assumption specifically because this property doesn't exist yet.
- `notification_channel_preference` — set after the first `delay_notification_opened` event, used to decide email vs SMS priority for that customer going forward.

## The one funnel this taxonomy exists to answer

`order_delay_detected` → `delay_notification_sent` → `delay_notification_opened` → `order_delivered` → `review_submitted`, split by `was_notified = true` vs `was_notified = false`.

That split is the actual test of the PRD's hypothesis: does a notified customer's `review_score` land higher than a delay-matched customer who wasn't notified? `sql/04_olist_delay_vs_reviews.sql` already shows the baseline (unnotified) relationship between delay and review score using real data. This funnel is what you'd build in Amplitude once the feature ships, to see if notifying actually moves the score, not just correlates with it.

## Guardrail, instrumented

The PRD's guardrail metric (false-positive rate: told a customer it'd be late, it arrived on time) is `order_delay_detected` events where the matching `order_delivered` event later shows `days_late <= 0`. That's a segmentation on two events already in this taxonomy, not a new one — a guardrail should almost always be answerable from events you're already tracking for the primary metric, not a bolt-on.

## What I'd actually need to build this for real

Real event data from a real notification system, which doesn't exist yet since this feature hasn't shipped. This taxonomy is the specification that would go into a ticket for whoever wires up analytics before v1 ships, not a dashboard you can click into today.
