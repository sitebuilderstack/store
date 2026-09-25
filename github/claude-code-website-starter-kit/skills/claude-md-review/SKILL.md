---
name: claude-md-review
description: Review a CLAUDE.md against what actually makes instructions get followed - length, specificity, and whether each rule belongs in a prompt file at all rather than a hook, a skill or a path-scoped rule.
when_to_use: Use when asked to review, improve, shorten or audit a CLAUDE.md, or when Claude keeps ignoring project instructions.
allowed-tools: Read Grep Glob
---

# CLAUDE.md review

Review the project's `CLAUDE.md` (and any `.claude/rules/`, nested `CLAUDE.md` files
and `CLAUDE.local.md`).

## What you are checking against

`CLAUDE.md` is loaded into the context window at the start of every session and
delivered as a **user message after the system prompt** — not as part of it. It is
strongly-placed context, not enforced configuration. Two consequences drive this whole
review:

- **Every line is paid for on every turn.** Length is the main failure mode. Target
  under 200 lines.
- **A rule can be ignored.** If something must happen regardless, it is a hook, not a
  line in this file.

## Report, in this order

**1. Length.** Line count, and whether it is over 200. If it is, do not just say
"shorten it" — identify which content should move where:

| Content | Belongs in |
| --- | --- |
| Applies to one area of the codebase | a path-scoped rule in `.claude/rules/` with `paths:` frontmatter |
| A procedure run occasionally | a skill — costs nothing until invoked |
| Mechanical and unconditional | a hook — runs whether or not anyone read the file |
| Derivable by reading the repo | delete it |
| Restates the linter config | delete it |

Note that **imports do not help here**: an imported file is expanded and loaded at
launch just the same.

**2. Rules that cannot be checked.** For each rule, ask whether someone reading a diff
could tell it was followed. Rewrite the weak ones:

| Weak | Strong |
| --- | --- |
| Write good tests | A change to behaviour needs a test that fails without it |
| Be careful with secrets | Secrets live in the environment; never read, printed, logged or committed |
| Follow our style | Match the surrounding file's conventions over any general preference |
| Don't break things | A deploy is not finished until the smoke check passes |

**3. Contradictions.** Across the main file, nested files and `.claude/rules/`. Where
two rules conflict, Claude may pick one arbitrarily. List every pair.

**4. Missing essentials.** The commands that are non-obvious or easy to get wrong; what
must not import what; the definition of done; and the things that have already gone
wrong once.

**5. Scope.** Is anything here that belongs in `~/.claude/CLAUDE.md` (personal, every
project) or `CLAUDE.local.md` (personal, this project, gitignored)?

## Output

For each finding: the line, what is wrong, and the specific replacement — not general
advice. End with a proposed line count after your changes.

## Then say how to test it

The file is only worth what it changes. Three checks, increasing in strength:

1. **Ask** — "what does CLAUDE.md tell you about testing here?" A vague answer means a
   vague section.
2. **Bait** — ask for something the file forbids. It should refuse and cite the reason.
3. **Observe** — note which rules get broken over a week. A rule broken repeatedly is
   either badly written or belongs in a hook.

Run `/context` and check **Memory files** to confirm which files actually loaded. If a
file is not listed there, Claude cannot see it and no rewrite will help.

See `CLAUDE.md` in this repository for a starter, and
https://sitebuilderstack.com/blogs/guides/production-claude-md-web-development for the
full reasoning.
