---
title: "A production CLAUDE.md: the ten sections, the one test for what belongs, and why length is the main failure"
subtitle: "The file Claude Code loads at the start of every session — and how to keep it short enough to be obeyed"
canonical: https://sitebuilderstack.com/blogs/guides/production-claude-md-web-development
tags: claude, ai-tools, developer-tools, web-development, productivity
---

`CLAUDE.md` is a Markdown file that Claude Code loads automatically at the start of every session in your project. Its contents become part of the context for every request, without you pasting anything. That is the whole mechanism — and almost every question people have about the file (why a rule was ignored, why two files disagree, why it seemed to vanish) is answered by how it loads.

This is a condensed version of the [full guide on Site Builder Stack](https://sitebuilderstack.com/blogs/guides/production-claude-md-web-development), which has the complete 95-line template and a real one from a live Shopify theme.

## Why it matters at all

An agent working in your repository makes dozens of small decisions you never stated: which HTTP client, whether errors throw or return, how files are named, whether a new dependency is acceptable, what "done" means. It will make each one reasonably. Reasonable is not the same as consistent with your project, and inconsistency compounds — a session that picks differently from the last one leaves a codebase with two of everything.

## How it reaches Claude, and why length is the main failure

It is loaded at the start of every session, whole, into the context window — not fetched when relevant, not summarised. Every line is paid for on every turn for the rest of the session. It arrives as a user message after the system prompt, which is the single most clarifying fact about it: it is strong guidance, not a hard constraint, and it competes for attention with everything else in context.

That is why the common failure is not an incomplete file but a bloated one. Claude Code's own documentation suggests staying under roughly 200 lines, and the reason is how instructions behave in a long context: as the file grows, individual rules get *less* attention. A 600-line file where forty lines matter is worse at communicating those forty than a 90-line file containing only them. You have diluted your own signal.

## The one test for what belongs

**Could this be worked out by reading the codebase?**

If yes, leave it out. Directory structures, what each module does, the dependency list, how a function works — the code is the source of truth, and a second copy in Markdown drifts, and drifted instructions are worse than absent ones.

If no, it belongs: conventions no tool enforces, prohibitions, non-obvious constraints, decisions with history behind them, commands that are not discoverable, and the mistakes people reliably make.

## The ten sections

1. **Project** — two or three sentences on what this is and who it is for. The mobile share and the stated priority order change decisions later; anything that does not change a decision is filler.
2. **Stack** — a list, version families only. No explanation of what Astro is.
3. **Commands** — run, build, test, check, deploy. The section that pays for itself immediately; without it every session spends a turn reading `package.json`. Put the prohibition beside the command it applies to.
4. **Conventions** — only the ones no formatter enforces.
5. **Architecture rules** — the structural decisions that must hold.
6. **Do not** — the explicit prohibitions.
7. **Quality bar** — what "done" means here.
8. **Before finishing** — the checklist for every task.
9. **Gotchas** — the non-obvious things that catch people.
10. **Ask first** — where the agent should stop and check.

Sections six, eight and ten do most of the behavioural work. Skip any section with nothing real to say rather than filling it with generalities.

## Writing a rule that gets followed

The difference is specificity.

| Weak | Strong |
|---|---|
| Write clean code | Functions under 40 lines; extract rather than nest past three levels |
| Be careful with the database | Migrations are additive-only. Never drop a column in the same release that stops using it. |
| Follow accessibility best practices | Every control has a visible associated label. A placeholder is not a label. |
| Test your changes | Run `npm run check` and show me the output before reporting complete |
| Don't add unnecessary dependencies | Ask before adding any dependency. Say what it costs and why the platform cannot do it. |

The right-hand column is specific, checkable, placed where it applies, and phrased as the action rather than the value.

## A real one, from a live Shopify theme

A generic template is one thing; a mature `CLAUDE.md` is mostly a record of specific mistakes. The file behind sitebuilderstack.com contains rules that look strange out of context and each exist because something went wrong: Shopify rejects `templates/policy.json` with an error and then *silently ignores* `templates/policy.liquid`, so policy pages are styled by branching in the layout; the `agents.md` template renders in a restricted Liquid context where `shop` is empty with no error; a section's `max_blocks` must be raised and pushed before a section group that exceeds it. None of that is inferable from the repository, and the first one cost an hour.

## Starting from /init

`/init` analyses the codebase and generates a starting file — a reasonable inventory of stack, structure and scripts. What it cannot produce is the prescriptive half: it does not know which patterns are deliberate and which are accidents, and it has no way to know what people get wrong. Treat the output as a first draft with an editing job: delete the descriptions (usually half the file, and the half with no value), verify the commands, then add the prohibitions and gotchas yourself.

## When the file is too long: rules, not imports

Imports (`@path`) split a long file across several files but do not make it shorter in context — every imported file is expanded at launch. If the problem is size, `.claude/rules/` is the tool: a rule file with `paths` frontmatter only enters context when Claude works with a matching file. Rules that apply everywhere stay in `CLAUDE.md`; rules for one area become path-scoped. Personal preferences — commit style, tone — go in `~/.claude/CLAUDE.md`, not the project file.

## Instructions, settings, hooks

Three mechanisms, differing in whether compliance is guaranteed. `CLAUDE.md` is followed but not guaranteed. `.claude/settings.json` permission rules are enforced by the tool. Hooks are enforced by your own code. If the consequence of a rule being missed is serious — "never commit directly to main" — put it where it cannot be missed.

## Testing whether it works

A `CLAUDE.md` nobody has tested is a hypothesis. In a fresh session, ask what it thinks the rules are; anything vague where the file is specific is not currently working. Give it a small task in an area with a prohibition and see whether the prohibition holds unprompted. Ask for any change and watch the end: did it run the checks and show the output?

## Keeping it true

The failure mode for a good file is drift, not neglect. Update it when it fails — the moment you correct the same thing twice, that correction belongs in the file; this is the primary source of good rules. Review it when the project changes shape; deleting is most of the work. Audit it quarterly.

The [full guide](https://sitebuilderstack.com/blogs/guides/production-claude-md-web-development) has the complete template and the free [CLAUDE.md starter](https://sitebuilderstack.com/pages/resources). The [Website Launch System](https://sitebuilderstack.com/products/claude-code-website-launch-system) ships a production `CLAUDE.md` per platform alongside the build systems it governs.

---

*Adapted from [Creating a production CLAUDE.md for web development](https://sitebuilderstack.com/blogs/guides/production-claude-md-web-development) on Site Builder Stack. Independent; not affiliated with Anthropic.*
