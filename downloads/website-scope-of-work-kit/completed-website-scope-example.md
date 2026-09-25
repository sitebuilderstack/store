# Website scope of work — Harbourline Physiotherapy

> **FICTIONAL EXAMPLE.** Harbourline Physiotherapy does not exist. Every name,
> figure and date here was invented to demonstrate the template. The day rate
> and totals are **not** market rates and should not be used as a benchmark.

Drafted from [`example-client-brief.md`](example-client-brief.md).

---

## 1. Project summary

```
Client:      Harbourline Physiotherapy Ltd
Project:     Website rebuild
Prepared by: [Your name]
Date:        21 March 2027
Version:     v1 — draft for approval
Approver:    R. Okonkwo (Owner). Sole approver for this project.
```

> **Note on the approver.** The brief said the practice manager would brief and
> the owner would sign off. This scope names the owner as the single approver
> and the manager as day-to-day contact. This was confirmed by email on 19
> March before drafting.

## 2. Objectives

1. The practice can update the class timetable without contacting a developer.
2. Enquiries arrive by a tracked route rather than only by phone, so the
   practice can see how many there are.
3. The site is accurate about both clinics: addresses, hours, and which
   practitioners work where.

> Not an objective: "more enquiries" as a number. The site can make enquiring
> easier and measurable. It cannot commit to a volume, and a scope that
> promises one is promising something outside the builder's control.

## 3. Deliverables

| # | Deliverable | Count | Notes |
|---|-------------|-------|-------|
| 1 | Designed and built pages | 9 | See inventory. Three share one service layout. |
| 2 | Responsive implementation | 1 set | Phone, tablet, desktop. Same nine pages. |
| 3 | Editable timetable | 1 | One table, both clinics, editable by the practice. |
| 4 | Enquiry form | 1 | Sends to one named address. |
| 5 | Analytics configuration | 1 | GA4, using the client's existing property. |
| 6 | Redirect map from the old site | 1 | Every old URL to its new equivalent, or to the closest page. |
| 7 | Handoff pack | 1 | Credentials, deploy steps, what is safe to edit. |

## 4. Page and content inventory

| # | Page | Layout | Content source |
|---|------|--------|----------------|
| 1 | Home | Home | Client copy, revised by client |
| 2 | About | Standard | Client copy |
| 3 | Our team | Team | Client copy + 6 headshots (client) |
| 4 | Services | Index | Client copy |
| 5 | Musculoskeletal physiotherapy | Service | Client copy |
| 6 | Sports rehabilitation | Service | Client copy |
| 7 | Post-operative rehabilitation | Service | Client copy |
| 8 | Class timetable | Timetable | Client-maintained after handoff |
| 9 | Contact | Contact | Client copy, both clinics |

**Nine pages.** Pages 5–7 share one layout; a fourth service page would be a
change request, not a variation.

## 5. Functional requirements

| # | Requirement | How it will be demonstrated |
|---|-------------|------------------------------|
| F1 | The enquiry form sends to one named address | A test submission is sent and the approver confirms receipt |
| F2 | The form rejects an empty required field with a visible message | Submit empty; the message is shown and no email is sent |
| F3 | The practice can edit the timetable without a developer | The manager edits a class and the change appears, unassisted, observed |
| F4 | Both clinics' addresses and hours appear on Contact | Compared against the client's written details |
| F5 | GA4 records a pageview and a form submission | Checked in the client's GA4 realtime view |
| F6 | Every old URL resolves | The redirect map is tested; each returns one hop to a 200 |
| F7 | Pages are usable on a 390px screen | Checked on a real device; no horizontal scroll |

## 6. Exclusions

Not included in this project:

- **Online booking or appointment scheduling.** Discussed as "maybe eventually".
- **Online payments** of any kind.
- **A patient portal, login, or any handling of patient data.**
- **A blog**, including its layout and any posts.
- **Copywriting.** All page copy is supplied by the client.
- **Photography.** Headshots are supplied by the client.
- **Logo redesign or recreation.** See assumption A2.
- **Ongoing SEO work**, content production or link building.
- **Multilingual versions.**
- **Email hosting, migration or configuration.**
- **A fourth or subsequent service page.**
- **Hosting and domain fees**, which the client pays directly.

