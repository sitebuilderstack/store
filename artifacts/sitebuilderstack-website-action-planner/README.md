# SiteBuilderStack Website Action Planner

An interactive Claude Artifact. A visitor picks a website goal, answers five
more short questions, and gets a practical action plan, an original starter
Claude Code prompt they can keep, and one product recommendation that explains
itself — or an honest "buy nothing yet".

| | |
| --- | --- |
| **Artifact URL** | <https://claude.ai/artifact/8oUQrAFJyAZdKG86KeNZLX> |
| **Access state** | **Private to the owner.** Nobody else can open it until the owner shares it from the page's Share menu. |
| **Published** | version 4, 24 September 2026 |
| **Runtime capability** | `downloads` (the Markdown export) |
| **Catalogue snapshot** | verified 24 September 2026, 30-day freshness window |

## Files

```
artifacts/sitebuilderstack-website-action-planner/
  index.html              THE PUBLISHED FILE — generated. Do not edit by hand.
  build.py                assembles index.html from the sources below
  products.json           the verified catalogue snapshot (source of truth)
  recommendation-rules.js the decision engine — pure, DOM-free, testable
  refresh-catalogue.py    re-verifies products.json against the live storefront
  src/
    styles.css            the visual system (the storefront's own tokens)
    analytics.js          the event interface and the outbound link builder
    config.js             the artifact's own published URL
    app.js                the interface
  tests/
    run.sh                every check, in order
    test-rules.js         46 offline checks of the engine (the 12 named scenarios + more)
    test-browser.js       88 checks of the built page in Chromium
    test-links.js         31 live checks that every outbound URL returns 200
    preview.html          generated — the built page inside the runtime's document shell
  README.md  measurement.md  launch-copy.md
```

`index.html` is self-contained: the catalogue, the engine, the styles and the
app are all inlined, so the published page depends on nothing being served
beside it. It loads no font, no library and no image, and makes no network
request of any kind.

## Working on it

```bash
cd artifacts/sitebuilderstack-website-action-planner
python3 build.py                     # regenerate index.html + tests/preview.html
bash tests/run.sh                    # rules + browser (offline)
bash tests/run.sh --links            # also check the live storefront
```

Then republish to the **same URL** — from this conversation, republish the same
file path; from any other conversation, pass
`url: https://claude.ai/artifact/8oUQrAFJyAZdKG86KeNZLX`. Publishing without the
URL creates a *second* artifact rather than updating this one.

Editing `index.html` directly is always wrong: the next `build.py` overwrites it.

## Refreshing the products and the prices

`products.json` is a **build-time snapshot**. The artifact never calls Shopify.

```bash
python3 refresh-catalogue.py            # report differences only
python3 refresh-catalogue.py --write    # update price/currency/status/availability/title/dates
python3 build.py && bash tests/run.sh --links
# then republish index.html to the artifact URL above
```

**The freshness window is 30 days** (`snapshot.freshnessWindowDays`). Once the
snapshot is older than that, the engine stops printing prices and savings
entirely: every price becomes "See current price", and the bundle comparison
says the snapshot is out of date instead of claiming a number. That behaviour
is tested (`tests/test-rules.js`, "An expired snapshot…"), so letting the
snapshot go stale degrades honestly rather than lying.

What `refresh-catalogue.py` will **not** do is rewrite the descriptive fields —
`useCase`, `benefits`, `exclusions`, `prerequisites`, `inclusions`. Those were
read from each product's own published description by a person. If a product
description changes materially, edit those fields by hand against the live page.

## The decision engine

`recommendation-rules.js` exports pure functions and is loaded both by the page
and by Node. The important entry point is
`decide(answers, catalogue, {today}) -> result`.

Routing is goal-first: **the platform never picks the product.** Selecting
Shopify does not produce the Automation toolkit; only selecting Shopify
administration as the goal does, and only when a real repetitive task is named.

