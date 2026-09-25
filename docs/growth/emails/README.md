# CLAUDE.md Starter Kit — email sequence

Five emails, plain text, sent over eight days after someone downloads the free kit.

**None of this is configured or sending.** See "What has to happen before any of this
runs" at the bottom — there are two blockers, and one of them is that the signup form has
never successfully produced a subscriber.

## The shape

```
Value → Education → Proof → Use case → Offer
```

Not five sales emails. Four of the five are worth reading if the reader never buys
anything, which is the only reason the fifth gets opened.

| # | Day | Subject | Job | Product mention |
| --- | --- | --- | --- | --- |
| 1 | 0 (immediate) | Your CLAUDE.md Starter Kit | Deliver, and give one quick win | One line at the end |
| 2 | 2 | Why "build me a website" isn't enough | Teach the underlying idea | None |
| 3 | 4 | Five production problems this caught | Proof, from the case study | One link |
| 4 | 6 | Which of these are you building? | Let them self-identify | Contextual |
| 5 | 8 | What's actually in the Launch System | The offer | The CTA |

## Voice

Technical, pragmatic, concise. No hype, no countdown timers, no fake scarcity, no
"Hey {{first_name}}!". Assume the reader can read a diff. Every email should be shorter
than the reader expects.

## Files

| File | |
| --- | --- |
| [`email-1-delivery.md`](email-1-delivery.md) | Immediate |
| [`email-2-context.md`](email-2-context.md) | Day 2 |
| [`email-3-proof.md`](email-3-proof.md) | Day 4 |
| [`email-4-workflows.md`](email-4-workflows.md) | Day 6 |
| [`email-5-offer.md`](email-5-offer.md) | Day 8 |

## After email 5

A slow stream, at most monthly, and only when there is something: a new guide, a new free
checklist, a change in Claude Code worth knowing about. **No email purely to maintain
frequency.** An empty month gets no email.

## Compliance

- Consent is collected at the form. The kit is delivered on the strength of that request;
  marketing consent is a separate, explicit opt-in and must not be assumed from it.
- Every email carries a working unsubscribe link and a real postal address.
- Sender name and reply-to must be a monitored address — `admin@sitebuilderstack.com`.
- Subject lines describe the contents. No false "Re:" or "Fwd:".
- The privacy policy must describe what the list is used for before the first send.
- Nobody is imported, added, or subscribed without having asked.

## What has to happen before any of this runs

**Blocker 1 — there is no email platform.** The store has three apps installed: Messaging,
the custom Admin API app, and Digital Products. No Shopify Email, no Klaviyo, no Mailchimp.
Marketing automations cannot be created through the Admin API, so this cannot be scripted:
somebody has to install an email app and build the five-step automation in its UI.

**Blocker 2 — the form has never produced a subscriber.** A query of every customer record
on the store returns two, neither tagged `claude-md-kit`, and the only one with an email
address is `NOT_SUBSCRIBED`. The opt-in has been live for days with zero signups.

That second one matters more. Before building an automation on top of this form, somebody
has to submit it once, by hand, and confirm three things:

1. A customer record is created.
2. It carries the `claude-md-kit` tag. **This is specifically unverified.** The form posts
   `contact[tags]`, and whether Shopify applies it on this endpoint has not been observed
   once — storefront hCaptcha blocks automated submission, correctly, so it could not be
   tested from here.
3. `emailMarketingConsent.marketingState` is what you expect.

Run `python3 scripts/funnel-metrics.py` afterwards; it reports all three.

If the tag does not apply, the trigger has to key off newsletter consent plus signup date
instead, and every automation below has to be built on that instead.
