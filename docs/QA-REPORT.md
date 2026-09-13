# QA Report — Site Builder Stack

**Date:** 2026-08-26
**Scope:** product bundle v1.0, Shopify product, development theme `191797854500`
**Verdict:** **PASS WITH BLOCKERS** — the build is sound; four owner actions
remain before orders can be taken (`REMAINING-MANUAL-STEPS.md`).

---

## What was verified, and how

Every row below was actually executed. Nothing is marked as passing on
inspection alone.

| Area | Method | Result |
| --- | --- | --- |
| Bundle integrity | `validate-product.py` over 113 files | **Pass** — 0 errors, 3 benign warnings |
| No secrets in bundle | pattern scan + literal credential match | **Pass** |
| No build paths in bundle | pattern scan | **Pass** |
| Internal links in bundle | resolved every relative link and `NN-Module/FILE.md` cross-reference | **Pass** |
| Duplicate content | byte-identical + Jaccard shingle similarity across all documents | **Pass** |
| Prompt count | regex count of prompt IDs | **Pass** — exactly 100 |
| Archive integrity | CRC test, entry count, no empty entries, credential scan | **Pass** — 113 entries |
| Archive round-trip | extracted and recomputed the content digest | **Pass** — digest matches |
| Documented verify command | ran the command printed in the manifest | **Pass** — reproduces the digest |
| Liquid correctness | `shopify theme check` on the full theme | **Pass** — 0 offences in our 27 files |
| Theme check control | injected a deliberate error, confirmed it was reported, restored | **Pass** — the check genuinely covers our files |
| Storefront claims | `audit-storefront-claims.py` — every number vs the real bundle | **Pass** — 26 claims verified, 0 failed |
| Links and anchors | `audit-theme-links.py` — resolved against live Shopify resources | **Pass** — 22 links, 0 broken |
| Structured data | parsed every JSON-LD block under both image/no-image branches | **Pass** — valid JSON, correct types |
| Contrast | computed in a real browser, every text node against its real backdrop | **Pass** — 0 failures |
| Horizontal overflow | measured at 320/390/768/1024/1440 on 6 templates | **Pass** — none |
| Heading structure | counted in the rendered DOM | **Pass** — exactly one `h1` per template |
| Accessible names | every interactive element in the rendered DOM | **Pass** — none unnamed |
| Tap targets | measured bounding boxes | **Pass** — one documented exception |
| Focus indicators | focused each element and read computed styles | **Pass** — all visible |
| JavaScript | FAQ toggle, sticky bar at 4 scroll positions, keyboard tab order | **Pass** |
| Console errors | captured across all templates and viewports | **Pass** — zero |
| Contact form labelling | rendered DOM: labels, input types, autocomplete, aria-describedby | **Pass** |
| Liquid in page bodies | scanned every stored page body | **Pass** — none |
| Dark patterns | scanned theme files and settings | **Pass** — all disabled |
| Product configuration | read back from the Admin API | **Pass** |

---

## Defects found and fixed

Five real bugs. Three were invisible to static analysis and were only caught by
rendering the page in a browser — which is the argument for doing so.

### D-01 — Primary CTA text invisible · **Critical**

`.sbs a { color: var(--accent) }` has specificity (0,1,1);
`.sbs-btn--primary { color: var(--accent-ink) }` has (0,1,0). The element
selector won, so the primary button rendered **accent text on accent
background** — computed contrast **1:1**, completely unreadable. Every buy
button on the site.

The same conflict also broke the logo wordmark and would have made the skip link
invisible.

**Fix:** base element rules wrapped in `:where()` so they carry zero
specificity. **Verified:** computed colour is now `rgb(11,13,18)` on
`rgb(138,166,255)` — 8.31:1.

### D-02 — Add-to-cart button text unreadable · **Critical**

Same class of bug, different selector: the reset's
`.sbs button { color: inherit }` (0,1,1) beat `.sbs-btn--primary` (0,1,0), so the
`<button>` inherited surrounding text colour — **1.98:1**.

**Fix:** reset wrapped in `:where()`. **Verified:** the rendered contrast audit
now reports zero failures.

### D-03 — Horizontal overflow on mobile · **Major**

At 320px the page scrolled to **492px** and at 390px to 495px. Cause: grid and
flex children default to `min-width: auto`, so the pre-formatted terminal blocks
could not shrink below their content.

**Fix:** `min-width: 0` on grid/flex children plus `max-width: 100%` on the
terminal. **Verified:** `scrollWidth == clientWidth` at all five widths on all
five templates.

