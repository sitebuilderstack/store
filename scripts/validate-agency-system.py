#!/usr/bin/env python3
"""Validate the Agency & Client Delivery System before packaging.

Structural checks — required files, every module document in the promised
shape (audience line, Goal, Common mistakes), every command in the
seven-section shape with an audience line, every CSV parseable with its
declared columns, YAML/JSON parseable, every script runnable with --help and
standard-library only, the example project internally consistent — plus the
checks that would embarrass this product in particular:

  * A credential, a `.env`, or our own store's private hostnames anywhere.
  * A plaintext credential-storage template (a "password" field with a value).
  * A real-looking client domain in the example (it must be .example).
  * A fabricated metric in the example (an outcome percentage with no source).
  * The ten operating rules missing from CLAUDE.md or a command's rules.
  * Legal-advice or guarantee language: "this contract", "legally binding",
    "guaranteed results", or a testimonial written for a client.
  * A price literal for this product that is not $39.99, or any forbidden
    neighbour ($39, $39.00, $39.95, $49, $59, $79, $99, $129).

Run with --self-test to prove every check fires.
"""
import csv
import io
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUNDLE = os.path.join(ROOT, "product", "Claude-Code-Agency-Client-Delivery-System")

REQUIRED_FILES = ["START-HERE.md", "QUICK-START.md", "README.md", "LICENSE.md", "VERSION.md", "CHANGELOG.md",
                  "templates/client-config.yaml", "templates/CLAUDE.md", "templates/lead-intake.md", "templates/access-inventory.md",
                  "templates/proposal-simple.md", "templates/proposal-standard.md", "templates/proposal-audit-and-build.md", "templates/proposal-redesign.md",
                  "templates/proposal-shopify.md", "templates/proposal-maintenance.md", "templates/client-kickoff-agenda.md", "templates/client-meeting-notes.md",
                  "templates/requirements-traceability.csv", "templates/project-tracker.csv", "templates/client-action-items.csv", "templates/change-request.md",
                  "templates/change-log.csv", "templates/revision-tracker.csv", "templates/client-handoff.md", "templates/maintenance-retainer-proposal.md",
                  "templates/project-risk-register.csv", "templates/decision-log.csv", "templates/assumptions-log.csv", "templates/project-status.json",
                  "templates/client-review-package.md", "templates/weekly-status-report.md", "templates/testimonial-request.md", "templates/.gitignore", "templates/.env.example",
                  "templates/client-project/README.md", "templates/client-project/15-maintenance/README.md",
                  "checklists/definition-of-done.md", "checklists/client-launch-checklist.md", "checklists/access-transfer.md",
                  "worksheets/project-estimation.csv", "worksheets/retainer-builder.md", "worksheets/project-profitability.csv",
                  "reports/client-discovery-report.md", "reports/client-website-audit.md", "reports/qa-report.md", "reports/monthly-maintenance-report.md",
                  "reports/discovery-report.md", "reports/website-audit.md", "reports/weekly-status-report.md", "reports/launch-readiness-report.md",
                  "reports/launch-report.md", "reports/handoff-report.md", "reports/project-closeout-report.md", "reports/monthly-client-report.md",
                  "reference/troubleshooting.md", "reference/pricing-guidance.md", "reference/pricing-examples.md", "reference/client-data-policy.md",
                  "reference/communication-rules.md", "reference/project-types.md", "reference/platform-workflows.md", "reference/master-workflow.md", "reference/bundle-readiness.md",
                  ".claude/commands/COMMANDS.md", "scripts/README.md", "scripts/new_client.py", "scripts/project_status.py", "scripts/estimate.py", "scripts/validate_client.py",
                  "examples/example-client-project/README.md", "examples/example-client-project/client-config.yaml", "examples/example-client-project/lead-intake.md",
                  "examples/example-client-project/client-discovery-report.md", "examples/example-client-project/client-website-audit.md", "examples/example-client-project/project-scope.md",
                  "examples/example-client-project/estimate.md", "examples/example-client-project/proposal.md", "examples/example-client-project/onboarding-checklist.md",
                  "examples/example-client-project/requirements.md", "examples/example-client-project/project-plan.md", "examples/example-client-project/qa-report.md",
                  "examples/example-client-project/weekly-2026-11-06.md", "examples/example-client-project/launch-report.md", "examples/example-client-project/client-handoff.md",
                  "examples/example-client-project/retainer-recommendation.md", "examples/example-client-project/retrospective.md"]
