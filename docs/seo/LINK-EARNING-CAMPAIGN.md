# Link-earning campaign

The operational version of [`link-earning-strategy.md`](link-earning-strategy.md): who to
approach, with which asset, and what to say. The strategy document explains why; this one
is the work.

**Nothing here has been executed.** No outreach has been sent. The tracker at
[`link-prospects.csv`](link-prospects.csv) is empty of contacts by design — see
"Researching prospects" below.

## Current position

| | |
| --- | --- |
| Referring domains | **0** |
| Assets that can be linked to | 5 ungated resources, 19 guides, 1 case study |
| GitHub repository | Built, **not published** — see [`GITHUB-STARTER-KIT.md`](GITHUB-STARTER-KIT.md) |
| Target | 20–30 relevant referring domains over 6–12 months |

The target is a direction, not a quota. Ten links from places developers actually read
beats a hundred from directories nobody visits, and chasing the number is how link building
turns into spam.

## The blocker is cleared

The repository is live at **https://github.com/sitebuilderstack/sitebuilderstack_store**. Awesome-lists
take repositories, not storefronts, so the categories below that were waiting on it are
now open.

One thing worth aiming at deliberately: the kit ships five Claude Code **skills**, and
"claude code skills" is the highest-demand term this project touches — 1,970 Bing
impressions in a month against 90 for "claude.md file". Lists that collect Claude Code
skills specifically are the highest-value targets on the list below.

## The assets, and what each one is for

| Asset | URL | Best-fit audiences |
| --- | --- | --- |
| Free resources hub | `/pages/resources` | General developer lists, newsletters |
| Production CLAUDE.md starter | `/pages/production-claude-md-starter` | Claude Code lists, AI-coding newsletters |
| Launch checklist | `/pages/claude-code-launch-checklist` | Web-dev newsletters, agency blogs |
| SEO checklist | `/pages/claude-code-seo-checklist` | SEO communities, technical SEO writers |
| Security checklist | `/pages/claude-code-security-checklist` | DevOps and security lists |
| Website audit checklist | `/pages/claude-code-website-audit-checklist` | Freelance and agency audiences |
| Case study | `/pages/case-study` | Bloggers, podcasts, Hacker News, DEV |
| Starter kit repo | *not yet published* | Awesome-lists, GitHub topic browsing |

## Categories, ranked by expected return per hour

### 1. Curated GitHub lists — highest return, blocked on the repo

`awesome-claude-code` and similar collections, AI-coding-tool lists, `awesome-seo` for the
checklists specifically. These exist to collect exactly this kind of resource and their own
pages attract links, so a place on one compounds.

**Format:** a pull request adding one line in the list's existing format, pointing at the
**repository**, not the storefront. Read `CONTRIBUTING.md` first and follow it exactly.
Disclose that you maintain it.

### 2. Developer newsletters — high return, available now

Web-development weeklies, AI-and-developer-tooling newsletters, Shopify developer
newsletters, DevOps and platform-engineering newsletters.

**Format:** email the editor. One sentence on what it is, one on who it helps, the link.
Editors decide in seconds and a pitch longer than a paragraph gets skipped. Archives are
indexed permanently, so a single mention keeps returning.

### 3. Answering questions in public — slow, compounding

Stack Overflow, r/ClaudeAI, r/webdev, r/shopify, r/devops, Claude Code Discord and Slack
communities, GitHub Discussions.

**Rules that are not optional:** answer the question completely *in the reply*. The link is
supporting evidence, never the answer. Several of these communities ban self-promotion
outright — read each one's rules, and where linking is not allowed, answer anyway. The
standing you build is what makes a later link acceptable rather than reportable.

### 4. Platform and framework communities

Shopify Community developer forums and Partner channels; Astro Discord; WordPress developer
groups; DevOps communities where the author has genuine standing.

**Angle:** the platform-specific guide, not the homepage. A Shopify developer wants the
Shopify article.

