# Workflow Club — Release 01

## The client change request, end to end

**Status:** pilot release, written 24 September 2026. Not yet delivered to
anyone; the membership is not open.

---

### Who this is for

Someone who maintains a live website for a client or an employer, uses Claude
Code to do the work, and receives changes in ones and twos — "can we reword the
homepage headline", "the contact form should copy in Sam", "add a pricing FAQ".
Freelancers and small agencies, typically with no staging environment worth the
name and no formal release process.

It is not for building a new site (that is the Launch System), not for a
scheduled maintenance sweep (Operations), and not for deciding whether a change
is in scope or billable (the Agency System's module 14, which this picks up
*after*).

### The gap it fills

The existing products cover the business decision and the big projects. What
none of them covers is the small live change: the request arrives in an email,
somebody makes it, and nobody records what the page looked like before, what
exactly changed, or how anyone would know it worked. That is where the
embarrassing regressions come from — the reworded headline that broke the H1,
the form field that stopped copying anyone, the FAQ that shipped without its
schema.

This release is one loop, four steps, with a record at the end that the client
can read.

### Prerequisites

- Claude Code, logged in, with access to the site's repository or theme
- The URL of the live page the change affects
- An approved change request (who asked, what for, what "done" means)
- Python 3.8+ if you use the verification script (standard library only)
- **No credentials of the client's are needed by anything in this release**

### Inputs and outputs

| In | Out |
| --- | --- |
| The change request, in the client's words | `changes/CR-NN/request.md` — the request restated as an observable outcome |
| The live URL(s) affected | `changes/CR-NN/before.json` — evidence captured before anything is touched |
| The implementation | A branch, a diff, and the checks that ran |
| — | `changes/CR-NN/after.json` and a pass/fail comparison |
| — | `changes/CR-NN/handoff.md` — what changed, what was verified, what was not, how to reverse it |

---

## Step 1 — Restate the request as an observable outcome

A change request in a client's words is rarely testable. "Make the homepage
headline clearer" cannot pass or fail. Restate it, once, as the thing an
outsider could check:

> **Asked:** make the homepage headline clearer.
> **Observable outcome:** the `<h1>` on `/` reads "Physiotherapy in Harbourline —
> same-week appointments" instead of "Welcome", and remains the only `<h1>` on
> the page.

Send the restatement back before doing the work. It takes a line of email and
it is where most rework is avoided: the client either confirms it or says "no,
I meant the section below", and either answer is cheap at this point.

**Prompt:**

```text
Read this change request and restate it as an observable outcome.

Request: [PASTE THE CLIENT'S WORDS]
Page(s): [URL]

Rules:
- The outcome must be checkable by someone who was not in the conversation, by
  looking at the page or a response.
- Name the element, the text, the destination, or the behaviour — not the
  intention.
- If the request is ambiguous, list the two or three readings and ask which,
  rather than choosing.
- State what must NOT change on that page as a result. Be specific: headings,
  canonical, form behaviour, the primary call to action.
- Do not implement anything in this run.
```

## Step 2 — Capture the before state

Before touching a file. The point is not ceremony: it is that "it used to work"
is unprovable an hour later, and a client who sees a before/after table stops
asking whether anything else broke.

`capture.py` in this release fetches a URL and records, from the response as
served: status and final URL after redirects, `<title>`, every `<h1>`,
canonical, robots directive, the count of `<form>` elements and their actions,
the primary call-to-action text and href if you name a selector, and a hash of
the main content. It writes JSON. It changes nothing and needs no credentials.

```bash
python3 capture.py https://example.com/ --label before --out changes/CR-07
```

**Prompt, for the parts a script cannot see:**

```text
Read-only. Before I make change CR-07, record the current state of [URL] as
evidence:
- What the page currently says where the change will be made (quote it)
- Which template or file renders that region, and its path
- What else that template renders (so I know the blast radius)
- Any test, check or workflow in this repository that touches it
Do not change anything. Output a short markdown block I can paste into
changes/CR-07/request.md.
```

## Step 3 — Implement, on a branch, with the blast radius named

```text
Implement CR-07 on a new branch.

Outcome required: [THE RESTATED OUTCOME]
Must not change: [THE LIST FROM STEP 1]

Rules:
- One change. If you find a second thing that looks wrong, write it down at the
  end; do not fix it in this run.
- Touch the fewest files that achieve the outcome; say why each one is needed.
- Run this project's checks and show the output. If there are none, say so
  rather than inventing a command.
- Finish with: the files changed, the checks run and their result, and what you
  did not verify.
```

The "one change" rule is the whole discipline. An agent that fixes three things
produces a diff nobody can review and a rollback nobody can scope.

## Step 4 — Verify against the before state, then hand off

```bash
python3 capture.py https://example.com/ --label after --out changes/CR-07
python3 compare.py changes/CR-07/before.json changes/CR-07/after.json
```

`compare.py` prints one row per checked property: what it was, what it is, and
whether that field was supposed to change. Fields you listed as "must not
change" appearing in the changed column is a failure, and it is the check that
catches the reworded headline that silently removed the only `<h1>`.

Then the handoff. `handoff-template.md` in this release is four short sections —
what was asked, what changed, what was verified (with the before/after table
pasted in), and how to reverse it. It is written to be sent to the client
as-is.

---

## Worked example

`example/` contains a complete run of CR-07 against a fixture: a small static
site with a homepage whose `<h1>` says "Welcome" and a contact form that posts
to `/api/contact`.

- `example/request.md` — the client's words, the restated outcome, and the
  must-not-change list
- `example/before.json` — captured from the fixture before the change
- `example/after-good.json` — after the intended change
- `example/after-bad.json` — after a plausible *wrong* implementation: the
  headline was replaced by editing the hero template, which changed the `<h1>`
  into a `<p>` and left the page with no `<h1>` at all
- `example/comparison-good.txt` and `example/comparison-bad.txt` — what
  `compare.py` prints for each
- `example/handoff.md` — the client-facing summary for the good run

The bad run is the point of the example. It looks correct in a browser: the new
headline is on the page, in the right place, at the right size. The comparison
catches it in one line.

## Verification steps for this release itself

1. `python3 capture.py --self-test` — parses a fixture document and asserts every
   extracted field, including the "no `<h1>`" case.
2. `python3 compare.py --self-test` — asserts that an expected change passes, an
   unexpected change fails, and a missing field is reported rather than ignored.
3. Both scripts were run against the fixture in `example/` and against one live
   URL (`https://sitebuilderstack.com/`) to confirm they work on a real
   response. Output in `example/`.

## Limitations

- **The scripts read what a fetch returns.** A page whose content is assembled
  in the browser after load will capture as whatever the server sent. For those,
  the comparison is a weaker check and the prompt-based steps do the work.
- **No authentication.** Nothing here logs in, and it should not: staging behind
  basic auth needs a different approach than putting a password in a script.
- **Not a test suite.** This proves the specific change and the specific
  must-not-change list. It does not tell you the rest of the site is fine.
- **Tested environment:** Python 3.12 on Linux, against the fixture in
  `example/` and one live HTTPS URL, on 24 September 2026. Not tested against
  authenticated pages, non-HTML responses, or sites requiring JavaScript to
  render their main content.
- Every host, client and request in the example is fictional except the one
  live URL named above, which is this site's own homepage.
