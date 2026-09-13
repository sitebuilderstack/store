This is one complete workflow from the [Claude Code Conversion & Revenue Optimization
Toolkit](/products/claude-code-conversion-revenue-optimization-toolkit), reproduced in full
and free to use. The toolkit contains seventy of them.

Two things about it are worth noticing before you run it, because they are the whole
method rather than details of this one workflow.

**It runs in AUDIT mode, which changes nothing.** It produces findings. An audit whose
fixes land in the same session leaves you with a diff and no report, and afterwards nobody
can tell which finding was real or whether the fix was the right one.

**Every finding carries an honesty label.** Proven bug, strong heuristic, experiment
opportunity, or insufficient data. Most conversion reports have no way to say "I don't
know", so everything is written up as though it were known and the reader cannot tell the
reproduced bug from the hunch.

Nothing here will predict a percentage lift, and nothing will recommend a countdown timer.

---

> **Mode: AUDIT** — analysis only.

## Goal

Assess a single-purpose page — the destination of an ad, an email, or a campaign
— against the promise that brought the visitor there and the one action it
exists to produce.

## When to use it

- You are paying for the traffic arriving on this page
- The page has one job and is not doing it
- Ad click-through is healthy and conversion is not
- Before increasing spend on a campaign pointing here

## Inputs you must supply

- `[URL]` — the landing page
- `[SOURCE]` — where the traffic comes from
- `[THE PROMISE]` — the exact ad copy, subject line, or link text that preceded
  the click. This is the single most valuable input; without it you are auditing
  the page in isolation, which is not how it is experienced.
- `[CONVERSION]` — the one action
- `[CURRENT RATE]` — if known

## The prompt

```
Audit the landing page at [URL].

Visitors arrive from [SOURCE] after seeing: "[THE PROMISE]".
The page exists to produce: [CONVERSION].

### Objective
Determine why visitors who clicked do not convert. Change nothing.

### Constraints
- Analysis only.
- Judge every element against the promise above. A landing page is not audited
  in isolation; it is audited as the second half of a two-part sequence.
- 390px first.
- No manufactured urgency or scarcity, no unattributed proof, no pattern from
  01-core/ETHICAL-BOUNDARIES.md.
- Label each finding with its evidence class.

### Phase 1 — Message match
Quote the promise and the page's headline side by side. Rate the match: does the
page continue the sentence the ad started, or does the visitor have to work out
that they are in the right place? Look for the specific words from the promise
appearing on the page.

### Phase 2 — Singularity
Count the distinct actions available: CTAs, navigation links, footer links,
external links, chat widgets. A landing page with site navigation is offering
the visitor a way to leave. Report the count and each exit.

### Phase 3 — The offer
State exactly what the visitor gets, what it costs, and what happens after they
act. If any of those three is not answerable from the page, it is a finding.

### Phase 4 — The form or action
Count fields. For each, state whether the business genuinely needs it before
this conversion, or whether it could be collected later. Note required vs
optional, input types on mobile, error handling, and what happens on success.

### Phase 5 — Friction and reassurance
Identify what would make a reasonable person hesitate at the moment of acting,
and whether the page addresses it at that moment rather than 800px earlier.

### Phase 6 — Load and stability
Measure or estimate: how long until the headline is readable, and whether
anything moves after it appears. A page that shifts under the thumb loses taps.

### Phase 7 — Measurement
Is the conversion tracked? Is the source distinguishable in analytics? Can this
page's conversions be separated from the rest of the site's?

### Deliverables
1. Message match assessment with both texts quoted
2. Exit inventory
3. Field-by-field form analysis
4. Findings in the standard format
5. The three changes most likely to matter, with the reasoning
```

## Expected output

A short, sharp report. Landing pages are small; an audit producing forty
findings has lost the plot. Five to fifteen, with the message-match verdict at
the top.

## Validation

- Read the ad and then the headline aloud, in that order. Does the second follow
  from the first?
- Count the ways off the page yourself and check the audit found them all.
- Try the form on a real phone, including a deliberate validation error.

## Common mistakes

**Auditing the page without the ad.** Most landing page failures are continuity
failures, and they are invisible when the page is viewed alone.

**Removing fields the business needs.** Shorter forms usually convert better and
sometimes produce leads nobody can act on. The question is what is needed *now*,
not what is nice to have.

**Adding urgency to compensate.** If the offer is not compelling, a timer does
not fix it, and a fake one is prohibited here.

**Testing a landing page with too little traffic.** Most campaign pages never
reach the volume an A/B test needs. Fix the obvious things on judgement; save
testing for pages that can support it. See
`08-experimentation/WHEN-NOT-TO-TEST.md`.

## Next actions

- `04-elements/FORM-AUDIT.md` for a form-heavy page
- `04-elements/OBJECTION-HANDLING.md` if the offer is understood but resisted
- `03-funnels/TRAFFIC-SOURCE-FIT.md` if match is fine and conversion is not


---

## What the full toolkit adds

Nothing has been removed from this workflow to make the paid version look better. The
[full toolkit](/products/claude-code-conversion-revenue-optimization-toolkit) adds the
other sixty-nine across thirteen modules: the master CRO audit, the other seven page
audits, funnel mapping and drop-off diagnosis, CTAs and forms and pricing presentation,
the Shopify and SaaS systems, analytics verification, the experimentation system — which
works out whether you have the traffic to test at all — and the report templates.

Plus 68 ready commands and four worked examples, each including what the first pass got
wrong.
