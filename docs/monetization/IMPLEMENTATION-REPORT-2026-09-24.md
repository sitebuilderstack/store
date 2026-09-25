# Monetization implementation report — 24 September 2026

Four commercial paths built, tested and deployed today. Written so a reader can
tell, per path, whether money can actually be taken.

---

## 1. Status table

| Path | What was implemented | URL | Mode | Can it take money / earn commission **today**? | Remaining dependency |
| --- | --- | --- | --- | --- | --- |
| **Team & agency licensing** | Public page explaining seats vs client-work rights, a three-option seat table, a working quote-request form (name, work email, organisation, seats, product, question, optional marketing opt-in), a draft team licence addendum, and entry points from the licence page, the Agency product and the footer | `/pages/team-licenses` | **Live inquiry** | **No.** No multi-seat price exists and no team variant is for sale. The path produces real quote requests. | Owner sets multi-seat pricing; approves the addendum; then either quote-and-invoice by hand (no further build) or create a team variant with files attached in the Digital Products app |
| **Membership — Workflow Club** | Landing page, a complete pilot release (workflow, two tested scripts, worked example with a failing run, handoff template), a public preview of the failing run, and an interest-list form | `/pages/membership` | **Live interest list (waitlist)** | **No.** No subscription exists; nothing is charged. A waitlist is not recurring revenue. | A subscription app (none installed; no selling plan groups exist on this store), a price the owner approves, real member-only delivery, cancellation and payment-failure handling, terms |
| **Website Launch & Conversion Review** | Public page with explicit scope and exclusions, intake form (name, email, URL, platform, goal, concern, up to five URLs), report template, scope-and-fulfilment checklist with costed assumptions, and a sample report that is a real review of this site | `/pages/website-review` | **Live inquiry** | **No.** No price, turnaround or availability is published; the reply carries the offer and the offer is the booking. | Owner approves price ($149 hypothesis), capacity and turnaround; then payment by invoice or a Shopify service product |
| **Curated recommendations** | Hub with five verified tools, a reusable recommendation component that renders a commission disclosure only when a link is actually compensated, three contextual placements in guides, and a public partner register | `/pages/recommended-tools` | **Editorial (no monetization)** | **No.** No affiliate relationship exists for any tool — none applied for, none pending. Every link is an ordinary link with `rel="noopener"`, and the page says so. | Owner applies to a program; on approval the register records the tracking URL and the card's `affiliate` flag is ticked, which switches on `rel="sponsored nofollow noopener"` and the disclosure |

**Summary in one line:** four paths shipped, **zero of them can take money
today**; three capture real demand, one is editorial.

---

## 2. Files changed

### New pages (published, live)

| Page | Source | Template |
| --- | --- | --- |
| `/pages/team-licenses` | `content/pages/team-licenses.md` | `theme/dev/templates/page.team-licenses.json` |
| `/pages/membership` | `content/pages/membership.md` | `theme/dev/templates/page.membership.json` |
| `/pages/website-review` | `content/pages/website-review.md` | `theme/dev/templates/page.website-review.json` |
| `/pages/recommended-tools` | `content/pages/recommended-tools.md` | `theme/dev/templates/page.recommended-tools.json` |

### New theme code

- `theme/dev/sections/sbs-offer.liquid` — one section for all three offer pages: status banner, page copy, and a block-driven intake form on Shopify's native `{% form 'contact' %}`
- `theme/dev/sections/sbs-recommendations.liquid` — the recommendations hub
- `theme/dev/snippets/sbs-recommend.liquid` — one recommendation card, reusable in guides
- `theme/dev/assets/sbs.css` — styles for both, plus a grid `min-width: 0` fix found by the phone-width audit
- `theme/dev/assets/sbs.js` — four monetization events in the existing allowlist; `initMonetization()`
- `theme/dev/sections/sbs-footer.liquid` + `sbs-footer-group.json` — Support column extended to 16 links; three added

### Content changed

- `content/articles/34-maintenance.html`, `27-deploy-github-cloudflare.html`, `21-search-console.html` — one contextual recommendation each (republished)
- Product descriptions (via Admin API): Agency System → team licences; SEO Toolkit and Conversion Toolkit → review service
- `/pages/licence` (Admin API): "Get in touch about multi-seat terms" now links to the new page. **Single-user terms unchanged.**

### New documents

