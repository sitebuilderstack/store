#!/usr/bin/env python3
"""Run the agency system's scripts against a temp workspace, offline.

new_client.py creates a project and refuses to recreate it; project_status.py
reads the example project's files and reproduces the documented status;
estimate.py totals the example worksheet and refuses a row where
low > expected; validate_client.py passes a clean project, fails one with a
.env file or a credential-shaped string, and warns about a placeholder in a
client-facing file. Nothing touches the network.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUNDLE = os.path.join(ROOT, "product", "Claude-Code-Agency-Client-Delivery-System")
SCRIPTS = os.path.join(BUNDLE, "scripts")
EXAMPLE = os.path.join(BUNDLE, "examples", "example-client-project")
failures = 0


def run(script, *args, cwd=None):
    p = subprocess.run([sys.executable, os.path.join(SCRIPTS, script)] + [str(a) for a in args], capture_output=True, text=True, cwd=cwd, timeout=60,
                       env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    return p.returncode, p.stdout, p.stderr


def check(name, ok, detail=""):
    global failures
    failures += 0 if ok else 1
    print("  %s  %s%s" % ("PASS" if ok else "FAIL", name, ("  -> " + detail.strip()[-300:]) if detail and not ok else ""))


def main():
    tmp = tempfile.mkdtemp()
    try:
        rc, out, err = run("new_client.py", "Northwind Supply", "--project", "Website Redesign", "--platform", "wordpress", "--type", "redesign", "--dir", os.path.join(tmp, "clients"))
        proj = os.path.join(tmp, "clients", "northwind-supply")
        check("new_client: creates the project (exit 0)", rc == 0 and os.path.isdir(proj), out + err)
        check("new_client: config filled with the client, project, platform, type", all(x in open(os.path.join(proj, "client-config.yaml")).read() for x in ("name: Northwind Supply", "name: Website Redesign", "platform: wordpress", "type: redesign", "status: lead")))
        check("new_client: CLAUDE.md filled and rules intact", "Northwind Supply" in open(os.path.join(proj, "CLAUDE.md")).read() and "Flag scope creep" in open(os.path.join(proj, "CLAUDE.md")).read())
        check("new_client: phase directories and tracking files present", all(os.path.exists(os.path.join(proj, x)) for x in ("01-discovery", "15-maintenance", "project-tracker.csv", "decision-log.csv", "access-inventory.md", ".gitignore", ".env.example")))
        check("new_client: example rows removed from the tracker", len(open(os.path.join(proj, "project-tracker.csv")).read().strip().splitlines()) == 1)
        rc, out, err = run("new_client.py", "Northwind Supply", "--dir", os.path.join(tmp, "clients"))
        check("new_client: refuses to overwrite an existing project (exit 2)", rc == 2 and "refusing" in err, out + err)
        rc, out, err = run("project_status.py", "--dir", proj)
        check("project_status: a fresh project is ON TRACK at discovery", rc == 0 and "Overall Status:  ON TRACK" in out and "Current Phase:   discovery" in out, out + err)
        ex = os.path.join(tmp, "example"); shutil.copytree(EXAMPLE, ex)
        rc, out, err = run("project_status.py", "--dir", ex, "--today", "2026-11-06", "--json", "status.json")
        j = json.load(open(os.path.join(ex, "status.json")))
        check("project_status: the example is BLOCKED on 2026-11-06 (copy overdue past the review window)", rc == 0 and j["status"] == "BLOCKED" and j["phase"] == "build", out + err)
        check("project_status: blockers, overdue client actions and HIGH risks are listed", any("Copy for 11 pages" in b for b in j["blockers"]) and any("overdue by 7 day(s)" in a for a in j["client_actions"]) and any("Content delay" in r for r in j["risks"]), json.dumps(j)[:400])
        check("project_status: JSON matches the shipped project-status.json", json.load(open(os.path.join(EXAMPLE, "project-status.json")))["status"] == j["status"] and json.load(open(os.path.join(EXAMPLE, "project-status.json")))["phase"] == j["phase"])
        rc, out, err = run("project_status.py", "--dir", ex, "--today", "2026-10-20")
        check("project_status: --today before the copy deadline shows no overdue action", rc == 0 and "overdue" not in out, out)
        rc, out, err = run("estimate.py", os.path.join(EXAMPLE, "project-estimation.csv"), "--contingency", "15", "--rate", "90")
        check("estimate: totals the example worksheet as a range", rc == 0 and "TOTAL" in out and "135.8" in out and "156.1" in out, out + err)
        check("estimate: lists the assumptions from the notes", "ASSUMPTIONS" in out and "Page assembly:" in out)
        bad = os.path.join(tmp, "bad.csv"); open(bad, "w").write("work_item,phase,quantity,complexity,low_hours,expected_hours,high_hours,notes\nX,Build,1,M,10,5,20,\n")
        rc, out, err = run("estimate.py", bad)
        check("estimate: refuses low > expected (exit 2)", rc == 2 and "does not hold" in err, out + err)
        rc, out, err = run("validate_client.py", "--dir", ex)
        check("validate_client: the example project is clean (exit 0)", rc == 0, out + err)
        open(os.path.join(ex, ".env"), "w").write("CRM_API_KEY=abc\n")
        rc, out, err = run("validate_client.py", "--dir", ex)
        check("validate_client: a .env inside the project fails (exit 2)", rc == 2 and ".env" in out, out + err)
        os.remove(os.path.join(ex, ".env"))
        open(os.path.join(ex, "notes.md"), "w").write("api_key: sk_live_ABCDEFGHIJKLMNOP1234\n")
        rc, out, err = run("validate_client.py", "--dir", ex)
        check("validate_client: a credential-shaped string fails", rc == 2 and "credential" in out, out + err)
        os.remove(os.path.join(ex, "notes.md"))
        os.makedirs(os.path.join(ex, "14-reports"), exist_ok=True); open(os.path.join(ex, "14-reports", "monthly.md"), "w").write("# Report\n\nTraffic: {sessions}\n")
        rc, out, err = run("validate_client.py", "--dir", ex)
        check("validate_client: a placeholder in a client-facing file warns (exit 1)", rc == 1 and "placeholder" in out, out + err)
        open(os.path.join(ex, "project-tracker.csv"), "a").write("bad,row\n")
        rc, out, err = run("validate_client.py", "--dir", ex)
        check("validate_client: still parses CSVs with a short row (columns check) and reports", rc >= 1, out + err)
        for f in sorted(os.listdir(SCRIPTS)):
            if f.endswith(".py"):
                rc, out, err = run(f, "--help")
                check("%s --help" % f, rc == 0 and "usage" in out.lower(), err)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("\n%d failure(s)" % failures)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
