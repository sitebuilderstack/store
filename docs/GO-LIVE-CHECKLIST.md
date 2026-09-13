# Go-Live Checklist

Work top to bottom on the day. Anything unchecked is a decision to launch
without it — write down what you skipped and why.

Launch when you can watch it for two hours afterwards.

---

## Before the day

- [ ] `REMAINING-MANUAL-STEPS.md` items 1–4 complete
- [ ] Product published to the Online Store sales channel
- [ ] Digital delivery app installed, file attached, download limit decided
- [ ] Settings → Policies populated
- [ ] Payment provider live; **test mode off**
- [ ] A real test order placed, delivered, verified, and refunded
- [ ] Download SHA-256 matches `dist/*.sha256`
- [ ] **Download URL confirmed unreachable without an order** (private window)
- [ ] Store contact email is monitored
- [ ] Two-factor authentication on the store owner account

## Record the rollback first

```text
Current live theme:   one-speaker
Theme ID:             191794807076
To roll back:         Online Store → Themes → publish the above
Expected duration:    under 1 minute
Recorded by:          ______________________
```

## Publish

- [ ] Preview the development theme in the admin theme editor once more
- [ ] Publish **Site Builder Stack — Development**
- [ ] Note the time

## T+5 minutes — decisive checks

If any of these fail, **roll back first and investigate afterwards.**

- [ ] Homepage loads over HTTPS
- [ ] Zero console errors
- [ ] Zero failed network requests
- [ ] Header, hero, and buy section render
- [ ] Favicon appears

## T+15 minutes — the conversion

- [ ] **Complete a real purchase, end to end**
- [ ] Order appears in the admin
- [ ] Confirmation email arrives
- [ ] Download link works and the file opens
- [ ] Checksum matches
- [ ] Refund the test order

## T+30 minutes — on a real phone

Use an actual phone on mobile data, not a resized browser.

- [ ] Homepage renders; no horizontal scrolling
- [ ] CTA visible without scrolling
- [ ] Sticky bar appears after the hero and does not cover the buy form
- [ ] FAQ expands and collapses
- [ ] Purchase completable

## T+45 minutes — pages and links

- [ ] Every header nav link resolves
- [ ] Every footer link resolves
- [ ] All six policy/content pages load and are readable
- [ ] Product page loads at `/products/claude-code-website-launch-system`
- [ ] Cart page works — add, update quantity, remove
- [ ] A nonsense URL returns a real **404**, not a 200

## Remove the password

Only once everything above passes.

- [ ] Online Store → Preferences → remove the storefront password
- [ ] Confirm the site loads in a private window with no password prompt

## T+1 hour — technical

- [ ] `/robots.txt` returns 200 and contains no `Disallow: /`
- [ ] `/sitemap.xml` returns 200 and is valid XML
- [ ] Sample five sitemap URLs — each returns 200 and is canonical
- [ ] View source: **no `noindex`** on the homepage or product page
- [ ] Canonical tag correct on homepage, product, and a policy page
- [ ] Open Graph image renders in a link preview
- [ ] Structured data validates in a rich-results test

## T+2 hours — search engines

- [ ] Google Search Console: verify a **domain property**
- [ ] Check manual actions (should be none)
- [ ] Submit the sitemap
- [ ] Inspect the homepage with **Test live URL**
- [ ] Request indexing for the homepage and product page — those two only
- [ ] Bing Webmaster Tools: verify, submit sitemap

## Cross-browser

- [ ] Chrome
- [ ] Firefox
- [ ] **Safari — desktop and iOS.** Test this specifically.
- [ ] Edge

## End of day

- [ ] No errors in the Shopify admin
- [ ] Any 404s from real traffic reviewed
- [ ] Traffic plausible
- [ ] Someone who has not seen the store looked at it and understood what it
      sells within ten seconds

## Then

Hand over to `14-Checklists/POST-LAUNCH-CHECKLIST.md` in the product for the
first 24 hours, then the 7-day and 30-day reviews.

---

## If something breaks

**Roll back first. Diagnose second.** Fixing forward under pressure turns a
five-minute incident into an hour.

| Symptom | Check first |
| --- | --- |
| Styling broken | Cached CSS; hard-refresh, then check the asset URL |
| Buy button does nothing | Product published to Online Store? Variant available? |
| Checkout asks for shipping | `requiresShipping` on the variant — must be false |
| No download after purchase | Delivery app configured? File attached to the right variant? |
| Page 404s | Template file present in the published theme? |
| Not indexed | Password still on? `noindex` shipped? |

## Digital delivery gate

```
scripts/verify-digital-delivery.py
```

Exit 0 means the store can deliver what it sells. Anything else means it
cannot, and the script names which check failed.

It covers the five things that have to be true together:

1. A digital delivery app is installed. Shopify's Admin API has no mutation
   that attaches a file to a product or a variant — 452 mutations, and every
   one containing "delivery" is about physical shipping. Delivery on Shopify
   is entirely app-provided, so this cannot be automated from here.
2. The product is active, untracked, weightless, and does not require
   shipping. A *tracked* digital item can sell out, which is its own outage.
3. The real cart, built through `/cart/add.js`, reports
   `requires_shipping: false` — so checkout never asks for an address.
4. The paid archive is **not** in Shopify Files. Anything uploaded there gets
   a public CDN URL, which hands the product away without payment.
5. Recent orders actually reached `FULFILLED`.

The app-detection regex is deliberately broad (`digital products`,
`downloads`, `SendOwl`, `Sky Pilot`, `Filemonk`, …) so swapping provider does
not quietly turn check 1 into a no-op. It is control-tested in both
directions — it must match the real delivery apps and must not match
Messaging, Shopify Email, or Flow.

**None of it substitutes for a real test order.** Pay, receive the email,
click the link, open the file, then refund yourself. Every intermediate step
can be correct while the last one fails.