### D-04 — Sticky buy bar shown at page top · **Minor**

The IntersectionObserver used `rootMargin: '0px 0px -80% 0px'`, so at page load
the hero CTA sat outside the shrunken root and reported as not intersecting —
showing the bar immediately, when it should appear only after the hero scrolls
away.

**Fix:** check `!isIntersecting && boundingClientRect.top < 0` to distinguish
"scrolled past" from "not reached yet". **Verified:** hidden at top, visible
mid-page, hidden over the buy section, hidden again on return to top.

### D-05 — Liquid comment rendered as visible text on the contact page · **Minor**

The contact page's stored body contained a `{% comment %}` block. Shopify emits
page content as raw HTML and does not evaluate Liquid inside it, so the comment
markup would have appeared on the page as literal text.

Found by scanning every page's stored body for Liquid delimiters.

**Fix:** the comment was removed, and a purpose-built contact template
(`templates/page.contact.json` + `sections/sbs-contact.liquid`) now renders a
real Shopify contact form alongside the page content — the page previously
promised a form and had none. **Verified:** no page body contains Liquid; every
form control has an associated `<label for>`, correct input types,
`autocomplete` on name and email, and resolving `aria-describedby` hints.

---

## Documented exception

**Tap target below 24×24:** one link — `code.claude.com/docs`, 195×20 — inside a
sentence in a FAQ answer. WCAG 2.2 SC 2.5.8 explicitly exempts targets that are
inline in a block of text. No change required.

---

## Inherited issues — not ours, but worth knowing

`shopify theme check` reports **3,327 offences** across the ONE theme:

| Count | Check | Note |
| --- | --- | --- |
| 2,517 | `MatchingTranslations` | Vendor's locale files are inconsistent |
| 395 | `DeprecatedFilter` | Deprecated Liquid filters in `nov-*` sections |
| 105 | `ImgWidthAndHeight` | Images without dimensions — causes layout shift |
| 98 | `VariableName` | Naming convention |
| 32 | `UndefinedObject` | |
| 30 | `HardcodedRoutes` | |
| 23 | `DeprecatedTag` | `{% include %}` instead of `{% render %}` |
| 11 | `LiquidHTMLSyntaxError` | In vendor sections |

**None of these are in files we authored.** They affect only the templates still
served by ONE's layout: blog, article, collection, search, and list-collections
— none of which is linked from anywhere on this store.

They are worth knowing about because they are a maintenance liability. The
store has since grown to three products, and /collections/all is now a real
page on the landing layout rather than an unlinked leftover — but the blog,
article, search and list-collections templates are still ONE's.

---

## What was NOT verified — read this

**The storefront was never rendered from Shopify.** The store is
password-protected, and the Shopify CLI states plainly that a password-protected
storefront cannot be previewed with an Admin API token:

```text
Known limitations:
  • Password protected storefronts
```

Everything visual and behavioural above was verified against a **local static
render** built by `scripts/render-preview.py`, which resolves our own Liquid
constructs so the real CSS and JS run in a real browser. That is a genuine test
of layout, contrast, overflow, and JavaScript — and it found three of the four
defects above. **It is not proof that Shopify renders the Liquid identically.**
`shopify theme check` covers Liquid correctness; the combination is strong but
not the same as loading the real page.

**Also not verified:**

| Item | Why | How to verify |
| --- | --- | --- |
| Add to cart on the real storefront | Password + product not published | Place a test order |
| Checkout completion | Requires a live payment | Place a test order |
| Digital delivery | No delivery app installed | Steps 2 and 4 of `REMAINING-MANUAL-STEPS.md` |
| Transactional emails | Requires a real order | Place a test order |
| Real Safari / Firefox behaviour | Only Chromium available here | Open the published site on each |
| Field performance data | Requires real traffic | Search Console after launch |
| Screen reader behaviour | None available in this environment | Test with NVDA or VoiceOver |
| Shopify's own `robots.txt` / `sitemap.xml` | Generated at request time; store is private | Fetch after the password is removed |

**The screen reader gap is worth stating plainly.** The markup was reviewed for
the patterns that cause screen reader problems — accessible names, landmarks,
heading order, `aria-controls` resolution, live-region use, focus management —
and the rendered audit confirmed names and structure programmatically. But no
screen reader was run, so that portion is *predicted from markup*, not verified.

---

## Sign-off

