# SEO Audit Navigator — funnel analytics design

The navigator is a claude.ai artifact (`artifacts/seo-audit-navigator/`,
published 18 September 2026). This document is the contract between the
artifact, sitebuilderstack.com and any future dashboard: which surface fires
which event, from what authority, with what identifier, and what can and
cannot be measured where.

## The funnel and who fires each stage

| # | Stage | Event | Fires from | Authority |
| --- | --- | --- | --- | --- |
| 1 | Artifact opened | `artifact_opened` | artifact | page initialised (once per session, never on rerender) |
| 2 | Audit started | `audit_started` | artifact | the first problem card was chosen (not when the page was shown) |
| 3 | Audit completed | `audit_completed` | artifact | the plan was generated |
| 4 | Report downloaded | `report_downloaded` | artifact | the `downloads` capability resolved the save (not when the button was shown; not if declined) |
| 5 | Upgrade clicked | `upgrade_button_clicked` | artifact | a CTA was clicked (`cta_location` = navigation, audit_results, report, audit_planner, toolkit_explorer, break_test, upgrade_page, footer) |
| 6 | Product page visited | `sitebuilderstack_product_page_visited` | **store** (theme `sbs.js`) | the page carrying `artifact_ref=` finished loading |
| 7 | Account created | `account_created` | **Shopify** → collector webhook | `customers/create` webhook, HMAC-verified |
| 8 | Product purchased | `product_purchased` | **Shopify** → custom pixel | `checkout_completed` standard event (the order exists) |
| 9 | Returning user session | `returning_user_session` | artifact | a new session for a visitor with `visit_count > 1` |

Names are canonical on every surface; nothing renames them. The custom
pixel forwards them with `e: <name>`; Plausible receives the store-side
events as custom events with the same names.

## Identifiers

- `anonymous_visitor_id` (`v_` + 24 hex): minted in the artifact, kept in
  its localStorage. Travels to the store as `artifact_ref` in every CTA URL,
  is stored there in a first-party cookie `sbs_aref` (90 days) and attached
  by the pixel to `product_purchased`. It is never joined to an email, name,
  customer id or IP.
- `session_id` (`s_` + 24 hex): per tab-session; a new one after 30 idle
  minutes. A refresh, a route change or a second tab inside the window is
  the same session (tested in `scripts/test-navigator-analytics.js`).
- `audit_id` (`a_` + 24 hex): one per audit run; `audit_started` and
  `audit_completed` are sent once per audit id.
- `order_id`: Shopify's order id (or checkout token), used only for
  deduplication.

## Deduplication strategy

| Event | Where | How |
| --- | --- | --- |
| `artifact_opened`, `returning_user_session` | artifact | sessionStorage flag per session id |
| `audit_started`, `audit_completed` | artifact | sessionStorage flag per session id + audit id |
| `sitebuilderstack_product_page_visited` | store | sessionStorage flag per `artifact_ref` + product |
| `product_purchased` | pixel **and** collector | pixel: sessionStorage flag per order id (a refreshed thank-you page re-emits `checkout_completed`); collector: KV key `seen\|<order_id>\|<product>` checked before any counter moves, kept 400 days. Revenue is summed under `rev\|<day>\|<product>\|artifact/other` only on first sight. |
| `account_created` | collector | KV key `seen\|customer\|<id>` |

## What is measurable where — stated plainly

- **Inside the claude.ai artifact sandbox no request can leave the page**:
  the Content Security Policy blocks fetch, beacons, image pixels and every
  script host but a few CDNs. So stages 1–5 and 9 are recorded in the
  visitor's own browser (a capped journal shown under Help) and **cannot be
  collected server-side from the artifact as published on claude.ai**. The
  `db` capability would give server storage but makes the artifact
  organization-internal — unusable for a public funnel — so it is not used.
- **The upgrade link carries the visit's funnel state**: `sbs_st` (opened /
  audit_started / audit_completed / report_downloaded), `sbs_pf` (platform),
  `sbs_pp` (primary problem). The store's arrival event records them, so for
  every visitor who reaches the store the artifact-side stage and segments
  are known, and "report downloaders vs non-downloaders", "top converting
  platform" and "top converting problem" can be computed from the store
  side alone.
