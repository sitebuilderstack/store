# Claude Code Website Development Benchmark 2026 — methodology

**Status: no trials have been run. There are no results.** This document exists so
the method can be criticised before any data is collected, which is the only order
in which that criticism is worth anything.

## The question

When Claude Code is asked to do the same website task on five different platforms,
what differs — and how much of the difference is the platform rather than the task?

Not "which platform is best". That question has no answer, and a benchmark
claiming to have found one would be measuring its own task selection.

## What is held constant

- The same task list, written before any trial (`TASKS.md`).
- The same acceptance criteria per task, written at the same time.
- One model, one Claude Code version, both recorded per trial.
- A fresh working directory per trial. No carry-over context between trials.
- No `CLAUDE.md` unless the task specifies one, because supplying a good one is
  exactly the intervention this benchmark should not silently make.

## What varies

Only the platform, and whatever the platform forces to differ — the starter
project, the build command, the deploy target.

## Why five platforms

Shopify, WordPress, Astro, Next.js and static HTML/CSS/JS cover the range that
actually matters for the difference being measured: a hosted platform with a
templating language and an admin API; a PHP CMS with a plugin surface; a static
site generator with a zero-JavaScript default; a React framework with a build
step and server rendering; and a baseline with no framework at all.

## How trials are run

1. `benchmark-harness.py init` creates the trial directory and records the
   environment: model id, tool version, platform, task, run number.
2. The task's prompt is sent verbatim. It is in `TASKS.md` and is not adapted per
   platform beyond naming the platform.
3. Every correction a human makes is logged with `--intervene "<what was said>"`.
   The quote is stored, so the count can be audited.
4. `benchmark-harness.py measure` runs the objective checks — build, tests,
   Lighthouse, axe — and records their raw output alongside the row.
5. `benchmark-harness.py finish --success/--fail` closes the trial against the
   acceptance criteria.

The harness never scores anything itself. It records what commands returned.

## Repeats

Three runs per platform/task pair, minimum. Agentic output varies between
identical prompts, and a single run per cell would produce a table that looks
authoritative and is mostly noise. If three runs disagree, that disagreement is
the finding and gets reported as a range, never as a mean with the spread
discarded.

## What this cannot measure

- **Whether the code is good.** Lint findings and Lighthouse scores are proxies,
  and weak ones. A passing build says nothing about whether the abstraction was
  right.
- **Long-horizon maintenance.** Every task here is short. The failure mode that
  costs most in real projects — a decision that is wrong six months later — is
  invisible at this timescale.
- **Accessibility.** The automated checks catch a minority of WCAG failures. A
  perfect axe run is not an accessible site and will not be described as one.
- **The counterfactual.** There is no human control arm. This measures how the
  tool behaves across platforms, not whether using it was better than not.

## Conflict of interest

This benchmark is published by a store that sells Claude Code workflows. That is
a real conflict and stating it does not remove it.

Two things partially offset it: the raw dataset is published so anyone can
recompute the summary, and the harness is in the public repository so the
collection can be repeated. If a result favours the products sold here, that
should be treated as the least reliable result in the set.

## Publication rules

- No result is published before the full run for that task completes on all five
  platforms. Partial tables invite the comparison the missing cell would change.
- Every published figure is traceable to a row in `results.ndjson`.
- The page states the date tested, the model, and the tool version, because all
  three will be stale within months and a benchmark without them is folklore.
- Corrections are appended to an update history rather than edited silently.
