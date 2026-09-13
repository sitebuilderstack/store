# Remaining Manual Steps

> ## ⚠ URGENT — four products can take money they cannot fulfil
>
> **Updated 13 September 2026.** The storefront is **public**, and **five
> products are published and buyable**:
>
> | Product | Price | Delivery attached? |
> | --- | --- | --- |
> | Claude Code Website Launch System | $19.99 | Yes — the only one proven |
> | SEO & Website Audit Toolkit | $19.99 | **Unproven** |
> | Conversion & Revenue Optimization Toolkit | $19.99 | **Unproven** |
> | Complete Site Builder Stack | $39.99 | **No — needs all three attached** |
> | Website Operations & Maintenance System | $39.99 | **No — new today, nothing attached** |
>
> The operations system is new as of today and definitely has nothing attached:
> `dist/claude-code-website-operations-maintenance-system-v1.0.zip` (SHA-256 in
> the `.sha256` beside it) must be uploaded to the product in the
> digital-delivery app. The bundle likewise. The other two are *unproven* rather
> than definitely broken: the digital-delivery app stores files privately and
> **the Admin API cannot see whether a file is attached.** Only a fulfilled paid
> order proves delivery works.
>
> `scripts/verify-digital-delivery.py` fails deliberately on exactly this, and
> now fails for four products.
>
> **Do one of these:**
> 1. Attach the archives in the digital-delivery app — three files on the bundle,
>    one on each single product — then place a real test order on each; or
> 2. Set the unproven products to Draft until you can. I have not done this
>    because you published them deliberately.
>
> ---
>
> **Done since the last update:** the Complete Site Builder Stack shipped at $149
> with every price computed from the live products; a Conversion category and
> answer-derived product recommendations were added to the readiness score; task
> and stage were added to the prompt builder; learning progress, `/pages/my-learning`
> and the 2026 benchmark shipped; two free product samples were published; three
> segmented email sequences were written; and `/collections/all` got the meta
> description it had never had.

> ## Engagement is not being measured
>
> **Added 8 September 2026.** The storefront publishes **49 custom events** and
> **nothing collects them.** Measured: `webPixel` returns *"No web pixel was
> found for this app."* Shopify delivers custom events to Web Pixels and nowhere
> else, so every tool completion, lesson completion and product-placement click
> since launch has fired into nothing.
>
> This could not be automated. `webPixelCreate` fails with **"No extension
> found"** — it installs an *app* pixel, which needs the app to ship a web pixel
> extension, and this store's app is an Admin API client. A custom pixel can
> only be created by a person in **Settings → Customer events**.
>
> `analytics/` holds the pixel, a first-party Cloudflare Worker collector, and
> the install steps. It is deliberately not pointed at an analytics vendor:
> doing so would reverse the store's recorded decision to run no second vendor
> and would add a processor to the privacy policy.
>
> **Not installing it is a legitimate choice.** Half-installing it is the worst
> of the three options — it costs a privacy disclosure and returns data nobody
> reads. See `analytics/README.md`.

> ## No product walkthrough video exists
>
> Three product pages carry a video component that accepts MP4, YouTube or
> Vimeo, and honestly says no video is published rather than showing a play
> button over a still. The plumbing is done and verified; **the recording is
> the missing part, and it needs a person with a screen and a microphone.**
>
> Video is the largest single lever on time-on-page available to this site, and
> it is the one asset where the infrastructure exists and the content does not.

> ## Prices changed on 13 September 2026 — two archives need re-attaching
>
> All three products are now **$19.99** and the bundle **$39.99**. Every place
> a price is written has been updated and verified live. The theme reads prices
> from the products, so the storefront was correct the moment you changed them.
>
> Two of the paid downloads carry a comparison table in their README that named
> the old prices. Both were corrected and rebuilt:
>
> | Archive | New SHA-256 |
> | --- | --- |
> | `claude-code-seo-website-audit-toolkit-v1.0.zip` | `559ddca3…1aa7aed` |
> | `claude-code-conversion-revenue-optimization-toolkit-v1.0.zip` | `2bffc3cd…41f657d` |
>
> **If either file is attached in the digital-delivery app, re-upload it** —
> the attached copy still has the old prices inside. The Launch System archive
> did not change.
>
> The three publish scripts now leave the price alone on an update run unless
> `--set-price` is passed. Before this, re-running one to change a description
> would have silently reverted your price.

Everything below requires either a permission this app does not hold, or a
decision that is the store owner's to make. Each item says **why** it could not
be automated, so you can judge whether to delegate it.

**Nothing here is optional if you intend to take orders.** Items 1–3 are
blockers.

---

## 1. Publish the product to the Online Store  ·  DONE

**Completed by the store owner, 27 August 2026.** The product is published to
Online Store, Shop, Point of Sale, and Microsoft Copilot, and is live at
<https://sitebuilderstack.com/products/claude-code-website-launch-system>.

---

## 2. Configure digital delivery  ·  ⚠ URGENT

**Status: not configured, and the store is now selling.** Verified by API — no
delivery app is installed and no file is attached to the product or its variant.

The archive is built and validated at
`dist/claude-code-website-launch-system-v1.0.zip` and has deliberately **not**
been uploaded to Shopify Files, because those are served from a public CDN URL
that bypasses checkout. The upload script refuses archives for that reason.

**Do this:**

1. Install Shopify's free **Digital Products** app:
   <https://apps.shopify.com/digital-downloads>
2. Attach `dist/claude-code-website-launch-system-v1.0.zip` to the product
3. Check the customer-facing filename
4. Set the download limit and expiry deliberately

