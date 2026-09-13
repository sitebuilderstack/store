# Claude Code Website Audit Checklist

For auditing a website that already exists — yours or someone else's. The launch checklist
asks "is this ready to ship?". This one asks "what is wrong with what already shipped, and
which of it matters?".

Work through it as an inspection, not a to-do list. Record findings with evidence: the URL,
what you observed, and how you observed it. An audit whose findings cannot be reproduced is
an opinion.

**Prioritise by impact, not by section order.** A dead checkout outranks a missing meta
description no matter which appears first here.

## How to run it

1. Crawl the site and record status, title, description, canonical and word count per URL.
2. Fetch the rendered HTML for one page of each template type.
3. Open the site as a visitor, on a phone, and try to do the thing it wants you to do.
4. Only then start reading the code.

Steps 3 and 4 are in that order deliberately. Reading the templates first tells you what
the site is *supposed* to do, which makes it much harder to see what it does.

## 1. First impressions

- [ ] Within five seconds, is it obvious what this site offers and to whom?
- [ ] Is there one clear next action, above the fold, on the homepage?
- [ ] Does the page look finished, or does it look like a template with content dropped in?
- [ ] Is anything visibly broken on first load — layout, images, fonts, spacing?
- [ ] Does the site feel trustworthy? Real name, real contact route, real policies?

## 2. Content

- [ ] Placeholder text: `lorem ipsum`, `TODO`, `Your Company`, `example.com`
- [ ] Claims that cannot be supported
- [ ] Testimonials, logos, review counts or ratings with nothing real behind them
- [ ] Stale content: outdated years, discontinued products, dead announcements
- [ ] Duplicated content across pages
- [ ] Pages with no discernible purpose
- [ ] Inconsistent product names, prices, or contact details between pages
- [ ] Spelling, grammar, and a single consistent spelling convention
- [ ] Author identified where it matters, with credentials that are true

## 3. Conversion

- [ ] Every call-to-action is visible, contrasting, and clearly clickable
- [ ] Every call-to-action goes somewhere that exists — check them from non-home pages too
- [ ] Fragment links (`#buy`) do not appear on pages where that section does not exist
- [ ] Price, what you get, and what happens next are all stated before the buy button
- [ ] Forms are short, labelled, and explain what happens after submission
- [ ] The path from landing to conversion is countable in clicks, and short
- [ ] Objections are answered on the page: refunds, licensing, support, delivery
- [ ] Nothing important is hidden behind a hover, a carousel, or an accordion

## 4. Navigation and information architecture

- [ ] Every page is reachable from the homepage
- [ ] Navigation labels describe destinations, not internal jargon
- [ ] Current location is indicated
- [ ] Breadcrumbs present where the hierarchy is more than one level deep
- [ ] Footer contains the pages people look for there: contact, policies, about
- [ ] Search exists if the site is large enough to need it, and returns useful results
- [ ] Mobile navigation opens, closes, traps focus correctly, and is keyboard-operable

## 5. Broken things

- [ ] Full internal-link crawl: no 404s, no 500s
- [ ] No links to redirects internally — point at the destination
- [ ] No redirect chains or loops
- [ ] External links resolve, use HTTPS, and open safely (`rel="noopener"` on `target="_blank"`)
- [ ] In-page anchors resolve to an element that exists
- [ ] Images all load; no broken or missing media
- [ ] Forms submit and the data arrives
- [ ] The crawl actually completed — a partial run reporting zero errors is not a pass

## 6. Technical SEO

- [ ] Unique title and meta description on every indexable page
- [ ] No duplicate titles, no duplicate H1s
- [ ] Self-referencing canonicals, absolute and HTTPS
- [ ] No unintended `noindex` in the rendered HTML
- [ ] `robots.txt` valid and not blocking rendering resources
- [ ] Sitemap present, current, and containing only canonical 200s
- [ ] One canonical hostname; variants redirect in one hop
- [ ] Search Console: coverage errors, manual actions, security issues
- [ ] Cannibalisation: two or more pages competing for one query

## 7. Structured data

- [ ] Present where it should be, absent where it would be false
- [ ] Valid JSON in the rendered HTML
- [ ] No duplicate or conflicting entities of the same type on one page
- [ ] Product data matches the visible price, currency and availability
- [ ] Article author and dates are real
- [ ] Breadcrumb markup matches the visible breadcrumb
- [ ] **Review or rating markup with no real reviews behind it** — flag as a compliance risk

## 8. Accessibility

