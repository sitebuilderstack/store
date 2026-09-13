# Sprint: search, sales and engagement — September 2026

Branch `feature/seo-sales-engagement-2026`. Two commits, 78 files, ~7,400 lines.

The detailed reports are in `reports/`. This is the short version and the parts
worth arguing with.

## What decided the shape of the work

Three numbers, all measured rather than assumed:

- **1,093 impressions, 3 clicks** over 90 days. The site is fourteen days into
  Search Console.
- **24 of 57 sitemap URLs are "discovered — currently not indexed."**
- **Eight query/page rows** in positions 4–20, most of them one person's
  certification quiz question pasted into Google.

The second is the binding constraint. A page Google has chosen not to fetch
cannot rank, and publishing more pages competes for crawl budget the site has
not earned. So this cycle published **two** new pages and improved existing ones,
against a brief that could have been read as asking for a content programme.

## The three judgement calls worth challenging

**1. Two suggested pages were not created.** The brief asked for
`/pages/website-readiness-score` and `/pages/claude-code-prompt-builder`. Both
already exist under different names, are indexed and are linked from several
places. Creating the suggested URLs would have manufactured exactly the
cannibalisation the same brief asked me to remove, in the same cycle. Both
existing tools were extended to the specified functionality instead.

**2. The bundle was built without demand evidence.** `BUNDLE-ARCHITECTURE.md`
listed the signals that would justify one — repeat multi-product buyers,
pre-sales questions, carts with two products. None was present, because the
store has had one paid order in its lifetime. The bundle exists because the brief
asked for it, not because the data called for it. That is recorded in the doc
rather than glossed.

**3. A guide ranking #2 with zero clicks got new content, not a new title.**
`/blogs/guides/build-shopify-store-with-claude-code` ranked 2.0 for a
theme-check query and did not mention theme-check anywhere. Rewriting the title
to match the query would have made the title more accurate about the query and
less accurate about the page. The missing content was added instead, verified by
running the tool, and the description then updated to something true.

## Tools that were wrong before the site was

Three audits reported findings on their first run that were the tool's fault:

- The internal-linking audit said **all 27 guides** fail to link to their hub.
  They all do, five times each, from the template.
- The indexation audit reported **13 findings that were correct behaviour** —
  deliberately noindexed tag archives, legitimately indexed policy pages, and a
  working 301 reported as a duplicate.
- The cannibalisation classifier reported **four false pairs** sharing only a
  word like "audit" in their titles.

In each case the rule was tightened and a self-test added for that specific
mistake. A check that fires on every row is almost always the check being wrong,
and the cheap response — accepting the finding and changing the site — would have
done real damage in at least two of the three.

## What is enforced rather than intended

- The bundle publisher refuses a description that states any money, invents a
  discount, misstates the totals, or prices the bundle at or above the separate
  total. Six guards, all control-tested by breaking them.
- The agents auditor verifies that the stated $197 still equals the sum of the
  live component prices, so a price change breaks the check rather than the
  claim.
- The benchmark page's results section is generated from the raw rows, so it
  cannot imply a result it does not have, and the suite fails if the published
  CSV carries a row the raw store does not.
- The readiness score recommends nothing at all when every category is strong,
  and that is the first assertion its test makes.

## Still blocked, and on whom

| Blocked on | What |
| --- | --- |
| Store owner | Attach three archives to the bundle and one each to the two toolkits, then place a real test order on each. Three products are purchasable and undeliverable. |
| Store owner | Connect an email platform. Three sequences are written; nothing sends. |
| Whoever runs it | 90 benchmark trials. The infrastructure is complete and the page says plainly that no data exists. |
