# RANK sequence

For subscribers tagged `goal-rank`: they have a website and need more organic traffic.

---

## Email 1 — day 0

**Subject:** Your SEO checklist
**Preheader:** Start with crawlability. Everything else depends on it.

Here it is: **[The Claude Code SEO checklist](https://sitebuilderstack.com/pages/claude-code-seo-checklist)**

**Do this first, before anything on the list.** Open your own site in a private window and
fetch one important page with `curl`. Then compare what you see in the browser against what
came back in the response body. If a heading, your main copy, or your internal links only
exist in the browser version, you have a rendering problem, and no amount of title
optimisation will matter until it is fixed.

That check takes two minutes and reorders the rest of your work.

---

## Email 2 — day 2

**Subject:** Why technically good sites fail to rank
**Preheader:** Usually it is not a ranking problem at all.

Most "we can't rank" problems are not ranking problems. They are indexing problems wearing
a ranking problem's clothes.

A page that Google has not indexed cannot rank for anything, and Search Console will tell
you this plainly if you ask it the right question. "Discovered — currently not indexed"
means Google knows the URL exists and has chosen not to fetch it. That is not a penalty and
it is not a metadata problem. It is usually a site that is new, thin on links, or asking
for more crawl budget than its authority justifies.

The reason this matters: the standard response is to publish more pages. That makes it
worse. More unindexed URLs do not help the unindexed URLs you already have.

On this site, 24 of 57 URLs are currently in that state. I am not fixing it by publishing
more. I am fixing it by improving the ones that already have impressions and by earning
links.

Check yours before you write anything new. Search Console → Pages → the "Why pages aren't
indexed" table.

No product in this email.

---

## Email 3 — day 4

**Subject:** The audit order that stops you wasting work
**Preheader:** Dependency order, not importance order.

Most SEO audits are a flat list, which is why acting on them is so unsatisfying: you
optimise a title on a URL that is about to be canonicalised away, and the work evaporates.

Run them in dependency order instead:

1. **Crawlability.** Can it be fetched at all? robots, response codes, rendering.
2. **Canonicals.** Which URL is the real one? Absolute, self-referencing, and pointing
   somewhere that returns 200.
3. **Indexing decisions.** Which URL families *should* be indexed? A decision, stated per
   family, not a default you inherited.
4. **Metadata.** Titles and descriptions — only now, once you know which URLs survive.
5. **Structured data.** Only where it describes something visible on the page.
6. **Speed.** Core Web Vitals at the 75th percentile, segmented mobile and desktop.

Each step invalidates work done out of order. That is the whole argument for the sequence.

The [Search Console workflow](https://sitebuilderstack.com/blogs/guides/google-search-console-claude-code)
guide covers pulling this from the API rather than clicking through the interface.

---

## Email 4 — day 6

**Subject:** A real Search Console analysis, including the dead ends
**Preheader:** What 1,093 impressions actually told me.

I ran the striking-distance analysis on this site. Real numbers, and the useful part is
what they did *not* support.

1,093 impressions, 3 clicks, 134 queries, 21 pages, over 90 days. Small, because the site
is young.

What the "positions 4–20" band contained: mostly one person's certification quiz question,
pasted into Google verbatim, several times. Optimising for it would have been pointless.

What was actually there, and worth acting on:

- One guide ranking **position 2** for a technical query, with **zero clicks** across 12
  impressions. The page did not mention the thing being searched for — Google was ranking
  it on adjacency. That is not a title problem. Rewriting the title to mention it would
  have made the title more accurate about the query and less accurate about the page.
  I added the missing content instead, then updated the description.
- The **highest-demand query cluster on the site sitting at position ~50.** No metadata
  change reaches position 50. That is a coverage and authority problem.

The lesson I keep relearning: the report tells you what to *look* at. It does not tell you
what is true. The page still has to be opened.

---

## Email 5 — day 8

**Subject:** The SEO & Website Audit Toolkit
**Preheader:** Twenty audits, in dependency order.

The [SEO & Website Audit
Toolkit](https://sitebuilderstack.com/products/claude-code-seo-website-audit-toolkit) is
the sequence from email 3, written out in full: twenty audit prompts across fourteen
modules, in dependency order, each stating its role, objective, discovery phase,
constraints, evidence requirements and deliverables.

Two things it does that a general "audit my site" request does not:

**Every finding has to come with evidence** — the URL, the response, the exact markup. Not
a summary you have to trust.

**Audits are forbidden from fixing.** An audit whose findings disappear into a commit
leaves you with a diff and no report, and afterwards you cannot tell which finding was real
or whether the fix was right.

55 files, plain Markdown, one payment. It will not promise you rankings, and any workflow
in it that could be read as promising rankings is written specifically to refuse.

---

## Email 6 — day 11

**Subject:** Traffic you cannot convert is still a problem
**Preheader:** Two of the three, or all three.

Ranking is the middle of three problems. Building the site is before it; converting the
traffic is after.

The one after is where SEO work goes to die. Doubling organic sessions doubles nothing at
all if the page they land on does not do its job, and the work of finding out which part
is failing is a different discipline with different evidence standards.

The [Complete Site Builder Stack](https://sitebuilderstack.com/products/complete-site-builder-stack)
is all three: build, rank, convert. $39.99 together; $59.97 bought separately. Both prices are
real, and the difference is not a discount off a former price — there was never one.

If ranking is genuinely your only problem, buy the SEO toolkit on its own. That is the
honest recommendation more often than not.