- [ ] Keyboard-only pass through the primary journey, start to finish
- [ ] Visible focus on every interactive element
- [ ] Heading structure: one `h1`, no skipped levels
- [ ] Landmarks present and used correctly
- [ ] Images: meaningful `alt` on informative, empty `alt` on decorative
- [ ] Forms labelled; errors announced and not colour-only
- [ ] Contrast: 4.5:1 text, 3:1 large text and UI components
- [ ] Target sizes meet 24×24 CSS pixels or a documented exception
- [ ] Zoom to 200% without loss of content or function
- [ ] Automated scan run, and a manual pass done — automation catches well under half

## 9. Mobile

- [ ] No horizontal scroll at 320px
- [ ] Content parity with desktop
- [ ] Tap targets comfortable and not overlapping
- [ ] Fixed headers and sticky bars do not cover content or the primary action
- [ ] Checked on real hardware, on mobile data

## 10. Performance

- [ ] LCP, CLS and INP measured on the live site, on mobile
- [ ] Field data reviewed in Search Console where traffic allows
- [ ] Page weight and request count noted; the largest contributors identified
- [ ] Images oversized for their rendered dimensions
- [ ] Render-blocking scripts and stylesheets
- [ ] Third-party tags inventoried — each one named, justified, and costed
- [ ] Fonts: subset, preloaded, fallback stack, no invisible-text flash
- [ ] Layout shift traced to a cause, not just observed

## 11. Security

- [ ] HTTPS enforced, no mixed content, certificate valid
- [ ] Security headers present: CSP, nosniff, referrer policy, frame protection, HSTS
- [ ] `/.env`, `/.git/config`, backup filenames all return 404
- [ ] No secrets in the client bundle or page source
- [ ] Debug output, stack traces and verbose errors absent in production
- [ ] Public forms have spam protection
- [ ] Admin surfaces not publicly reachable or indexable
- [ ] Dependency versions in the client bundle checked for known vulnerabilities

## 12. Commerce

- [ ] Payment provider genuinely activated, not merely configured
- [ ] A real end-to-end test purchase, with a real card
- [ ] Checkout works on mobile
- [ ] Price consistency: page, cart, checkout, receipt
- [ ] Order confirmation arrives, is accurate, and its links work
- [ ] Digital delivery produces a link that downloads the correct file
- [ ] Delivery works for every checkout path the store allows, including phone-only
- [ ] Refund and cancellation paths exist and have been tried
- [ ] Policies reachable from checkout and consistent with what the store actually does

## 13. Analytics and measurement

- [ ] Analytics installed, firing once per page view, on the production hostname
- [ ] Conversion events defined and verified by triggering them
- [ ] Bot and internal traffic identifiable — otherwise the numbers mean nothing
- [ ] Reported traffic sanity-checked against server logs or platform data
- [ ] Consent handling correct where required
- [ ] Someone looks at the data on a schedule

## 14. Legal and trust

- [ ] Privacy policy, terms, and refund/returns policy exist and are reachable
- [ ] They describe what the site actually does
- [ ] Contact details are real, current, and consistent everywhere
- [ ] No leftover branding, domains or addresses from a previous business
- [ ] Ownership is identifiable — a name, a company, or both
- [ ] Any affiliation or independence claim is accurate

## 15. Operations

- [ ] Deploys are reproducible from a clean checkout
- [ ] Rollback path exists and has been exercised
- [ ] Backups exist and a restore has been tested
- [ ] Uptime and error monitoring in place, with someone receiving alerts
- [ ] Domain and certificate renewal will not lapse unnoticed
- [ ] Documentation exists for whoever inherits this

## Writing up the audit

For each finding record: **URL**, **what was observed**, **how it was observed**,
**why it matters**, **severity**. Then sort by severity, not by section.

Severity is usually clear:

| Severity | Examples |
| --- | --- |
| Critical | Cannot buy, cannot contact, data exposed, site not indexable |
| High | Broken primary CTA, no delivery, major accessibility barrier, fabricated reviews |
| Medium | Duplicate titles, missing structured data, slow LCP, thin pages |
| Low | Inconsistent spacing, minor copy issues, cosmetic warnings |

Findings without evidence go at the bottom, marked as unverified. Say plainly which checks
you could not complete and why — an audit that hides its own gaps is worse than a short one.

## Related

- [Claude Code website audit: complete production checklist](https://sitebuilderstack.com/blogs/guides/claude-code-website-audit)
- [Claude Code website launch checklist](https://sitebuilderstack.com/pages/claude-code-launch-checklist)
- [Claude Code SEO checklist](https://sitebuilderstack.com/pages/claude-code-seo-checklist)
- [Claude Code security checklist](https://sitebuilderstack.com/pages/claude-code-security-checklist)

The [Claude Code Website Launch System](https://sitebuilderstack.com/products/claude-code-website-launch-system) contains
the audit prompts that produce these findings with evidence attached.

## Licence

Free to use in any project, including client work. Do not resell or republish it as your own.
