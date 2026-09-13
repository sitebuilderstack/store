# Email 2 — day 2

**Subject:** Why "build me a website" isn't enough
**Preheader:** The problem isn't the model. It's how much you left it to guess.

---

Ask Claude Code to "build me a website" and you get a website. It will look fine. It will
also have invented a framework choice, a directory structure, a testing approach and a
deployment target — none of which you specified, all of which you now live with.

The model is not the constraint. **The specification is.**

## What a vague prompt actually leaves open

Every one of these gets decided by something, and if you did not decide it, the model did:

- Which framework, and which version
- Where files go, and what may import what
- Whether there are tests, and what counts as passing
- What happens to secrets
- What "done" means

None of these are hard questions. They are just questions nobody asked out loud.

## The fix is boring and it works

Four things, before any code:

1. **Project context** — the commands, the boundaries, the standard. This is what your
   `CLAUDE.md` is for, and it is why that was the first thing I sent you.
2. **Constraints** — what must not happen. "Do not add a dependency without asking" is
   worth more than three paragraphs about code quality.
3. **Architecture, decided by you** — an assistant is good at executing a structure and
   unreliable at choosing one you will still like in six months.
4. **A definition of done** — which command, producing which result. Not "when it works".

## The one that catches people

Number four. "It works" is not checkable, so it gets claimed rather than verified. Replace
it with something a person reading the diff can confirm: lint and typecheck pass, tests
pass, the page was actually loaded.

The [complete website workflow](https://sitebuilderstack.com/blogs/guides/how-to-build-a-website-with-claude-code)
is the long version of this — fifteen steps, each with the thing you check before moving
on. Free, no signup, about a twenty-minute read.

Next: five things that were broken on this site while every automated check reported them
healthy.

— James
