# Claude Code SEO Checklist

A technical SEO checklist you can hand to Claude Code and work through in order. Every
item is something a machine can verify, which is the point: this list deliberately stops
where SEO becomes guesswork about ranking factors nobody outside Google can measure.

The order matters. Crawlability gates indexing, indexing gates everything else. Fixing
metadata on a page Google cannot reach is wasted effort.

**A note on scope.** An LLM is excellent at the verifiable half of SEO — status codes,
canonicals, markup, link graphs, heading structure — and unreliable at the half that
requires external data, such as search volume, keyword difficulty, or competitor
backlinks. If a tool tells you a keyword gets a specific number of monthly searches
without querying a data source, that number was invented. Get those figures from Search
Console, Bing Webmaster Tools, or a keyword tool with an API.

## 1. Crawlability

- [ ] `robots.txt` returns 200 and is valid
- [ ] Nothing needed to render the page is disallowed — CSS, JS, fonts, images
- [ ] No blanket `Disallow: /` left over from staging
- [ ] Sitemap URL declared in `robots.txt`
- [ ] Crawl-blocking is intentional everywhere it exists, and you can say why for each rule
- [ ] Server does not rate-limit or block legitimate crawler user agents
- [ ] No infinite crawl spaces: calendars, faceted filters, session IDs in URLs

## 2. Indexability

- [ ] Rendered HTML contains no `<meta name="robots" content="noindex">` on pages meant to rank
- [ ] No `X-Robots-Tag: noindex` response header on those pages
- [ ] Check the **rendered** page, not the template — noindex is often injected
- [ ] Staging, preview and password-protected environments *are* noindexed
- [ ] Thin, duplicate or utility pages are deliberately excluded, not accidentally included
- [ ] Search Console shows the important pages as "Indexed", not "Discovered — currently not indexed"

## 3. Canonicals

- [ ] Every indexable page has exactly one `<link rel="canonical">`
- [ ] It is absolute, HTTPS, and uses the production hostname
- [ ] It is self-referencing unless a duplicate genuinely exists
- [ ] Parameterised URLs (`?utm_`, `?sort=`, `?variant=`) canonicalise to the clean URL
- [ ] Paginated pages self-canonicalise; they do not all point at page one
- [ ] Canonical target returns 200, not a redirect or a 404
- [ ] No conflicting signals: canonical says one thing, sitemap or internal links say another

## 4. URLs and redirects

- [ ] One canonical hostname; the other variants redirect to it in a single hop
- [ ] HTTP redirects to HTTPS sitewide
- [ ] No redirect chains longer than one hop, no loops
- [ ] Permanent moves use 301/308, temporary use 302/307 — and the choice is deliberate
- [ ] Old URLs from any previous site redirect to the closest equivalent, not all to the homepage
- [ ] URLs are lowercase, hyphenated, readable, and stable
- [ ] Trailing-slash behaviour is consistent and enforced by redirect

## 5. XML sitemap

- [ ] Reachable, returns 200, valid XML
- [ ] Contains only canonical, indexable, 200-status URLs
- [ ] Contains no redirects, 404s, noindexed pages, or non-canonical variants
- [ ] Under 50,000 URLs and 50MB uncompressed per file; index file used above that
- [ ] `<lastmod>` reflects real modification dates, or is omitted
- [ ] `<priority>` and `<changefreq>` are ignored by Google — do not agonise over them
- [ ] Submitted in Search Console and Bing Webmaster Tools, showing "Success"
- [ ] On a hosted platform, validate the generated sitemap rather than replacing it

## 6. Titles and meta descriptions

- [ ] Every indexable page has a `<title>`; no page shares one with another
- [ ] Titles lead with the query intent, not the brand
- [ ] Roughly 50–60 characters so they are not truncated
- [ ] Every page has a meta description; none are duplicated
- [ ] Descriptions are roughly 140–155 characters and read as a reason to click
- [ ] No keyword stuffing, no pipe-separated keyword lists
- [ ] No unresolved template variables or HTML entities in either
- [ ] The homepage title is not the raw domain or the platform default

## 7. Headings and on-page structure

- [ ] Exactly one `<h1>` per page, matching the page's actual subject
- [ ] Heading levels descend without skipping (no `h2` straight to `h4`)
- [ ] Headings describe the section, and would work as a table of contents
- [ ] The primary topic appears naturally in the first paragraph
- [ ] Content answers the query it targets in the first screenful
- [ ] No hidden text, no text-coloured-as-background, no keyword blocks

## 8. Structured data

- [ ] Valid JSON-LD in the rendered HTML
- [ ] One Organization (or Person) entity, consistent across the site
- [ ] WebSite entity present where appropriate
- [ ] Article/BlogPosting on articles, with headline, datePublished, dateModified, author, publisher
- [ ] Author is a real, identifiable entity — a Person where a person wrote it
- [ ] Product markup on product pages matching visible price, currency, availability
- [ ] BreadcrumbList matching the visible breadcrumb hierarchy
- [ ] No duplicate entities of the same type on one page
- [ ] **No Review/AggregateRating markup without real reviews.** This is a manual-action risk
- [ ] Validated against Google's Rich Results Test on the live URL

