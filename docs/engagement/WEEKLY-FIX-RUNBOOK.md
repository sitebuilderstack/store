# Weekly Website Fix — editorial runbook

The series is a Shopify blog (`weekly-fix`, id `gid://shopify/Blog/126271160612`)
with one article per challenge, template suffix `challenge`, published every
**Thursday at 09:00 in the store timezone (America/Los_Angeles)**. The hub is
`/pages/weekly-fix`; the archive is `/blogs/weekly-fix`; the feed is
`/blogs/weekly-fix.atom` (Shopify's own).

## Sources of truth

| What | Where |
| --- | --- |
| The schedule (number, handle, title, publish date, guide, lab, module, criteria) | `content/content-graph.json` → `challenges` |
| The article body | `content/challenges/NN-<id>.html` |
| The hub's schedule list | `theme/dev/snippets/sbs-weekly-schedule.liquid`, **generated** by `scripts/build-weekly.py` |
| Publisher | `scripts/publish-challenges.py` |

`scripts/validate-graph.py` refuses a challenge that is not on a Thursday, is
not seven days after the previous number, reuses a number or handle, or points
at a guide, lab or module that does not exist.

## State on 17 September 2026

| # | Handle | State | Publish |
| --- | --- | --- | --- |
| 1 | `does-your-contact-form-actually-deliver` | **published** (storefront 200) | 2026-09-17 07:01 PDT |
| 2 | `does-your-main-call-to-action-go-where-its-label-promises` | **scheduled** (isPublished false, publishedAt 2026-09-24T16:00:00Z; storefront 404 until then) | 2026-09-24 09:00 PDT |
| 3 | `can-you-safely-reverse-your-last-deployment` | **scheduled** (publishedAt 2026-10-01T16:00:00Z) | 2026-10-01 09:00 PDT |
| 4 | `does-your-claude-md-match-the-real-project` | **scheduled** (publishedAt 2026-10-08T16:00:00Z) | 2026-10-08 09:00 PDT |

Shopify's `ArticleCreateInput` documents `publishDate` as "the date and time
when the article should become visible"; it refuses `isPublished: true` with a
future date, so a scheduled article is `isPublished: false` plus the future
date. Verify each one goes live with `python3 scripts/publish-challenges.py
--verify` on the day (it fetches the storefront URL and expects 200). If one
did not, `python3 scripts/publish-challenges.py <id>` republishes it
immediately (a date that is today or past publishes now).

## Adding challenge #5 and onward

1. Add an entry to `content/content-graph.json` → `challenges`: next number,
   a handle phrased as the question, the Thursday date (seven days on), the
   guide/lab/module it connects to, `criteria` (four to six self-reportable
   lines), `summary`, `seo` (≤ 158 chars), `file`.
2. Write `content/challenges/NN-<id>.html` with the same sections as the
   first four: lede, problem, prerequisites, scope, safe inspection workflow
   (observe before change), copyable prompt (`<pre data-sbs-copy="prompt">`),
   example evidence (labelled as an example), completion criteria (same list
   as the graph), common mistakes, go further (guide + lab). No invented
   numbers, no testimonials.
3. `python3 scripts/validate-graph.py && python3 scripts/build-weekly.py`,
   then push `snippets/sbs-weekly-schedule.liquid` to the dev theme, check
   the hub, push to live.
4. `python3 scripts/publish-challenges.py --dry-run` then without
   `--dry-run`. Commit the graph, the article and the generated snippet.

## Reminders

The hub carries the site's existing Shopify customer form (`sbs-optin`
section) with its own tag `weekly-fix`, segmentation off, no download, and
copy that states the frequency honestly: at most one email a week, sent when
a challenge goes live, none if a week is skipped. **Nothing sends
automatically.** When a challenge publishes, send one Shopify Email to the
segment `customer_tags CONTAINS 'weekly-fix'` with the challenge link and the
unsubscribe footer Shopify adds. Never send to that segment for anything
else; never add existing subscribers to it.

The form's markup and POST target were verified in the theme preview; a live
submission was not made, because it would create a customer record.

## Rollback

- Unpublish a challenge: `articleUpdate` with `isPublished: false` (or the
  admin). The hub's schedule shows it as "coming <date>" again; nothing else
  changes, and nothing a reader saved in My Projects is touched.
- Remove the series entirely: unpublish the four articles and the
  `weekly-fix` page; the blog can stay (an empty blog renders the archive's
  "no challenges yet" state).
