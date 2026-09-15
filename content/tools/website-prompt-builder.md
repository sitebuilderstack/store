Describe what you are building, say what you need done and at what stage, and
this produces a structured prompt for Claude Code: role, objective, a discovery
phase that changes nothing, requirements, constraints, validation and
deliverables.

It runs in your browser. Nothing you describe is sent anywhere.

## Task and stage change the prompt, not a line in it

The two dropdowns at the top do more work than they look like they do.

**Task** decides whether the prompt permits changing files at all. Every
auditing task — audit, security, accessibility, performance, SEO, conversion —
generates a prompt that forbids editing anything and asks for findings instead.
That is not a stylistic preference. An audit whose fixes land in the same run
leaves you with a diff and no report, and afterwards nobody can tell which
finding was real or whether it was fixed correctly.

**Stage** decides what carries risk. A prompt for a site in production opens by
saying so, and requires the blast radius and the rollback for every change
before it is made. A planning prompt refuses to write implementation code at
all. The same project at two stages should not get the same instructions.

## The part that matters most

Every prompt this generates begins with a **discovery phase that forbids
changing anything**. Read the repository, report the structure and versions from
the manifest and lockfile rather than inferring them, run the commands that
already exist and show their output, then stop and wait.

That single constraint prevents the most expensive failure in agent-assisted
work: forty files changed on assumptions that were never checked, in a session
too large to review.

## Why the validation section is written the way it is

The generated prompt says every check must be seen failing before it is trusted.
That is not a stylistic preference. A link crawler reporting "0 broken links"
that has never found one is not evidence of anything, and a checker pointed at
the wrong directory will report clean forever.

Break the thing, watch it go red, restore it, watch it go quiet. Two minutes,
and every future green run means something.

It also requires structural checks to run against the **built output** rather
than the source. Those are different artefacts, and only one of them is what
visitors receive.

## What to change before you use it

Read it and cut. The generated prompt is deliberately complete rather than
minimal, and a request that names ten requirements will be followed less
carefully than one that names three. If you are building this in stages — and
you should be — delete the sections that belong to later stages and bring them
back when you get there.

The reasoning behind each section is in [how to build a website with Claude
Code](/blogs/guides/how-to-build-a-website-with-claude-code), and the prompt
patterns are covered in [best Claude Code prompts for web
development](/blogs/guides/best-claude-code-prompts-for-web-development).