- `docs/monetization/TEAM-LICENCE-ADDENDUM.md` — draft, for owner approval
- `docs/monetization/PARTNER-REGISTER.md` — five tools, verified facts, sources, dates, relationship status
- `docs/monetization/review-service/SCOPE-AND-FULFILMENT.md` — scope, exclusions, costed assumptions, 10-step checklist, when to decline
- `docs/monetization/review-service/REPORT-TEMPLATE.md`
- `docs/monetization/review-service/SAMPLE-REPORT.md` — a real review of this site
- `content/membership/pilot-01/` — the pilot release: `README.md`, `capture.py`, `compare.py`, `handoff-template.md`, `example/`
- `docs/monetization/ROLLBACK-STATE-2026-09-24.json` — pre-change bodies of the licence page and three product descriptions (these live in Shopify, not the repo)

### New tests

- `scripts/test-monetization.js` — 30 checks, in `tests/run-all.sh`
- Pilot script self-tests wired into the suite

**Products, variants and prices: none created, none changed.** No new SKU, no
new variant, no price edit anywhere.

---

## 3. Tests performed

| Test | Result |
| --- | --- |
| Full offline suite (`tests/run-all.sh`) | **57 passed, 0 failed** (was 55 before; two new checks) |
| `scripts/test-monetization.js` | 30 passed — disclosure honesty, no unapproved prices, no purchasable schema on inquiries, analytics payload reduction executed in a sandbox |
| Pilot scripts | `capture.py --self-test` 11 passed; `compare.py --self-test` 9 passed; both run against a fixture and one live URL |
| Offer pages in preview (`scripts/` harness) | Form renders and posts to `/contact#`, status banner present, every label bound to a real field, marketing consent unchecked, `monetization_offer_view` fires once with ids only, no lead event before submission — **all pass on three pages** |
| Form: invalid input | Required fields empty → browser blocks, no success state, no lead event. Malformed email rejected by the field. **Pass** |
| Form: valid submission | **Blocked by Shopify's own spam protection (hCaptcha) in an automated browser — by design.** A bare POST to `/contact` without a captcha token returns **403**. Verified instead: the success state renders correctly on Shopify's `contact_posted=true` confirmation, with the right wording, focus moved to it, and the lead event firing **exactly once** with ids only |
| Form: duplicate | Reloading the confirmation does not fire a second lead event. **Pass** |
| Form: backend failure | POST aborted → no false success shown, entered values preserved. **Pass** |
| Rendered accessibility (390 and 1280) | **Clean on all four pages** after fixing a grid blowout (546px of content in a 390px viewport) found by the audit |
| Live regression | Product cart forms intact at published prices; agency/SEO/CRO product pages carry their new links; licence page keeps single-user terms; cart loads; no console errors |
| In-guide recommendations (live) | All three render once, `rel="noopener"`, `mode=editorial`, carry the no-commission note; click fires `affiliate_link_clicked` with partner and placement only |
| Search engines | Sitemap resubmitted to Google (204) and Bing (200); five URLs to IndexNow and Bing (200). All four new pages are in the sitemap (89 URLs) |

### Not verified

- **That a submitted form arrives in the owner's inbox.** Submissions go to `admin@sitebuilderstack.com` (Settings → Store details) via Shopify's native contact form; this session has no access to that mailbox, and the captcha prevents an automated end-to-end send. **Owner action: submit one request from each page and confirm it arrives.**
- Custom field labels as they appear in the notification email — same reason.
- Any payment flow, because none exists for these offers.

---

## 4. Where the records appear

| Record | Where | Notes |
| --- | --- | --- |
| Team licence enquiries | Email to `admin@sitebuilderstack.com`, subject field `Request type: Team licence enquiry` | No customer record is created; no marketing list is joined |
| Membership interest list | Email, `Request type: Workflow Club interest list` | Same |
| Review requests | Email, `Request type: Website review request` | Same |
| Marketing opt-in | A field in the same email (`Marketing opt-in: yes`), only when the visitor ticked it | Actioned by hand; nothing is auto-subscribed |
| Orders and revenue | Shopify admin → Orders; `checkout_completed` in the custom pixel | Unchanged |
| Affiliate results | Nowhere — no program is joined. When one is, commissions come from **that program's dashboard**, never from click events | Pending and confirmed commissions to be reported separately |
| Behavioural events | `Shopify.analytics.publish` → **no subscriber**. The custom pixel and collector now know the four events, but the pixel is still not installed (Settings → Customer events), so nothing is collected yet | Unchanged, pre-existing condition; see `analytics/README.md` |

---

## 5. Proposed prices and assumptions — owner approval required

