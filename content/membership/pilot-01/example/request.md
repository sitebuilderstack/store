# CR-07 — homepage headline

**Fictional client engagement.** Harbourline Physio is a demonstration site
used throughout Site Builder Stack's examples; it does not exist and no client
work is described here.

**Received:** 24 September 2026, by email, from the practice manager.
**Classified:** in scope (module 14 of the Agency & Client Delivery System) —
a wording change inside an existing section, no new deliverable.

## What the client asked

> "The homepage just says Welcome. Can we make it clearer what we actually do?
> People land there from the ads and bounce."

## Restated as an observable outcome

The `<h1>` on `https://harbourline-physio.example/` reads
**"Physiotherapy in Harbourline — same-week appointments"** instead of
**"Welcome"**, and remains the only `<h1>` on the page.

Sent back for confirmation before any work started; confirmed the same day.

## Must not change

- `<title>` — it already carries the town and the service
- canonical and robots directive
- the contact form's `action` and field set
- the primary call to action: text "Book an assessment", href `/book`
- the `<h2>` structure

## Files touched

`templates/index.html`, hero section only. One line.

## Verification

`capture.py` before and after, `compare.py` with `--expect h1` and
`--require "h1=Physiotherapy in Harbourline"`. Results in
`comparison-good.txt`. The alternative implementation that a reviewer would
have passed by eye is in `comparison-bad.txt`.
