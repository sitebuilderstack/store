# Claude Code Website Development Benchmark 2026

**Status: no trials have been run. `results.csv` contains headers and no rows.**

That is the honest state, and it is deliberately the state the repository ships
in. Nothing here should be cited as a finding, and the public page says the same.

## What exists

| File | What it is |
| --- | --- |
| `METHODOLOGY.md` | How trials are run, what is held constant, and what this cannot measure |
| `TASKS.md` | Six tasks with acceptance criteria, written before any trial |
| `SCHEMA.md` | The data schema, field by field, with the definitions that would otherwise drift |
| `results.csv` | Published dataset. Headers only until trials are run. |
| `results.ndjson` | Working store, appended one line per trial. Absent until the first trial. |
| `../../scripts/benchmark-harness.py` | Records trials. Refuses rows that do not validate. |

## Running it

```bash
scripts/benchmark-harness.py --self-test          # prove the validation fires
scripts/benchmark-harness.py init --platform astro --task T-01 --run 1 \
    --model claude-opus-5 --tool-version "$(claude --version)"
scripts/benchmark-harness.py intervene --trial astro-T-01-1 --said "..."
scripts/benchmark-harness.py measure  --trial astro-T-01-1 --dir /tmp/trial \
    --build "npm run build" --test "npm test" --lighthouse lh.json
scripts/benchmark-harness.py finish   --trial astro-T-01-1 --success
scripts/benchmark-harness.py export               # regenerate results.csv
```

The harness records; it does not run Claude Code and it does not score. A harness
that produced and graded the work would be marking its own homework.

## Cost before starting

Six tasks × five platforms × three runs is **90 trials**. That is the smallest
honest version — fewer runs per cell produces a table that looks authoritative
and is mostly variance. Budget for that before starting, not after trial 30.

## Why nothing is published yet

Publishing a partial table invites exactly the comparison the missing cell would
change. The rule in `METHODOLOGY.md` is that no result is published before the
full run for that task completes on all five platforms.
