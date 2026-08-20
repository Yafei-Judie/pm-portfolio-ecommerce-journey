# Prototype: Delivery Delay Notification UI

Built with AI assistance (this session) as a working clickable mockup, not a mood board — directly demonstrating the "leverage AI to develop prototypes" requirement from the JD this project is scoped against.

## What's here

- `order-status-prototype.html` — an order tracking page in two states: normal delivery and delayed-with-proactive-notice. Open directly in a browser, no build step.
- `email-notification-preview.html` — the email a customer would receive when the delay trigger fires (TC-01 in `qa/test-plan.md`).

## How this maps back to the PRD

Every piece of copy and every data field shown (revised estimate, original estimate, order number) traces back to a field in `prd/proactive-delivery-notifications-prd.md` section 4. Nothing in the UI promises a capability the PRD doesn't scope for v1 — no SMS toggle, no predictive ETA, because those are v2/v3 in `roadmap/roadmap.md`.

## Real data check (done)

The revised-estimate date in both prototypes originally used an arbitrary placeholder — logged as DEF-01 in `qa/test-plan.md` and fixed. Both now show a delay window of ~11 days past the original estimate, matching the real average delay among late orders in `sql/04_olist_delay_vs_reviews.sql`'s output (10.6 days, n=6,534). Order number and exact dates are still illustrative; the delay magnitude isn't.

## Local testing note

Opening these files via `file://` doesn't work with the browser automation this project used for QA — serve the folder locally instead: `python3 -m http.server 8934` from this directory, then open `http://localhost:8934/order-status-prototype.html`. Opening the file directly by double-clicking in Finder works fine for normal browsing; this note only matters if you're automating it.
