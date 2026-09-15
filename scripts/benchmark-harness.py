#!/usr/bin/env python3
"""Record trials for the Claude Code Website Development Benchmark.

Records. It does not score anything and it does not run Claude Code — a harness
that both produced and graded the work would be marking its own homework.

Every trial is one line of NDJSON appended to research/benchmark/results.ndjson,
so an interrupted suite leaves every completed trial intact and parseable.

  benchmark-harness.py init --platform astro --task T-01 --run 1 \
      --model claude-opus-5 --tool-version 2.1.0
  benchmark-harness.py intervene --trial astro-T-01-1 --said "wrong build command"
  benchmark-harness.py measure --trial astro-T-01-1 --dir /path/to/project
  benchmark-harness.py finish --trial astro-T-01-1 --success
  benchmark-harness.py export            write results.csv from the NDJSON
  benchmark-harness.py --self-test       prove the validation fires

Usage of `measure` runs the project's own commands and Lighthouse if present. It
records exit codes and parsed scores; it never infers a result from a missing
tool, it records null and says so.
"""
import argparse
import datetime
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BENCH = os.path.join(ROOT, "research", "benchmark")
STORE = os.path.join(BENCH, "results.ndjson")
CSV = os.path.join(BENCH, "results.csv")

SCHEMA_VERSION = 1
PLATFORMS = ("shopify", "wordpress", "astro", "nextjs", "static")
TASK_RE = re.compile(r"^T-\d{2}$")

FIELDS = ["schema_version", "trial_id", "run", "platform", "task_id", "task_title",
          "model", "tool_version", "started_at", "ended_at", "success", "attempts",
          "human_interventions", "build_ok", "build_errors", "tests_ok",
          "lighthouse_performance", "lighthouse_accessibility", "lighthouse_seo",
          "lighthouse_best_practices", "axe_violations", "security_findings",
          "code_quality_issues", "deployment_ready", "notes"]


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


def task_titles():
    """Titles come from TASKS.md so a trial cannot name a task that does not exist."""
    p = os.path.join(BENCH, "TASKS.md")
    out = {}
    if os.path.exists(p):
        for m in re.finditer(r"^## (T-\d{2}) — (.+)$", open(p, encoding="utf-8").read(), re.M):
            out[m.group(1)] = m.group(2).strip()
    return out


def validate(rec):
    """Reasons this row must not be stored. Empty list means it is storable."""
    bad = []
    if rec.get("schema_version") != SCHEMA_VERSION:
        bad.append("schema_version must be %d" % SCHEMA_VERSION)
    if rec.get("platform") not in PLATFORMS:
        bad.append("platform must be one of %s" % (PLATFORMS,))
    if not TASK_RE.match(rec.get("task_id") or ""):
        bad.append("task_id must look like T-01")
    titles = task_titles()
    if titles and rec.get("task_id") not in titles:
        bad.append("task_id %r is not in TASKS.md" % rec.get("task_id"))
    if not isinstance(rec.get("run"), int) or rec["run"] < 1:
        bad.append("run must be a positive integer")
    if not rec.get("model"):
        bad.append("model is required — a family name is not a model id")
    if not rec.get("tool_version"):
        bad.append("tool_version is required")
    for k in ("lighthouse_performance", "lighthouse_accessibility",
              "lighthouse_seo", "lighthouse_best_practices"):
        v = rec.get(k)
        if v is not None and not (isinstance(v, int) and 0 <= v <= 100):
            bad.append("%s must be null or an integer 0-100" % k)
    if rec.get("ended_at") and rec.get("started_at") and rec["ended_at"] < rec["started_at"]:
        bad.append("ended_at is before started_at")
    return bad


def load():
    if not os.path.exists(STORE):
        return []
    out = []
    for line in open(STORE, encoding="utf-8"):
        line = line.strip()
        if line:
            out.append(json.loads(line))
    return out


