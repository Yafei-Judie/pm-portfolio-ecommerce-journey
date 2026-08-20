# Prototype: Delivery Delay Notification UI

Built with AI assistance (this session) as a working clickable mockup, not a mood board — directly demonstrating the "leverage AI to develop prototypes" requirement from the JD this project is scoped against.

## What's here

- `order-status-prototype.html` — an order tracking page in two states: normal delivery and delayed-with-proactive-notice. Open directly in a browser, no build step.
- `email-notification-preview.html` — the email a customer would receive when the delay trigger fires (TC-01 in `qa/test-plan.md`).

## How this maps back to the PRD

Every piece of copy and every data field shown (revised estimate, original estimate, order number) traces back to a field in `prd/proactive-delivery-notifications-prd.md` section 4. Nothing in the UI promises a capability the PRD doesn't scope for v1 — no SMS toggle, no predictive ETA, because those are v2/v3 in `roadmap/roadmap.md`.

## Next iteration

Once real Olist data is in from `sql/03`, the "revised estimate" copy in the prototype should get checked against a realistic days-late number instead of the current placeholder (currently shows "2-3 days" as an illustrative example only).
