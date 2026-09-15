# Four-guide sprint — 3 September 2026

Four supporting guides published. This is the record: what each one is, what it links to,
what was verified, and why none of them duplicates something that already existed.

---

## 1. Claude Code Website Security Audit: Complete Workflow

| | |
| --- | --- |
| URL | `/blogs/guides/claude-code-website-security-audit` |
| Words | 2,555 |
| Primary intent | claude code security audit |
| Pillar | How to Build a Website With Claude Code |
| Free resource | Claude Code Security Checklist |
| Diagram | `diagram-security-audit-reach.png` |

**Sections:** what an agent actually reaches · scope · the fifteen-pass workflow · secrets
including git history · dependencies and supply chain · authentication · authorisation ·
input handling · sessions · headers · browser exposure · APIs and webhooks · CI/CD and
logging · the audit prompt · finding format · fix and prove the fix · what this does not
replace.

**Links in:** build pillar (Security section), website audit guide, enterprise guide,
resources hub.
**Links out:** CLAUDE.md pillar, GitHub Actions, hooks, website audit, enterprise, build
pillar, security checklist, case study.

**Sources:** OWASP Top 10:2025, OWASP Cheat Sheet Series, MDN HTTP headers, GitHub secret
scanning, GitHub Actions hardening.

**Research note:** OWASP has published a **2025** edition. Writing from memory would have
cited the 2021 list. The article uses the current categories, including the two that
changed materially — A03:2025 Software Supply Chain Failures (new, expanded from the old
vulnerable-components category) and A09:2025 Security Logging & Alerting Failures
(renamed to emphasise alerting).

---

## 2. Google Search Console With Claude Code: Complete SEO Workflow

| | |
| --- | --- |
| URL | `/blogs/guides/google-search-console-claude-code` |
| Words | 2,765 |
| Primary intent | google search console claude code |
| Pillar | Claude Code SEO |
| Free resources | SEO Checklist, Website Audit Checklist |
| Diagram | `diagram-gsc-position-tiers.png` |

**Sections:** let the data choose the work · what the four metrics mean · queries against
pages both directions · windows and comparisons · position bands and the action each
deserves · CTR opportunities · content gaps and when not to write · the query-to-page
table · the Search Analytics API · handing data to Claude Code · improve the page that
already ranks · internal links decided by data · indexing states read correctly · a weekly
routine · what not to do.

**Links in:** SEO pillar, technical SEO audit, Shopify SEO, build pillar (Get indexed),
resources hub.
**Links out:** SEO pillar, technical SEO audit, Shopify SEO, website audit, security
audit, SEO checklist, audit checklist.

**Sources:** Google Search Analytics query API, Google page indexing report, Search
Central getting-started, Google sitemap documentation.

**Research note:** two facts came from primary sources and would likely have been wrong
otherwise. `dataState` defaults to `final`, not `all` — a script that omits it silently
excludes the last two days. And Google's own definition of "Discovered — currently not
indexed" is that it "wanted to crawl the URL but this was expected to overload the site;
therefore Google rescheduled the crawl", with no action required. Much published advice
treats that state as an error to fix by resubmitting.

**First-hand material:** the worked example is real — the skills guide earning 335
impressions with a third of its queries about installing a skill, an intent the page did
not cover. The query/page table uses real rows from this property.

---

## 3. Claude Code Performance Optimization: Core Web Vitals Workflow

| | |
| --- | --- |
| URL | `/blogs/guides/claude-code-performance-core-web-vitals` |
| Words | 2,281 |
| Primary intent | claude code core web vitals |
| Pillar | How to Build a Website With Claude Code |
| Free resources | Launch Checklist, Website Audit Checklist |
| Diagram | `diagram-perf-loop.png` |

**Sections:** what "faster" has to mean · Core Web Vitals precisely · the loop and the
one-variable rule · baseline · Lighthouse, PSI and DevTools · diagnosing LCP · diagnosing
INP · diagnosing CLS · images · JavaScript · CSS and fonts · Shopify · the performance
prompt · before/after reporting · mistakes.

**Links in:** build pillar (Performance section), SEO pillar, Shopify SEO, website audit,
accessibility guide, resources hub.
**Links out:** website audit, SEO pillar, build pillar, Shopify build guide, launch
checklist, audit checklist.

**Sources:** web.dev Core Web Vitals, optimize LCP / INP / CLS, Chrome DevTools
Performance panel, MDN PerformanceObserver.

**Research note:** thresholds verified as LCP ≤ 2.5 s, INP ≤ 200 ms, CLS ≤ 0.1, assessed
at the **75th percentile, segmented across mobile and desktop**. FID is retired — INP
became a stable Core Web Vital in 2024. The article states this explicitly, because
advice still optimising for FID is a useful freshness test.

**First-hand material:** the Shopify section uses this store's measured numbers — LCP
676 ms, CLS 0.0000, 145 requests, ~1 MB — and the point that most of the request count is
platform code that must not be removed.

---

## 4. Claude Code Accessibility Audit: Complete WCAG Workflow

| | |
| --- | --- |
| URL | `/blogs/guides/claude-code-accessibility-audit` |
| Words | 2,789 |
| Primary intent | claude code accessibility audit |
| Pillar | How to Build a Website With Claude Code |
| Free resources | Website Audit Checklist, Launch Checklist |
| Diagram | `diagram-a11y-automated-vs-human.png` |

**Sections:** what a scanner reaches · which standard · the workflow · automated tools ·
semantic HTML · headings · keyboard · focus management · forms · accessible names ·
images and alt text · colour and contrast · target size · ARIA · dynamic interfaces · the
prompt · the manual pass · what you must not claim.