REQUIRED_CHECKLISTS = ["discovery", "onboarding", "requirements", "development", "content", "seo", "analytics", "qa", "client-review", "pre-launch", "post-launch", "handoff", "maintenance", "offboarding"]
REQUIRED_COMMANDS = ["lead-qualification", "client-discovery", "client-intake", "technical-audit", "seo-audit", "conversion-audit", "client-website-audit",
                     "client-scope", "scope-change-check", "project-estimate", "generate-proposal", "client-onboarding", "requirements-document", "project-plan",
                     "setup-client-project", "delivery-workflow", "client-project-qa", "client-status-update", "weekly-client-report", "client-question",
                     "client-review-request", "change-request", "client-feedback-triage", "client-launch-readiness", "client-launch-report", "client-handoff",
                     "monthly-client-report", "retainer-opportunity", "client-offboarding", "project-retrospective", "case-study-draft", "agency-project-status",
                     "client-delay-notice", "client-approval-request", "client-review-package", "client-meeting-summary", "project-estimate-review"]
COMMAND_SECTIONS = ["## PURPOSE", "## INPUTS", "## REQUIRED CONTEXT", "## STEPS", "## SAFETY / BUSINESS RULES", "## OUTPUT FORMAT", "## VALIDATION"]
COMMAND_AUD = re.compile(r"^> \*\*(INTERNAL USE|CLIENT-FACING|INTERNAL USE → CLIENT-FACING after review)\*\*", re.M)
COMMAND_RULES = ["Never invent client facts", "Never promise rankings", "No credentials", "Nothing is sent by this command", "approved scope"]
RULES = ["Work only within approved scope", "Never invent client requirements", "Identify uncertainty", "Preserve existing functionality", "Do not expose credentials",
         "Document important changes", "Validate work before marking complete", "Flag scope creep", "Do not promise the client outcomes", "Maintain professional client-facing language"]
CSV_COLUMNS = {
    "project-tracker.csv": ["task", "phase", "owner", "priority", "status", "start_date", "due_date", "dependency", "client_blocked", "notes"],
    "client-action-items.csv": ["action", "owner", "requested_date", "due_date", "status", "impact_if_delayed", "notes"],
    "change-log.csv": ["id", "request", "requested_by", "date", "classification", "approved", "scope_impact", "schedule_impact", "status"],
    "decision-log.csv": ["date", "decision", "reason", "approved_by", "impact", "notes"],
    "assumptions-log.csv": ["assumption", "source", "validated", "impact_if_wrong", "status"],
    "project-risk-register.csv": ["risk", "likelihood", "impact", "severity", "mitigation", "owner", "status"],
    "requirements-traceability.csv": ["requirement_id", "requirement", "source", "deliverable", "status", "validation_method", "notes"],
    "revision-tracker.csv": ["feedback", "classification", "priority", "owner", "status", "scope_impact", "notes"],
    "project-estimation.csv": ["work_item", "phase", "quantity", "complexity", "low_hours", "expected_hours", "high_hours", "notes"],
    "project-profitability.csv": ["project", "revenue", "estimated_hours", "actual_hours", "direct_costs", "effective_hourly_rate", "gross_margin_estimate", "notes"],
}
MODULE_DOC = re.compile(r"^(0[1-9]|1[0-9]|2[01])-[a-z-]+/README\.md$")
REQUIRED_SECTIONS = ["## Goal", "## Common mistakes"]
AUDIENCE = re.compile(r"^\*\*Audience:\*\* (INTERNAL USE|CLIENT-FACING|the [^\n]+|INTERNAL USE[^\n]*|CLIENT-FACING[^\n]*)", re.M)