**Then verify all four:**

- [ ] Place a real test order
- [ ] The confirmation email contains a working download link
- [ ] The file's SHA-256 matches `dist/*.sha256`
- [ ] **The download URL serves nothing without an order** — check in a private
      window

Until this is done, either finish it or take the product out of the Online Store.

---

## 3. Populate Settings → Policies  ·  DONE

**Completed 27 August 2026**, once the reinstalled app granted
`write_legal_policies`. All five policies are live and rendering:

| Policy | Source | Live |
| --- | --- | --- |
| Privacy policy | Shopify's generated template, kept | `/policies/privacy-policy` |
| Terms of service | Written for this store | `/policies/terms-of-service` |
| Refund policy | Written for this store | `/policies/refund-policy` |
| Shipping policy | States plainly that nothing is shipped | `/policies/shipping-policy` |
| Contact information | Real address and email | `/policies/contact-information` |

The privacy policy was **left as Shopify's generated text** rather than replaced.
It is comprehensive, its `{{ shop_name }}` and `{{ last_updated }}` variables
render correctly on the storefront (verified), and platform-generated legal
language is worth preserving.

The three `/pages/*` duplicates were deleted and **301-redirected** to their
policy equivalents, so the legal text has one canonical home. `/pages/licence`,
`/pages/disclaimer`, and `/pages/contact` remain as pages — they have no Shopify
policy equivalent.

> **Read them before relying on them.** They are accurate to how this store
> operates, but they are not legal advice and no lawyer has reviewed them.

---

## 4. Place a real test order

Nothing above is verified until an order goes through end to end.

1. Settings → Payments → confirm the provider is live and **test mode is off**
   (a store left in test mode takes no money)
2. Buy the product yourself
3. Confirm: order appears, confirmation email arrives, download link works,
   file opens, checksum matches
4. Refund the test order

---

## 5. Remove the storefront password  ·  ADMIN UI ONLY

**Status:** password protection is **on**. The storefront is not public and is
not indexable.

**Why this cannot be automated — at all.** This is not a permissions gap. The
Admin API exposes `onlineStore.passwordProtection.enabled` as **read-only**, and
there is no mutation to change it: a schema search for password-related
mutations returns only `storefrontAccessTokenCreate` and
`storefrontAccessTokenDelete`, which are unrelated Storefront API tokens. The
REST `shop` resource reports `password_enabled` read-only and rejects `PUT`
with a 406. No access scope changes this.

**Do this:** Online Store → Preferences → remove the storefront password.

**Do not do it yet.** See the warning at the top of this document — with the
theme now live, removing the password makes a store public that cannot fulfil an
order.

---

## 6. Publish the development theme  ·  DONE

**Completed 26 August 2026.** **Site Builder Stack — Live** (`191797854500`) is
now the published theme. It is byte-identical to `theme/dev/` in this
repository, and all four CSS/JS defect fixes were confirmed present in the live
files after publishing.

The purchased **`one-speaker`** theme (`191794807076`) is retained
**unpublished** as the rollback target.

A fresh **Site Builder Stack — Development** (`191811453220`) has been created
for future work, and `theme_push.py` now refuses to push to
`191797854500` because it is `MAIN`.

**Rollback:** Online Store → Themes → publish `one-speaker`. Under a minute.
This returns the storefront to the purchased theme with its speaker demo
content — worse, but functional. Prefer fixing forward unless the site is
actually broken.

---

## 7. Point the custom domain

**Status:** `sitebuilderstack.com` currently resolves to `184.105.230.230`,
which is **not Shopify**. The store's primary domain is
`site-builder-stack.myshopify.com`.

**Do this:** Settings → Domains → connect `sitebuilderstack.com`, follow
Shopify's DNS instructions, then set it as the primary domain. Decide `www` or
apex and make sure the other redirects.

`10-Cloudflare/CLOUDFLARE-DNS-GUIDE.md` in the product covers the pre-switch
record audit — losing `MX` records during a nameserver change is the classic
failure, and it is silent.

---

## 8. Analytics

**Status:** none installed. The insertion point (`{{ content_for_header }}`) is
present in `layout/landing.liquid`.

See `docs/ANALYTICS-SETUP.md`. Do not add tracking you will not look at.

---

## 9. Search engines

Only after items 1–7, and only once the password is removed — a
password-protected store cannot be indexed.

1. Verify a **domain property** in Google Search Console
2. Submit the sitemap (Shopify generates `/sitemap.xml`)
3. Set up Bing Webmaster Tools — it can import from Search Console
4. Work `13-Search-Engines/INDEXING-READINESS-CHECKLIST.md` from the product

---

## Summary

| # | Item | Blocker | Why manual |
| --- | --- | --- | --- |
| 1 | ~~Publish product to Online Store~~ | ✅ Done | Completed 27 Aug |
| 2 | **Digital delivery app** | **⚠ URGENT** | Store is selling with no fulfilment |
| 3 | ~~Settings → Policies~~ | ✅ Done | Completed 27 Aug |
| 4 | Real test order | **Yes** | Requires a live payment |
| 5 | ~~Remove storefront password~~ | ✅ Done | Done by owner 27 Aug |
| 6 | ~~Publish the theme~~ | ✅ Done | Completed 26 Aug 2026 |
| 7 | ~~Custom domain~~ | ✅ Done | sitebuilderstack.com is live |
| 8 | Analytics | No | Owner's tooling choice |
| 9 | Search engines | No | Follows the launch |