**Links in:** build pillar (Accessibility section), website audit guide, performance
guide, resources hub.
**Links out:** website audit, performance, security audit, build pillar, CLAUDE.md pillar,
audit checklist, launch checklist, case study.

**Sources:** W3C WCAG overview, How to Meet WCAG 2.2, Understanding SC 2.5.8, W3C WAI on
evaluation tools, ARIA Authoring Practices Guide, MDN ARIA.

**Research note:** WCAG 2.2 confirmed as the current W3C Recommendation (5 October 2023,
updated 12 December 2024); WCAG 3 is an early draft and is not something to audit against.
SC 2.5.8 quoted with all five exceptions, because the **Inline** exception is what stops
a target-size check producing a wall of false positives on in-sentence links.

**First-hand material:** the 1:1 contrast failure on this site's primary CTA, caused by a
single point of CSS specificity; and the `aria-hidden` + `tabindex="-1"` card-thumbnail
pattern, which an audit script here wrongly flagged before the check was corrected.

---

## Cannibalisation review

Each guide was compared against every existing page before writing.

| Guide | Nearest existing content | Why it does not duplicate |
| --- | --- | --- |
| Security audit | Security Checklist (resource); build pillar §9; website audit §11; enterprise "what a security review will ask" | The checklist is a list; the pillar and audit each give it one section; the enterprise guide is about deploying Claude Code in an organisation, not auditing a website. No existing page is a security audit workflow |
| Search Console | SEO pillar "Search Console and submission"; technical SEO audit "Submission" | **This was the real risk.** Both existing pages cover *submitting*. Neither covers reading performance data — bands, CTR, query/page mapping, the API, the weekly routine. The new guide explicitly hands submission back to the technical SEO audit rather than re-explaining it |
| Performance | Build pillar §11; SEO pillar §11 Core Web Vitals; website audit §10 | Three single sections from three different angles. None is a diagnostic workflow, none covers the one-variable rule, none has the Shopify constraints |
| Accessibility | Build pillar §10 | One section. Clearest gap of the four |

**Nothing was created because a keyword existed.** No fifth article was written.

---

## Validation

| Check | Result |
| --- | --- |
| HTTP | 200 on all four |
| Canonical | Self-referencing on all four |
| H1 | Exactly one per page |
| Robots | No `noindex` on any |
| Title / description | Unique across the site; duplicate detection run over all 48 crawled URLs |
| Structured data | `BlogPosting` + `BreadcrumbList`, author `Person` / James Joyner IV, `datePublished` and `dateModified` present, image present. No duplicate Article entities |
| Open Graph / Twitter | 8 OG tags, 3 Twitter tags per page |
| Author box | Rendering on all four |
| Article validator | 23 articles, 0 failures, 0 warnings |
| Test suite | 9/9 |
| Site-wide SEO audit | 0 findings |
| Accessibility | Clean at 320 px and 1280 px on all four |
| Broken links | 0, across 28 pages and 59 internal URLs |
| Sitemap | All four present in `sitemap_blogs_1.xml` |
| `llms.txt` / `agents.md` | All 23 guides listed, including the four |
| IndexNow | Submitted, HTTP 200, key accepted |
| Bing URL submission | 8 URLs; quota decremented 95 → 87 |
| Google | Sitemap resubmitted, HTTP 204 |

**Indexing status:** all four are new, so Google has discovered but not yet crawled them.
That is the expected state and, per Google's own documentation, requires no action.

---

## Two defects found during validation

**Page two of the guide index shipped page one's title and description.** With 23 guides
the hub paginates at 12, so `/blogs/guides?page=2` is a second indexable URL and it
carried an exact duplicate of the first page's title tag — the same class of problem as
the tag archives fixed in a previous sprint. Both paginated pages now carry the page
number, and both stay indexable and self-canonicalising, which is what Google asks for;
pointing every page at page one would hide the eleven articles that only appear later.

**The site audit could not have found it.** `audit-seo-site.py` stripped every query
string before crawling, so no paginated URL was ever fetched. It now follows `?page=N`
while still collapsing other parameter variants, and the crawl went from 48 URLs to 74.

That second finding also produced a `?page=1` alias, which Shopify canonicalises onto the
bare URL correctly. Rather than special-case it the way the policy alias had been, the
rule is now general: **a crawled URL that canonicalises onto another crawled URL is the
platform resolving its own duplicate**, so a shared title there is a note rather than a
finding. The self-test was extended to prove the exemption does not swallow a real
duplicate, and that a canonical pointing at a URL nobody crawled still fails.

## A note on the guide cards

The cards on `/blogs/guides` show image, title, excerpt, date and reading time. They do
**not** show the author or the tags. That is deliberate rather than an omission: every
guide has the same author, so printing it twelve times per page adds no information, and
the tags already have their own archive pages. The byline and author box are on every
article, where they carry weight.

## Tooling changed along the way

`head()` in `scripts/generate-article-diagrams.py` now raises rather than silently
clipping a subtitle that exceeds the canvas. It immediately caught **three pre-existing
diagrams** whose subtitles had been cut off at the right edge since publication. All three
were rewritten and replaced in place.

`scripts/replace-file.py` is new. Uploading a filename that already exists makes Shopify
append a UUID, so the original URL keeps serving the old asset — the only way to update in
place is delete-then-reupload. The script verifies the canonical URL serves again before
reporting success, because the window between the two is a 404.
