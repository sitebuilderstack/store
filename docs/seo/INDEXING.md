# Indexing — what has been done, and what only time and links can do

State on 3 September 2026: **40 sitemap URLs, 18 indexed, 12 discovered but uncrawled,
10 unknown to Google.** This document records what was investigated, what was changed, and
what is genuinely outside the codebase.

## What was ruled out

Every one of the 22 unindexed URLs was checked individually. None has a defect:

| Check | Result |
| --- | --- |
| HTTP status to Googlebot's user agent | 200 on all |
| `robots` meta or `X-Robots-Tag` | absent on all |
| Canonical | self-referencing on all |
| Present in the live sitemap | all 10 "unknown" URLs confirmed present |
| Sitemap freshness | Google last downloaded it at 05:59:56; the four newest guides published at 05:56 — they were in the file it fetched |
| `robots.txt` | allows `/pages/`, `/blogs/`, `/products/` |
| Internal links | every one linked from at least one page Google has indexed |

**There is no technical fault to fix.** The site was password-protected until late August,
so despite `/pages/contact` carrying a January publish date, every URL on this domain has
been publicly reachable for about eight days. The coverage pattern is a clean chronological
gradient — 26–30 August indexed, 30 August–1 September discovered, 1–3 September unknown —
which is a crawl queue working through a new site in publication order, not a fault.

Google's own definition, quoted from the
[page indexing report](https://support.google.com/webmasters/answer/7440203): *"The page was
found by Google, but not crawled yet. Typically, Google wanted to crawl the URL but this was
expected to overload the site; therefore Google rescheduled the crawl."* It adds that no
resubmission is necessary.

## What was changed

Two structural improvements, both aimed at the one lever the codebase actually has —
**how few hops a page is from a URL Google already recrawls.**

### The five resource pages are now linked from the homepage

They were reachable only through `/pages/resources`, which is itself not yet indexed — so
each was two hops away, behind a page Google has never fetched. `production-claude-md-starter`
had exactly **one** indexed page linking to it.

`sections/sbs-guides.liquid` gained resource blocks, and the homepage now links all five
directly. The homepage is the most frequently recrawled URL on any site.

### All 23 guides are on one indexed page

`/blogs/guides` paginated at 12, so eleven guides sat on `?page=2` — a URL Google is far
less likely to prioritise. The blog now paginates at 24, putting every guide one hop from a
page that **is** indexed.

Two consequences were handled rather than left:

- **Cost.** The index went from 1,028 ms to 1,252 ms LCP and from 996 KB to 1,423 KB, for
  eleven more cards. Card images gained a `srcset` and dropped from a fixed 800 px request,
  which recovered part of it. Both figures remain well inside the 2.5 s threshold, and the
  trade — 400 KB against eleven pages moving a hop closer — is worth making while discovery
  is the binding constraint.
- **A new thin URL.** With one page of results, `?page=2` still returned 200 with an empty
  list. It is now `noindex, follow`. The layout works out the last page from
  `blog.articles_count` and a `BLOG_PER_PAGE` constant, and `tests/run-all.sh` asserts that
  constant matches `paginate blog.articles by N` in the section — a silent drift there would
  drop a real paginated page out of the index.

### Result

Every previously orphaned URL now has at least two indexed pages linking to it, and 17 of
20 are linked directly from the homepage.

| | Before | After |
| --- | --- | --- |
| Resource pages linked from the homepage | 0 of 5 | 5 of 5 |
| Guides one hop from an indexed page | 12 of 23 | 23 of 23 |
| Targets with no indexed page linking to them | 0 | 0 |
| Lowest indexed-source count for any target | 1 | 2 |

## What is left, and who has to do it

Nothing further can be done from the codebase. Two actions remain, both outside it.

**1. Request indexing in the Search Console UI.** There is no API for this — Google's
Indexing API accepts only `JobPosting` and `BroadcastEvent`. The UI button is manual and
rate-limited, so use it on the pages that matter rather than all 22:

```
/products/claude-code-website-launch-system
/blogs/guides/how-to-build-a-website-with-claude-code
/pages/case-study
/pages/resources
```

Once each. Repeated requests do nothing — Google states resubmission is unnecessary.

**2. Earn external links.** This is the actual constraint. Crawl budget on a new domain is
a function of authority, and authority comes from other sites linking to this one. The
plan is in [`LINK-EARNING-CAMPAIGN.md`](LINK-EARNING-CAMPAIGN.md); the highest-leverage
step remains publishing the GitHub repository, which is built and unpushed.

## How to re-check

```bash
python3 scripts/index-coverage.py          # every sitemap URL, with its state
python3 scripts/gsc-opportunities.py       # impressions, positions, tiers
```

Watch pages moving from *discovered* to *indexed*. That is the signal. Positions moving
from 50 to 40 is not, at this stage.