def save_all(rows):
    os.makedirs(BENCH, exist_ok=True)
    with open(STORE, "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, sort_keys=True) + "\n")


def get(rows, trial):
    for r in rows:
        if r["trial_id"] == trial:
            return r
    raise SystemExit("no such trial: %s (run `init` first)" % trial)


def cmd_init(a):
    titles = task_titles()
    rec = {f: None for f in FIELDS}
    rec.update(schema_version=SCHEMA_VERSION,
               trial_id="%s-%s-%d" % (a.platform, a.task, a.run),
               run=a.run, platform=a.platform, task_id=a.task,
               task_title=titles.get(a.task), model=a.model,
               tool_version=a.tool_version, started_at=now(),
               attempts=1, human_interventions=0, notes="")
    bad = validate(rec)
    if bad:
        for b in bad:
            print("  REFUSED %s" % b)
        raise SystemExit("the trial was not recorded")
    rows = load()
    if any(r["trial_id"] == rec["trial_id"] for r in rows):
        raise SystemExit("trial %s already exists; use a new --run" % rec["trial_id"])
    rows.append(rec)
    save_all(rows)
    print("started %s" % rec["trial_id"])
    return 0


def cmd_intervene(a):
    rows = load()
    r = get(rows, a.trial)
    r["human_interventions"] = (r.get("human_interventions") or 0) + 1
    # The quote is stored so the count can be audited rather than trusted.
    note = (r.get("notes") or "").rstrip()
    r["notes"] = (note + "\n" if note else "") + "intervention %d: %s" % (
        r["human_interventions"], a.said)
    if a.attempt:
        r["attempts"] = (r.get("attempts") or 0) + 1
    save_all(rows)
    print("%s now has %d intervention(s)" % (a.trial, r["human_interventions"]))
    return 0


def _run(cmd, cwd):
    try:
        p = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True,
                           text=True, timeout=900)
        return p.returncode, (p.stdout + p.stderr)
    except Exception as e:                                     # noqa: BLE001
        return None, "harness could not run it: %s" % type(e).__name__


def cmd_measure(a):
    rows = load()
    r = get(rows, a.trial)
    if a.build:
        code, out = _run(a.build, a.dir)
        r["build_ok"] = (code == 0) if code is not None else None
        r["build_errors"] = len(re.findall(r"(?im)^\s*error\b", out)) if code else 0
        print("  build   exit=%s errors=%s" % (code, r["build_errors"]))
    if a.test:
        code, _ = _run(a.test, a.dir)
        r["tests_ok"] = (code == 0) if code is not None else None
        print("  tests   exit=%s" % code)
    if a.lighthouse:
        # Parse a Lighthouse JSON report the caller already produced. The harness
        # does not run Lighthouse itself: doing so would bury the flags that
        # decide the numbers inside this script, where nobody would read them.
        try:
            d = json.load(open(a.lighthouse, encoding="utf-8"))
            cats = d.get("categories", {})
            for key, field in (("performance", "lighthouse_performance"),
                               ("accessibility", "lighthouse_accessibility"),
                               ("seo", "lighthouse_seo"),
                               ("best-practices", "lighthouse_best_practices")):
                v = cats.get(key, {}).get("score")
                r[field] = int(round(v * 100)) if isinstance(v, (int, float)) else None
            print("  lighthouse  perf=%s a11y=%s seo=%s bp=%s" %
                  (r["lighthouse_performance"], r["lighthouse_accessibility"],
                   r["lighthouse_seo"], r["lighthouse_best_practices"]))
        except Exception as e:                                 # noqa: BLE001
            print("  lighthouse report unreadable (%s) — left null" % type(e).__name__)
    bad = validate(r)
    if bad:
        for b in bad:
            print("  REFUSED %s" % b)
        raise SystemExit("measurements not saved")
    save_all(rows)
    return 0


def cmd_finish(a):
    rows = load()
    r = get(rows, a.trial)
    r["success"] = bool(a.success)
    r["ended_at"] = now()
    if a.deployment_ready is not None:
        r["deployment_ready"] = a.deployment_ready
    if a.note:
        note = (r.get("notes") or "").rstrip()
        r["notes"] = (note + "\n" if note else "") + a.note
    bad = validate(r)
    if bad:
        for b in bad:
            print("  REFUSED %s" % b)
        raise SystemExit("trial not closed")
    save_all(rows)
    print("finished %s success=%s" % (a.trial, r["success"]))
    return 0


