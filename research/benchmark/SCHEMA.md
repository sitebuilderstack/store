# Claude Code Website Development Benchmark — data schema

One row per **trial**: one task, attempted once, on one platform, with one
configuration. Repeats are separate rows sharing a `task_id` and differing in
`run`, so variance is visible rather than averaged away at collection time.

Stored as newline-delimited JSON in `results.ndjson`, and published as CSV.
NDJSON because a run appends one line and a crash mid-suite leaves every
completed trial intact and parseable.

## Fields

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `schema_version` | int | yes | 1. Bump on any breaking field change. |
| `trial_id` | string | yes | `<platform>-<task_id>-<run>`, unique. |
| `run` | int | yes | 1-based repeat number for this platform/task pair. |
| `platform` | enum | yes | `shopify`, `wordpress`, `astro`, `nextjs`, `static`. |
| `task_id` | string | yes | Stable id from `TASKS.md`. |
| `task_title` | string | yes | Human-readable, copied from `TASKS.md`. |
| `model` | string | yes | Exact model id, not a family name. |
| `tool_version` | string | yes | Claude Code version, from `claude --version`. |
| `started_at` | ISO 8601 | yes | UTC. |
| `ended_at` | ISO 8601 | yes | UTC. |
| `success` | bool | yes | Did the task meet its stated acceptance criteria? |
| `attempts` | int | yes | Prompts sent, including the first. |
| `human_interventions` | int | yes | Times a person corrected course. See below. |
| `build_ok` | bool | no | Did the project's own build command exit 0? |
| `build_errors` | int | no | Count of distinct build errors before success. |
| `tests_ok` | bool | no | Did the project's own test command exit 0? |
| `lighthouse_performance` | int 0–100 | no | Lab, desktop preset unless stated. |
| `lighthouse_accessibility` | int 0–100 | no | Automated only. See caveat. |
| `lighthouse_seo` | int 0–100 | no | Lighthouse's SEO category, not an SEO audit. |
| `lighthouse_best_practices` | int 0–100 | no | |
| `axe_violations` | int | no | Distinct axe-core rule violations. |
| `security_findings` | int | no | From the stated scanner, at the stated severity. |
| `code_quality_issues` | int | no | Lint/typecheck findings on the produced code. |
| `deployment_ready` | bool | no | Met the deploy checklist in `TASKS.md`. |
| `notes` | string | no | Free text. Anything surprising belongs here. |

## Definitions that would otherwise drift

**`human_interventions`** counts corrections, not messages. Asking "are you
done?" is not an intervention. Saying "you used the wrong build command" is.
Every intervention must be quoted in `notes`, so the count can be audited rather
than trusted.

**`success`** is judged against the acceptance criteria written in `TASKS.md`
*before* any trial was run. A task whose criteria were adjusted after seeing
results is disqualified, not rescored.

**`lighthouse_accessibility`** is an automated subset. It cannot detect most
WCAG failures, and a score of 100 does not mean accessible. It is recorded
because it is comparable across platforms, not because it is sufficient.

## What this schema deliberately does not have

No `quality_score`, no composite index, no weighting. Any single number
combining these would be a judgement presented as a measurement, and the
weighting would be doing all the work. Readers can compute one; the dataset
should not ship with one baked in.

No timing field beyond start and end. Wall-clock time on an agentic task is
dominated by model latency and network conditions on the day, and publishing it
would invite comparisons the data cannot support.
