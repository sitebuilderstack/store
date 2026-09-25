# Sources for the three engagement-cycle articles (September 2026)

Fetched and read on 2026-09-17 unless stated. Quotes are verbatim from the
page on that date. Nothing in the articles that depends on a version number,
a documented limit, or a platform behaviour is asserted without a line here.

## Playwright (article: claude-code-playwright-website-testing)

- https://playwright.dev/docs/intro — install: `npm init playwright@latest`;
  Node.js "latest 22.x, 24.x or 26.x"; tests run with `npx playwright test`;
  default test directory `tests` (or `e2e` if `tests` exists); generated
  files `playwright.config.ts`, `package.json`, `tests/example.spec.ts`.
- https://playwright.dev/docs/best-practices — "Prefer user-facing attributes
  to XPath or CSS selectors"; "Don't use manual assertions that are not
  awaiting the expect"; "Each test should be completely isolated from another
  test"; network mocking via `page.route(...)` with `route.fulfill`.
- https://playwright.dev/docs/ci-intro — GitHub Actions example (checkout@v6,
  setup-node@v6 with lts/*, `npm ci`, `npx playwright install --with-deps`,
  `npx playwright test`, upload `playwright-report/`).
- npm registry, 2026-09-17: `@playwright/test` latest **1.63.0**
  (next pre-release 1.64.0-alpha-2026-09-17). Chromium headless shell
  153.0.8010.12 downloaded by `npx playwright install chromium`.
- Local verification: downloads/playwright-website-tests run on Node 22 —
  15 passed, 1 skipped (mobile-only test on the desktop project); with the
  email check deliberately disabled in site/app.js, the email test failed with
  `Received: "Thanks! We will email you to confirm."`; restored, 15 passed.
  Outputs saved in the article; nothing in it is typed from memory.
- Observation from that run, used in the article: `getByRole('navigation')`
  excludes a landmark hidden by `display:none` at phone width; the fix is
  `includeHidden: true` on both the landmark and the links.

## Google Search (articles: migration, maintenance)

- https://developers.google.com/search/docs/crawling-indexing/site-move-with-url-changes
  — five phases; "Use server side permanent redirects if technically
  possible… such as 301 and 308"; "Keep the redirects for as long as
  possible, generally at least 1 year"; chains "ideally no more than 3 and
  fewer than 5"; "Don't redirect many old URLs to one irrelevant single URL
  destination, such as the home page of the new site. This can confuse users
  and might be treated as a soft 404 error"; Change of Address only for
  domain/subdomain moves; "Don't forget to remove any noindex or robots.txt
  blocks that were only needed for the migration"; submit the new sitemap.
- https://developers.google.com/search/docs/crawling-indexing/site-move-no-url-changes
  — "Consider lowering the TTL to a conservative low value (for example, a
  few hours) at least a week in advance"; remove temporary crawl blocks;
  monitor server logs, DNS propagation, Search Console; crawl rate may
  fluctuate after a hosting change; keep verification working.
- https://support.google.com/webmasters/answer/9012289 (URL Inspection) —
  "This is not a live test. The results shown are from most recently indexed
  version of a page"; "There is a per-property daily limit of live
  inspections"; a live test "follows any redirects… does not indicate that it
  has followed a redirect, nor will it display the final URL that was tested".
- https://developers.google.com/search/docs/appearance/structured-data/article
  — recommended properties: author (name, url), dateModified,
  datePublished, headline, image; "Images must represent the marked up
  content".

## Claude Code (all three)

- https://code.claude.com/docs/en/common-workflows — plan mode:
  `claude --permission-mode plan` ("Claude reads files and proposes a plan
  but makes no edits until you approve"); subagents for research; piping
  (`claude -p`) for CI; worktrees for parallel sessions.

## Certificates and hosting (maintenance)

- https://letsencrypt.org/docs/faq/ — "Our default certificates are valid for
  90 days"; "Subscribers can opt in to short-lived certificates which are
  valid for six days"; "We recommend renewing 90 day certificates every 60
  days and six day certificates every three days."

## Shopify (scheduling the Weekly Fix series; platform notes)

- https://shopify.dev/docs/api/admin-graphql/latest/input-objects/ArticleCreateInput
  — `isPublished`: "Whether or not the article should be visible";
  `publishDate`: "The date and time (ISO 8601 format) when the article
  should become visible." Used to schedule challenges #2–#4.

## What was not consulted

- Search Console and analytics for sitebuilderstack.com — not authorised for
  this cycle; no traffic, ranking or conversion figures appear in the
  articles.
- No third-party benchmarks or surveys. Every number in the articles comes
  from a run recorded above or is a documented limit with a source here.
