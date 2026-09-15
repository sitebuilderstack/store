# Engagement implementation

September 2026.

## The decision that shaped Actions 7 and 9

The brief asked for `/pages/website-readiness-score` and
`/pages/claude-code-prompt-builder`.

Both already exist under different names — `/pages/launch-readiness-score` and
`/pages/website-prompt-builder` — are indexed, and are linked from the tools hub,
the guides and the resources hub.

Creating the suggested URLs would have produced two pairs of near-identical
pages competing for the same queries: **exactly the cannibalisation Action 2
exists to remove**, self-inflicted in the same cycle. Both existing tools were
extended to the specified functionality instead.

## Action 7 — Website Readiness Score

### What changed

A seventh category, **Conversion**, with four questions:

- You know your conversion rate, and where the number comes from
- The main call to action says what happens next, not "Submit" or "Learn more"
- Every form field has been justified — you can say why each one is needed
- Someone outside your team has tried to complete the main task and you watched

Twenty questions became twenty-four. Category order in the Liquid and in
`READINESS_CATS` must match, because the form supplies a category index per
answer and a mismatch would silently file every answer under the wrong heading
rather than erroring. That is now stated in a comment above the array.

### Recommendations that genuinely derive from the answers

The rule lives next to the scoring so the two cannot drift:

- Three or more categories under 60 → **the bundle**, because that is a build,
  search and conversion problem rather than one of them
- Conversion weak → the conversion toolkit
- SEO weak → the SEO toolkit
- Security, deployment, performance or accessibility weak → the Launch System
- Otherwise → **nothing at all**

That last branch is the one that matters. A tool recommending a purchase whatever
you answer is not deriving anything, and the test asserts the negative case
first: a perfect score must show no card.

Every card is rendered server-side with a live title and price and hidden;
JavaScript reveals at most one. No product data is duplicated into the script,
and a drafted product simply has no card to reveal.

### Tested

- A perfect score recommends nothing — verified hidden, zero cards shown
- Everything weak recommends the bundle, and only the bundle
- Only Conversion weak recommends the conversion toolkit, at a live `$59`
- Twenty-four gaps listed when everything is answered "No"
- Seven categories painted in the score block

## Action 8 — Learning tracks and persistent progress

### Storage

One key, `sbs-learning`, holding `{done, saved}`. Deliberately separate from the
existing `sbs-route` roadmap key: that one answers "where do I start" and is
keyed by goal, this one records "what have I read" and is keyed by guide.
Merging them would mean changing goal discarded reading history.

Completion is keyed by **guide**, not by track-and-guide. A guide in two paths has
been read once, and ticking it in one place while it stays unticked in another is
the kind of detail that stops people trusting the feature.

Every access is wrapped in try/catch, and availability is **tested** rather than
assumed — `localStorage` throws on access in some privacy modes, not just on
write. Where it throws, the controls never appear. A button that pretends to
remember and then forgets is worse than no button.

### Three surfaces

**Guides** get Mark complete and Save for later, below the article. The lesson id
is the unqualified handle, because Liquid's `article.handle` is qualified
(`guides/claude-code-seo`) while the hubs' `steps` metafield is not — keying on
the qualified handle would record progress the hub could never find. The test
asserts the exact key for this reason.

**Hubs** show `N of M complete — P%` over their own path, with completed steps
struck through and their number badge filled. Completion is shown by a tick and a
strike as well as colour, never colour alone.

**`/pages/my-learning`** is new: four tracks, 21 lessons, all rendered
server-side from the hubs' own `sbs.steps` metafields. Nothing about the site's
structure is duplicated into JavaScript — reorder a path on its hub and this page
follows, because it is reading the same list the hub renders.

It shows overall completion, per-track progress, the next unread lesson on any
started track, saved guides with individual removal, and a reset behind a
confirmation.

Without JavaScript it is still a complete, crawlable index of every track and
lesson — 21 real links — with the progress furniture absent rather than broken.

### Tested, in both directions

`scripts/test-learning.js` asserts the full round trip across three pages:

- Nothing is stored before any click
- Marking complete stores exactly one lesson, under the handle the hub uses
- `aria-pressed` and the label both report state to assistive technology
- Clicking again clears it rather than accumulating
- The hub then shows `1 of 4 complete — 25%` with exactly one lesson struck
- My Learning counts it, ticks it, lists the saved guide, and offers a next step
- **Reset empties storage, not just the view** — asserted by reading
  `localStorage` afterwards, not by looking at the page
- The reset control withdraws once there is nothing to reset
- With JavaScript disabled, 4 tracks / 21 lessons / 21 links remain and no reset
  control is offered

## Action 9 — Claude Code Prompt Builder

Two dropdowns were added, and they change the **shape** of the generated prompt
rather than adding a line to it.

**Task** — build, fix, audit, SEO, security, accessibility, performance,
conversion, deploy, refactor. Every auditing task generates a prompt that opens
with *"This task changes nothing"*, forbids editing any file, replaces the
Implementation section with a Reporting section, and ends its deliverables with
"No code changes. None."

That is the whole point. An audit whose fixes land in the same run leaves a diff
and no report, and afterwards nobody can tell which finding was real.

**Stage** — planning, initial build, testing, pre-production, in production,
optimising. A production-stage prompt states that real users depend on it and
requires the blast radius and rollback for every change. A planning prompt
refuses to write implementation code at all.

Tested in both directions: a build task produces implementation deliverables and
no read-only clause; an audit task produces the clause, drops Implementation, and
adds Reporting; a deploy task in production demands a rollback without being
read-only.

## Events added

`lesson_completed`, `lesson_saved`, `learning_reset`,
`readiness_product_clicked`, and the three `lead_segment_*` events.

Only the handle is published, and only on the transition into the state.
**The stored progress itself never leaves the browser** — there is no identifier,
so the site can see that *a* guide was completed and never which browser
completed it. That is asserted by the test, not promised in a comment.