FORBIDDEN_NAMES = (".DS_Store", "Thumbs.db", ".gitkeep", "__MACOSX", ".env")
SECRET = re.compile(r"shp(?:at|ss|ca|pa|ut)_[0-9a-fA-F]{32}|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{36}|-----BEGIN [A-Z ]*PRIVATE KEY-----|xox[bap]-[0-9A-Za-z-]{10,}|sk_live_[0-9A-Za-z]{16,}")
PLAINTEXT_CRED = re.compile(r"(?im)^\s*(?:\|?\s*)?(password|passwd|api[_ -]?key|access token|secret)\s*[:|]\s*[A-Za-z0-9!@#$%^&*][^\s|]{5,}")
PRIVATE_HOSTS = re.compile(r"kjhvcj-yi\.myshopify\.com|site-builder-stack\.myshopify\.com|/opt/shopify-(client-id|secret)|SBS_TOKEN_CACHE|shopify_api\.py")
ATTACK_TOOLS = re.compile(r"\b(sqlmap|nikto|hydra|metasploit|msfconsole|gobuster|ffuf|wfuzz)\b", re.I)
PRICE = re.compile(r"\$(\d+(?:\.\d+)?)")
FORBIDDEN_PRICES = {"39", "39.00", "39.95", "49", "59", "79", "99", "129"}
LEGAL = re.compile(r"\b(this (?:document|proposal) (?:is|constitutes) a (?:legally )?binding|legally binding agreement|guaranteed (?:results|rankings|revenue|conversions))\b", re.I)
PREDICTED_LIFT = re.compile(r"(?:will|should|can|could|expect(?:\s+a)?|projected?(?:\s+to)?|estimated?(?:\s+to)?)\s+(?:\w+\s+){0,3}?(?:increase|improve|boost|lift|raise|grow|reduce|cut)\s+(?:\w+\s+){0,3}?by\s+(?:approximately\s+|around\s+|about\s+|roughly\s+)?\d+(?:\.\d+)?\s*%", re.I)
NEGATION = re.compile(r"\b(?:not|never|no|nor|avoid|refuse|prohibit\w*|exclude\w*|without|instead of|rather than|cannot|can't|don't|doesn't|won't|stop|nothing|none)\b", re.I)
EXAMPLE_HOST = re.compile(r"https?://([a-z0-9.-]+)")
ALLOWED_EXAMPLE_HOSTS = re.compile(r"(\.example|\.invalid|\.test|localhost|schema\.org)$")
FAKE_TESTIMONIAL = re.compile(r'"[^"\n]{40,}"\s*[—–-]\s*(?:Dr|Mr|Ms|Mrs)?\s*[A-Z][a-z]+ [A-Z][a-z]+,?\s*(?:director|owner|CEO|founder)', re.I)
STDLIB = set(sys.stdlib_module_names) if hasattr(sys, "stdlib_module_names") else set()
IMPORT = re.compile(r"^\s*(?:from\s+([A-Za-z_][\w.]*)\s+import|import\s+([A-Za-z_][\w.]*))", re.M)


def negated(body, start):
    window = re.split(r"[.!?\n]", body[max(0, start - 160):start])[-1]
    if NEGATION.search(window):
        return True
    prev = body[max(0, start - 160):start].rsplit("\n", 2)
    return len(prev) > 1 and bool(NEGATION.search(prev[-2]))


def walk(root):
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in ("__pycache__", ".git") and (not d.startswith(".") or d == ".claude")]
        for fn in fns:
            yield os.path.join(dp, fn)


