Answer a few questions about your project and this produces a starting
`CLAUDE.md` — the file Claude Code reads at the beginning of every session,
without being asked.

Everything happens in your browser. Nothing you type is sent to this site, to
an analytics service, or anywhere else.

## What makes a CLAUDE.md work

The failure mode is length, not detail. Every line in the file competes with
every other line for attention, so a 400-line file is followed **less**
reliably than a 120-line one. That is the opposite of how most documentation
works, and it is why this generator leaves out anything you did not fill in
rather than padding the file with plausible defaults.

A generated line saying `npm test` for a project with no tests is worse than
silence: it is an instruction the agent will try to follow.

Four things earn their place:

- **The real commands.** Not the ones you wish existed.
- **Conventions an agent could not infer.** If it is obvious from reading two files, leave it out.
- **Prohibitions with consequences.** "Never edit the parent theme" prevents a whole class of change that silently disappears at the next update.
- **A definition of done.** What must be true before the work is finished.

## What belongs somewhere else

Rules that are mechanical and unconditional should be a
[hook](/blogs/guides/claude-code-hooks), not a paragraph. A hook runs whether or
not anyone read the file. "Never commit to main" is enforceable; asking politely
is not.

Procedures you repeat should be a [skill](/blogs/guides/claude-code-skills) —
a named thing you invoke — rather than instructions sitting in context on every
session whether or not they are relevant.

## After you generate it

Put it at your project root, commit it, then test that it is doing something.
Start a session and ask what the file says about your testing conventions. A
vague answer means a vague section. Then ask for something the file forbids and
confirm it pushes back.

The long-form version of all this, including four complete worked examples, is
in the guide on [creating a production
CLAUDE.md](/blogs/guides/production-claude-md-web-development).
