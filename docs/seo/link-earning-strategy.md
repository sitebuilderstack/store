# Link-earning strategy

Site Builder Stack's content quality is not the constraint. Domain authority is. The
site is new, has no editorial backlinks, and competes for queries where the incumbents
are Anthropic's own documentation and established developer publications.

This document is the plan for changing that **ethically**: earning links by having
things worth linking to, and telling the right people they exist. It is a working
document, not a report — nothing here has been executed.

## Ground rules

These are not aspirational. Breaking any of them risks a manual action and would
undo more than it gains.

- **No paid links.** No sponsored placements described as editorial, no link
  exchanges, no PBNs, no "guest post for $X" networks.
- **No automated outreach.** Every message is written for a specific recipient by a
  human who has read what they publish.
- **No mass submission.** Directory spam is worthless and leaves a footprint.
- **No fake identities.** No sockpuppet accounts, no pretending to be a customer.
- **Disclose the affiliation.** Every time. "I built this" belongs in the first line.
- **Lead with the free resource, never the product.** The ask is always about
  something a reader can use without paying.
- **Take no for an answer.** One follow-up at most, then stop.

Community rules come first. Several of the communities below prohibit self-promotion
outright; where that is the case it is noted, and the entry is about participating
usefully rather than posting a link.

## What we actually have to offer

Outreach fails when there is nothing behind it. Current linkable assets:

| Asset | URL | Why someone would link to it |
| --- | --- | --- |
| Free resources hub | `/pages/resources` | One page collecting five ungated production documents |
| Production CLAUDE.md starter | `/pages/production-claude-md-starter` | A real file to copy, not an article about one |
| Website launch checklist | `/pages/claude-code-launch-checklist` | 18 sections; bookmarkable reference |
| SEO checklist | `/pages/claude-code-seo-checklist` | Scoped to verifiable checks, which is unusual |
| Security checklist | `/pages/claude-code-security-checklist` | Includes the AI-assisted-development section most lists omit |
| Website audit checklist | `/pages/claude-code-website-audit-checklist` | Severity scale and write-up format included |
| CLAUDE.md starter kit (zip) | `/#get-templates` | Four complete files by project type |
| 19 long-form guides | `/blogs/guides` | Primary-source-based, no invented statistics |
| GitHub starter kit | **not yet published** | See `docs/seo/GITHUB-STARTER-KIT.md` |

The GitHub repository is the single highest-leverage item on this list and it does not
exist yet. Publishing it should come before any outreach, because half the tactics
below are easier with a repository to point at.

## Priority order

Ranked by expected links per hour of effort, highest first.

### 1. Publish the GitHub starter kit — **do this first**

GitHub repositories accumulate links in ways a storefront cannot: awesome-lists, README
references, blog posts, "tools I use" pages. The repository is prepared; publishing it
takes minutes.

Once live: submit to the relevant awesome-lists (see below), add the topics, and link
it from the resources hub.

### 2. Curated lists and resource directories

The highest-yield category, because the whole point of these lists is to collect
exactly this kind of resource. Each requires reading the contribution guidelines and
following them exactly.

**Targets:**
- `awesome-claude-code` and similar Claude Code collections on GitHub
- `awesome-ai-coding` / AI developer-tooling lists
- `awesome-seo`, `awesome-web-development` — for the checklists specifically
- Anthropic's community showcase channels, where one exists
- Claude Code plugin and skill directories

**Angle:** a pull request adding one line, in the list's existing format, pointing at
the GitHub repository rather than the storefront. Lists reject commercial links far
more often than they reject repositories.

**Effort:** low. **Expected yield:** moderate but durable — these pages themselves
attract links.

### 3. Developer newsletters

Newsletters link out generously and their archives are indexed permanently.

