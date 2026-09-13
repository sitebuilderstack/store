# Store Architecture

How the Site Builder Stack storefront is put together, and why.

---

## The store

| | |
| --- | --- |
| **Name** | Site Builder Stack |
| **Shop ID** | `gid://shopify/Shop/98739257636` |
| **Permanent domain** | `kjhvcj-yi.myshopify.com` |
| **Primary domain** | `site-builder-stack.myshopify.com` |
| **Plan** | Basic |
| **Currency** | USD |
| **Timezone** | America/Los_Angeles |
| **Password protection** | **Enabled** — the storefront is not public. Cannot be changed via the Admin API; see `REMAINING-MANUAL-STEPS.md`. |

> **Note on domains.** The *permanent* domain is `kjhvcj-yi.myshopify.com`; the
> `site-builder-stack.myshopify.com` hostname is configured as the primary
> domain and is the one to use. `sitebuilderstack.com` currently resolves to
> `184.105.230.230`, which is not Shopify — the custom domain has not been
> pointed at the store yet.

## Business model

Four digital products plus a bundle of the first three, each with its own page
and its own price, and a homepage that still sells the flagship. There is no
catalogue navigation and no search; /collections/all exists and carries the
comparison, but the routes into the products are the header menu, the homepage's
four-product row, the bundle CTA beneath it, and the contextual links in the
guides.

- The Claude Code Website Launch System — $19.99 — build and launch
- Claude Code SEO & Website Audit Toolkit — $19.99 — get it found
- Claude Code Conversion & Revenue Optimization Toolkit — $19.99 — convert the traffic
- Claude Code Website Operations & Maintenance System — $39.99 — keep it running (added 13 September 2026; not in the bundle)
- Complete Site Builder Stack — $39.99 — the first three, as three downloads on one order

The operations system is the only product that ships code: eleven
standard-library Python scripts alongside the Markdown. `validate-ops-system.py`
runs each one's `--help`, refuses third-party imports and attack-tool
recommendations, and `test-ops-scripts.py` runs every script against a local
fixture site so the suite proves the scripts work without touching the network.

The bundle is one SKU with three attachments, not a fourth archive. Its page
computes both figures — $59.97 separately, $39.99 together — from the live products,
so no price is typed anywhere and the comparison is suppressed entirely if any
component becomes unavailable.

The homepage sells the flagship and nothing else until after the FAQ, where the
four-product row explains which product suits which problem and a single line
beneath it offers the first three together. That ordering is deliberate: a homepage that opens
with a catalogue sells none of the four. The near-the-top decision path is the
interactive roadmap, which routes through the free guides rather than the
products — deliberately, because someone who has not decided what they are doing
is not ready to be sold to.

## The product

| | |
| --- | --- |
| **Title** | The Claude Code Website Launch System |
| **Product ID** | `gid://shopify/Product/10779378221348` |
| **Handle** | `claude-code-website-launch-system` |
| **Variant ID** | `gid://shopify/ProductVariant/56105793847588` |
| **SKU** | `SBS-CCWLS-V1` |
| **Price** | $19.99 USD |
| **Status** | Active |
| **Requires shipping** | **No** |
| **Inventory tracked** | **No** (policy: continue selling) |
| **Weight** | 0 g |
| **Sales channel** | **Not published** — see `REMAINING-MANUAL-STEPS.md` |

Digital-product configuration is deliberate: `requiresShipping: false` and no
weight, so checkout never asks for a shipping address or calculates a rate.
Getting either wrong adds a step to checkout and costs orders.

## Theme architecture — the "landing layer"

The purchased theme is **ONE** (`one-speaker`, by NovaThemes), a large
multi-purpose catalogue theme. It was built for a physical-product store, it
ships 424 KB of CSS, jQuery, an icon font, and a set of dark-pattern components
including a fake purchase-notification popup.

Rather than fight it or replace it wholesale, the storefront uses a **layered**
approach:

```text
                     ┌─────────────────────────────────┐
  index, product,    │  layout/landing.liquid          │  purpose-built,
  page, cart, 404 ──▶│  + assets/sbs.css  (19 KB)      │  no jQuery,
                     │  + assets/sbs.js   (4.7 KB)     │  no icon font,
                     │  + sections/sbs-*.liquid        │  no popups
                     └─────────────────────────────────┘

  blog, article,     ┌─────────────────────────────────┐
  collection,     ──▶│  layout/theme.liquid  (ONE)     │  untouched,
  search, list       │  + all nov-* sections           │  still functional
                     └─────────────────────────────────┘
```

**Why this and not a full replacement:** the ONE theme's cart, account, search,
and policy plumbing works. Re-implementing it would add risk for no benefit on a
catalogue this small. The layered approach gives us the design we need on the
pages that matter, while leaving everything else intact and reversible.

**Why this and not section-level customisation of ONE:** the ONE homepage
sections are built around a speaker store. Bending them into a developer-tool
landing page would have produced worse markup than writing purpose-built
sections, and we would still be paying for the global CSS and JS on every page.

