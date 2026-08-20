# Findings

## GA4 acquisition funnel (`sql/01_ga4_acquisition_funnel.sql`)

Run against `bigquery-public-data.ga4_obfuscated_sample_ecommerce` (Google Merchandise Store, Nov 2020–Jan 2021) in BigQuery sandbox mode, 179 MB processed.

| Month | Viewed item | Added to cart | Began checkout | Purchased | View→Cart | Cart→Checkout | Checkout→Purchase | Overall conversion |
|---|---|---|---|---|---|---|---|---|
| 2020-11 | 21,440 | 2,060 | 4,219 | 1,532 | 9.6% | 204.8% | 36.3% | 7.1% |
| 2020-12 | 22,906 | 7,113 | 3,859 | 1,975 | 31.1% | 54.3% | 51.2% | 8.6% |
| 2021-01 | 19,629 | 3,832 | 1,924 | 1,069 | 19.5% | 50.2% | 55.6% | 5.4% |

**Read:** overall conversion (view→purchase) ranges 5.4%–8.6% across the three months, with December (holiday shopping) the strongest both in checkout completion (51.2%) and overall conversion (8.6%). View→cart is the weakest and most volatile stage (9.6%–31.1%), suggesting product-page/cart-add friction is the bigger lever here than checkout itself.

**Data quality note, stated plainly rather than smoothed over:** November's cart→checkout rate is 204.8% — more checkouts than cart-adds in the same month. That's a real artifact of this dataset, not a calculation error: Google's own docs for `ga4_obfuscated_sample_ecommerce` warn the obfuscation process limits internal consistency (some fields carry `<Other>` or null placeholders, and event-to-event linkage isn't guaranteed clean). Read November's checkout/purchase figures with that caveat; December and January are more internally consistent.

## GA4 channel performance (`sql/02_ga4_channel_performance.sql`)

Same dataset, all three months combined, 223 MB processed. Metric is `users_started_session` (distinct users triggering `session_start`) rather than a true session count — the dataset's `ga_session_id` event param wasn't reliably populated for `session_start` events, so an exact session-level join returned zero rows. Distinct users is the more robust and still-honest version of "reach."

| Source | Medium | Users (session_start) | Purchasers | Revenue |
|---|---|---|---|---|
| google | organic | 102,530 | 1,229 | $95,775 |
| (direct) | (none) | 75,025 | 1,054 | $79,650 |
| (data deleted) | (data deleted) | 16,969 | 680 | $50,064 |
| shop.googlemerchandisestore.com | referral | 25,350 | 568 | $46,521 |
| \<Other\> | referral | 32,362 | 468 | $37,000 |
| \<Other\> | \<Other\> | 50,776 | 499 | $35,470 |
| google | cpc | 15,449 | 152 | $9,056 |
| \<Other\> | organic | 10,012 | 97 | $8,232 |
| \<Other\> | (data deleted) | 372 | 9 | $397 |

**Read:** Google organic and direct traffic together account for roughly 60% of tracked revenue despite google/cpc (paid search) bringing in a comparable user count (15,449) to some organic-adjacent rows — cpc converts users to purchasers at roughly 1.0%, well below organic's ~1.2% and direct's ~1.4%. On this dataset, paid search isn't outperforming free channels enough to justify weighting a real budget toward it without a deeper look at what's actually being bid on.

## Olist delivery performance and delay-vs-review-score

Not run yet — pending Kaggle account setup and CSV download (`sql/03`, `sql/04`). This is the half of the analysis the PRD's problem statement actually depends on. Once it's in, `prd/proactive-delivery-notifications-prd.md` section 1 gets rewritten with the real numbers, replacing the current placeholder framing.