```text
Build quality:        PASS
Blockers to launch:   4 owner actions (REMAINING-MANUAL-STEPS.md items 1–4)
Defects outstanding:  0
Documented exceptions: 1 (inline tap target)
Not verified:         listed above
```


---

# Addendum — live site QA, 27 August 2026

The store went public, which closed the biggest gap in the original report: the
storefront could finally be audited as it actually serves.

## Defects found on the live site, and fixed

### D-06 — Homepage title was the myshopify domain · **High**

The live homepage rendered
`<title>site-builder-stack.myshopify.com – Site Builder Stack</title>`, **no
meta description at all**, and `og:title` set to the domain. Shopify's
`page_title` falls back to the shop domain when the Online Store → Preferences
homepage title is unset, and there is no Admin API mutation for that setting.

**Fixed** by taking the homepage title and description from theme settings in
`layout/landing.liquid`, with a new merchant-editable settings group so the copy
is not hardcoded. Verified live.

### D-07 — `og:image` emitted a Liquid error into the tag · **Medium**

`<meta property="og:image" content="http:Liquid error (layout/landing line 55):
invalid url input">`. `settings.share_image` had a value in `settings_data.json`
but no matching `image_picker` in `settings_schema.json`, so Liquid kept it as a
string and `image_url` failed on it. The `http:` prefix was also wrong.

**Fixed:** added the `image_picker`, guarded the tag on the image object, and
switched to `https:`. Verified live — it now resolves to a real CDN URL.

### D-08 — Policy pages fell back to the purchased theme · **Medium**

All five legal pages rendered in the ONE speaker-store design with its 424 KB
stylesheet and jQuery, while every other page used the site's own design.

Shopify has **no `policy` template type** — its validation rejects
`templates/policy.json`, and the documented template list does not include one.
Policy pages are rendered by `layout/theme.liquid` with `template` blank.

**Fixed** by branching `layout/theme.liquid`: policy pages get the landing
chrome, and everything else falls through to ONE's original markup
**byte-for-byte unchanged** (asserted in the build, and re-verified on the live
theme). Also overrode Shopify's injected `policy-*.css`, which centres the title
and imposes its own container.

### D-09 — `#buy` was a dead anchor on every non-home page · **Medium**

The header CTA fallback and the sticky mobile bar used a bare `#buy`. The buy
section only exists on the homepage, so on product, cart, policy, and content
pages the primary call to action went nowhere.

**Fixed:** all fallbacks are now root-relative. A live crawl of 11 pages now
reports zero dead anchors.

### D-10 — Product description skipped h1 → h3 · **Low**

The template supplies the `h1`; the description's own headings started at `h3`.
**Fixed** by promoting them to `h2`.

### D-11 — Dynamic checkout button below contrast minimum · **Low**

Shopify injects and styles its own accelerated-checkout button; as rendered it
measured **3.59:1** against our surface. **Fixed** by styling it onto our tokens.

### D-12 — Vendor Liquid error on every ONE-layout page · **Low**

`Liquid error (layout/theme line 146): Could not find asset
snippets/nov-popup-login.liquid` — the purchased theme's layout renders a
snippet it does not ship. Pre-existing, and visible on `/collections/frontpage`,
which is in the sitemap. **Fixed** with an empty stub rather than editing the
vendor's layout.

## Live verification

| Check | Result |
| --- | --- |
| Link crawl, 11 pages, all internal URLs | **0 broken, 0 dead anchors, 0 multi-hop redirects** |
| Accessibility audit, 7 pages × 2 viewports | **clean** — contrast, headings, names, alt, overflow, console |
| Liquid errors sitewide | **0** across 12 URLs |
| Metadata | Unique title + description on every page |
| Policy pages | All five 200, on-brand, with descriptions |
| `/pages/*` → `/policies/*` redirects | 301, one hop, 200 destination |
| Structured data | `Organization`+`WebSite` on home, `Product` on product |

## Still not verified

- **Checkout completion and digital delivery** — no delivery app is installed,
  so there is nothing to test. This is the outstanding blocker.
- **Safari and Firefox** — only Chromium is available in this environment.
- **Screen reader** — still predicted from markup, not run.
- **Field performance data** — needs real traffic.

## Known cosmetic gap

`/collections/frontpage` and `/search` still render in the purchased theme's
design. Neither is linked from the site; the collection is in Shopify's
generated sitemap. Left alone deliberately — changing them means touching ONE's
templates on a live store for pages nobody navigates to.
