# CR-07 — completed

**Site:** harbourline-physio.example (demonstration site)
**Change:** homepage headline
**Done:** 24 September 2026

## What you asked for

The homepage headline said "Welcome" and did not say what the practice does.

## What changed

One line, in the homepage hero. The headline now reads:

> **Physiotherapy in Harbourline — same-week appointments**

Nothing else on the page was edited.

## What was verified

The page was recorded before the change and again afterwards, and the two
records compared automatically:

| Checked | Before | After | Result |
| --- | --- | --- | --- |
| Headline (`h1`) | Welcome | Physiotherapy in Harbourline — same-week appointments | changed, as asked |
| Page title | Harbourline Physio — Physiotherapy in Harbourline | unchanged | held |
| Canonical URL | https://harbourline-physio.example/ | unchanged | held |
| Indexing directive | index,follow | unchanged | held |
| Contact form | posts to /api/contact, 1 form | unchanged | held |
| "Book an assessment" button | /book | unchanged | held |
| Section headings | Our services | unchanged | held |

Thirteen properties were compared; one changed, and it was the one you asked
for.

## What was not verified

- How the page looks on a specific phone or browser — the check reads what the
  server sends, not how it is painted.
- Whether the new wording performs better. That needs four weeks of the
  analytics you already have; this change makes the page say what you do, which
  is a different claim from saying it will convert better.
- Anything outside this page.

## How to reverse it

One line in `templates/index.html`, on branch `cr-07-homepage-headline`; the
previous wording is in the commit and in `before.json`. Reverting takes a
minute and needs no other change.