JSON templates support a `layout` attribute, which is what makes this possible
without a Liquid template (and therefore without losing theme-editor
customisation).

### Files we author

```text
layout/landing.liquid              minimal layout: metadata, OG, schema, skip link
assets/sbs.css                     design system, scoped to .sbs
assets/sbs.js                      FAQ, sticky bar, form busy state, anchor focus
snippets/sbs-schema.liquid         JSON-LD: Organization, WebSite, Product, Breadcrumb
sections/sbs-header-group.json     announcement + header
sections/sbs-footer-group.json     footer + sticky buy bar
sections/sbs-*.liquid              17 purpose-built sections
templates/index.json               homepage — 11 sections
templates/product.json             product page
templates/page.json                policy and content pages
templates/cart.json                cart
templates/404.json                 not found
config/settings_data.json          dark patterns off, demo content stripped
```

Every section carries a `{% schema %}` with presets and defaults, so the
merchant can edit, reorder, and remove them in the theme editor without code.

### Design system

Tokens live in `assets/sbs.css` under `.sbs`, so nothing leaks into the rest of
the ONE theme. Dark, high contrast, monospace accents. **Every contrast ratio
was computed, not assumed:**

| Pair | Ratio | Requirement |
| --- | --- | --- |
| body text on background | 16.43:1 | 4.5:1 |
| muted text on background | 8.90:1 | 4.5:1 |
| dim text on background | 5.36:1 | 4.5:1 |
| accent text on background | 8.31:1 | 4.5:1 |
| button label on accent | 8.31:1 | 4.5:1 |
| focus indicator (accent) | 8.31:1 | 3:1 |
| interactive borders | 5.36:1 | 3:1 |

Regenerate with the palette block in `scripts/` if the colours change.

## Dark patterns removed

The ONE theme ships these. All are disabled in `config/settings_data.json`, and
none is rendered by the landing layout at all:

| Component | Setting | State |
| --- | --- | --- |
| Fake purchase notifications | `show_fake_order` | off |
| Fake notifications on inner pages | `show_fake_order_inner_page` | off |
| Fake notifications on mobile | `show_fake_order_xs` | off |
| Fake order names / locations / times | `fake_order_*` | cleared |
| Newsletter interstitial | `show_newsletter_popup` | off |
| Wishlist popup | `show_popup_wishlist` | off |
| Countdown deal bar | `countdown_deal` | cleared |
| Page preloader | `enable_loadpage` | off |

There are no invented testimonials, ratings, customer counts, or scarcity
claims anywhere on the site, and no `Review` or `AggregateRating` structured
data.

## Pages

| Page | Handle | Purpose |
| --- | --- | --- |
| Privacy Policy | `privacy-policy` | Data handling |
| Terms of Service | `terms-of-service` | Sale terms |
| Refund Policy | `refund-policy` | Digital refunds, stated plainly |
| Product Licence | `licence` | Summary of `LICENSE.md` |
| Disclaimer | `disclaimer` | Independence, trademarks, no-results |
| Contact | `contact` | Support routes |

All are published, rendered through `templates/page.json` on the landing layout,
and linked from the footer.

> **These are Shopify *pages*, not Shopify *policies*.** This app does not hold
> `write_legal_policies`, so the documents under Settings → Policies (which
> Shopify links from checkout) have not been populated. See
> `REMAINING-MANUAL-STEPS.md`.

## Brand assets

Generated reproducibly by `scripts/generate-brand-assets.py` from the same
colour tokens as the CSS:

| Asset | Size | Used as |
| --- | --- | --- |
| `favicon.png` | 512×512 | Theme favicon |
| `og-share.png` | 1200×630 | Open Graph / Twitter card |
| `product-bundle.png` | 1600×1200 | Product image |

The product image depicts the **actual module contents** as a grid. It is not a
box mockup, and nothing on the site implies a physical item.

## SEO

- Canonical tag on every page, from `landing.liquid`
- Unique title and meta description per page; product SEO fields set explicitly
- Open Graph and Twitter Card with a real image
- One `<h1>` per template
- JSON-LD: `Organization` + `WebSite` on the homepage, `Product` + `Offer` on the
  product page, `BreadcrumbList` on pages
- **No review or rating markup** — there are no reviews
- Shopify generates `/sitemap.xml` and `robots.txt` automatically

## Analytics

Nothing is installed. `{{ content_for_header }}` is present in
`layout/landing.liquid`, which is the required insertion point for Shopify's own
analytics, the Customer Events pixel framework, and app-injected scripts. See
`docs/ANALYTICS-SETUP.md`.

## Theme history

| Date | Event |
| --- | --- |
| 2026-08-26 | Duplicated `one-speaker` to build the landing layer |
| 2026-08-26 | Published as **Site Builder Stack — Live** (`191797854500`) |
| 2026-08-26 | `one-speaker` (`191794807076`) retained unpublished as the rollback target |
| 2026-08-26 | Fresh **Site Builder Stack — Development** (`191811453220`) created for future work |
