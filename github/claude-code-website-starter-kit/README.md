# Claude Code Website Starter Kit

A `CLAUDE.md` starter and four production checklists for building, launching and
auditing websites with [Claude Code](https://code.claude.com/docs).

Everything here is plain Markdown. Copy what you need into your repository, delete
what does not apply, and edit the rest. There is nothing to install and nothing to
sign up for.

## What is in it

| File | What it is for |
| --- | --- |
| [`CLAUDE.md`](CLAUDE.md) | A starter project-context file: commands, architecture boundaries, coding standards, testing, security, accessibility, SEO, deployment, prohibited actions, and a definition of done |
| [`LAUNCH-CHECKLIST.md`](LAUNCH-CHECKLIST.md) | 18 sections between "it looks finished" and "it is live and behaving" |
| [`SEO-CHECKLIST.md`](SEO-CHECKLIST.md) | Technical SEO in dependency order, limited to checks a machine can verify |
| [`SECURITY-CHECKLIST.md`](SECURITY-CHECKLIST.md) | Secrets, headers, input handling, auth, sessions, webhooks, dependencies, CI/CD, production hygiene |
| [`WEBSITE-AUDIT-CHECKLIST.md`](WEBSITE-AUDIT-CHECKLIST.md) | Inspecting a site that already exists, with a severity scale and a write-up format |
| [`skills/`](skills) | Five ready-to-install Claude Code skills that run the checklists as procedures |

## Who it is for

Developers using Claude Code (or any coding assistant) to build real websites, who
want the operational layer around the tool rather than the tool itself. It assumes
you can read a diff and run a command. It does not assume any particular framework,
host, or language.

It is deliberately framework-agnostic. If you want a `CLAUDE.md` tuned to a specific
stack, start from the one here and cut.

## How to use it

### 1. Start with `CLAUDE.md`

Clone this repository, or download [`CLAUDE.md`](CLAUDE.md) on its own, and copy it
to the root of your project:

```bash
cp CLAUDE.md /path/to/your-project/CLAUDE.md
```

Open it and replace everything in angle brackets. Delete any section you cannot fill
in honestly — an empty section is worse than a missing one.

Then check it is actually doing something. Start a session and ask:

```
What does CLAUDE.md tell you about testing in this project?
```

A vague answer means a vague section. Then try asking for something the file forbids
and confirm it pushes back.

**Keep it short.** Aim for roughly 150 lines. Every line competes for attention with
every other line, so a 400-line file is followed less reliably than a 120-line one.
Rules that are mechanical and unconditional belong in a
[hook](https://code.claude.com/docs/en/hooks), where they run whether or not anyone
read them.

### 2. Use the checklists as prompts, not as reading

The checklists are written so each item is something you can hand over directly:

```
Work through SEO-CHECKLIST.md section 3 (Canonicals) against this repository.
For each item: state whether it passes, show the evidence, and stop if you
cannot verify it rather than assuming.
```

The "stop if you cannot verify it" clause matters more than it looks. The most
expensive failure in this kind of work is a check that reports success because it
never actually ran.

### 3. Prove the checks can fail

Before you trust a passing result, break the thing it is checking and confirm the
check notices. A link crawler that reports "0 broken links" without ever having found
one is not evidence of anything.

## The skills

The checklists tell you what to check. The skills in [`skills/`](skills) run them.

| Skill | What it does |
| --- | --- |
| `/seo-audit` | Technical SEO in dependency order, findings with evidence |
| `/a11y-audit` | WCAG 2.2 AA, separating what a tool can answer from what needs a person |
| `/security-review` | Defensive review of code and config you own — explicitly not pen testing |
| `/launch-check` | Pre-launch readiness, grouped into blockers and the rest |
| `/claude-md-review` | Reviews your `CLAUDE.md` for length, checkable rules and contradictions |

### Installing them

There is no package manager. A skill is a directory, and installing one means putting
it where Claude Code already looks:

```bash
# just you, every project
cp -r skills/seo-audit ~/.claude/skills/

# or this project, committed for the team
mkdir -p .claude/skills && cp -r skills/* .claude/skills/
```

Then type `/seo-audit` — or run `/skills` to confirm Claude Code can see them. You do
not need to restart; Claude Code watches those directories. The exception is creating a
top-level skills directory that did not exist when the session started, which needs a
restart before it is watched.

**The file must be called `SKILL.md` and live in a directory named for the skill.** A
loose `seo-audit.md` in the skills folder does nothing. That is the most common reason
a copied skill never appears.

### A note on what they will not do

Four of the five are marked `disable-model-invocation`, so Claude will not start them
on its own — they are long-running and you should choose when to spend the tokens.
They also refuse to fix anything in the same run that finds it, because an audit whose
findings disappear into a commit is not an audit.

Read the `SKILL.md` before running any skill from anyone, including these. It is a
prompt that runs against your repository, and it can carry an `allowed-tools` list that
pre-approves tool calls.

## An example workflow

Roughly the order these get used on a real build:

1. **Before writing code** — fill in `CLAUDE.md`, commit it.
2. **During the build** — `LAUNCH-CHECKLIST.md` sections 1–6 as you go.
3. **Before deploying** — sections 7–17, then fix what fails.
4. **After deploying** — section 18, on the live site, once DNS and caches have settled.
5. **Ongoing** — `SEO-CHECKLIST.md` after template changes;
   `SECURITY-CHECKLIST.md` after anything touching auth, input, or dependencies;
   `WEBSITE-AUDIT-CHECKLIST.md` when you inherit a site or come back to one.

## Longer-form guides

These checklists are the condensed versions. The reasoning behind them is published
in full, free to read:

- [How to build a website with Claude Code](https://sitebuilderstack.com/blogs/guides/how-to-build-a-website-with-claude-code)
- [Production CLAUDE.md for web development](https://sitebuilderstack.com/blogs/guides/production-claude-md-web-development)
- [Claude Code SEO: complete website optimization workflow](https://sitebuilderstack.com/blogs/guides/claude-code-seo-website-optimization)
- [Claude Code website audit: complete production checklist](https://sitebuilderstack.com/blogs/guides/claude-code-website-audit)
- [Claude Code hooks](https://sitebuilderstack.com/blogs/guides/claude-code-hooks)
- [All guides](https://sitebuilderstack.com/blogs/guides)

Primary sources for Claude Code itself are at
[code.claude.com/docs](https://code.claude.com/docs). Where this kit and the official
documentation disagree, the official documentation is right.

## Contributing

Corrections are welcome, particularly where a checklist item is out of date, wrong,
or describes behaviour that has since changed. Open an issue with what you observed
and where. Additions are held to one standard: an item has to be something a reader
can actually check, not general advice.

## About

Maintained by James Joyner IV, a senior software engineer with 25 years in technology
and a background in platform and infrastructure engineering. These are the working
documents behind [Site Builder Stack](https://sitebuilderstack.com).

If you want this assembled, tested and packaged rather than adapted by hand, the
[Claude Code Website Launch System](https://sitebuilderstack.com/products/claude-code-website-launch-system)
is the paid version. Nothing in this repository is a trial or a teaser for it — these
files are complete as they stand.

## Licence

[MIT](LICENSE). Use it in anything, including client work.

---

Site Builder Stack is an independent project and is not affiliated with, sponsored by,
or endorsed by Anthropic. "Claude" and "Claude Code" are product names and trademarks
of Anthropic, PBC, referenced here only to describe compatibility.
