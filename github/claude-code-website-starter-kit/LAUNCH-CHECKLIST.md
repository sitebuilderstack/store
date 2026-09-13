# Claude Code Website Launch Checklist

Everything worth checking between "the site looks finished" and "the site is live and
behaving". Written for people building with Claude Code, but almost all of it applies to
any website.

Work top to bottom. The order is deliberate: several later checks are meaningless if an
earlier one fails. A crawl report is worthless if the site is still behind a password, and
a performance number means nothing if the page renders the wrong content.

Where a check can be automated, run it. Where it can only be observed, open the page and
look. **The failure mode that costs the most is a check that reports success because it
never actually ran.** Prove each check can fail before you trust it passing.

## 1. Requirements

- [ ] The site's single purpose is written down in one sentence
- [ ] The primary conversion action is named, and there is exactly one per page
- [ ] Target audience and their entry point are known (search, referral, ads, direct)
- [ ] Content inventory exists: every page that must exist at launch is listed
- [ ] Legal pages identified: privacy, terms, refund/returns, cookie or consent notice
- [ ] Contact route decided and reachable by a real human
- [ ] Anything explicitly out of scope for launch is written down

## 2. Project setup

- [ ] `CLAUDE.md` exists, is under ~150 lines, and names the real commands
- [ ] `.gitignore` covers `.env`, build output, dependency directories, editor files
- [ ] `.env.example` lists variable names with no values
- [ ] Lockfile committed; install uses the frozen/locked path
- [ ] Node/Python/Ruby version pinned in a file the tooling reads
- [ ] Lint, format, typecheck and test commands all run clean on a fresh clone

## 3. Architecture

- [ ] Routes and URLs decided before pages are built; URLs are stable and readable
- [ ] URL casing, trailing slashes and word separators are consistent sitewide
- [ ] Navigation reflects the real hierarchy, not the build order
- [ ] Shared layout/header/footer is one component, not copied per page
- [ ] Nothing in the client bundle imports server-only code
- [ ] Build output directory is git-ignored and reproducible from a clean checkout

## 4. Content

- [ ] No placeholder text anywhere: `lorem ipsum`, `TODO`, `TKTK`, `XXX`, `Your Company`
- [ ] No placeholder links: bare `href="#"`, `example.com`, `localhost`
- [ ] Every claim on the site is one you can support
- [ ] No fabricated testimonials, reviews, ratings, logos, or customer counts
- [ ] Prices on the page match prices at checkout
- [ ] Contact details are correct and consistent everywhere they appear
- [ ] Dates ("Updated…", copyright year) are real and current
- [ ] Spelling and grammar checked; one spelling convention throughout

## 5. Responsive and cross-browser

- [ ] Renders correctly at 320px width with no horizontal scroll
- [ ] Renders correctly at 768px, 1024px, 1440px
- [ ] Text reflows at 200% browser zoom without loss of content or function
- [ ] Tables, code blocks and wide media scroll inside their own container, not the page
- [ ] Checked in at least two rendering engines (Chromium and WebKit or Gecko)
- [ ] Checked on a real phone, not only a simulator
- [ ] Touch targets are comfortable; nothing important sits under a fixed bar

## 6. Accessibility

- [ ] Keyboard alone can reach and operate every control, in a sensible order
- [ ] Focus is always visible; no `outline: none` without a replacement
- [ ] Skip-to-content link present and functional
- [ ] One `<h1>` per page; heading levels descend without skipping
- [ ] Landmarks used: `header`, `nav`, `main`, `footer`
- [ ] Every informative image has meaningful `alt`; decorative images have `alt=""`
- [ ] Form inputs have associated labels; errors are announced, not colour-only
- [ ] Text contrast ≥ 4.5:1, large text and UI components ≥ 3:1
- [ ] Interactive targets meet the 24×24 CSS pixel minimum, or qualify for an exception
- [ ] Page has a `lang` attribute
- [ ] Content is not lost when animation or motion is reduced
- [ ] Automated audit run *and* a manual keyboard pass done — automation finds under half

## 7. Technical SEO

- [ ] Every page has a unique, intent-matching `<title>` under ~60 characters
- [ ] Every page has a unique meta description under ~155 characters
- [ ] One self-referencing `<link rel="canonical">` per page, absolute, HTTPS
- [ ] No accidental `noindex` on pages that should rank — check the rendered HTML
- [ ] `robots.txt` reachable, does not block CSS/JS needed for rendering
- [ ] XML sitemap reachable, lists only indexable, canonical, 200-status URLs
- [ ] Sitemap referenced from `robots.txt`
- [ ] Internal links use descriptive anchor text
- [ ] No orphan pages: every indexable page is reachable by a link
- [ ] Pagination, filters and sort parameters do not create crawlable duplicates
- [ ] One hostname wins: www/non-www and http/https all redirect to it, in one hop
- [ ] Redirects from any old URLs are in place and land on 200s

## 8. Structured data

- [ ] JSON-LD parses as valid JSON in the *rendered* HTML, not just the template
- [ ] Types describe what is genuinely on the page
- [ ] Organization or Person entity present and consistent sitewide
- [ ] Product markup matches the visible price, currency and availability
- [ ] Article/BlogPosting has headline, dates, author and publisher
- [ ] BreadcrumbList matches the visible breadcrumb
- [ ] No duplicate or conflicting entities of the same type on one page
- [ ] **No review, rating, or aggregateRating markup unless real reviews exist**
- [ ] Tested against a rich-results validator, and warnings understood rather than blindly "fixed"

## 9. Open Graph and social

