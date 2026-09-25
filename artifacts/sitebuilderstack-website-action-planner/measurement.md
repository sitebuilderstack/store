# Measurement and attribution — Website Action Planner

**Status: internal engagement measurement is unavailable.** Nothing the
artifact records is transmitted anywhere. The only thing that reaches
SiteBuilderStack is a campaign-tagged link the visitor chooses to click, and
what happens after that click is measured on the storefront, not here.

This document says exactly what is measured, what is not, and what has been
tested — so that nothing in a later report is mistaken for data it is not.

## 1. Why remote transmission is off

The claude.ai artifact viewer serves each page from a sandboxed
`*.claudeusercontent.com` origin under a Content Security Policy that permits
`fetch`, XHR and WebSocket **only to the page's own origin and the Google Fonts
hosts**, and blocks every other external script, stylesheet, image and font.
There is therefore no destination this page could send an event to, and none
has been verified. Consequently, in `src/analytics.js`:

```js
var REMOTE = false;
var REMOTE_REASON = 'No permitted destination has been verified for this runtime…';
```

Turning it on later is one object with a `send(name, props)` method — and a
verified delivery path. Until both exist, it stays off. The page states this
to the visitor under **What this page measures**, and a browser test asserts
`remoteEnabled === false`.

## 2. The event interface

Ten canonical names. Anything not on this list is dropped before it is recorded.

| Event | Fired when | Once per |
| --- | --- | --- |
| `artifact_opened` | the page mounts | page view |
| `planner_started` | "Build my free plan" | page view |
| `planner_completed` | "Show my plan" produces a result | page view |
| `recommendation_viewed` | the result renders | each result |
| `starter_prompt_copied` | the clipboard write **resolved** | each copy |
| `plan_export_requested` | Export is clicked | each click |
| `plan_export_completed` | `downloads.save()` resolved with `status: "saved"` | each save |
| `product_cta_clicked` | any product link is clicked | each click |
| `free_resource_clicked` | the free-next-step link is clicked | each click |
| `planner_share_clicked` | "Share the planner" is clicked | each click |

`plan_export_completed` is only fired on an observable completion: the
capability resolves `"saved"` only after the viewer accepts and the file is
handed to the host's save surface. A declined or failed save fires nothing.
Likewise `starter_prompt_copied` fires on the promise resolving, never on the
click — a refused clipboard produces a failure message and a selectable-text
fallback instead.

### Properties

Only these six may travel with an event, and `reduce()` drops everything else
before it is recorded:

`artifact_name`, `artifact_version`, `product_id`, `cta_placement`,
`environment`, `timestamp`.

**Never recorded:** questionnaire answers, ownership selections, free text,
email addresses, website URLs. There is no free-text field in the planner at
all. A browser test asserts that no answer key appears anywhere in the journal.

### The local journal

Events are appended to an in-memory array, capped at 200, and mirrored into
`sessionStorage` inside a `try/catch` so a private window or blocked storage
changes nothing. It is visible to the visitor under **What this page measures →
Show the local journal**.

It is debug instrumentation. **It counts what one browser did in one tab.** It
is not analytics, not a visitor count, and must never be reported as one.

## 3. Outbound attribution

Every link from the artifact to sitebuilderstack.com is built by
`SBSPlannerAnalytics.tag(url, placement)`, which:

- refuses anything that is not `https://sitebuilderstack.com` (returned unchanged),
- **preserves existing query parameters** and sets the campaign ones with
  `URLSearchParams.set`, so a target that already carries a parameter keeps it,
- sets `utm_content` from a fixed list, falling back to `unknown_placement`.

```
utm_source=claude_artifact
utm_medium=interactive_tool
utm_campaign=website_action_planner
utm_content=<one of the ten placements below>
```

| `utm_content` | Where |
| --- | --- |
| `primary_recommendation` | the main product card CTA |
| `recommendation_repeat` | the single repeat CTA after the useful result |
| `complementary_recommendation` | the optional second product |
| `bundle_comparison` | the bundle card, when the arithmetic offers it |
| `product_comparison` | a row in the on-demand comparison table |
| `free_next_step` | the free guide or tool |
| `example_result` | any product link clicked from the worked example, so example clicks stay separable |
| `header_brand` | the wordmark and the header link |
| `footer_brand` | the footer link |

There is deliberately no `share_planner` placement. "Share the planner" copies
the artifact's own claude.ai URL, which is not a sitebuilderstack.com link and
carries no campaign parameters, no answers and no identifier.

