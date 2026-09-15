Twenty-four questions across seven categories, producing a score out of 100 with a
per-category breakdown and a prioritised list of what to fix first.

It runs entirely in your browser and nothing is transmitted.

## Read this before you read your score

**This is a self-assessment, not a technical audit.** It reports what you told
it. If you answer "Yes" to a question you have not actually checked, the score
goes up and your site does not improve. That is not a flaw in the tool; it is
what a questionnaire is.

The useful way to use it is backwards: answer honestly, then treat every "Yes"
as a claim to verify against the live site. Most people discover that two or
three of their confident yeses were assumptions.

"Not sure" scores the same as "No" on purpose. An unverified control is not a
control.

## The seven categories

- **SEO** — titles, canonicals, robots and sitemap, and whether you have made a decision about what should be indexed rather than accepting a default.
- **Performance** — Core Web Vitals at the 75th percentile, layout stability, third-party scripts, fonts.
- **Accessibility** — keyboard operation, measured contrast, useful alt text, real form labels.
- **Security** — credentials, dependencies, server-side validation, error responses that do not leak.
- **Analytics and legal** — whether analytics actually records a visit, and whether the required notices exist and are reachable.
- **Conversion** — whether you know your conversion rate and where the number comes from, whether the main call to action says what happens next, and whether anyone outside your team has been watched trying to complete the main task.
- **Deployment and operations** — a pipeline with checks that can fail, and a rollback you have performed at least once on purpose.

That last question is the one most sites fail. The first time you roll back
should not be during an incident.

## After the score

The recommendations come back ordered: outright gaps first, partial ones after,
grouped so the list reads as a plan rather than a pile of anxieties.

Below them the score may point at one of the paid systems. That suggestion is
derived from the category percentages and nothing else — a strong score
recommends nothing at all, which is the behaviour you should check for first if
you suspect a tool like this of selling to you regardless of the answers.

For the full versions, the free [website launch
checklist](/pages/claude-code-launch-checklist) has 140 items you can tick off
and come back to, and the [website audit
guide](/blogs/guides/claude-code-website-audit) covers how to inspect a site
you did not build.
