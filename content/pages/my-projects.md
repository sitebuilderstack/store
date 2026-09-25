## What this is

A place to keep the things this site helps you make for one website — a generated checklist, an audit prompt, a migration plan, a test plan — next to the guides you have read, the labs you have run, and a short task list. The page always offers one next action, chosen from your unfinished work, so coming back after a week does not start with “where was I”.

## Where it lives

In this browser, under a single storage key, and nowhere else. There is no account, no email address and no identifier. The site's analytics receive only that *a* project was created or resumed and which kind of thing was saved — never its name, URL, objective or contents.

That has costs, stated plainly:

- It does not follow you to another device or browser. The JSON export is the only way to move it.
- Clearing site data clears it. Export before you do.
- It is **not encrypted**. Anyone who can open this browser profile can read it. Do not put passwords, API tokens or client secrets into a project — not in the objective, not in a task, not in a saved result.
- Private windows and browsers that block site data keep nothing after the tab closes. The page says so when that is the case, and everything still works for the visit.
- There is a limit: up to 25 projects and around 2 MB in total, because that is what browsers reliably allow. The page refuses a save that would go past it rather than silently losing something.

## What the states mean

- **Not started / in progress / read** — where you are with a guide, lab or challenge, as you recorded it.
- **Generated** — a result written from your answers by one of the generators. It is a starting point, not a finding.
- **Self-reported** — you told a page that something is true about your site. Nothing checked it.
- **Verified against example** — you matched a lab's known-answer fixture. That verifies you against the example, not your site against anything.

The distinction is kept on purpose. A workspace that let “I generated a checklist” drift into “this site was checked” would be the opposite of useful.

## My Learning

Your progress page at [My Learning](/pages/my-learning) keeps working unchanged. The first time you open this page, the guides you had saved or completed there are copied into a default project called “My website”; the original record is left as it was.

## Importing safely

An import is checked before anything changes: it must be a JSON export from this page, under 4 MB, with a version this page understands and at least one usable project. Unknown fields are dropped, text is stored as text, and nothing in a file is ever run. You choose *merge* or *replace* and confirm before either happens.