def check(root, run_scripts=True):
    bad = []
    if not os.path.isdir(root):
        return ["bundle directory missing: %s" % root]
    files = sorted(walk(root))
    rel = [os.path.relpath(f, root).replace(os.sep, "/") for f in files]
    known = set(rel)
    bodies = {}
    for f, r in zip(files, rel):
        base = os.path.basename(f)
        if base in FORBIDDEN_NAMES or base.startswith("._") or (base.startswith(".env") and base != ".env.example"):
            bad.append("must not ship: %s" % r)
        if base.endswith((".pyc", ".tmp", ".bak", ".orig", ".swp")):
            bad.append("temporary file: %s" % r)
        try:
            body = io.open(f, encoding="utf-8", newline="").read()
        except (UnicodeDecodeError, IOError):
            bad.append("unreadable or non-text file: %s" % r); continue
        bodies[r] = body
        if not body.strip():
            bad.append("empty file: %s" % r)
        if SECRET.search(body):
            bad.append("credential pattern in %s" % r)
        if PLAINTEXT_CRED.search(body) and r not in ("scripts/validate_client.py",):
            bad.append("%s: a plaintext credential field with a value" % r)
        if PRIVATE_HOSTS.search(body):
            bad.append("private store reference in %s" % r)
        if "\r\n" in body:
            bad.append("windows line endings in %s" % r)
        if ATTACK_TOOLS.search(body):
            bad.append("%s: mentions an attack tool" % r)
        for m in PRICE.finditer(body):
            if m.group(1) in FORBIDDEN_PRICES:
                bad.append("%s: forbidden price literal $%s" % (r, m.group(1)))
        if r.endswith(".md"):
            for m in PREDICTED_LIFT.finditer(body):
                if not negated(body, m.start()):
                    bad.append("%s: predicted percentage improvement: %r" % (r, m.group(0)))
            for m in LEGAL.finditer(body):
                if not negated(body, m.start()):
                    bad.append("%s: legal/guarantee language: %r" % (r, m.group(0)))
            if FAKE_TESTIMONIAL.search(body):
                bad.append("%s: looks like a written testimonial attributed to a person" % r)
        if r.startswith("examples/"):
            for m in EXAMPLE_HOST.finditer(body):
                if not ALLOWED_EXAMPLE_HOSTS.search(m.group(1)):
                    bad.append("%s: non-fictional host in the example: %s" % (r, m.group(1))); break
        if r.endswith(".csv"):
            try:
                rows = list(csv.DictReader(io.StringIO(body)))
                have = [(h or "").strip() for h in (rows[0].keys() if rows else body.splitlines()[0].split(","))]
                want = CSV_COLUMNS.get(base)
                if want and have != want:
                    bad.append("%s: columns %s, expected %s" % (r, have, want))
                for i, row in enumerate(rows, 2):
                    if None in row or any(v is None for v in row.values()):
                        bad.append("%s: row %d has the wrong number of fields" % (r, i)); break
            except csv.Error as e:
                bad.append("%s: CSV does not parse (%s)" % (r, e))
        elif r.endswith(".json"):
            try:
                json.loads(body)
            except ValueError as e:
                bad.append("%s: JSON does not parse (%s)" % (r, e))
        elif r.endswith((".yaml", ".yml")):
            for i, line in enumerate(body.splitlines(), 1):
                s = line.split("#")[0].rstrip()
                if "\t" in s:
                    bad.append("%s:%d: tab in YAML" % (r, i)); break
                if s and not s.startswith((" ", "- ")) and ":" not in s:
                    bad.append("%s:%d: not key: value" % (r, i)); break
            if re.search(r"(?im)^\s*(password|token|api_key|secret)\s*:\s*\S", body):
                bad.append("%s: a credential field in a config template" % r)

    for name in REQUIRED_FILES:
        if name not in known:
            bad.append("missing required file: %s" % name)
    for name in REQUIRED_CHECKLISTS:
        if "checklists/%s-checklist.md" % name not in known:
            bad.append("missing checklist: %s-checklist.md" % name)
    modules = sorted({r.split("/")[0] for r in rel if re.match(r"^\d{2}-", r)})
    if len(modules) != 21:
        bad.append("expected 21 numbered modules, found %d" % len(modules))
    for r in [x for x in rel if MODULE_DOC.match(x)]:
        body = bodies.get(r, "")
        for h in REQUIRED_SECTIONS:
            if h not in body:
                bad.append("%s: missing section %r" % (r, h))
        if not AUDIENCE.search(body):
            bad.append("%s: no audience declared" % r)
        if len(body.split()) < 300:
            bad.append("%s: only %d words, too thin to be useful" % (r, len(body.split())))
    for name in REQUIRED_COMMANDS:
        if ".claude/commands/%s.md" % name not in known:
            bad.append("missing command: %s" % name)
    cmd_files = [r for r in rel if r.startswith(".claude/commands/") and r != ".claude/commands/COMMANDS.md"]
    for r in cmd_files:
        body = bodies[r]; name = r.split("/")[-1][:-3]
        for h in COMMAND_SECTIONS:
            if h not in body:
                bad.append("%s: missing %r" % (r, h))
        if not COMMAND_AUD.search(body):
            bad.append("%s: no INTERNAL USE / CLIENT-FACING line" % r)
        if "# /%s" % name not in body:
            bad.append("%s: heading does not name the slash command" % r)
        for rule in COMMAND_RULES:
            if rule.lower() not in body.lower():
                bad.append("%s: business rule missing: %r" % (r, rule)); break
        for ref in re.findall(r"`((?:templates|checklists|worksheets|reference|scripts|examples)/[0-9A-Za-z_./-]+\.(?:md|csv|yaml|json|py))`", body):
            if ref not in known:
                bad.append("%s: references a file that does not exist: %s" % (r, ref))
    index = bodies.get(".claude/commands/COMMANDS.md", "")
    rows = re.findall(r"^\| `/([a-z-]+)` \|", index, re.M)
    for r in cmd_files:
        stem = r.split("/")[-1][:-3]
        if stem not in rows:
            bad.append("COMMANDS.md does not list /%s" % stem)
    if index and ("%d slash commands" % len(cmd_files)) not in index:
        bad.append("COMMANDS.md states a count that is not %d" % len(cmd_files))
    cm = bodies.get("templates/CLAUDE.md", "")
    for rule in RULES:
        if rule.lower() not in cm.lower():
            bad.append("templates/CLAUDE.md missing operating rule %r" % rule)
    if re.search(r"(?i)password|token", bodies.get("templates/access-inventory.md", "")) and re.search(r"(?im)^\|[^|]*\|[^|]*\|[^|]*\|\s*(?:Received|Requested)[^|]*\|[^|]*\|\s*[A-Za-z0-9]{12,}\s*\|", bodies.get("templates/access-inventory.md", "")):
        bad.append("templates/access-inventory.md stores a credential value")
    if "credential" not in bodies.get("templates/access-inventory.md", "").lower():
        bad.append("templates/access-inventory.md must say it holds no credentials")
    gi = bodies.get("templates/.gitignore", "")
    if not re.search(r"^\.env$", gi, re.M):
        bad.append("templates/.gitignore must ignore .env")
    for r in [x for x in rel if x.startswith("scripts/") and x.endswith(".py")]:
        body = bodies[r]; base = r.split("/")[-1]
        for m in IMPORT.finditer(body):
            mod = (m.group(1) or m.group(2)).split(".")[0]
            if mod in STDLIB or not STDLIB:
                continue
            bad.append("%s: non-standard-library import %r" % (r, mod))
        if 'if __name__ == "__main__"' not in body:
            bad.append("%s: not runnable" % r)
        if run_scripts:
            p = subprocess.run([sys.executable, os.path.join(root, r), "--help"], capture_output=True, text=True, timeout=30, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
            if p.returncode != 0 or "usage" not in (p.stdout + p.stderr).lower():
                bad.append("%s: --help failed (exit %d)" % (r, p.returncode))
    # the example must be internally consistent: same client name and project everywhere
    ex = "examples/example-client-project/"
    if ex + "client-config.yaml" in bodies:
        m = re.search(r"^\s+name: (.+)$", bodies[ex + "client-config.yaml"], re.M)
        client = m.group(1).strip() if m else ""
        for r in (ex + "proposal.md", ex + "project-scope.md", ex + "launch-report.md", ex + "client-handoff.md", ex + "README.md"):
            if r in bodies and client and client not in bodies[r]:
                bad.append("%s: does not name the example client %r" % (r, client))
        for r, body in bodies.items():
            if r.startswith(ex) and r.endswith(".md") and r != ex + "README.md":
                if re.search(r"\{[a-z][^}\n]{0,60}\}", body) and r not in (ex + "client-handoff.md", ex + "proposal.md"):
                    bad.append("%s: unfilled placeholder in the example" % r)
    # references to the bundle's own files must resolve; paths under the client project's phase
    # directories (01-discovery/ … 15-maintenance/) are outputs and are not checked here
    bundle_dirs = {r.split("/")[0] for r in rel if "/" in r}
    for r, body in bodies.items():
        if not r.endswith(".md"):
            continue
        here = os.path.dirname(r)
        resolve = lambda ref: os.path.normpath(os.path.join(here, ref)).replace(os.sep, "/")
        for ref in re.findall(r"`((?:[0-9]{2}-[a-z-]+|\.claude/commands|examples|templates|checklists|scripts|reference|reports|worksheets)/[0-9A-Za-z_./-]+\.(?:md|py|csv|json|yaml))`", body):
            top = ref.split("/")[0]
            if top not in bundle_dirs and top != ".claude":
                continue
            if resolve(ref) in known or ref in known:
                continue
            bad.append("%s: references a file that does not exist: %s" % (r, ref))
    return bad


def counts(root):
    files = sorted(walk(root))
    rel = [os.path.relpath(f, root).replace(os.sep, "/") for f in files]
    words = 0
    for f in files:
        try:
            words += len(io.open(f, encoding="utf-8").read().split())
        except (UnicodeDecodeError, IOError):
            pass
    return {"files": len(rel),
            "modules": len({r.split("/")[0] for r in rel if re.match(r"^\d{2}-", r)}),
            "docs": len([r for r in rel if re.match(r"^\d{2}-[a-z-]+/.*\.md$", r)]),
            "commands": len([r for r in rel if r.startswith(".claude/commands/") and r != ".claude/commands/COMMANDS.md"]),
            "scripts": len([r for r in rel if r.startswith("scripts/") and r.endswith(".py")]),
            "templates": len([r for r in rel if r.startswith("templates/") and not r.startswith("templates/client-project/") and r != "templates/README.md"]),
            "reports": len([r for r in rel if r.startswith("reports/") and r != "reports/README.md"]),
            "checklists": len([r for r in rel if r.startswith("checklists/") and r != "checklists/README.md"]),
            "worksheets": len([r for r in rel if r.startswith("worksheets/") and r != "worksheets/README.md"]),
            "examples": len([r for r in rel if r.startswith("examples/")]),
            "words": words}


def main():
    if "--self-test" in sys.argv:
        return self_test()
    bad = check(BUNDLE)
    for b in bad:
        print("  FAIL %s" % b)
    c = counts(BUNDLE)
    print("%d file(s), %d module(s), %d document(s), %d command(s), %d script(s), %d template(s), %d report template(s), %d checklist(s), %d worksheet(s), %d example file(s), %s words, %d failure(s)"
          % (c["files"], c["modules"], c["docs"], c["commands"], c["scripts"], c["templates"], c["reports"], c["checklists"], c["worksheets"], c["examples"], format(c["words"], ","), len(bad)))
    return 1 if bad else 0


def self_test():
    import shutil
    import tempfile
    tmp = tempfile.mkdtemp()
    root = os.path.join(tmp, "kit")
    shutil.copytree(BUNDLE, root)
    fails = 0
    write = lambda p, s: io.open(p, "w", encoding="utf-8").write(s)

    def run(name, mutate, restore=None, run_scripts=False):
        nonlocal fails
        mutate()
        ok = bool(check(root, run_scripts=run_scripts))
        print("  %s  detects: %s" % ("PASS" if ok else "FAIL", name))
        fails += 0 if ok else 1
        if restore:
            restore()

    assert not check(root, run_scripts=False), "bundle must be clean before the self-test: %s" % check(root, run_scripts=False)[:3]
    w = os.path.join(root, "05-project-scoping", "README.md")
    original = io.open(w, encoding="utf-8").read()
    restore = lambda: write(w, original)
    run("a module missing a required section", lambda: write(w, original.replace("## Common mistakes", "## Gotchas")), restore)
    run("a module with no audience declared", lambda: write(w, original.replace("**Audience:**", "Audience —")), restore)
    run("a credential pattern", lambda: write(w, original + "\ntoken shpat_" + "a" * 32 + "\n"), restore)
    run("a plaintext credential field", lambda: write(w, original + "\nPassword: hunter2hunter2\n"), restore)
    run("our private store hostname", lambda: write(w, original + "\nsee kjhvcj-yi.myshopify.com\n"), restore)
    for p in ("$39", "$39.00", "$39.95", "$49", "$59", "$79", "$99", "$129"):
        run("a forbidden price literal %s" % p, lambda p=p: write(w, original + "\nOnly %s.\n" % p), restore)
    run("an attack tool", lambda: write(w, original + "\nRun sqlmap first.\n"), restore)
    run("a predicted percentage improvement", lambda: write(w, original + "\nThis will increase conversions by 20%.\n"), restore)
    run("legal/guarantee language", lambda: write(w, original + "\nThis proposal is a legally binding agreement.\n"), restore)
    run("a written testimonial attributed to a person", lambda: write(w, original + '\n"They transformed our business and we could not be happier with the result" — Jane Smith, Director\n'), restore)
    run("windows line endings", lambda: write(w, original.replace("\n", "\r\n")), restore)
    run("an empty file", lambda: write(w, ""), restore)
    env = os.path.join(root, ".env")
    run("a .env file in the bundle", lambda: write(env, "TOKEN=x\n"), lambda: os.remove(env))
    c = os.path.join(root, ".claude", "commands", "generate-proposal.md"); orig_c = io.open(c).read()
    run("a command missing its audience line", lambda: write(c, orig_c.replace("> **CLIENT-FACING**", "> client")), lambda: write(c, orig_c))
    run("a command missing a section", lambda: write(c, orig_c.replace("## VALIDATION", "## CHECKS")), lambda: write(c, orig_c))
    run("a command missing a business rule", lambda: write(c, orig_c.replace("Never invent client facts", "Invent nothing")), lambda: write(c, orig_c))
    run("a command referencing a missing template", lambda: write(c, orig_c + "\nSee `templates/nope.md`.\n"), lambda: write(c, orig_c))
    run("a missing command", lambda: os.rename(c, c + ".x"), lambda: os.rename(c + ".x", c))
    idx = os.path.join(root, ".claude", "commands", "COMMANDS.md"); orig_idx = io.open(idx).read()
    run("an index count that is no longer true", lambda: write(idx, re.sub(r"\d+ slash commands", "99 slash commands", orig_idx)), lambda: write(idx, orig_idx))
    s = os.path.join(root, "scripts", "estimate.py"); orig_s = io.open(s).read()
    run("a third-party import", lambda: write(s, "import requests\n" + orig_s), lambda: write(s, orig_s))
    run("a script whose --help fails", lambda: write(s, orig_s.replace("import sys", "import sys\nraise SystemExit(4)", 1)), lambda: write(s, orig_s), run_scripts=True)
    run("a missing script", lambda: os.rename(s, s + ".x"), lambda: os.rename(s + ".x", s))
    cm = os.path.join(root, "templates", "CLAUDE.md"); orig_cm = io.open(cm).read()
    run("CLAUDE.md missing an operating rule", lambda: write(cm, orig_cm.replace("Flag scope creep", "Watch scope")), lambda: write(cm, orig_cm))
    ai = os.path.join(root, "templates", "access-inventory.md"); orig_ai = io.open(ai).read()
    run("an access inventory that does not disclaim credentials", lambda: write(ai, orig_ai.replace("credential", "detail")), lambda: write(ai, orig_ai))
    gi = os.path.join(root, "templates", ".gitignore"); orig_gi = io.open(gi).read()
    run(".gitignore that does not ignore .env", lambda: write(gi, orig_gi.replace(".env\n", "", 1)), lambda: write(gi, orig_gi))
    cfg = os.path.join(root, "templates", "client-config.yaml"); orig_cfg = io.open(cfg).read()
    run("a credential field in the config template", lambda: write(cfg, orig_cfg + "\nhosting:\n  password: hunter2\n"), lambda: write(cfg, orig_cfg))
    run("a YAML file that is not key: value", lambda: write(cfg, orig_cfg + "\nthis is not yaml\n"), lambda: write(cfg, orig_cfg))
    tr = os.path.join(root, "templates", "project-tracker.csv"); orig_tr = io.open(tr).read()
    run("a CSV with the wrong columns", lambda: write(tr, orig_tr.replace("client_blocked", "blocked")), lambda: write(tr, orig_tr))
    run("a CSV row with the wrong number of fields", lambda: write(tr, orig_tr + "only,three,fields\n"), lambda: write(tr, orig_tr))
    js = os.path.join(root, "templates", "project-status.json"); orig_js = io.open(js).read()
    run("a JSON file that does not parse", lambda: write(js, orig_js + "}"), lambda: write(js, orig_js))
    ex = os.path.join(root, "examples", "example-client-project", "launch-report.md"); orig_ex = io.open(ex).read()
    run("a real host in the example", lambda: write(ex, orig_ex.replace("harbourlinephysio.example", "harbourlinephysio.co.uk")), lambda: write(ex, orig_ex))
    run("an unfilled placeholder in the example", lambda: write(ex, orig_ex + "\n{owner}\n"), lambda: write(ex, orig_ex))
    run("an example file that does not name the client", lambda: write(ex, orig_ex.replace("Harbourline Physio", "Some Clinic")), lambda: write(ex, orig_ex))
    sh = os.path.join(root, "START-HERE.md"); orig_sh = io.open(sh).read()
    run("a reference to a file that does not exist", lambda: write(sh, orig_sh + "\nSee `05-project-scoping/NOPE.md`.\n"), lambda: write(sh, orig_sh))
    run("a missing required file", lambda: os.rename(sh, sh + ".x"), lambda: os.rename(sh + ".x", sh))
    ck = os.path.join(root, "checklists", "qa-checklist.md")
    run("a missing checklist", lambda: os.rename(ck, ck + ".x"), lambda: os.rename(ck + ".x", ck))
    art = os.path.join(root, ".DS_Store")
    run("a development artefact", lambda: write(art, "x"), lambda: os.remove(art))
    shutil.rmtree(tmp)
    print("self-test: %d failure(s)" % fails)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
