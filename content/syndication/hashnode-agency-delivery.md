---
title: "Running a client website project with Claude Code: from the enquiry to the retainer"
subtitle: "The engagement around the build is where freelancers lose money and reputation. A system for it, as commands over one set of files per client."
canonical: https://sitebuilderstack.com/products/claude-code-agency-client-delivery-system
tags: freelancing, agency, claude, web-development, project-management
---

Most developers know how to build a website. The engagement around it is where the money and the reputation go: a proposal improvised the night before, a scope that said "and anything else needed", an estimate that was a guess, revisions that never end because nobody counted the rounds, a handoff that is a folder of files, and no process for turning a finished project into next month's income. Each engagement starts from scratch; each one teaches the same lesson again.

Ask a capable model to "write a proposal" and you get the other problem: confident prose with invented requirements, a budget the client never stated, a promise about rankings, and a signature block that looks like a contract.

What follows is the shape of a repeatable delivery system, as it is implemented in the [Agency & Client Delivery System](https://sitebuilderstack.com/products/claude-code-agency-client-delivery-system) on Site Builder Stack — the design is the useful part whether or not you use those files.

## One set of files per client

The foundation is not a prompt; it is a place where the facts live. Per client: a `client-config.yaml` (who, what, platform, primary conversion, the approver, the review window, the rollback facts); a `CLAUDE.md` with the engagement's summary and ten operating rules; the scope document as the contract; and four logs — decisions, assumptions, changes, risks — as the memory. Every command reads them. None invents. A new person, or a new Claude Code session, reads those files and is caught up.

## The lifecycle, and where the gates are

```text
LEAD → QUALIFY → DISCOVER → AUDIT → SCOPE → PROPOSE → ONBOARD → PLAN → BUILD → QA → CLIENT REVIEW → LAUNCH → HANDOFF → MAINTAIN → RETAIN
```

Each stage has a gate with a file that proves it was passed. A few of them do most of the work:

**Qualify before unpaid hours.** The intake is quoted, not paraphrased; a budget the prospect did not state stays blank. The score — STRONG / POSSIBLE / WEAK — comes with reasons, and the unknowns become the next call's questions. WEAK means "not on these terms", not "no".

**Audit with evidence.** Every finding has an issue, evidence (the URL, the value, the date), business impact in the client's terms — "unknown" is allowed — a recommendation, an effort and a priority from CRITICAL to OPPORTUNITY. The priority actions become the candidate scope. An OPPORTUNITY needs a business reason; otherwise it is padding, and clients notice.

**Scope with counts.** "Up to 8 pages from 4 templates", "2 revision rounds on design", "1 form with up to 8 fields posting to the CRM". Uncounted scope is unlimited scope. The out-of-scope list names what the client will think of later — copywriting, photography, ongoing SEO, subscriptions, members areas — and sits *before* the price. Every deliverable has a criterion someone can test. Client responsibilities carry dates and the day-for-day rule.

**Estimate as a range.** Work items with low, expected and high hours and a note per row saying what each assumes; contingency as a line, not a feeling; review cycles and QA as rows, because they are hours. Quote the range or the high — never the low alone. Compare with actuals at the end; estimates improve only when measured.

## Scope creep, classified in a minute

Every new request — in a meeting, an email, a review comment — is checked against the scope text, quoted rather than remembered, and classified: IN SCOPE (do it, no ceremony), AMBIGUOUS (decide once, generously, and record it so the boundary is clearer next time), OUT OF SCOPE (a change request with four impacts — scope, schedule, cost, technical — and the client's decision). Not every change costs money. Every change is logged; the log is what lets the tenth free change be declined calmly.

## Bounded review rounds

Two per phase. Each has a package — where to look, what was done, what to review, what is *not* part of this review, how to give feedback (one consolidated list), the deadline from the agreement, the launch dependency — and a triage of every feedback item into six classes: bug, content change, design revision, in-scope request, out-of-scope request, question. Silence is not approval unless the agreement says so; the package says you will chase, and you do.

## Launch on evidence

Thirteen checks, each with the file, the log entry or the test that proves it: scope, requirements, QA on the *production* build, written approval, backup, DNS plan, SSL, redirects, SEO (production not noindexed, canonicals not to staging), analytics, forms, environment, rollback. Any blocker is NO-GO regardless of the date. A NO-GO with a new date is cheaper than a rollback.

## Communication rules the drafts follow

Concise. Facts before assumptions, and labelled. No blame — "three pages are outstanding", not "you have not sent". Blockers stated with their effect. Client actions in their own section with dates and why each matters. No jargon the client has not used. No promised rankings, conversion increases, revenue, or a launch date while an input is outstanding. And nothing sent automatically: a command drafts; a person reads and sends.

## The retainer, from evidence

At handoff, the ongoing services the site actually needs — each with the evidence in the project's own files: the platform's update burden, how often content changed during the project, whether organic traffic exists to protect, whether conversion events are configured. "No retainer needed" is a valid answer. Response expectations are targets, not guarantees; exclusions keep it sustainable.

## The clean ending

Access transferred to accounts the client owns and yours removed; data returned and archived with a deletion date, never deleted on the day; an honest testimonial *asked for*, never written for them; a retrospective in which every improvement is an edit to a template or a checklist, made now.

## What it is not

Not legal advice — proposals are not contracts, scope documents do not replace agreements. Not accounting advice — the pricing reasoning is reasoning, with hypothetical figures. Not a guarantee of any client outcome. Those disclaimers are in the templates themselves, because the alternative is a document that looks more official than it is.

The system is on Site Builder Stack: [21 modules, 37 commands, the templates, checklists, a fictional engagement to read end to end](https://sitebuilderstack.com/products/claude-code-agency-client-delivery-system). The technical side of the work — [building](https://sitebuilderstack.com/products/claude-code-website-launch-system), [auditing](https://sitebuilderstack.com/products/claude-code-seo-website-audit-toolkit), [maintaining](https://sitebuilderstack.com/products/claude-code-website-operations-maintenance-system) — is separate, and the [lifecycle page](https://sitebuilderstack.com/pages/build-rank-convert) explains which applies.

---

*Adapted from the Agency & Client Delivery System on Site Builder Stack. Independent; not affiliated with Anthropic.*