| Item | Proposed | Basis | Status |
| --- | --- | --- | --- |
| Team licence, 3 seats | Baseline **single-user price × 3** (e.g. $59.97 for a $19.99 product) | Arithmetic on the published price. **No discount is asserted anywhere** | Not published, not approved |
| Team licence, 5 seats | Baseline × 5 | Same | Not published, not approved |
| Team licence, 6+ | Quoted | — | Not published |
| Workflow Club | **$19/month** hypothesis | The brief's figure; no market test | **Not published on the page at all** |
| Website review | **$149** pilot | Internal hypothesis | **Not published on the page at all** |
| Review fulfilment time | **3.5–5 hours** (≈$30–43/hour at $149) | Estimate from a stage-by-stage breakdown, not from completed engagements | Assumption |

The review's implied hourly rate is the number most worth the owner's
attention: defensible as a pilot to learn the real cost, not a rate to build a
business on.

---

## 6. Costs and commitments

### Verified costs

- **$0 additional software.** Everything uses what is already installed: Shopify's native contact form, the existing theme, the existing analytics layer. No app installed, no subscription started, no charge incurred.

### Estimated costs, if the blocked paths are activated

- **Subscription app** for the membership: Shopify's own Subscriptions app is free to install; third-party apps typically $20–60/month. **Not verified — no app was installed or priced from a live listing.**
- **Fulfilment time** — human, recurring:
  - Membership: one workflow release + worked example per month. The pilot took roughly a working day to write and test. **That is the real cost of the membership** and the reason four releases should exist before it opens.
  - Review service: 3.5–5 hours per engagement plus time on declined requests.
  - Team licences: ~30 minutes per quote, plus invoicing.

---

## 7. Rollback

Nothing here changes an existing product, price, download or customer right, so
rollback is removal, not repair.

**Pages** — unpublish in the Shopify admin, or:
```
pageUpdate(id: <page id>, page: { isPublished: false })   # per page
```

**Theme** — the new sections and snippet are additive; removing the four
`page.*.json` templates makes the pages fall back to the default template.
`assets/sbs.js`, `assets/sbs.css` and `sections/sbs-footer.liquid` were edited:
`git show monetization-baseline:theme/dev/<path>` is the previous version of
each, and `git revert` of this branch's commits restores them.

**Footer links** — remove `label_14/15/16` and `url_14/15/16` from the Support
column in `sections/sbs-footer-group.json`.

**Product descriptions and the licence page** — the exact pre-change bodies are
in `docs/monetization/ROLLBACK-STATE-2026-09-24.json`; write them back with
`productUpdate` / `pageUpdate`.

**Guides** — `git revert` restores the three articles; republish with
`scripts/publish-articles.py`.

**What rollback must never touch:** the eight products, their prices, their
attached downloads, existing orders, and the single-user licence every customer
already holds. None of them was modified today.

---

## 8. Smallest remaining owner decisions

1. **Team licences** — set a price for 3 seats and 5 seats (or confirm "baseline × seats, no discount"), and approve or amend `TEAM-LICENCE-ADDENDUM.md`. That alone makes the path revenue-capable by invoice, with no further build.
2. **Review service** — approve or change the $149 pilot price, and say how many you can fulfil per month. Until then the page correctly promises nothing.
3. **Membership** — decide whether to install a subscription app at all. If yes, that plus three more releases written in advance is the whole gap.
4. **Affiliates** — decide whether to apply to any program. UptimeRobot and Plausible are the two that appear in guides and would matter most.
5. **Email verification** — send one test request from each of the three forms and confirm it reaches `admin@sitebuilderstack.com`. This is the one test this session could not run.

---

## 9. The honest distinction

- **Revenue-ready today:** *none of the four.* The eight existing products remain the only thing on this site that can take money.
- **Interest capture, working and live:** team licence enquiries, review requests, membership waitlist. These produce real, owner-visible demand signals and cost nothing to run.
- **Editorial, no monetization:** the recommendations hub and its three in-guide placements. Useful whether or not a commission ever exists; the component is built so that switching one flag turns on correct disclosure and link attributes.
- **Blocked:** recurring billing (no subscription app), paid team checkout (no price, no attached files on a team variant), paid review booking (no approved price or capacity), affiliate commissions (no program joined).

**This work does not raise revenue and should not be scored as if it did.** What
it does is make three kinds of demand *measurable* and one kind of recommendation
*honest*, at zero recurring cost, with every claim on every page matching what
the site can actually deliver today.
