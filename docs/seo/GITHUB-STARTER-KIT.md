# GitHub starter kit — published

## Status: **published**

**https://github.com/sitebuilderstack/sitebuilderstack_store** — public, 13 files, MIT.

Pushed 4 September 2026 over SSH as `sitebuilderstack`. The repository was empty; this
is its first commit.

### What was checked before pushing

The repository is public and the source tree tracks all 113 files of the paid product,
so the payload was verified rather than assumed:

| Check | Result |
| --- | --- |
| Files pushed | 13 — the kit only |
| Paid-product files included | none |
| Verbatim paragraphs shared with the bundle | 0, checked programmatically |
| Secrets, tokens, private keys | none |
| Absolute paths, `myshopify` domains | none |

The push used an isolated working copy rather than a subtree of the main repository, so
there is no path by which the product could have been included.

## Contents

```
claude-code-website-starter-kit/
├── README.md                     what it is, who it is for, how to use it, example workflow
├── CLAUDE.md                     the starter project-context file
├── LAUNCH-CHECKLIST.md           18 sections, requirements → post-launch validation
├── SEO-CHECKLIST.md              16 sections, crawlability → ongoing validation
├── SECURITY-CHECKLIST.md         15 sections, secrets → final adversarial pass
├── WEBSITE-AUDIT-CHECKLIST.md    15 sections, inspection + severity scale
├── skills/                       five installable Claude Code skills
│   ├── seo-audit/SKILL.md
│   ├── a11y-audit/SKILL.md
│   ├── security-review/SKILL.md
│   ├── launch-check/SKILL.md
│   └── claude-md-review/SKILL.md
└── LICENSE                       MIT
```

The skills are validated by `scripts/validate-skills.py`, which is in the test suite.
A skill with a typo'd frontmatter field or the wrong filename is silently ignored by
Claude Code, so it is checked mechanically rather than by eye.

**Why skills are in here at all.** Bing's keyword API reports **1,970 impressions for
"claude code skills"** and 1,643 for "claude skills" over a month, against 90 for
"claude.md file". Skills is the highest-demand topic this project touches by a wide
margin, and the site's one guide on it sits at position 74 with no realistic path to
page one on a domain with no external links. A repository can rank where the storefront
cannot, and skills is the term worth pointing it at.

Site-relative links from the storefront copies were rewritten to absolute
`https://sitebuilderstack.com/...` URLs during assembly, so every link works on GitHub.

## Still to do, in the GitHub UI

Neither can be done from here: there is no `gh` CLI and no API token on this machine,
only an SSH key, which git can use but the REST API cannot.

**Description** — paste into the repository's About panel:

```
A CLAUDE.md starter, four production checklists, and five Claude Code skills for building, launching and auditing websites.
```

**Topics** — the first three are the terms with real search demand behind them:

```
claude-code-skills  claude-skills  agent-skills  claude-code  claude  anthropic
ai-assisted-development  web-development  seo-checklist  security-checklist
website-audit  launch-checklist  claude-md
```

**Website** — `https://sitebuilderstack.com`

## Done on the site side

- `Organization.sameAs` on the homepage now carries `https://github.com/sitebuilderstack`,
  set through the **Site Builder Stack — SEO** theme setting rather than hard-coded.
  `author_sameas` stays empty: the account is the project's, not a personal handle.
- Linked from the skills guide, the free resources hub, and `agents.md` / `llms.txt`.
- Sitemap resubmitted and the three changed URLs pushed to Bing and IndexNow.

## Keeping it in sync

The checklists are generated from `resources/*.md`, which are the single source of
truth. When one changes, re-run the assembly step rather than editing the GitHub copy
by hand, or the two will drift:

```bash
scripts/build-github-kit.sh
```
