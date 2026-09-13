#!/usr/bin/env python3
"""Validate the Website Operations & Maintenance System before packaging.

Structural checks (required files, every module documented in the shape the
README promises, every command in the seven-section shape, every script
runnable with --help) plus the checks that would embarrass this product in
particular:

  * A credential, or anything that looks like one, anywhere in the bundle.
    The product's own rule is "never expose secrets"; shipping one would be
    the product contradicting itself. Also our own store's private hostnames.
  * A recommendation to run an attack tool. The security module is explicit
    that it is hygiene, not penetration testing; a file that tells the reader
    to run sqlmap would be the thing the product exists to refuse.
  * A third-party import in a script. The scripts promise "standard library
    only, nothing to install"; one `import requests` breaks that promise on
    every customer's machine.
  * A predicted percentage improvement. Same rule as the other products.

Run with --self-test to prove every check fires.
"""
import io
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUNDLE = os.path.join(ROOT, "product", "Claude-Code-Website-Operations-Maintenance-System")

REQUIRED_FILES = ["START-HERE.md", "QUICK-START.md", "README.md", "LICENSE.md",
                  "VERSION.md", "CHANGELOG.md", "templates/CLAUDE.md",
                  "templates/ops-config.yml", "templates/endpoints.txt",
                  "templates/baseline.json", "commands/COMMANDS.md"]

# The command library the product page and README promise. Every name here is
# a file in commands/ and a slash command a buyer will type.
REQUIRED_COMMANDS = [
    "website-health-check", "security-check", "dependency-audit", "check-backups",
    "performance-check", "performance-regression", "seo-maintenance-check",
    "link-check", "redirect-audit", "check-forms", "check-critical-flows",
    "pre-deploy-check", "post-deploy-check", "log-analysis", "incident-diagnose",
    "monthly-maintenance", "generate-maintenance-report",
    "website-operations-audit", "update-plan",
]
COMMAND_SECTIONS = ["## Purpose", "## Preconditions", "## Inputs", "## Steps",
                    "## Safety rules", "## Output format", "## Validation"]

REQUIRED_SCRIPTS = ["check_http.py", "check_ssl.py", "check_dns.py", "crawl_links.py",
                    "audit_redirects.py", "check_headers.py", "validate_sitemap.py",
                    "test_endpoints.py", "compare_baseline.py", "generate_report.py"]

REQUIRED_CHECKLISTS = ["DAILY", "WEEKLY", "MONTHLY", "QUARTERLY", "PRE-DEPLOYMENT",
                       "POST-DEPLOYMENT", "INCIDENT", "SECURITY", "BACKUP"]
REQUIRED_REPORTS = ["MONTHLY-MAINTENANCE-REPORT", "EXECUTIVE-HEALTH-REPORT", "SECURITY-REPORT",
                    "INCIDENT-REPORT", "PERFORMANCE-REPORT", "SEO-MAINTENANCE-REPORT",
                    "BACKUP-REPORT", "EXECUTIVE-SUMMARY"]
REQUIRED_PLATFORMS = ["SHOPIFY", "WORDPRESS", "ASTRO-STATIC", "NODEJS"]
CLAUDE_MD_FIELDS = ["SITE_NAME", "SITE_URL", "STAGING_URL", "SITE_TYPE", "REPOSITORY",
                    "DEPLOYMENT_PROVIDER", "DNS_PROVIDER", "HOSTING_PROVIDER",
                    "ANALYTICS_PROVIDER", "IMPORTANT_URLS", "CRITICAL_FORMS", "CRITICAL_FLOWS"]

# A module document is a Markdown file in one of the numbered modules 01-17.
# The build script counts them with the same definition.
MODULE_DOC = re.compile(r"^(0[1-9]|1[0-7])-[a-z-]+/[^/]+\.md$")
# Fill-in templates and indexes are not workflow documents.
NOT_WORKFLOWS_PREFIX = ("15-reporting/",)
NOT_WORKFLOWS = {"15-reporting/README.md"}
REQUIRED_SECTIONS = ["## Goal", "## Common mistakes"]
MODE = re.compile(r"^> \*\*Mode: (AUDIT|PLAN|IMPLEMENT|VALIDATE|SETUP|REFERENCE)", re.M)

FORBIDDEN_NAMES = (".DS_Store", "Thumbs.db", ".gitkeep", "__MACOSX")
SECRET = re.compile(
    r"AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{36}|shp(at|ss|ca|pa)_[0-9a-fA-F]{32}"
    r"|AIza[0-9A-Za-z_-]{35}|-----BEGIN [A-Z ]*PRIVATE KEY-----"
    r"|xox[bap]-[0-9A-Za-z-]{10,}|sk_live_[0-9A-Za-z]{16,}")