**No answer is ever encoded in a campaign parameter**, and no visitor
identifier is attached. A browser test asserts every rendered CTA uses a
placement from this list.

### If the planner is ever hosted on sitebuilderstack.com

Do **not** use these UTM links on an onsite copy. An internal UTM link
overwrites the visitor's original acquisition source in every analytics tool.
An onsite copy should fire the storefront's existing custom events instead
(`theme/dev/assets/sbs.js`, `track()`), the way the other onsite tools do.

## 4. Authoritative commerce events

A product click is a click. It is **not** a product-page visit, a session, a
checkout, a purchase, or a new customer.

| Question | Where the answer actually lives |
| --- | --- |
| Did the click become a visit? | Shopify Analytics → Sessions by referrer / landing page, filtered to `utm_campaign=website_action_planner`; and Plausible, where UTM parameters appear as sources |
| Did the visit reach checkout? | Shopify Analytics → conversion funnel; the storefront's `checkout_completed` event |
| Was there an order, and for how much? | Shopify Orders. Order value and currency are Shopify's figures, never the artifact's |
| Was the buyer new? | Shopify's customer record, via the `customers/create` webhook route described in `docs/analytics/ARTIFACT-FUNNEL.md` |

### How to inspect the tagged visits

1. Shopify admin → Analytics → Reports → *Sessions by UTM campaign*, and read
   the row `website_action_planner`. Compare against `utm_content` to see which
   placement produced them.
2. Plausible → Sources → the `claude_artifact` entry, then the campaign
   breakdown.
3. For a specific product page, filter Shopify's landing-page report to the
   product URL and the campaign.

### Known gaps — do not describe this as complete cross-domain attribution

- **No visitor identifier crosses the boundary.** The planner deliberately
  attaches none, so a click and a later purchase cannot be joined for an
  individual. Only campaign-level aggregates are available.
- **The storefront's custom pixel is still not installed.** The store publishes
  custom events with no subscriber (see `docs/REMAINING-MANUAL-STEPS.md`), so
  the onsite half of the funnel is currently Shopify Analytics and Plausible
  only.
- **Artifact-side engagement is unmeasurable** for the reason in section 1.
  How many people opened the planner, started it, or copied a prompt is
  **not known and cannot be reported.**
- Ad blockers, privacy modes and stripped referrers reduce even the
  campaign-level figures.

## 5. What was tested, and what was not

**Tested (`tests/test-browser.js`, 88 checks):**

- The expected events fire, one-shot events fire once per page view.
- Only the six allowlisted properties are ever recorded.
- No answer key appears anywhere in the journal.
- `remoteEnabled === false`.
- **The page makes no network request at all** during a complete run —
  asserted against every request Chromium issued.
- No console errors during a complete run.
- Every rendered CTA carries the three campaign parameters, a documented
  placement, `target="_blank"` and `rel="noopener"`.
- The primary CTA resolves to the exact product URL, not the homepage.
- The clipboard success path *and* the refused-clipboard fallback.
- Export is hidden, and explained, when the capability is absent.

**Tested live (`tests/test-links.js`, 31 checks):** every product URL and every
free-resource URL returns HTTP 200 **with the campaign parameters attached**.

**Not tested, and why:**

- `downloads.save()` — the capability resolves only inside the claude.ai
  viewer, so the save path cannot run in a local browser. The absent-capability
  branch is tested; the save branch needs the owner (section 6).
- Signed-out public access — the artifact is private.
- Any figure about real visitors. There are none yet, and none would be
  measurable from inside the artifact if there were.

## 6. Owner actions

These need the store owner or the artifact owner; they are genuine
dependencies, not deferred work.

1. **Open the published artifact and click "Export as Markdown."** Confirm the
   confirmation dialog appears and the file saves. This is the one path that
   cannot be exercised outside the viewer.
2. **Decide the access state.** The artifact is private. To let anyone open it,
   use the **Share** control in the artifact page header and choose a public
   link. On this plan a public link is the only way to share. Nothing in this
   repository can change that setting, and it has not been changed.
3. **After sharing, open the link in a signed-out browser** and confirm the
   planner runs, before the URL goes into any of the launch copy.
4. **Check the campaign shows up.** After the first shared traffic, read
   Shopify Analytics → Sessions by UTM campaign for `website_action_planner`.
   If it is empty after real clicks, the click-to-visit path is broken and the
   links need re-testing.
5. **Re-run `refresh-catalogue.py` before 24 October 2026** — the 30-day
   freshness window. After that date the planner stops showing prices until the
   snapshot is refreshed and republished. That is deliberate.