- [ ] `og:title`, `og:description`, `og:url`, `og:type` set per page
- [ ] `og:image` is an absolute HTTPS URL, at least 1200×630, and actually loads
- [ ] `twitter:card` set (`summary_large_image` for pages with an image)
- [ ] No HTML entities leaking into meta content (`&amp;ndash;` and friends)
- [ ] Share preview checked for the homepage and at least one deep page

## 10. Images and media

- [ ] Served at the dimensions they render, not scaled down in the browser
- [ ] Modern format where supported (WebP/AVIF) with a fallback
- [ ] `width` and `height` set on every image to reserve space
- [ ] Below-the-fold images lazy-loaded; the LCP image is **not**
- [ ] Descriptive filenames, no `IMG_4021.jpg`
- [ ] Alt text is descriptive and not keyword-stuffed
- [ ] Video does not autoplay with sound; captions available where there is speech

## 11. Performance

- [ ] Largest Contentful Paint ≤ 2.5s on a mid-range mobile connection
- [ ] Cumulative Layout Shift ≤ 0.1
- [ ] Interaction to Next Paint ≤ 200ms
- [ ] Total blocking JavaScript understood; every third-party script justified
- [ ] Fonts subset and preloaded, with a real fallback stack, no invisible-text flash
- [ ] Compression (gzip/brotli) on for text assets
- [ ] Cache headers set: long, immutable for fingerprinted assets; short for HTML
- [ ] Measured on the deployed site, not the dev server

## 12. Security

- [ ] HTTPS enforced; HTTP redirects to it; no mixed content
- [ ] No secrets in the repository, the client bundle, or template source
- [ ] `.env` files not deployed or served
- [ ] Security headers present: CSP, `X-Content-Type-Options`, `Referrer-Policy`, HSTS
- [ ] Forms validated server-side; user input escaped before HTML, SQL or shell
- [ ] Spam protection on public forms
- [ ] Dependencies audited; no known critical vulnerabilities shipped
- [ ] Admin, staging and preview surfaces not publicly reachable or indexable
- [ ] Debug mode, verbose errors and source maps off in production
- [ ] Error pages reveal nothing about the stack

## 13. Forms and conversion

- [ ] Every form submits successfully end to end, on the live site
- [ ] The submitted data actually arrives where you expect it
- [ ] Validation errors are clear, specific, and keyboard-accessible
- [ ] Success state is unmistakable and does not lose the user
- [ ] Autocomplete attributes set on name, email, address and payment fields
- [ ] Confirmation email sends, is not in spam, and links in it work
- [ ] Every call-to-action goes somewhere that exists — including from non-home pages

## 14. Commerce (if applicable)

- [ ] A real end-to-end test purchase completed, with a real payment method
- [ ] Payment provider is activated, not just configured
- [ ] Tax and currency correct for at least two regions you sell to
- [ ] Order confirmation email arrives and is accurate
- [ ] Digital delivery, if any, produces a link that actually downloads the file
- [ ] Delivery works for every checkout path, including phone-only and guest checkout
- [ ] Refund and cancellation paths tested, not assumed
- [ ] Storefront password removed at go-live

## 15. Analytics and monitoring

- [ ] Analytics installed and firing on the live domain, once per page view
- [ ] Internal and bot traffic filtered or at least identifiable
- [ ] Key conversion events tracked and verified by triggering them
- [ ] Consent handling in place where required
- [ ] Uptime check on the homepage and one critical path
- [ ] Error reporting collecting from production
- [ ] Someone actually receives the alerts

## 16. Search engine registration

- [ ] Google Search Console property verified for the exact production hostname
- [ ] Sitemap submitted in Search Console; status is "Success"
- [ ] Bing Webmaster Tools verified and sitemap submitted
- [ ] IndexNow key file reachable at the site root, returning 200 and the key text
- [ ] Live URL inspection on the homepage shows it as crawlable and indexable
- [ ] No manual actions or security issues reported

## 17. Deployment

- [ ] Deploys from a clean checkout, reproducibly, with a documented command
- [ ] Rollback path exists and has been tried at least once
- [ ] Environment variables set in production and not printed by the build
- [ ] Custom domain resolves; DNS propagated; certificate valid and auto-renewing
- [ ] `www` and apex both resolve to the same canonical host
- [ ] 404 page returns a real 404 status, not 200
- [ ] Staging is not indexable

## 18. Post-launch validation

Do this **on the live site**, after DNS and caches have settled.

- [ ] Full internal-link crawl: zero broken links, zero unexpected redirect chains
- [ ] Fetch every page and confirm status, title, description and canonical
- [ ] Structured data validated on rendered HTML for each template type
- [ ] Search Console coverage checked after 48 hours for unexpected exclusions
- [ ] Core Web Vitals measured on the live domain
- [ ] Test purchase or test form submission repeated on production
- [ ] Analytics shows your own visit
- [ ] Site opened on a phone, on mobile data, by someone who did not build it

## The check that catches the rest

After everything above passes, deliberately break one thing and confirm the relevant check
fails. A link crawler that reports "0 broken links" without ever having found one is not
evidence of anything. This single habit catches more real problems than any individual
item on this list.

## Related

- [How to build a website with Claude Code](https://sitebuilderstack.com/blogs/guides/how-to-build-a-website-with-claude-code)
- [Claude Code website audit: complete production checklist](https://sitebuilderstack.com/blogs/guides/claude-code-website-audit)
- [Claude Code SEO checklist](https://sitebuilderstack.com/pages/claude-code-seo-checklist)
- [Claude Code security checklist](https://sitebuilderstack.com/pages/claude-code-security-checklist)

The [Claude Code Website Launch System](https://sitebuilderstack.com/products/claude-code-website-launch-system) packages
these checks as runnable prompts and audits rather than a list you tick by hand.

## Licence

Free to use in any project, including client work. Do not resell or republish it as your own.
