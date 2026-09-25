---
title: "A technical SEO audit where every check has to fail once"
subtitle: "Knowing what to check is the easy half. The hard half is running it so that it produces evidence rather than reassurance."
canonical: https://sitebuilderstack.com/blogs/guides/claude-code-technical-seo-audit
tags: seo, claude, ai-tools, web-development, testing
---

There is no shortage of technical SEO checklists. The list is not the hard part. The hard part is running it in a way that produces evidence rather than reassurance — and the failure mode is specific enough to name: **checks that report success on exactly the condition they exist to catch.**

This is a condensed version of the [full guide on Site Builder Stack](https://sitebuilderstack.com/blogs/guides/claude-code-technical-seo-audit), which has the crawler, the prompts and the CI subset in full. It assumes you already know what to look at and covers how to look, how to prove you looked, and what to do with the result.

## The rule: a check you have not seen fail is not a check

Take any check that just passed and ask what else would produce that same output. Usually three things: the check ran correctly; the check ran against the wrong page, file or attribute; the check never executed. All three print the same green line.

The remedy is a minute of work per check. Break the thing on purpose and confirm the check goes red. Delete a canonical tag from a local copy. Point one internal link at a URL that does not exist. Rename the file the script reads. If the output does not change, you have learned something far more valuable than a passing result. Do it the moment you write the check, not later.

## The crawler, and the partial-run trap

Almost everything downstream needs the URL inventory, so start with the crawl — and know its characteristic failure. An earlier version of the crawler behind this guide reported **zero broken links** across a run in which nine of twenty-eight seed URLs had returned 429. It had retried a few times, given up, and treated an unreachable page as nothing to report.

After the fix — more attempts backing off to sixty seconds, honouring `Retry-After`, and a *distinct exit code for a partial run* — the same crawl reached all 28 pages and found 44 URLs where the throttled run had found 25. The link report had not been wrong so much as based on two-thirds of the site. A crawl that cannot say "I did not finish" will tell you the site is fine.

## Rendered HTML beats template source

An assistant with repository access will happily audit your templates. Templates describe intentions; search engines read responses. Whole categories of problem exist only in the response:

- **Platform fallbacks** — a homepage `<title>` that silently becomes the raw platform domain when a setting is empty.
- **Injected directives** — a `noindex` added by a plugin, a header or a platform preference that appears nowhere in the theme.
- **Double-escaping** — a title captured with an entity in it, then escaped again for `og:title`, printing `&amp;ndash;` into the tag. Correct in the template, wrong in the output.
- **Request-time canonicals** — the canonical for `?variant=` or `?utm_source=` is decided at request time and can only be checked there.

Fetch the page. Read the tag out of the response.

## Structured data: two questions, and people ask only the second

**Does it parse?** Extract every `application/ld+json` block from the rendered HTML and run it through a JSON parser. A trailing comma from a Liquid or JSX conditional is invisible to the eye and fatal to the markup. This is the check most often skipped and the cheapest to run.

**Does it describe the page honestly?** Compare each property against what a visitor sees: the price in the markup against the price on the page, the author against the byline, the breadcrumb list against the visible trail. Not automatable, and worth doing by hand for one page per type. Never add review, rating or aggregate markup without real reviews.

## Four false passes, and what caused each

All four are from auditing the store this guide was written for. The root cause is the same every time: the failure path was never exercised.

| What it reported | What was true | Cause |
|---|---|---|
| 0 broken links | nine of 28 pages never fetched | 429s counted as nothing to report |
| Checkout healthy | store could not take payments | the notice is injected by JavaScript, absent from the initial HTML |
| Checkout accepts email | never actually checked | it read `innerText`; the wording was in a `placeholder` |
| Page has a Liquid error | the page was fine | a regex matched prose *about* Liquid errors in an article |

Three false negatives — a real problem reported as fine — and one false positive. Same discipline fixes both.

## Turning findings into a diff

Audit and repair are separate phases, and mixing them loses the record of what was wrong. Once the findings are written down, work through them one at a time: the fix, the check that the fix did not break the page it was copied from, and — the important one — a demonstration of *both* branches of the condition just written. That is the control-test discipline applied to a fix rather than a check.

## Submission behaves differently in three places

**Google Search Console** — verify the property for the exact production hostname, submit the sitemap, and know that submission is a hint, not an instruction. It ignores `<priority>` and `<changefreq>` entirely. What is worth watching is coverage: "Discovered — currently not indexed" is a quality signal, not a technical fault, and resubmission does not change it. **Bing Webmaster Tools** — faster and more literal. **IndexNow** — a key file and a POST per changed URL; useful, and not a substitute for either.

## The subset worth running on every deploy

An audit run once is a snapshot. The value is in the second run. Small and fast enough for CI: crawl every URL and fail on any 404, 500, redirect chain or *incomplete run*; fail on duplicate titles or descriptions; fail on a missing or non-self-referencing canonical; fail on JSON-LD that does not parse; fail on an unexpected `noindex`. Everything else — content quality, cannibalisation, field Core Web Vitals — is judgement or needs traffic, and belongs in a monthly review rather than a build gate.

## What not to automate

Anything requiring external data: search volume, keyword difficulty, competitor backlinks. An assistant with no data source that produces a specific number has invented it. Whether the content is any good — a script can tell you the title is unique; it cannot tell you the page is worth ranking. Intent overlap — deciding two pages compete and which should win needs someone who understands why both were written.

The [full guide](https://sitebuilderstack.com/blogs/guides/claude-code-technical-seo-audit) has the crawler and the prompts. Running these checks in dependency order, on a schedule, with each one forbidden from fixing in the same run, is what the [SEO & Website Audit Toolkit](https://sitebuilderstack.com/products/claude-code-seo-website-audit-toolkit) packages; the [free SEO checklist](https://sitebuilderstack.com/pages/resources) is the list without the tooling.

---

*Adapted from [Running a technical SEO audit with Claude Code](https://sitebuilderstack.com/blogs/guides/claude-code-technical-seo-audit) on Site Builder Stack. Independent; not affiliated with Anthropic.*
