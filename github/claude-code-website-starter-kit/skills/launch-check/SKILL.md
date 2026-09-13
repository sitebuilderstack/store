---
name: launch-check
description: Work through the pre-launch checklist for a website and report what is ready and what is not, with evidence. Covers content, responsive, accessibility, technical SEO, structured data, performance, security, forms, commerce, analytics and deployment.
when_to_use: Use before taking a site live, before taking payment, or when asked whether something is ready to launch.
disable-model-invocation: true
argument-hint: [url or path]
allowed-tools: Read Grep Glob Bash WebFetch
---

# Pre-launch check

Work through **$1** and report readiness. Do not fix anything in this run.

## The rule that decides whether this is worth running

**A check you have not seen fail is not a check.** After anything passes, break the
thing it checks and confirm it goes red. A link crawler reporting "0 broken links"
without ever having found one is not evidence. This costs a minute per check and it
catches more than any individual item below.

## Blockers — a "no" here stops the launch

- [ ] A real end-to-end transaction completed, with a real payment method
- [ ] Payment provider genuinely **activated**, not merely configured
- [ ] Every form submits and the data arrives where you expect
- [ ] Digital delivery, if any, produces a link that downloads the correct file
- [ ] Delivery works for every checkout path the store allows, including phone-only
- [ ] Order confirmation arrives, is accurate, and its links work
- [ ] Storefront password removed
- [ ] No secrets in the repository, the client bundle, or template source
- [ ] Debug mode, verbose errors and source maps off
- [ ] HTTPS enforced; no mixed content; certificate valid and auto-renewing

## Then, in order

**Content.** No `lorem ipsum`, `TODO`, `Your Company`, `example.com`, bare `href="#"`.
No claim you cannot support. **No fabricated testimonials, reviews, ratings or logos.**
Prices on the page match prices at checkout. Contact details consistent everywhere.

**Responsive.** 320px with no horizontal scroll; 768, 1024, 1440; 200% zoom without
loss; wide content scrolls inside its own container; checked on real hardware.

**Accessibility.** Keyboard-only through the primary journey; focus always visible;
one `h1`, no skipped levels; landmarks; alt text; labelled forms; 4.5:1 and 3:1
contrast; 24×24 targets or a documented exception.

**Technical SEO.** Unique title and description per page; self-referencing canonicals;
no accidental `noindex` in the *rendered* HTML; `robots.txt` not blocking rendering
resources; sitemap listing only canonical 200s; one hostname; no orphans.

**Structured data.** Valid JSON-LD in rendered HTML; types describe what is on the
page; **no review or rating markup without real reviews**.

**Performance.** LCP ≤ 2.5s, CLS ≤ 0.1, INP ≤ 200ms, measured on the deployed site at
the 75th percentile, mobile and desktop separately. The LCP image is **not**
lazy-loaded.

**Analytics.** Firing once per page view on the production hostname; conversion events
verified by triggering them; bot and internal traffic identifiable; someone receives
the alerts.

**Search engines.** Search Console verified for the exact production hostname; sitemap
submitted and showing success; Bing Webmaster Tools likewise.

**Deployment.** Reproducible from a clean checkout; rollback exercised at least once;
404 returns a real 404 status; staging not indexable.

## Output

Group as **Blockers**, **Should fix before launch**, **After launch**. For each: what
was observed and how. State plainly what you could not check — an unchecked item is not
a passing one.

See `LAUNCH-CHECKLIST.md` in this repository for the full eighteen sections.