**Targets:** general web-development weeklies, AI-and-developer-tooling newsletters,
Shopify-developer newsletters, and newsletters covering DevOps and platform
engineering (a natural fit given the author's background).

**Angle:** email the editor with one sentence on what the resource is, one sentence on
who it helps, and the link. No pitch deck, no press release. Editors decide in seconds.

**Effort:** low per newsletter. **Expected yield:** a burst of referral traffic and a
permanent archive link.

### 4. Answering real questions, in public

Slower, but the links are the most credible kind and it compounds.

**Targets:** Stack Overflow, Reddit (r/ClaudeAI, r/webdev, r/shopify, r/devops),
Discord and Slack communities for Claude Code and adjacent tools, GitHub Discussions
on relevant repositories.

**Rules:** answer the question completely in the reply itself. The link is supporting
evidence, not the answer. Several of these communities ban self-promotion — read the
rules per community, and where linking is not allowed, answer anyway without a link.
Reputation there is what makes a later link acceptable.

**Effort:** high and ongoing. **Expected yield:** mostly nofollow, but real traffic
from people with the exact problem, and the visibility that leads to editorial links.

### 5. Platform and framework communities

The guides already cover Shopify explicitly and generalise to static sites and web
applications. Communities worth being present in:

- **Shopify:** the Shopify Community developer forums, Shopify Partners channels
- **Astro / static sites:** the Astro Discord, static-site-generator communities
- **WordPress:** developer-focused groups, where AI-assisted workflow content is welcome
- **DevOps / platform:** communities where the author has genuine standing

**Angle:** the platform-specific guides, not the homepage. A Shopify developer wants
the Shopify article, not a product page.

### 6. Technical bloggers and podcasts

**Targets:** people already writing or talking about Claude Code workflows, AI-assisted
development, or developer productivity.

**Angle:** not "please link to us". Either (a) offer the checklists as a resource for
something they are already writing, or (b) offer a specific, concrete story — the five
production failures documented on the About page are genuinely unusual material, and
"every automated check reported a healthy checkout while checkout was broken" is a real
hook that stands on its own.

**Effort:** high per contact. **Expected yield:** low volume, high quality. These are
the links that move authority most.

### 7. Original research or data

Nothing here yet, and the most defensible long-term play. Options that are honest and
achievable:

- A measured comparison of `CLAUDE.md` length against rule adherence, run over real
  sessions with the method published.
- A survey of what actually breaks on AI-assisted website builds, if enough responses
  can be gathered honestly.
- A public, reproducible audit of a sample of sites against the SEO checklist, with
  the script published.

**Rule:** publish the method and the raw data. Research whose numbers cannot be checked
is worth less than no research, and inventing figures is out of the question.

## Outreach templates

Use as a starting point. Rewrite for each recipient; a template sent verbatim reads
like one.

### To a newsletter editor

> Subject: Free Claude Code website launch checklist — for [newsletter]
>
> Hi [name],
>
> I built a set of free, ungated checklists for developers shipping websites with
> Claude Code — launch, SEO, security, and auditing an existing site. No email
> required, plain Markdown, MIT-licensed on GitHub.
>
> [link]
>
> The SEO one might be the most useful to your readers: it is deliberately limited to
> checks a machine can verify, which rules out most of what usually pads these lists.
>
> I'm the author and I sell a paid version, so treat this as self-interested — but the
> free ones are complete and I'd rather they got used.
>
> [name]

### To a curated list (pull request description)

> Adds the Claude Code Website Starter Kit: a `CLAUDE.md` starter and four production
> checklists (launch, SEO, security, website audit), MIT-licensed.
>
> Disclosure: I maintain it. Happy to adjust the wording or drop it if it is not a fit
> for this list.

### To a blogger or podcaster

> Hi [name],
>
> Your piece on [specific thing] matched something I ran into building a store with
> Claude Code: the checkout was broken for a period and every automated check I had
> reported it healthy, because the "can't accept payments" notice is injected by
> JavaScript and absent from the initial HTML.
>
> I wrote up that and four other failures from the same build here: [link]. Free, no
> sign-up. If any of it is useful for something you are working on, take it.
>
> Full disclosure: I sell a paid product on the same site.
>
> [name]

## Measuring it

Track these monthly. Do not report an outreach document as a result.

| Metric | Where | What good looks like |
| --- | --- | --- |
| Referring domains | Search Console → Links | Any growth from zero |
| Top linking pages | Search Console → Links | Editorial, not directory |
| Referral sessions | Shopify analytics | Sessions that are not bots |
| GitHub stars / forks | Repository | A proxy for whether it is useful |
| Resource page entrances | Shopify analytics | Are the free pages the entry point? |
| Rankings for the four commercial clusters | Search Console → Performance | Impressions before positions |

Expect impressions to move before positions, and positions before traffic. Anything
that moves faster than that is worth investigating rather than celebrating.

## What is explicitly out of scope

- Buying links, link exchanges, or "we'll link if you link"
- Comment links, forum signature links, profile-spam links
- Automated or templated mass email
- Fabricated reviews, testimonials, or endorsements
- Creating pages purely to be link targets
- Any use of the Site Builder Stack email list for outreach it did not opt into

## Status

**Nothing in this document has been executed.** No outreach has been sent, no
repository published, no list submitted to. It exists so that the work is easy to pick
up, not to be reported as done.
