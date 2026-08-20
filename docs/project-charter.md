# Project Charter: Delivery Delay Notifications

*(Stands in for a Confluence page — same content discipline, different tool.)*

## Objective

Use real order/delivery/review data to find one concrete, data-justified product improvement in the post-purchase experience, then carry it through the full PM loop: analysis → PRD → roadmap → prototype → QA.

## Stakeholders (roles, as they'd exist on a real team)

- Product Management — owns the PRD, roadmap, release date
- Engineering — owns the trigger logic and email send implementation
- QA — owns test execution against `qa/test-plan.md`
- CX/Support — owns the proactive-compensation flag workflow in v2
- Marketing/Creative — owns the notification's actual copy and branding (referenced but not written here — outside PM scope)

## Timeline

| Milestone | Target |
|---|---|
| Datasets connected, queries run | Setup step — see `SETUP.md` |
| `analysis/findings.md` written from real query output | After datasets connected |
| PRD finalized with real numbers | After findings |
| Roadmap RICE scores finalized with real reach numbers | After findings |
| Prototype built | After PRD scope is locked |
| QA pass against `qa/test-plan.md` | After prototype |

## Decision log

Kept here as things get decided, not written in advance. First real entry goes in once the delivery/review data comes back and the PRD's problem statement gets rewritten with actual numbers instead of the placeholder framing.

## Working agreement

- No number in `analysis/`, `prd/`, or `roadmap/` gets stated as fact unless it came out of a query that was actually run. Placeholders are marked as placeholders, not smoothed over.
- Scope changes get logged here, not silently absorbed into the PRD.
