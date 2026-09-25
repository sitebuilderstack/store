## What this would be

One new workflow a month, for people who use Claude Code on websites they have
to keep working after launch.

A workflow is not an article. Each release is a procedure with the parts that
make a procedure usable: who it is for, what it needs, the prompts, a script
where a script earns its place, a worked example run end to end, the
verification steps, and an honest list of what it does not cover.

The proposed format, every month:

- **One workflow release** — a task you actually meet, taken from request to
  verified result
- **One worked example** — the same workflow run against a demonstration site,
  with the output included, including a run that fails on purpose
- **Verification steps, limitations, and a compatibility note** — what was
  tested, where, and what was not

That is the whole proposition. Not a community, not coaching, not support
hours, not a library of everything.

## What it is not

- **Not the updates you already have.** Every product here includes updates
  within the same major version at no extra cost, through your original
  purchase channel. That does not change, and membership is not a way to get
  them.
- **Not a re-sale of the free guides.** The [36 guides](/blogs/guides), the
  [labs](/pages/labs), the [tools](/pages/tools) and the
  [Weekly Website Fix](/pages/weekly-fix) stay free and stay where they are.
- **Not the products.** A membership release is a standalone workflow; it does
  not include, replace, or unlock any paid product.
- **No unlimited support, live calls, community moderation, or personalised
  engineering help.** If a release is wrong, tell us and we fix the release.

## The distinction, plainly

| | You pay | You get |
| --- | --- | --- |
| **Product** (e.g. the Launch System) | Once | The whole system, plus same-major-version updates |
| **Update to a product** | Nothing | Corrections and additions to what you bought |
| **Membership release** | Monthly, if it launches | A new workflow that is not part of any product |

## The pilot release

Written, tested, and readable below — **Release 01: the client change request,
end to end**. It covers the small live change that no existing product does:
the wording tweak, the extra form recipient, the new FAQ block. The bit between
"the client asked for it" and "it is done", where regressions come from.

Four steps: restate the request as something checkable, capture the page's state
before touching it, implement one change on a branch, then compare before and
after and hand the client a summary they can read.

It ships with two standard-library Python scripts — `capture.py` records what a
page actually serves; `compare.py` says whether the change did what was asked
*and nothing else* — plus a worked example with two runs: the correct
implementation, and a plausible wrong one that looks right in a browser and
fails the check in one line.

<div class="sbs-preview">

**From the worked example — the run that fails:**

```text
Change verification — before -> after-bad
URL: https://harbourline-physio.example/

status           unchanged
final_url        unchanged
title            unchanged
h1               FAIL — new value does not contain 'Physiotherapy in Harbourline'
                   before: Welcome
                   after:  []
canonical        unchanged
forms            unchanged
cta              unchanged

13 checked, 1 failed
Failed: h1
```

The headline is on the page. It is the right words, in the right place, at the
right size. Somebody restyled the hero and the `<h1>` became a `<p>`, so the
page now has no heading at all — invisible in a browser, one line in the check.

</div>

The full release — the four steps, both scripts, the worked example with both
runs, the handoff template — is what a member would receive.

## Status

**Nothing is for sale on this page.** There is no subscription, no price has
been set, and no launch date has been promised. What exists today is the pilot
release above and an interest list.

Joining the list does not reserve a price, hold a place, or commit you to
anything. It is one email if and when this opens, and nothing else.

## What has to be true before this could open

Stated so the list is not mistaken for a launch:

1. A subscription system that can take recurring payment and be cancelled.
2. Delivery that actually restricts access to members — not a hidden page.
3. A price, set by the owner, and the terms that go with recurring billing.
4. Enough releases written in advance that the second month is not a scramble.

Until all four are true, this page takes no money.