- **Stages 1–5 as counts** become measurable the day the same app is
  hosted on sitebuilderstack.com (it is plain HTML/JS; `analytics.js`
  detects `Shopify.analytics` and switches provider automatically, keeping
  the journal as the visitor's transparent log). That is the recommended
  next step if artifact-side rates are wanted, and it costs no code change.
- **Stage 7 (`account_created`)**: the store uses Shopify's new customer
  accounts (`customerAccountsVersion: NEW_CUSTOMER_ACCOUNTS`), which the
  theme cannot observe and login is not required at checkout. The only
  authoritative source is the `customers/create` webhook; the collector
  route exists (`/webhooks/customers-create`), HMAC-verified, deduped by
  customer id. Attribution to an artifact visitor is not available for this
  stage (no attribution field passes through registration); it is counted,
  not attributed. For a $19.99 digital product bought at guest checkout this
  stage is usually skipped, and the funnel should read 6 → 8 directly.

## Metrics a dashboard can derive

From the collector's keys (`c|hour|event|path`, `l|day|event|label`,
`m|day|event|id`, `a|day|event|artifact`, `u|day|event|ref`, `rev|day|product|source`):

- Artifact → store arrival: distinct `u|…|sitebuilderstack_product_page_visited|*` per day.
- Arrivals by CTA (`utm_content` in the label), by platform/problem/stage
  (the arrival payload's `platform`, `primary_problem`, `funnel_stage`).
- Purchases and revenue: `product_purchased` counts and `rev|…` sums; split
  `artifact` vs `other` by the presence of `artifact_ref`.
- Artifact → purchase conversion: distinct purchasing refs / distinct arriving refs.
- Report-downloader purchase rate: arrivals with `funnel_stage=report_downloaded`
  that later purchase (join on ref) vs those without.
- Returning purchasers: a ref that appears on more than one day before purchasing.
- Revenue per 1,000 artifact opens, audit start/completion/abandonment rates,
  average completion time: **only once the app is hosted on the store**, from
  the artifact-side events; until then these are journal-only and no rate is
  claimed for them anywhere.

No rate is asserted in this document or in the artifact; nothing has been
measured yet.

## Store-side integration (what exists, what is pending)

| Piece | Status |
| --- | --- |
| Theme: `initArtifactAttribution()` in `assets/sbs.js` — reads `artifact_ref`/utm/segments, sets `sbs_aref` + `sbs_acamp` cookies (90 d), fires the arrival event once per session (Shopify analytics + Plausible); product pages expose handle and price via `data-sbs-product-*` | implemented, pushed to dev and live themes |
| Custom pixel: subscribes to the arrival event; derives `product_purchased` from `checkout_completed` with order-id dedupe and the cookie ref | implemented in `analytics/custom-pixel.js`; **installing/updating the pixel is a manual step in Settings → Customer events** |
| Collector: `r`, `o`, `v` fields; purchase dedupe + revenue; `/webhooks/customers-create` | implemented in `analytics/collector-worker.js`; **not deployed** (needs `wrangler deploy`, `READ_KEY`, `SHOPIFY_WEBHOOK_SECRET`, and a `customers/create` webhook subscription pointing at it) |
| Validation | `scripts/validate-pixel.py` (pixel, collector, docs agree); `scripts/test-navigator-analytics.js` (artifact modules) |

### Webhook subscription (once the collector is deployed)

    mutation { webhookSubscriptionCreate(topic: CUSTOMERS_CREATE, webhookSubscription: { callbackUrl: "https://<worker>/webhooks/customers-create", format: JSON }) { userErrors { field message } } }

Set `SHOPIFY_WEBHOOK_SECRET` on the worker to the app's client secret (the
value Shopify signs webhooks with). Never commit it.

## Privacy

Nothing typed into the navigator leaves the page. URLs to the store carry an
anonymous id, campaign parameters and three coarse categories. The pixel
reads no customer field; the webhook handler stores a customer id only for
deduplication. No email, name, address, payment data or Search Console data
is collected anywhere in this design.
