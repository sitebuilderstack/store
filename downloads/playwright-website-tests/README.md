# Playwright website tests — companion project

A small, runnable Playwright suite for a marketing site, written for the guide
[Playwright Testing With Claude Code: Forms, Links, and Regression Checks](https://sitebuilderstack.com/blogs/guides/claude-code-playwright-website-testing).

It ships with its own fixture site (`site/`, a fictional physiotherapy clinic)
and a dependency-free static server, so nothing here touches a real website.

## Run it

    npm install
    npx playwright install --with-deps chromium
    npx playwright test

Requires Node.js 22 or newer. `@playwright/test` is pinned to 1.63.0, the
current release when this was written; `npm outdated` will tell you if a newer
one exists.

## What the tests cover

- `tests/booking-form.spec.ts` — required-field error, malformed email rejected
  before any success message, a valid submission posts the right fields
  (endpoint **mocked** with `page.route`), a failed send is reported.
- `tests/cta-and-navigation.spec.ts` — the primary call to action lands on the
  booking form; every main-navigation link returns 200; on the mobile project,
  the menu opens and closes and reports `aria-expanded`.
- `tests/regression.spec.ts` — the success message waits for the server
  response (a bug that was fixed once and must stay fixed).

## What they do not cover

A mocked submission proves the page posts the right fields and handles the
response. It does not prove that anyone received an email. Delivery is checked
by a marked submission against the real form and a look at the inbox — the
guide explains why that stays manual and off the CI path.

## Show a test failing

Trust a test only after you have seen it fail. Open `site/app.js`, change the
email check so it accepts anything, run the suite, watch the email test fail
with the received text, then restore the file.

## Licence

Use freely in your own projects. No attribution required.