def cmd_export(a):
    import csv as _csv
    rows = load()
    open_trials = [r["trial_id"] for r in rows if r.get("ended_at") is None]
    with open(CSV, "w", newline="", encoding="utf-8") as fh:
        w = _csv.DictWriter(fh, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print("wrote %s (%d trial(s))" % (CSV, len(rows)))
    if open_trials:
        print("  %d trial(s) still open and exported with no result: %s"
              % (len(open_trials), ", ".join(open_trials[:5])))
    return 0


def self_test():
    """Prove the validation refuses what it should and accepts what it should."""
    ok, bad = [], []

    def check(name, got, want):
        (ok if got == want else bad).append("%s: got %r want %r" % (name, got, want))

    base = {"schema_version": 1, "trial_id": "astro-T-01-1", "run": 1,
            "platform": "astro", "task_id": "T-01", "model": "claude-opus-5",
            "tool_version": "2.1.0", "started_at": "2026-09-07T00:00:00+00:00"}
    check("a complete row is accepted", validate(base), [])
    check("an unknown platform is refused",
          bool(validate(dict(base, platform="squarespace"))), True)
    check("an unknown task is refused",
          bool(validate(dict(base, task_id="T-99"))), True)
    check("a malformed task id is refused",
          bool(validate(dict(base, task_id="one"))), True)
    check("a missing model is refused", bool(validate(dict(base, model=""))), True)
    check("a missing tool version is refused",
          bool(validate(dict(base, tool_version=None))), True)
    check("run zero is refused", bool(validate(dict(base, run=0))), True)
    check("a Lighthouse score of 101 is refused",
          bool(validate(dict(base, lighthouse_seo=101))), True)
    check("a null Lighthouse score is fine",
          validate(dict(base, lighthouse_seo=None)), [])
    check("a 0-100 Lighthouse score is fine",
          validate(dict(base, lighthouse_seo=0)), [])
    check("end before start is refused",
          bool(validate(dict(base, ended_at="2026-09-06T00:00:00+00:00"))), True)
    check("a wrong schema version is refused",
          bool(validate(dict(base, schema_version=2))), True)
    check("TASKS.md actually parsed", len(task_titles()) >= 6, True)

    for l in ok:
        print("  ok   %s" % l)
    for l in bad:
        print("  FAIL %s" % l)
    print("\n%d passed, %d failed" % (len(ok), len(bad)))
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--self-test", action="store_true")
    sub = ap.add_subparsers(dest="cmd")

    p = sub.add_parser("init")
    p.add_argument("--platform", required=True, choices=PLATFORMS)
    p.add_argument("--task", required=True)
    p.add_argument("--run", type=int, default=1)
    p.add_argument("--model", required=True)
    p.add_argument("--tool-version", required=True)
    p.set_defaults(fn=cmd_init)

    p = sub.add_parser("intervene")
    p.add_argument("--trial", required=True)
    p.add_argument("--said", required=True, help="quote what was actually said")
    p.add_argument("--attempt", action="store_true", help="also count a new prompt")
    p.set_defaults(fn=cmd_intervene)

    p = sub.add_parser("measure")
    p.add_argument("--trial", required=True)
    p.add_argument("--dir", default=".")
    p.add_argument("--build")
    p.add_argument("--test")
    p.add_argument("--lighthouse", help="path to a Lighthouse JSON report")
    p.set_defaults(fn=cmd_measure)

    p = sub.add_parser("finish")
    p.add_argument("--trial", required=True)
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--success", action="store_true")
    g.add_argument("--fail", dest="success", action="store_false")
    p.add_argument("--deployment-ready", type=lambda s: s.lower() == "true", default=None)
    p.add_argument("--note")
    p.set_defaults(fn=cmd_finish)

    p = sub.add_parser("export")
    p.set_defaults(fn=cmd_export)

    a = ap.parse_args()
    if a.self_test:
        raise SystemExit(self_test())
    if not getattr(a, "fn", None):
        ap.print_help()
        return 1
    return a.fn(a)


if __name__ == "__main__":
    raise SystemExit(main())