Qualification runs before any ranking. The gates, each of which prints its
reason on the result page:

| Gate | Effect |
| --- | --- |
| `convert_not_live` | A conversion goal on a site at idea/building stage routes to the Launch System. |
| `convert_no_traffic` | A conversion goal on a live site with no traffic routes to the SEO toolkit. |
| `seo_before_launch` | An SEO goal before launch routes to the Launch System. |
| `maintain_not_live` | A maintenance goal before launch routes to the Launch System. |
| `shopify_admin_wrong_platform` | Shopify administration on a non-Shopify platform recommends nothing. |
| `shopify_admin_no_task` | "I'm on Shopify but bulk admin isn't my problem" recommends nothing. |
| `shopify_admin_task_unknown` | "Not sure" keeps the toolkit but makes action 1 *name the task first*. |
| `agency_defers` | An agency goal plus a project goal puts the project product first, agency second. |
| `not_ready` | "Not comfortable with a terminal yet" produces a free getting-started path and de-emphasises the product. |
| ownership | An owned product is never re-sold; owning the bundle counts as owning its three members. |

Unknown conversion measurement never produces a diagnosis — it produces a
measurement check as the first action.

### Bundle arithmetic

The bundle is the **Launch System + SEO toolkit + Conversion toolkit only**
(verified 24 September 2026). It is offered *only* when
`bundleComparison()` returns `bundle_cheaper` for the products the visitor's
answers actually justify, minus anything they own:

| Unowned products needed | Individually | Bundle | What the page says |
| --- | --- | --- | --- |
| 3 | $59.97 | $39.99 | $19.98 less — offered |
| 2 | $39.98 | $39.99 | Buying the two is $0.01 cheaper; the bundle adds a third product you did not ask for — **not** offered |
| 1 | $19.99 | $39.99 | Buying the bundle for one product costs $20.00 more — not offered |

Because a visitor can name at most two goals, the answer-derived set is at most
two products, so the bundle is effectively never pushed by default. It is
reachable through the **on-demand comparison** on the result page, where the
visitor ticks what they expect to use and the arithmetic recomputes live. That
is the "explicitly selected near-term plan" case.

## Tests

| Suite | Count | Needs |
| --- | --- | --- |
| `tests/test-rules.js` | 46 | nothing (offline) |
| `tests/test-browser.js` | 88 | Chromium via `PUPPETEER_EXECUTABLE_PATH` |
| `tests/test-links.js` | 31 | network access to sitebuilderstack.com |

The twelve scenarios named in the brief are the first twelve checks in
`test-rules.js` and are labelled with their numbers.

## Deliberate omissions

- **No email capture.** The brief allowed linking to an existing, verified
  SiteBuilderStack opt-in experience. There is not one: the storefront has no
  newsletter form, and the free CLAUDE.md starter kit is an ungated direct
  download. So the planner has no email field, links to no signup, and promises
  no emailed plan. Adding a form that goes nowhere would have been worse than
  omitting it.
- **No persistence of answers.** Results live in memory only. A reload loses
  them, which the page states. Nothing about a visitor is written to shared
  artifact storage, and storage availability is never a prerequisite for using
  the tool — the only thing in `sessionStorage` is the local debug journal, and
  it degrades silently to memory when storage is blocked.
- **No embed of the planner on the storefront.** Whether an artifact renders
  inside a storefront iframe has not been tested and cannot be until the
  artifact is shared publicly. `launch-copy.md` says so rather than assuming.

## What could not be verified here

- **The `downloads` capability.** `claude.use('downloads')` only resolves inside
  the claude.ai artifact viewer. Locally, `window.claude` is absent, the export
  button is hidden, and the page says so — that branch is tested. The *save*
  branch can only be exercised by opening the published artifact and clicking
  Export; see the owner actions in `measurement.md`.
- **Public access.** The artifact is private. Only the owner can change that.
