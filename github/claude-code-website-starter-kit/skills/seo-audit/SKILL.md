---
name: seo-audit
description: Run a technical SEO audit against a site or repository and report findings with evidence. Checks crawlability, indexability, canonicals, metadata, headings, structured data, internal links and Core Web Vitals, in dependency order.
when_to_use: Use before a launch, after a template change, or when asked to check SEO, indexing, canonicals, metadata, schema, sitemap or robots.txt.
disable-model-invocation: true
argument-hint: [url or path]
allowed-tools: Read Grep Glob Bash WebFetch
---

# Technical SEO audit

Audit **$1** and report findings. Do not fix anything in this run.

## Rules

1. **Inspect the rendered response, not the template.** A `noindex` is often injected
   by a platform or plugin and appears nowhere in source. Fetch the URL.
2. **Every finding needs evidence** — a file and line, or the actual response. A
   finding you cannot evidence is marked `UNVERIFIED`.
3. **Never invent search volume, difficulty, traffic or rankings.** You do not have
   that data. Say "not measured" and name where the figure would come from.
4. **Say what you could not check, and why.** An audit that hides its gaps reads as
   complete.

## Order

Work top to bottom. Each step gates the ones after it — fixing metadata on a page
that cannot be crawled achieves nothing.

1. **Crawlability** — `robots.txt` reachable and valid; nothing needed to render is
   disallowed; no blanket `Disallow: /` left from staging; sitemap declared.
2. **Indexability** — no `noindex` in the *rendered* HTML or `X-Robots-Tag` header on
   pages meant to rank; staging and preview surfaces are noindexed.
3. **Canonicals** — one per page, absolute, HTTPS, self-referencing unless a genuine
   duplicate exists; parameter variants collapse to the clean URL; the target returns 200.
4. **URLs and redirects** — one canonical hostname; HTTP redirects to HTTPS; no chains
   or loops; old URLs land on 200s, not the homepage.
5. **Sitemap** — reachable, valid, only canonical indexable 200s; no redirects, 404s or
   noindexed URLs. On a hosted platform, validate the generated file rather than
   replacing it.
6. **Metadata** — every indexable page has a unique title and description; titles
   around 50–60 characters, descriptions 140–155; no duplicates; no unresolved
   template variables or HTML entities.
7. **Headings** — exactly one `h1`; levels descend without skipping.
8. **Structured data** — parse every `application/ld+json` block from the rendered
   HTML. Report any that does not parse. Check no duplicate entities of one type on a
   page. **Flag any review or rating markup that has no real reviews behind it as a
   compliance risk.**
9. **Internal links** — no orphans; descriptive anchor text; no links to redirects; no
   broken links.
10. **Core Web Vitals** — LCP, CLS and INP measured on the live site, mobile first.

## Output

One block per finding:

```
Finding:
Severity:       critical | high | medium | low
Location:       file:line, or the URL
Evidence:       what you observed
Why it matters:
Fix:            the smallest change that resolves it
Validation:     how I confirm the fix worked
```

Sort by severity, not by the order above. End with a list of what you could not check.

## Before you report a clean result

Break one thing the audit checks — delete a canonical from a local copy, point an
internal link at a URL that does not exist — and confirm the check reports it. **A
check you have not seen fail is not evidence of anything.**

See `SEO-CHECKLIST.md` in this repository for the full list this works through.
