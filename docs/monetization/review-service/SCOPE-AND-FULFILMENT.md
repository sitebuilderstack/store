# Website Launch & Conversion Review — scope and fulfilment checklist

**Status: internal. Not published. The public page takes requests only; no
price, turnaround or availability is advertised until the owner approves the
figures in section 5.**

---

## 1. What the service is

A fixed-scope, asynchronous review of one public website, delivered as a written
report. No access to the customer's systems, no changes made on their behalf,
no meetings required.

## 2. Included

- One public website
- Up to five agreed public URLs
- Review of four things, on those URLs only:
  1. **Messaging** — does the page say what the business does, for whom, and does
     it match the traffic source it is reached from
  2. **Navigation and structure** — can a visitor get from arrival to the action
     the page exists for; do the promises on buttons match their destinations
  3. **Visible technical issues** — what the served response shows: status codes,
     redirects, canonical and robots directives, titles and descriptions,
     heading structure, structured data, obvious render-blocking weight
  4. **The visitor-to-purchase journey** — the path from landing to the point of
     commitment, and where it asks for something it has not yet earned
- A prioritised set of findings, each with the evidence it rests on
- Recommended next action per finding, and a Claude Code prompt for the ones
  where a prompt is the right tool
- One round of written clarification questions after delivery

## 3. Excluded — stated on the public page too

- Any change to the customer's website
- Penetration testing, vulnerability scanning, or security certification
- Legal, privacy, or accessibility certification (observations are not an audit
  against a standard)
- Guaranteed ranking, traffic, sales, or performance improvement
- Unlimited revisions, ongoing advice, or a support relationship
- Access to analytics, admin, hosting, or any private system — if a finding
  would need that, it is listed as "needs data we do not have"
- Competitor research beyond what the named pages show

## 4. The rule that keeps it honest

**Public pages show what a page says, not what visitors do.** Nothing in a
report may describe a conversion rate, a bounce rate, a drop-off, or "most
visitors" — those need analytics the review does not have. A finding says what
was observed on the page and why it matters; the customer's own data decides
whether it mattered.

## 5. Pricing and capacity — ASSUMPTIONS, owner approval required

| Item | Value | Basis |
| --- | --- | --- |
| Pilot price | **$149** | Internal hypothesis. Not published, not charged. |
| Estimated fulfilment time | **3.5–5 hours** | Estimate, from the timed dry run in section 6 plus writing. Not measured across multiple real engagements. |
| Implied hourly | $30–43 | Arithmetic on the two rows above. |
| Turnaround | not advertised | Cannot be promised until capacity is confirmed. |
| Concurrent slots | not advertised | Same. |

Breakdown of the estimate:

| Stage | Estimate |
| --- | --- |
| Read the request, agree the five URLs, decline or accept | 15 min |
| Capture the five pages (responses, headings, metadata, CTAs) | 30 min |
| Messaging and journey review, by hand | 60–90 min |
| Technical pass over the captures | 45–60 min |
| Write and prioritise the report | 60–90 min |
| Clarification round | 20 min |

**At $149 and 4.5 hours this is roughly $33/hour before tax and before the
time spent on requests that are declined.** That is the number the owner should
decide on: it is defensible as a pilot to learn what the work actually takes,
and it is not a rate to build a business on. Options if it is too low: raise the
price, tighten the scope to three URLs, or productise the capture step further.

## 6. Fulfilment checklist

Run in order. Nothing is promised to the customer until step 3.

- [ ] **1. Request received** — an email from the intake form at
      `/pages/website-review`, subject "Website review request"
- [ ] **2. Triage** — is the site public, in English, and within scope? Is the
      goal something a page review could plausibly speak to? If not, decline by
      reply and say why. A decline costs 10 minutes and is not a failure.
- [ ] **3. Accept** — reply with: the five URLs as agreed, the price, what is
      excluded, when the report will be sent, and how to pay. **This message is
      the booking; nothing before it is.**
- [ ] **4. Payment** — received before the review starts.
- [ ] **5. Capture** — `content/membership/pilot-01/capture.py` for each URL,
      saved with the date. This is the evidence the report cites.
- [ ] **6. Review** — the four areas in section 2, in that order. Record every
      finding with its evidence as you go; do not write from memory afterwards.
- [ ] **7. Write** — from `REPORT-TEMPLATE.md`. Priority per finding, evidence
      per finding, and the "not checked" section filled in honestly.
- [ ] **8. Deliver** — PDF or Markdown by email, with the captures attached.
- [ ] **9. Clarification** — one round, within 14 days, by email.
- [ ] **10. Record** — date, URLs, hours actually taken, price, outcome. After
      five engagements, revisit section 5 with real numbers.

## 7. When to decline

- The site is behind a login, unfinished, or not in English
- The request is really "fix my site" — that is not this service
- The goal stated is one a page review cannot speak to ("we need more traffic
  next week")
- Anything requiring access to systems
- A competitor of an existing customer, where the review would use what was
  learned in that engagement
