# Change request — Harbourline Physiotherapy

> **FICTIONAL EXAMPLE**, continuing from `completed-website-scope-example.md`.
> The effort figures are invented for illustration and are not market rates.

---

## The request, as it arrived

> **From:** practice manager
> **Date:** 6 May
> **Subject:** couple of things
>
> Hi — a few bits after the team looked at staging:
>
> 1. Can we get the Contact page phone number bigger on mobile? It's tiny.
> 2. Rav wants to add a fourth service — dry needling. Same as the others.
> 3. We've decided we do want online booking after all. The team all use
>    Cliniko, is it just a case of plugging it in?
>
> Thanks!

Three requests in one friendly email. They are three different things, and
answering them as one is how a project loses a fortnight.

---

## Classification

Each request compared against the approved scope, **before** any estimate.

### 1. Phone number size on mobile — **IN SCOPE**

Scope reference: **F7** — "Pages are usable on a 390px screen" — and section 10,
which says anything that does not match the scope is a fix, not a review round.

A phone number too small to read on a phone fails F7. This is a defect against
the agreed criteria.

**Outcome:** fixed, no charge, does not consume a review round.

### 2. A fourth service page — **OUT OF SCOPE**

Scope reference: section 4 lists **nine pages**, three of which are service
pages. Section 6 excludes "a fourth or subsequent service page" by name.

This was anticipated and written down, which is why it takes thirty seconds to
answer rather than an uncomfortable conversation.

**Outcome:** estimated separately. It is a small, well-understood piece of work
— the layout exists, so it is content entry, a navigation update and a
redirect check.

```
Change request CR-01
Add a fourth service page (Dry needling), using the existing Service layout.

Includes:  page build, navigation entry, sitemap entry, links from Services index
Excludes:  copy (client supplies, per C1), photography
Effort:    3 hours
Cost:      [rate x 3]
Schedule:  no impact IF copy arrives by 13 May. After that, +2 working days
           to launch, because it lands inside the review window.
Needs:     approver's yes in writing, and the copy
```

### 3. Online booking with Cliniko — **OUT OF SCOPE, and bigger than it looks**

Scope reference: section 6 excludes "online booking or appointment scheduling"
and "online payments", both by name, and assumption **A1** records that the
project assumes **no patient or health data is handled anywhere on the site**.

"Is it just a case of plugging it in?" is a fair question and the answer is no —
not because embedding is hard, but because of what the request changes about the
project.

**The honest answer:**

- An embedded booking widget is genuinely quick to place on a page.
- But booking collects health-related personal data. A1 assumed the site
  handles none. That assumption is now wrong, and A1 says what happens when an
  assumption is wrong: the scope is re-drafted before any work.
- That pulls in a privacy notice covering the new processing, a data-processing
  position with the booking provider, cookie consent for the embed, and a
  decision about what the practice is responsible for versus the provider.
- None of that is web development, and some of it needs advice this project does
  not provide.

**Outcome:** not estimated as a line item. Proposed as a separate, later piece
of work, so it does not hold up a launch that is otherwise three weeks away.

> **Note on tone.** Nothing above says "that will cost extra" as a first
> response. Two of the three requests are answered before money is mentioned,
> and one of them is simply done. A change process that prices every question
> teaches a client to stop asking questions, which is worse for both sides.

---

## The reply

> Hi — thanks, these are all useful. Taking them in turn:
>
> **1. Phone number on mobile.** Agreed, that is too small. It falls under the
> "usable on a 390px screen" criterion we agreed, so I am treating it as a fix
> rather than a revision — no charge, and it does not use up a review round.
> It will be on staging by Thursday.
>
> **2. Fourth service page (dry needling).** Happy to add it. It sits outside
> the nine pages we scoped, so I have written it up as a small change request:
> 3 hours, [cost], and no impact on the launch date provided the copy reaches
> me by 13 May. After that it lands in the review window and pushes launch by
> about two days. Say the word and I will start; I just need the copy and a
> yes in writing.
>
> **3. Online booking.** I would like to do this, but not as part of this
> project, and I want to be straight about why. Embedding the widget is the
> easy part. Taking bookings means the site starts handling health-related
> personal data, and we scoped this project on the basis that it handles none
> — that is written into the assumptions. Changing it brings in a privacy
> notice, the agreement with Cliniko, consent for the embed, and a few
> questions you would want proper advice on rather than mine.
>
> My suggestion: launch on 30 May as planned, then look at booking properly as
> a second phase in June. I will put together what it involves so you can
> decide with the actual picture in front of you.
>
> Is that alright? If you would rather bring booking forward, that is your
> call — but the launch date moves and I would want to say by how much before
> you decide.

---

## Recorded in the scope

After the approver replies, the scope document is updated:

**Section 14, open questions** — add:

| # | Question | Owner | Needed by |
|---|----------|-------|-----------|
| Q4 | Is online booking a phase 2? If so, when does scoping start? | Client | 30 May |

**Section 14, assumptions** — A1 is annotated, not deleted:

> **A1** — No patient or health data is collected anywhere on the site.
> *6 May: challenged by a request for online booking. Confirmed still true for
> this project; booking deferred to a separate phase. If booking is brought
> into this project, this scope is re-drafted first.*

**Change log** — add:

| CR | Date | Request | Class | Outcome |
|----|------|---------|-------|---------|
| — | 6 May | Phone number size, mobile | In scope | Fixed, no charge |
| CR-01 | 6 May | Fourth service page | Out of scope | Estimated, awaiting approval |
| — | 6 May | Online booking | Out of scope | Deferred to a later phase |

The annotation on A1 is the part worth copying. In six months, "why doesn't the
site take bookings?" has a dated answer, written at the time, by the person who
asked.