## 7. Client responsibilities

| # | Provides | By when | If late |
|---|----------|---------|---------|
| C1 | Final copy for all 9 pages | 11 April | Build start moves day for day |
| C2 | 6 practitioner headshots, min 1000px | 11 April | Team page ships with placeholders, revisited as a fix |
| C3 | Logo in a vector format, or written acceptance of A2 | 4 April | See A2 |
| C4 | GA4 property ID and access | 18 April | F5 cannot be demonstrated; acceptance for F5 defers |
| C5 | DNS registrar access, or a named person who has it | 25 April | Launch date moves |
| C6 | Both clinics' addresses, hours, phone numbers in writing | 4 April | Contact page cannot be built |
| C7 | Consolidated feedback from the approver within 5 working days of each review | per round | Subsequent dates move by the delay |

## 8. Dependencies

- DNS registrar access (C5). The registrar is not yet identified — see Q1.
- The client's existing GA4 property (C4).
- The current site staying online until cutover, so the redirect map can be
  verified against it.

## 9. Milestones

| Milestone | Target | Assumes |
|-----------|--------|---------|
| Scope approved | 28 March | Approver responds by 27 March |
| Design of 3 key layouts | 18 April | C1, C3 complete; one round of feedback within 5 working days |
| Build complete, staging | 16 May | Design approved 25 April; C2, C6 complete |
| Client review on staging | 23 May | C7 |
| Launch | 30 May | C5 complete; acceptance criteria met; not a Friday |

> **On "before the summer".** These dates hold only if the assumptions hold.
> The binding one is C1: copy for nine pages by 11 April. If that slips a
> fortnight, launch slips a fortnight. This is stated now rather than
> negotiated in May.

## 10. Review rounds

```
Rounds included per deliverable: 2
A round is:     one consolidated set of feedback from R. Okonkwo.
Not a round:    typos, broken links, or anything that does not match this scope.
                Those are fixes and are not counted.
Beyond 2:       a change request under section 12.
```

## 11. Acceptance criteria

| # | Criterion | Checked by |
|---|-----------|------------|
| A1 | All 9 pages exist and are reachable from the navigation | Clicking each, in order |
| A2 | F1–F7 each demonstrated to the approver | Demonstration on staging |
| A3 | No page scrolls horizontally at 390px | Real device |
| A4 | Every old URL resolves in one hop | Redirect map tested |
| A5 | The manager edits a timetable entry unaided | Observed, once |
| A6 | Handoff pack delivered and opened by the client | Confirmed in writing |

## 12. Change-request process

As the template, section 12. Requests are classified **in scope / ambiguous /
out of scope** before any estimate is produced.

## 13. Handoff

- Credentials transferred by the client's password manager, not by email
- Deploy steps documented in the repository
- Decisions log handed over
- Safe for the client to change: timetable, page copy, practitioner details
- Not safe without asking: navigation structure, redirects, form configuration
- Support after handoff: 14 days for defects against section 11. No new work.

## 14. Open questions and assumptions

### Open questions

| # | Question | Owner | Needed by |
|---|----------|-------|-----------|
| Q1 | Which registrar holds the domain, and who can access it? | Client | 25 April |
| Q2 | Is the timetable one table for both clinics, or one each? | Client | 4 April |
| Q3 | Is the existing GA4 property still receiving data? | Builder | 18 April |

> Q2 changes the timetable build. It is **not** assumed. Until it is answered,
> deliverable 3 reads "one table, both clinics" and the alternative is a change
> request. That is deliberate: guessing here silently doubles the work.

### Assumptions

| # | Assumed | If wrong |
|---|---------|----------|
| A1 | No patient or health data is collected anywhere on the site | Materially different project; scope re-drafted before any work |
| A2 | No vector logo exists; the JPEG is used at its current quality | Client supplies vector, or accepts the JPEG in writing |
| A3 | Copy is supplied in editable text, not as PDFs or images | Re-typing is a change request |
| A4 | Both clinics keep the same opening hours year-round | Contact page needs seasonal handling — change request |

---

**Status:** draft for approval. Not approved. Not a contract.
