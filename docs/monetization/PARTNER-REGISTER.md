# Partner register — affiliate relationship status

Every tool recommended on `/pages/recommended-tools`, with what was verified,
from where, and on what date. **This register contains no account numbers, no
tracking IDs, no program credentials and no private correspondence** — there
are none to record, because no program has been applied to. If that changes,
the approved tracking URL goes here and the account login stays out.

**Status as of 24 September 2026: no affiliate relationship exists for any tool
below.** Every outbound link on the recommendations page is an ordinary link to
the vendor's own site. The page says so, and nothing on the site is described
as commission-earning.

| Status | Meaning |
| --- | --- |
| `approved` | Applied, accepted, tracking URL issued and verified working |
| `pending` | Applied, awaiting a decision |
| `not enrolled` | A program exists; we have not applied |
| `none found` | No affiliate program found in official sources |
| `unverified` | Not yet checked |

---

## 1. Plausible Analytics

| | |
| --- | --- |
| **Official URL** | https://plausible.io/ |
| **Reader use case** | Privacy-friendly analytics for a small site whose owner does not want a cookie banner or a Google Analytics property |
| **Verified facts** | "Plausible is powerful, lightweight analytics. No cookies, just insights. Made and hosted in the EU"; from $9/month for 10k monthly pageviews; 30-day free trial, no card; open source ("The code is public and auditable") |
| **Source** | https://plausible.io/ |
| **Affiliate program** | **none found** — not mentioned on the homepage; `/docs/affiliate-program` returns 404 |
| **Relationship status** | **not enrolled** (no program located) |
| **Tracking URL** | none |
| **Date checked** | 2026-09-24 |
| **Note** | This site runs Plausible itself, installed 17 September 2026 — the only tool in this register we can say we use, and the page says so. |

## 2. Cloudflare (Pages and Workers)

| | |
| --- | --- |
| **Official URL** | https://www.cloudflare.com/plans/ · https://developers.cloudflare.com/pages/ |
| **Reader use case** | Hosting and deploying a static or full-stack site, with DNS and a CDN in the same place |
| **Verified facts** | Free tier includes Workers at 100k requests/day and 10 ms CPU per request, R2 at 10 GB-month, Workers KV 1 GB, D1 5 GB; Pages "Deploy full-stack applications instantly to the Cloudflare global network" with "500 deploys per month on the Free plan" |
| **Source** | https://www.cloudflare.com/plans/ ; https://developers.cloudflare.com/pages/ |
| **Affiliate program** | **none found** for individuals on the pricing page (Cloudflare operates partner programs for agencies and resellers; not applied to, not verified) |
| **Relationship status** | **not enrolled** |
| **Tracking URL** | none |
| **Date checked** | 2026-09-24 |

## 3. Netlify

| | |
| --- | --- |
| **Official URL** | https://www.netlify.com/pricing/ |
| **Reader use case** | Deploying a static or framework site from Git with deploy previews, when Cloudflare's model is more than the project needs |
| **Verified facts** | Free tier includes a global CDN, unlimited deploy previews, functions, a database and blob storage (bandwidth and build minutes not stated on the pricing page); first paid tier "Personal" at $9/month per member |
| **Source** | https://www.netlify.com/pricing/ |
| **Affiliate program** | **none found** on the pricing page |
| **Relationship status** | **not enrolled** |
| **Tracking URL** | none |
| **Date checked** | 2026-09-24 |

## 4. UptimeRobot

| | |
| --- | --- |
| **Official URL** | https://uptimerobot.com/pricing/ |
| **Reader use case** | Knowing the site is down before a customer tells you — the single cheapest maintenance check there is |
| **Verified facts** | Free plan: 50 monitors, 5-minute monitoring interval; first paid tier "Solo" $13/month, $12/month billed annually |
| **Source** | https://uptimerobot.com/pricing/ |
| **Affiliate program** | **none found** on the pricing page (the `ref=` parameters visible there are internal) |
| **Relationship status** | **not enrolled** |
| **Tracking URL** | none |
| **Date checked** | 2026-09-24 |

## 5. Buttondown

| | |
| --- | --- |
| **Official URL** | https://buttondown.com/pricing |
| **Reader use case** | An email list for a site that has readers but no shop — the lightest way to keep in touch without a marketing suite |
| **Verified facts** | "Absolutely nothing for your first 100 subscribers"; add-ons from +$9/month; base paid pricing not stated on the pricing page |
| **Source** | https://buttondown.com/pricing |
| **Affiliate program** | **none found** on the pricing page |
| **Relationship status** | **not enrolled** |
| **Tracking URL** | none |
| **Date checked** | 2026-09-24 |

---

## Deliberately not listed

- **Claude Code / Anthropic.** No affiliate program has been verified, and this
  site's whole relationship with Anthropic is "independent, not affiliated".
  Recommending it for commission would compromise that statement. It is named
  throughout the site as a requirement, never as a recommendation to buy.
- **Shopify.** This store runs on Shopify and the site sells a Shopify
  automation toolkit; recommending it for commission where we also sell into it
  is a conflict worth avoiding until there is a reason not to.
- **Anything not used for the tasks the guides describe.** The register grows
  by need, not by commission rate.

## If a program is applied to later

1. Apply from the vendor's official page; record the date here as `pending`.
2. On approval, record the tracking URL here and set `approved`.
3. Only then may the link on the page carry the tracking URL, `rel="sponsored
   nofollow noopener"`, and the per-recommendation disclosure.
4. Never modify a signed or parameterised tracking link, and never add
   parameters a program's terms do not permit.
5. Commissions are reported from the program's own dashboard, never inferred
   from `affiliate_link_clicked` events. Pending and confirmed commissions are
   reported separately.