## 9. Internal linking

- [ ] Every indexable page is reachable from the homepage in a few clicks
- [ ] No orphan pages
- [ ] Anchor text is descriptive; no "click here", "read more" as the only link text
- [ ] Anchor text varies naturally; no sitewide exact-match keyword links
- [ ] Pillar pages link down to their supporting pages, and supporting pages link back up
- [ ] Related pages within a topic cluster link to each other
- [ ] Navigation and footer links are HTML anchors, not JavaScript handlers
- [ ] No broken internal links and no internal links to redirects

## 10. Content quality

- [ ] Each page targets one search intent, and no two pages target the same one
- [ ] Cannibalisation checked: search `site:yourdomain.com <query>` and confirm one clear winner
- [ ] Content demonstrates first-hand experience where the topic calls for it
- [ ] Claims are supported; statistics have a source; commands and APIs are real
- [ ] Author is identified, with credentials that are true
- [ ] Publish and update dates are real
- [ ] No scaled or templated pages produced primarily for search engines
- [ ] Every page would still be worth publishing if search engines did not exist

## 11. Images

- [ ] Descriptive filenames
- [ ] Meaningful, non-stuffed `alt` on informative images; empty `alt` on decorative ones
- [ ] Served at rendered size, compressed, modern format with fallback
- [ ] `width` and `height` set
- [ ] Lazy-loaded below the fold, eager for the LCP image
- [ ] Images appear in the sitemap or are otherwise discoverable, if image search matters to you

## 12. Performance and Core Web Vitals

- [ ] LCP ≤ 2.5s, CLS ≤ 0.1, INP ≤ 200ms, measured on the live site
- [ ] Measured on mobile as well as desktop
- [ ] Field data checked in Search Console once enough traffic exists — lab data is a proxy
- [ ] Render-blocking resources minimised
- [ ] Layout shift eliminated at the source (dimensions, font fallbacks, reserved ad slots)
- [ ] Third-party scripts audited; each one still earns its cost

## 13. Mobile

- [ ] Mobile rendering is the one that matters — indexing is mobile-first
- [ ] Content parity: mobile shows the same content and links as desktop
- [ ] No horizontal scroll at 320px
- [ ] Tap targets comfortable and not overlapping
- [ ] Interstitials do not obscure content on arrival from search

## 14. International (only if you serve multiple locales)

- [ ] `hreflang` annotations are reciprocal and use valid language-region codes
- [ ] An `x-default` exists
- [ ] Each locale's URLs are distinct and canonical to themselves
- [ ] Skip this section entirely if you serve one language — a broken `hreflang` is worse than none

## 15. Search engine integration

- [ ] Google Search Console verified for the exact production hostname
- [ ] Sitemap submitted; status "Success"; discovered URL count looks right
- [ ] Coverage report reviewed for unexpected exclusions
- [ ] Live URL inspection run on the homepage and one key page
- [ ] Bing Webmaster Tools verified, sitemap submitted
- [ ] IndexNow key file reachable at the site root and returning the key as plain text
- [ ] IndexNow submissions return 200 or 202 — **note that Google does not use IndexNow**
- [ ] URL submission reserved for genuinely new or changed pages, not run on a timer

## 16. Ongoing validation

- [ ] A crawl script you can re-run after every deploy
- [ ] It fails loudly on a partial run rather than reporting a clean result
- [ ] Duplicate title and description detection is part of it
- [ ] Structured data re-validated after template changes
- [ ] Search Console checked monthly for new coverage errors and manual actions
- [ ] Query and page performance reviewed against what you actually publish

## What this list does not do

It does not tell you what to write about, and it will not rank a page that has nothing to
say. Technical SEO removes obstacles; it does not create demand. Every item here is a way
of making sure a genuinely useful page is not held back by something mechanical.

## Related

- [Claude Code SEO: complete website optimization workflow](https://sitebuilderstack.com/blogs/guides/claude-code-seo-website-optimization)
- [Claude Code technical SEO audit: complete workflow](https://sitebuilderstack.com/blogs/guides/claude-code-technical-seo-audit)
- [Shopify SEO with Claude Code](https://sitebuilderstack.com/blogs/guides/shopify-seo-with-claude-code)
- [Claude Code website launch checklist](https://sitebuilderstack.com/pages/claude-code-launch-checklist)

The [Claude Code Website Launch System](https://sitebuilderstack.com/products/claude-code-website-launch-system) turns
this checklist into prompts and audit scripts that produce evidence rather than opinions.

## Licence

Free to use in any project, including client work. Do not resell or republish it as your own.