# Our own store's private hostnames and tokens never belong in a customer file.
PRIVATE_HOSTS = re.compile(r"[a-z0-9-]+\.myshopify\.com|SHOPIFY_ADMIN_TOKEN|shopify_api\.py", re.I)
ATTACK_TOOLS = re.compile(r"\b(sqlmap|nikto|hydra|metasploit|msfconsole|burp ?suite|wpscan --enumerate|nmap -s[SUVT]|gobuster|dirbuster|ffuf|wfuzz)\b", re.I)
PREDICTED_LIFT = re.compile(
    r"(?:will|should|can|could|expect(?:\s+a)?|projected?(?:\s+to)?|estimated?(?:\s+to)?)\s+(?:\w+\s+){0,3}?"
    r"(?:increase|improve|boost|lift|raise|grow|reduce|cut)\s+(?:\w+\s+){0,3}?"
    r"by\s+(?:approximately\s+|around\s+|about\s+|roughly\s+)?\d+(?:\.\d+)?\s*%", re.I)
NEGATION = re.compile(r"\b(?:not|never|no|nor|avoid|refuse|prohibit\w*|exclude\w*|without|instead of|rather than|cannot|can't|don't|doesn't|won't|stop)\b", re.I)

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
        dns[:] = [d for d in dns if not d.startswith(".") and d != "__pycache__"]
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
        if base in FORBIDDEN_NAMES or base.startswith("._"):
            bad.append("development artefact: %s" % r)
        if base.endswith((".pyc", ".tmp", ".bak", ".orig", ".swp")) or "__pycache__" in r:
            bad.append("temporary file: %s" % r)
        try:
            body = io.open(f, encoding="utf-8", newline="").read()
        except (UnicodeDecodeError, IOError):
            bad.append("unreadable or non-text file: %s" % r)
            continue
        bodies[r] = body
        if SECRET.search(body):
            bad.append("credential pattern in %s" % r)
        if PRIVATE_HOSTS.search(body):
            bad.append("private store reference in %s" % r)
        if "\r\n" in body:
            bad.append("windows line endings in %s" % r)
        for m in ATTACK_TOOLS.finditer(body):
            if not negated(body, m.start()):
                bad.append("%s: recommends an attack tool: %r" % (r, m.group(0)))
        if r.endswith(".md"):
            for m in PREDICTED_LIFT.finditer(body):
                if not negated(body, m.start()):
                    bad.append("%s: predicted percentage improvement: %r" % (r, m.group(0)))

    for name in REQUIRED_FILES:
        if name not in known:
            bad.append("missing required file: %s" % name)

    # Modules: 17 numbered directories, every document in the promised shape.
    modules = sorted({r.split("/")[0] for r in rel if re.match(r"^\d{2}-", r)})
    if len(modules) != 17:
        bad.append("expected 17 numbered modules, found %d" % len(modules))
    docs = [r for r in rel if MODULE_DOC.match(r)]
    for r in docs:
        if r in NOT_WORKFLOWS or r.startswith(NOT_WORKFLOWS_PREFIX):
            continue
        body = bodies.get(r, "")
        for h in REQUIRED_SECTIONS:
            if h not in body:
                bad.append("%s: missing section %r" % (r, h))
        if not MODE.search(body):
            bad.append("%s: no mode declared" % r)
        if len(body.split()) < 400:
            bad.append("%s: only %d words, too thin to be useful" % (r, len(body.split())))

    # Commands: every promised name, every section, and an index that agrees.
    for name in REQUIRED_COMMANDS:
        r = "commands/%s.md" % name
        if r not in known:
            bad.append("missing command: %s" % r)
            continue
        body = bodies.get(r, "")
        for h in COMMAND_SECTIONS:
            if h not in body:
                bad.append("%s: missing section %r" % (r, h))
        if "# /%s" % name not in body:
            bad.append("%s: heading does not name the slash command" % r)
    cmd_files = [r for r in rel if r.startswith("commands/") and r != "commands/COMMANDS.md"]
    index = bodies.get("commands/COMMANDS.md", "")
    index_rows = re.findall(r"^\| `/([a-z-]+)` \|", index, re.M)
    for name in cmd_files:
        stem = name[len("commands/"):-3]
        if stem not in index_rows:
            bad.append("commands/COMMANDS.md does not list /%s" % stem)
    for stem in index_rows:
        if "commands/%s.md" % stem not in known:
            bad.append("commands/COMMANDS.md lists /%s which does not exist" % stem)
    words = {19: "Nineteen", 18: "Eighteen", 20: "Twenty", 17: "Seventeen"}
    if index and words.get(len(cmd_files), str(len(cmd_files))) not in index.split("\n", 3)[2]:
        bad.append("commands/COMMANDS.md states a count that is not %d" % len(cmd_files))

    # Scripts: promised names present, stdlib only, --help exits 0.
    for name in REQUIRED_SCRIPTS:
        if "scripts/%s" % name not in known:
            bad.append("missing script: scripts/%s" % name)
    for r in [x for x in rel if x.startswith("scripts/") and x.endswith(".py")]:
        body = bodies.get(r, "")
        for m in IMPORT.finditer(body):
            mod = (m.group(1) or m.group(2)).split(".")[0]
            if mod == "_common" or mod in STDLIB or not STDLIB:
                continue
            bad.append("%s: non-standard-library import %r" % (r, mod))
        if r != "scripts/_common.py" and 'if __name__ == "__main__"' not in body:
            bad.append("%s: not runnable as a script" % r)
        if run_scripts and r != "scripts/_common.py":
            p = subprocess.run([sys.executable, os.path.join(root, r), "--help"],
                               capture_output=True, text=True, timeout=30,
                               env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
            if p.returncode != 0 or "usage" not in (p.stdout + p.stderr).lower():
                bad.append("%s: --help failed (exit %d)" % (r, p.returncode))

    for name in REQUIRED_CHECKLISTS:
        if "checklists/%s.md" % name not in known:
            bad.append("missing checklist: checklists/%s.md" % name)
    for name in REQUIRED_REPORTS:
        if "15-reporting/%s.md" % name not in known:
            bad.append("missing report template: 15-reporting/%s.md" % name)
    for name in REQUIRED_PLATFORMS:
        if "17-platforms/%s.md" % name not in known:
            bad.append("missing platform guide: 17-platforms/%s.md" % name)
    cm = bodies.get("templates/CLAUDE.md", "")
    for field in CLAUDE_MD_FIELDS:
        if field + ":" not in cm:
            bad.append("templates/CLAUDE.md missing field %s" % field)
    for name in ("16-automation/run-checks.sh", "16-automation/crontab.sample",
                 "16-automation/github/site-health.yml"):
        if name not in known:
            bad.append("missing automation sample: %s" % name)

    # Internal references resolve.
    dirs = {os.path.dirname(r) + "/" for r in rel if os.path.dirname(r)}
    external = {"CLAUDE.md", "ops/RESTORE.md", "ops/CHANGE-LOG.md", "ops/flows/<name>.md",
                "ops/reports/YYYY-MM-monthly.md", "ops/top-pages.txt"}
    for r, body in bodies.items():
        if not r.endswith(".md"):
            continue
        here = os.path.dirname(r)
        resolve = lambda ref: os.path.normpath(os.path.join(here, ref)).replace(os.sep, "/")
        for ref in re.findall(r"`((?:[0-9]{2}-[a-z-]+|commands|examples|templates|checklists|scripts)/[0-9A-Za-z_./<>-]+\.(?:md|py|yml|txt|csv|json|sh|sample))`", body):
            if ref in external or "<" in ref:
                continue
            if resolve(ref) not in known and ref not in known:
                bad.append("%s: references a file that does not exist: %s" % (r, ref))
        for ref in re.findall(r"`((?:[0-9]{2}-[a-z-]+|commands|examples|templates|checklists|scripts)/)`", body):
            if ref not in dirs and resolve(ref).rstrip("/") + "/" not in dirs:
                bad.append("%s: references a directory that does not exist: %s" % (r, ref))
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
    return {
        "files": len(rel),
        "modules": len({r.split("/")[0] for r in rel if re.match(r"^\d{2}-", r)}),
        "docs": len([r for r in rel if MODULE_DOC.match(r)]),
        "commands": len([r for r in rel if r.startswith("commands/") and r != "commands/COMMANDS.md"]),
        "scripts": len([r for r in rel if r.startswith("scripts/") and r.endswith(".py") and not r.endswith("_common.py")]),
        "checklists": len([r for r in rel if r.startswith("checklists/") and r != "checklists/README.md"]),
        "reports": len([r for r in rel if r.startswith("15-reporting/") and r != "15-reporting/README.md"]),
        "platforms": len([r for r in rel if r.startswith("17-platforms/")]),
        "examples": len([r for r in rel if r.startswith("examples/") and r != "examples/README.md"]),
        "words": words,
    }


def main():
    if "--self-test" in sys.argv:
        return self_test()
    bad = check(BUNDLE)
    for b in bad:
        print("  FAIL %s" % b)
    c = counts(BUNDLE)
    print("%d file(s), %d module(s), %d document(s), %d command(s), %d script(s), %d checklist(s), "
          "%d report template(s), %d platform guide(s), %d example(s), %s words, %d failure(s)"
          % (c["files"], c["modules"], c["docs"], c["commands"], c["scripts"], c["checklists"],
             c["reports"], c["platforms"], c["examples"], format(c["words"], ","), len(bad)))
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

    assert not check(root, run_scripts=False), "bundle must be clean before the self-test"
    w = os.path.join(root, "02-website-health", "WEBSITE-HEALTH-CHECK.md")
    original = io.open(w, encoding="utf-8").read()
    restore = lambda: write(w, original)
    run("a module missing a required section", lambda: write(w, original.replace("## Common mistakes", "## Gotchas")), restore)
    run("a module with no mode declared", lambda: write(w, original.replace("> **Mode: AUDIT**", "Analysis only.")), restore)
    run("a module too thin to be useful", lambda: write(w, "# x\n\n> **Mode: AUDIT**\n\n## Goal\n\n## Common mistakes\n"), restore)
    run("a credential pattern", lambda: write(w, original + "\ntoken shpat_" + "a" * 32 + "\n"), restore)
    run("a private store hostname", lambda: write(w, original + "\nsee example-store.myshopify.com\n"), restore)
    run("a recommended attack tool", lambda: write(w, original + "\nRun sqlmap against the login form.\n"), restore)
    run("a predicted percentage improvement", lambda: write(w, original + "\nThis will reduce load time by 40%.\n"), restore)
    run("a prohibition later contradicted", lambda: write(w, original + "\nNever run nikto here.\n" + ("filler " * 60) + "\n\nNow run nikto on the site.\n"), restore)

    c = os.path.join(root, "commands", "link-check.md")
    orig_c = io.open(c, encoding="utf-8").read()
    run("a command missing a section", lambda: write(c, orig_c.replace("## Safety rules", "## Rules")), lambda: write(c, orig_c))
    run("a missing command", lambda: os.rename(c, c + ".moved"), lambda: os.rename(c + ".moved", c))
    idx = os.path.join(root, "commands", "COMMANDS.md")
    orig_idx = io.open(idx, encoding="utf-8").read()
    run("an index count that is no longer true", lambda: write(idx, orig_idx.replace("Nineteen", "Twenty-two")), lambda: write(idx, orig_idx))
    run("an index row for a command that does not exist", lambda: write(idx, orig_idx + "\n| `/nope` | x | `x` | never |\n"), lambda: write(idx, orig_idx))

    s = os.path.join(root, "scripts", "check_dns.py")
    orig_s = io.open(s, encoding="utf-8").read()
    run("a third-party import in a script", lambda: write(s, "import requests\n" + orig_s), lambda: write(s, orig_s))
    run("a script whose --help fails", lambda: write(s, orig_s.replace("import argparse", "import argparse\nraise SystemExit(4)")), lambda: write(s, orig_s), run_scripts=True)
    run("a missing script", lambda: os.rename(s, s + ".moved"), lambda: os.rename(s + ".moved", s))

    cl = os.path.join(root, "checklists", "DAILY.md")
    run("a missing checklist", lambda: os.rename(cl, cl + ".moved"), lambda: os.rename(cl + ".moved", cl))
    cm = os.path.join(root, "templates", "CLAUDE.md")
    orig_cm = io.open(cm, encoding="utf-8").read()
    run("a CLAUDE.md template missing a field", lambda: write(cm, orig_cm.replace("CRITICAL_FLOWS:", "FLOWS:")), lambda: write(cm, orig_cm))
    sh = os.path.join(root, "START-HERE.md")
    orig_sh = io.open(sh, encoding="utf-8").read()
    run("a reference to a file that does not exist", lambda: write(sh, orig_sh + "\nSee `02-website-health/NOPE.md`.\n"), lambda: write(sh, orig_sh))
    run("a reference to a directory that does not exist", lambda: write(sh, orig_sh + "\nSee `99-nope/`.\n"), lambda: write(sh, orig_sh))
    run("a missing required file", lambda: os.rename(sh, sh + ".moved"), lambda: os.rename(sh + ".moved", sh))
    art = os.path.join(root, ".DS_Store")
    run("a development artefact", lambda: write(art, "x"), lambda: os.remove(art))
    run("windows line endings", lambda: write(w, original.replace("\n", "\r\n")), restore)

    shutil.rmtree(tmp)
    print("self-test: %d failure(s)" % fails)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