### 5. Technical bloggers and podcasts — low volume, highest value

People already writing about Claude Code workflows, AI-assisted development, or developer
productivity.

**Angle:** not "please link to us". Offer the case study as material. The line that works
is a specific, checkable story: *every automated check reported a healthy checkout while
checkout was broken, because the failure notice is injected by JavaScript.* That stands on
its own and is the kind of detail a writer can build a paragraph around.

### 6. DEV, Hashnode, Hacker News

Cross-post genuinely useful material with a canonical tag pointing home. Hacker News works
only for something that stands alone — the case study is the candidate; a product page is
not, and posting one is how an account gets flagged.

### 7. Original research — the strongest long-term play, nothing yet

Options that are honest and achievable: a measured comparison of `CLAUDE.md` length against
rule adherence over real sessions; a reproducible audit of a sample of sites against the SEO
checklist with the script published. **Publish the method and the raw data.** Research whose
numbers cannot be checked is worth less than none.

## Outreach angles per asset

Lead with the resource. Never with the product.

**CLAUDE.md starter** — "A free, production-oriented `CLAUDE.md` starter for web projects.
Plain Markdown, MIT-licensed, no signup."

**SEO checklist** — "A free technical SEO checklist scoped deliberately to checks a machine
can verify — crawlability, canonicals, schema, Search Console, post-launch validation. It
leaves out everything that needs data an LLM does not have."

**Launch checklist** — "Eighteen sections between 'it looks finished' and 'it is live and
behaving'."

**Security checklist** — "Includes a section most lists omit: what changes when a coding
assistant can read your repository."

**Case study** — "Five production failures on a real store, each of which every automated
check reported as healthy, with the mechanism behind each one."

## Templates

Rewrite for each recipient. A template sent verbatim reads like one.

### Newsletter editor

> Subject: Free Claude Code checklists — for [newsletter]
>
> Hi [name],
>
> I built a set of free, ungated checklists for developers shipping websites with Claude
> Code — launch, SEO, security, and auditing an existing site. No email required, plain
> Markdown.
>
> [link]
>
> The SEO one may suit your readers best: it is limited to checks that can actually be
> verified, which rules out most of what usually pads these lists.
>
> I'm the author and I sell a paid version, so treat this as self-interested — the free
> ones are complete as they stand.
>
> [name]

### Curated list pull request

> Adds the Claude Code Website Starter Kit: a `CLAUDE.md` starter and four production
> checklists (launch, SEO, security, website audit), MIT-licensed.
>
> Disclosure: I maintain it. Happy to adjust the wording or drop it if it is not a fit.

### Blogger or podcaster

> Hi [name],
>
> Your piece on [specific thing] matched something from building a store with Claude Code:
> checkout was broken for a period and every automated check I had reported it healthy,
> because the "can't accept payments" notice is injected by JavaScript and absent from the
> initial HTML.
>
> That and four other failures from the same build: [case study link]. Free, no signup.
> Take any of it if it is useful.
>
> Full disclosure: I sell a paid product on the same site.
>
> [name]

## Researching prospects

`link-prospects.csv` ships with the categories and no contacts. That is deliberate:
**inventing an email address is worse than an empty row.** Fill it in by hand, from the
actual newsletter or repository, recording where the address came from.

The `source` column exists for that. A row without one has not been researched.

## Rules

- No paid links, link exchanges, or PBNs
- No automated or templated mass email
- No sockpuppet accounts
- Disclose the affiliation every time, in the first line
- One follow-up at most, then stop
- Community rules come first; where self-promotion is banned, participate without linking

## Measuring it

Monthly, from Search Console → Links. **An outreach document is not a result** — the only
number that counts is referring domains, and it is currently zero.

| Metric | Where | Now |
| --- | --- | --- |
| Referring domains | Search Console → Links | 0 |
| Top linking pages | Search Console → Links | none |
| Referral sessions | Shopify Analytics | none |
| GitHub stars | Repository | 0 |
