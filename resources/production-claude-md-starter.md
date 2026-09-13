# Production CLAUDE.md Starter

A working `CLAUDE.md` you can drop into a repository today, plus the reasoning behind
each section so you can cut what does not apply to you.

`CLAUDE.md` is the file Claude Code reads automatically at the start of a session. It is
persistent project context: the commands, boundaries and standards that would otherwise
be repeated in every prompt. It is not documentation for humans, and it is not a place to
describe your codebase — Claude can read the codebase.

## The one rule that matters most

**Keep it short.** Every line competes for attention with every other line. A 400-line
`CLAUDE.md` is followed less reliably than a 120-line one, because the important rules are
diluted by the obvious ones. If a rule is mechanical and unconditional — "format after
every edit" — it belongs in a hook, where it runs whether or not it was read.

Aim for roughly 150 lines. When you add something, look for something to remove.

## What belongs in it

| Belongs | Does not belong |
| --- | --- |
| Commands that are non-obvious or easy to get wrong | Anything derivable by reading the repo |
| Boundaries: what must not import what | A tour of the directory structure |
| Rules with a consequence attached | Generic advice ("write clean code") |
| Things that have already gone wrong once | Aspirations nobody enforces |
| The definition of "done" for this project | Duplicates of your linter's config |

## The starter file

Copy this to `CLAUDE.md` in your repository root. Replace everything in angle brackets.
Delete sections that do not apply — a section you cannot fill in honestly is worse than
no section.

{{INCLUDE:production-claude-md-starter/CLAUDE.md}}

## How to tell whether it is working

A `CLAUDE.md` that is never tested is a wish list. Three checks, in increasing strength:

1. **Ask.** Start a session and ask "what does CLAUDE.md tell you about testing here?"
   If the answer is vague, the section is vague.
2. **Bait.** Ask for something the file forbids — adding a dependency, pushing to the
   production branch. It should push back and cite the reason.
3. **Observe.** Over a week, note which rules get broken. A rule broken repeatedly is
   either badly written or does not belong in a prompt file at all. Move it to a hook.

## Strong rules versus weak ones

| Weak | Strong |
| --- | --- |
| Write good tests | A change to behaviour needs a test that fails without it |
| Be careful with secrets | Never read, print, log, or commit secrets; they live in the environment |
| Follow our style | Match the surrounding file's conventions over any general preference |
| Don't break things | A deploy is not finished until the smoke check passes |

The difference is that the strong version is checkable. Someone reading the diff can tell
whether it was followed.

## Scope: which file wins

Claude Code reads `CLAUDE.md` from several places and combines them. In practice:

- **`~/.claude/CLAUDE.md`** — your personal preferences, on every project. Keep it tiny.
- **`<repo>/CLAUDE.md`** — the project file. Committed. This is the one that matters.
- **`<repo>/<subdir>/CLAUDE.md`** — rules for one package in a monorepo, loaded when you
  work in that directory.
- **`CLAUDE.local.md`** — your own overrides, git-ignored.

Put a rule at the narrowest scope where it is true. A rule about the Shopify theme does
not belong in the file the API package also reads.

## What this starter leaves out

This is deliberately a starter. It does not include per-framework files, migration rules,
incident-response conventions, or the review checklists that turn a `CLAUDE.md` into a
working standard for a team. The
[Claude Code Website Launch System](/products/claude-code-website-launch-system)
contains the fuller versions along with the audits that check whether they are being
followed.

## Related reading

- [Production CLAUDE.md for web development](/blogs/guides/production-claude-md-web-development) — the full guide
- [CLAUDE.md examples for production web development](/blogs/guides/claude-md-examples-web-development) — worked examples by project type
- [Claude Code hooks](/blogs/guides/claude-code-hooks) — where mechanical rules belong instead
- [Anthropic: memory and CLAUDE.md](https://code.claude.com/docs/en/memory) — the primary source

## Licence

Free to use in any project, including client work. Do not resell or republish it as your own.
