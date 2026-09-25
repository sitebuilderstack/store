#!/usr/bin/env python3
"""Validate the Website Migration & Replatforming System before packaging.

Structural checks — required files, every module document in the promised
shape (mode line, Goal, Common mistakes), every command in the nine-section
shape with one of the three mode lines, every script runnable with --help
and standard-library only, the example project complete — plus the checks
that would embarrass this product in particular:

  * A credential, a `.env`, or our own store's private hostnames anywhere.
  * A real customer domain in the example (it must be fictional: .example).
  * The safety rules missing from CLAUDE.md or any command.
  * A homepage-dump redirect sample (every missing page → /).
  * A price literal for this product that is not $29.99, or any of the
    forbidden neighbours ($29, $29.00, $29.95, $39, $49, $59, $69).
  * A predicted percentage improvement or a guarantee of rankings/traffic.

Run with --self-test to prove every check fires.
"""
import io
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUNDLE = os.path.join(ROOT, "product", "Claude-Code-Website-Migration-Replatforming-System")

REQUIRED_FILES = ["START-HERE.md", "QUICK-START.md", "README.md", "LICENSE.md", "VERSION.md", "CHANGELOG.md",
                  "templates/migration-config.yaml", "templates/url-inventory.csv", "templates/url-map.csv", "templates/redirect-map.csv",
                  "templates/critical-pages.csv", "templates/content-inventory.csv", "templates/media-inventory.csv", "templates/dns-inventory.csv",
                  "templates/migration-risk-register.csv", "templates/launch-readiness.md", "templates/cutover-plan.md", "templates/CLAUDE.md",
                  "templates/redirects/nginx-redirects.conf", "templates/redirects/apache-redirects.htaccess", "templates/redirects/netlify-redirects",
                  "templates/redirects/vercel-redirects.json", "templates/redirects/shopify-redirects.csv",
                  ".claude/commands/COMMANDS.md", "scripts/README.md", "scripts/_common.py", "scripts/_inv.py",
                  "reports/migration-plan-template.md", "reports/pre-migration-audit.md", "reports/launch-readiness-report.md",
                  "reports/post-migration-report.md", "reports/executive-migration-summary.md", "reports/website-migration-audit.md",
                  "reference/migration-types.md", "reference/go-no-go-matrix.md", "reference/rollback-decision-matrix.md", "reference/monitoring-windows.md",
                  "reference/scorecard.md", "reference/troubleshooting.md", "reference/safety-rules.md",
                  "20-platform-guides/wordpress-to-astro.md", "20-platform-guides/wordpress-to-shopify.md", "20-platform-guides/wordpress-to-wordpress.md",
                  "20-platform-guides/shopify-replatforming.md", "20-platform-guides/static-html-to-astro.md", "20-platform-guides/domain-migration.md",
                  "20-platform-guides/url-structure-migration.md",
                  "examples/wordpress-to-astro/README.md", "examples/wordpress-to-astro/discovery-report.md", "examples/wordpress-to-astro/source-url-inventory.csv",
                  "examples/wordpress-to-astro/url-map.csv", "examples/wordpress-to-astro/redirect-map.csv", "examples/wordpress-to-astro/seo-baseline.csv",
                  "examples/wordpress-to-astro/target-url-inventory.csv", "examples/wordpress-to-astro/coverage-report.csv", "examples/wordpress-to-astro/launch-checklist.md",
                  "examples/wordpress-to-astro/post-migration-report.md", "examples/wordpress-to-astro/migration-audit.md"]
REQUIRED_CHECKLISTS = ["migration-discovery", "pre-migration", "content-migration", "seo-migration", "redirect", "staging", "dns-cutover", "launch",
                       "post-launch", "rollback", "24-hour", "7-day", "30-day"]
REQUIRED_COMMANDS = ["migration-discovery", "migration-plan", "url-inventory", "target-url-inventory", "url-map", "url-coverage", "content-inventory",
                     "media-inventory", "seo-baseline", "analytics-baseline", "metadata-compare", "schema-compare", "internal-link-audit", "redirect-map",
                     "redirect-validation", "staging-validation", "performance-baseline", "performance-compare", "dns-inventory", "cutover-plan",
                     "pre-launch-check", "migration-cutover", "post-migration-audit", "critical-page-validation", "old-domain-scan", "tracking-validation",
                     "rollback-readiness", "migration-report", "website-migration-audit", "migration-go-no-go", "media-validation", "form-validation"]
COMMAND_SECTIONS = ["## Purpose", "## Mode", "## Inputs", "## Preconditions", "## Safety rules", "## Steps", "## Expected output", "## Validation", "## Rollback"]
COMMAND_MODE = re.compile(r"^> \*\*MODE: (READ ONLY|MODIFIES FILES|PRODUCTION IMPACT POSSIBLE)\*\*", re.M)
REQUIRED_SCRIPTS = ["crawl_site.py", "compare_urls.py", "test_redirects.py", "compare_metadata.py", "find_old_domain_refs.py", "validate_sitemap.py",
                    "check_robots.py", "check_canonicals.py", "html_to_markdown.py", "normalize_content.py", "content_inventory.py", "slug_mapper.py",
                    "validate_frontmatter.py", "generate_redirects.py", "url_map.py", "schema_compare.py", "internal_link_audit.py", "seo_baseline.py",
                    "media_inventory.py", "tracking_check.py", "performance_baseline.py", "dns_inventory.py", "critical_pages.py", "merge_inventories.py",
                    "migration_audit.py", "migration_plan.py", "rollback_readiness.py", "staging_validation.py"]
SAFETY_RULES = ["Never destroy the source before target validation", "Never change DNS without recording current DNS", "Never delete redirects without review",
                "Never assume old URLs have no value", "Never redirect every missing page to the homepage",
                "Never assume a successful deployment means a successful migration", "Never launch without rollback preparation",
                "Never leave production accidentally noindexed", "Never leave production canonicali", "Never expose credentials or secrets"]
EXTRA_RULE = "Never treat a website migration as permission to overwrite unrelated mail or DNS records"
SCORECARD_LINES = ["URL Coverage", "Redirect Integrity", "Metadata Preservation", "Canonical Integrity", "Internal Links", "Media Integrity", "Analytics", "Forms", "Critical Pages", "Overall Migration Health"]

MODULE_DOC = re.compile(r"^(0[1-9]|1[0-9]|20)-[a-z-]+/README\.md$")
GUIDE_DOC = re.compile(r"^20-platform-guides/(?!README)[a-z-]+\.md$")
REQUIRED_SECTIONS = ["## Goal", "## Common mistakes"]
MODE = re.compile(r"^\*\*Mode:\*\* (READ ONLY|MODIFIES FILES|PRODUCTION IMPACT POSSIBLE|varies)", re.M)

FORBIDDEN_NAMES = (".DS_Store", "Thumbs.db", ".gitkeep", "__MACOSX", ".env")
SECRET = re.compile(r"shp(?:at|ss|ca|pa|ut)_[0-9a-fA-F]{32}|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{36}|-----BEGIN [A-Z ]*PRIVATE KEY-----|xox[bap]-[0-9A-Za-z-]{10,}|sk_live_[0-9A-Za-z]{16,}")
PRIVATE_HOSTS = re.compile(r"kjhvcj-yi\.myshopify\.com|site-builder-stack\.myshopify\.com|/opt/shopify-(client-id|secret)|SBS_TOKEN_CACHE|shopify_api\.py|sitebuilderstack\.com/admin")
ATTACK_TOOLS = re.compile(r"\b(sqlmap|nikto|hydra|metasploit|msfconsole|gobuster|ffuf|wfuzz)\b", re.I)
PRICE = re.compile(r"\$(\d+(?:\.\d+)?)")
FORBIDDEN_PRICES = {"29", "29.00", "29.95", "39", "49", "59", "69"}
PREDICTED_LIFT = re.compile(
    r"(?:will|should|can|could|expect(?:\s+a)?|projected?(?:\s+to)?|estimated?(?:\s+to)?)\s+(?:\w+\s+){0,3}?"
    r"(?:increase|improve|boost|lift|raise|grow|reduce|cut)\s+(?:\w+\s+){0,3}?"
    r"by\s+(?:approximately\s+|around\s+|about\s+|roughly\s+)?\d+(?:\.\d+)?\s*%", re.I)
GUARANTEE = re.compile(r"\bguarantee[sd]?\s+(?:\w+\s+){0,3}?(?:rankings?|traffic|revenue|no\s+(?:traffic|ranking)\s+loss)", re.I)
NEGATION = re.compile(r"\b(?:not|never|no|nor|avoid|refuse|prohibit\w*|exclude\w*|without|instead of|rather than|cannot|can't|don't|doesn't|won't|stop|nothing|none)\b", re.I)
# the example must be fictional: any real-looking host that is not .example / .invalid / localhost is a leak
EXAMPLE_HOST = re.compile(r"https?://([a-z0-9.-]+)")
ALLOWED_EXAMPLE_HOSTS = re.compile(r"(\.example|\.invalid|\.test|localhost|127\.0\.0\.1|schema\.org|www\.w3\.org|sitemaps\.org|netlify\.app|googletagmanager\.com|www\.googletagmanager\.com|fonts\.googleapis\.com)$")
STDLIB = set(sys.stdlib_module_names) if hasattr(sys, "stdlib_module_names") else set()
IMPORT = re.compile(r"^\s*(?:from\s+([A-Za-z_][\w.]*)\s+import|import\s+([A-Za-z_][\w.]*))", re.M)
LOCAL_MODULES = {"_common", "_inv"}


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
        if base in FORBIDDEN_NAMES or base.startswith("._") or base.startswith(".env"):
            bad.append("must not ship: %s" % r)
        if base.endswith((".pyc", ".tmp", ".bak", ".orig", ".swp")):
            bad.append("temporary file: %s" % r)
        try:
            body = io.open(f, encoding="utf-8", newline="").read()
        except (UnicodeDecodeError, IOError):
            bad.append("unreadable or non-text file: %s" % r); continue
        bodies[r] = body
        if SECRET.search(body):
            bad.append("credential pattern in %s" % r)
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
            for m in GUARANTEE.finditer(body):
                if not negated(body, m.start()):
                    bad.append("%s: promises a ranking/traffic guarantee: %r" % (r, m.group(0)))
        if r.startswith("examples/"):
            for m in EXAMPLE_HOST.finditer(body):
                if not ALLOWED_EXAMPLE_HOSTS.search(m.group(1)):
                    bad.append("%s: non-fictional host in the example: %s" % (r, m.group(1))); break

    for name in REQUIRED_FILES:
        if name not in known:
            bad.append("missing required file: %s" % name)
    for name in REQUIRED_CHECKLISTS:
        if "checklists/%s-checklist.md" % name not in known:
            bad.append("missing checklist: %s-checklist.md" % name)

    modules = sorted({r.split("/")[0] for r in rel if re.match(r"^\d{2}-", r)})
    if len(modules) != 20:
        bad.append("expected 20 numbered modules, found %d" % len(modules))
    for r in [x for x in rel if MODULE_DOC.match(x)]:
        body = bodies.get(r, "")
        for h in REQUIRED_SECTIONS:
            if h not in body:
                bad.append("%s: missing section %r" % (r, h))
        if not MODE.search(body):
            bad.append("%s: no mode declared" % r)
        if len(body.split()) < 300:
            bad.append("%s: only %d words, too thin to be useful" % (r, len(body.split())))
    for r in [x for x in rel if GUIDE_DOC.match(x)]:
        body = bodies.get(r, "")
        for h in ("## What changes", "## AUTOMATABLE / SEMI-AUTOMATABLE / MANUAL here", "## What always breaks"):
            if h not in body and not (h.startswith("## What changes") and r.endswith(("shopify-replatforming.md",))):
                bad.append("%s: missing section %r" % (r, h))
        if len(body.split()) < 400:
            bad.append("%s: only %d words" % (r, len(body.split())))

    for name in REQUIRED_COMMANDS:
        r = ".claude/commands/%s.md" % name
        if r not in known:
            bad.append("missing command: %s" % r)
    cmd_files = [r for r in rel if r.startswith(".claude/commands/") and r != ".claude/commands/COMMANDS.md"]
    for r in cmd_files:
        body = bodies[r]; name = r.split("/")[-1][:-3]
        for h in COMMAND_SECTIONS:
            if h not in body:
                bad.append("%s: missing %r" % (r, h))
        if not COMMAND_MODE.search(body):
            bad.append("%s: no READ ONLY / MODIFIES FILES / PRODUCTION IMPACT POSSIBLE mode line" % r)
        if "# /%s" % name not in body:
            bad.append("%s: heading does not name the slash command" % r)
        for rule in SAFETY_RULES:
            if rule.lower() not in body.lower():
                bad.append("%s: safety rule missing: %r" % (r, rule)); break
    index = bodies.get(".claude/commands/COMMANDS.md", "")
    rows = re.findall(r"^\| `/([a-z-]+)` \|", index, re.M)
    for r in cmd_files:
        stem = r.split("/")[-1][:-3]
        if stem not in rows:
            bad.append("COMMANDS.md does not list /%s" % stem)
    if index and ("%d slash commands" % len(cmd_files)) not in index:
        bad.append("COMMANDS.md states a count that is not %d" % len(cmd_files))

    for name in REQUIRED_SCRIPTS:
        if "scripts/%s" % name not in known:
            bad.append("missing script: scripts/%s" % name)
    for r in [x for x in rel if x.startswith("scripts/") and x.endswith(".py")]:
        body = bodies[r]; base = r.split("/")[-1]
        for m in IMPORT.finditer(body):
            mod = (m.group(1) or m.group(2)).split(".")[0]
            if mod in LOCAL_MODULES or mod in STDLIB or not STDLIB:
                continue
            bad.append("%s: non-standard-library import %r" % (r, mod))
        if not base.startswith("_") and 'if __name__ == "__main__"' not in body:
            bad.append("%s: not runnable" % r)
        if run_scripts and not base.startswith("_"):
            p = subprocess.run([sys.executable, os.path.join(root, r), "--help"], capture_output=True, text=True, timeout=30,
                               env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
            if p.returncode != 0 or "usage" not in (p.stdout + p.stderr).lower():
                bad.append("%s: --help failed (exit %d)" % (r, p.returncode))
    if "scripts/generate_redirects.py" in bodies and "homepage" not in bodies["scripts/generate_redirects.py"].lower():
        bad.append("generate_redirects.py must guard against the homepage dump")

    cm = bodies.get("templates/CLAUDE.md", "")
    for rule in SAFETY_RULES + [EXTRA_RULE]:
        if rule.lower() not in cm.lower():
            bad.append("templates/CLAUDE.md missing safety rule %r" % rule)
    sr = bodies.get("reference/safety-rules.md", "")
    if sr and EXTRA_RULE.lower() not in sr.lower():
        bad.append("reference/safety-rules.md missing the mail/DNS rule")
    rm = bodies.get("templates/redirect-map.csv", "")
    if rm:
        rows_ = [l.split(",") for l in rm.strip().split("\n")[1:] if l.strip()]
        if rows_ and sum(1 for x in rows_ if len(x) > 1 and x[1].strip() == "/") > len(rows_) / 2:
            bad.append("templates/redirect-map.csv redirects most rows to the homepage")
    cfg = bodies.get("templates/migration-config.yaml", "")
    for k in ("source:", "target:", "rollback:", "critical_pages:", "analytics:"):
        if k not in cfg:
            bad.append("templates/migration-config.yaml missing %s" % k)
    if re.search(r"(password|token|api_key|secret)\s*:\s*\S", cfg, re.I):
        bad.append("templates/migration-config.yaml carries a credential field")
    audit = bodies.get("reports/website-migration-audit.md", "")
    for line in SCORECARD_LINES + ["LAUNCH RECOMMENDATION", "GO WITH WARNINGS", "NO-GO"]:
        if line not in audit:
            bad.append("reports/website-migration-audit.md missing %r" % line)
    for r in ("examples/wordpress-to-astro/migration-audit.md",):
        body = bodies.get(r, "")
        if body and ("Overall Migration Health:" not in body or "LAUNCH RECOMMENDATION" not in body):
            bad.append("%s: not in the master audit shape" % r)
    for r, body in bodies.items():
        if r.endswith(".md") and r.startswith("examples/") and re.search(r"\{[a-z][^}]*\}", body) and r != "examples/wordpress-to-astro/README.md":
            if r.endswith(("post-migration-report.md", "discovery-report.md", "launch-checklist.md", "cutover-log.md")):
                bad.append("%s: unfilled placeholder in a completed example document" % r)

    for r, body in bodies.items():
        if not r.endswith(".md"):
            continue
        here = os.path.dirname(r)
        resolve = lambda ref: os.path.normpath(os.path.join(here, ref)).replace(os.sep, "/")
        for ref in re.findall(r"`((?:[0-9]{2}-[a-z-]+|\.claude/commands|examples|templates|checklists|scripts|reference|reports)/[0-9A-Za-z_./-]+\.(?:md|py|yml|txt|csv|json|yaml|conf|htaccess))`", body):
            if resolve(ref) in known or ref in known:
                continue
            if ref.startswith("reports/") and not ref.endswith("-template.md"):
                continue  # reports/<name>.md is the user's output unless it is a template shipped here
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
            "guides": len([r for r in rel if GUIDE_DOC.match(r)]),
            "commands": len([r for r in rel if r.startswith(".claude/commands/") and r != ".claude/commands/COMMANDS.md"]),
            "scripts": len([r for r in rel if r.startswith("scripts/") and r.endswith(".py") and not r.split("/")[-1].startswith("_")]),
            "templates": len([r for r in rel if r.startswith("templates/") and not r.endswith("README.md")]),
            "reports": len([r for r in rel if r.startswith("reports/") and r != "reports/README.md"]),
            "checklists": len([r for r in rel if r.startswith("checklists/") and r != "checklists/README.md"]),
            "examples": len([r for r in rel if r.startswith("examples/")]),
            "words": words}


def main():
    if "--self-test" in sys.argv:
        return self_test()
    bad = check(BUNDLE)
    for b in bad:
        print("  FAIL %s" % b)
    c = counts(BUNDLE)
    print("%d file(s), %d module(s), %d document(s), %d platform guide(s), %d command(s), %d script(s), %d template(s), %d report template(s), "
          "%d checklist(s), %d example file(s), %s words, %d failure(s)"
          % (c["files"], c["modules"], c["docs"], c["guides"], c["commands"], c["scripts"], c["templates"], c["reports"], c["checklists"], c["examples"], format(c["words"], ","), len(bad)))
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
    w = os.path.join(root, "12-redirects", "README.md")
    original = io.open(w, encoding="utf-8").read()
    restore = lambda: write(w, original)
    run("a module missing a required section", lambda: write(w, original.replace("## Common mistakes", "## Gotchas")), restore)
    run("a module with no mode declared", lambda: write(w, original.replace("**Mode:** MODIFIES FILES", "Mode: writes")), restore)
    run("a credential pattern", lambda: write(w, original + "\ntoken shpat_" + "a" * 32 + "\n"), restore)
    run("our private store hostname", lambda: write(w, original + "\nsee kjhvcj-yi.myshopify.com\n"), restore)
    for p in ("$29", "$29.00", "$29.95", "$39", "$49", "$59", "$69"):
        run("a forbidden price literal %s" % p, lambda p=p: write(w, original + "\nOnly %s.\n" % p), restore)
    run("an attack tool", lambda: write(w, original + "\nRun sqlmap first.\n"), restore)
    run("a predicted percentage improvement", lambda: write(w, original + "\nThis will increase traffic by 20%.\n"), restore)
    run("a ranking guarantee", lambda: write(w, original + "\nWe guarantee your rankings survive.\n"), restore)
    run("windows line endings", lambda: write(w, original.replace("\n", "\r\n")), restore)
    env = os.path.join(root, ".env")
    run("a .env file in the bundle", lambda: write(env, "TOKEN=x\n"), lambda: os.remove(env))
    c = os.path.join(root, ".claude", "commands", "migration-cutover.md"); orig_c = io.open(c).read()
    run("a command missing its mode line", lambda: write(c, orig_c.replace("> **MODE: PRODUCTION IMPACT POSSIBLE**", "> production")), lambda: write(c, orig_c))
    run("a command missing a section", lambda: write(c, orig_c.replace("## Rollback", "## Undo")), lambda: write(c, orig_c))
    run("a command missing a safety rule", lambda: write(c, orig_c.replace("Never change DNS without recording current DNS", "Record DNS")), lambda: write(c, orig_c))
    run("a missing command", lambda: os.rename(c, c + ".x"), lambda: os.rename(c + ".x", c))
    idx = os.path.join(root, ".claude", "commands", "COMMANDS.md"); orig_idx = io.open(idx).read()
    run("an index count that is no longer true", lambda: write(idx, re.sub(r"\d+ slash commands", "99 slash commands", orig_idx)), lambda: write(idx, orig_idx))
    s = os.path.join(root, "scripts", "test_redirects.py"); orig_s = io.open(s).read()
    run("a third-party import", lambda: write(s, "import requests\n" + orig_s), lambda: write(s, orig_s))
    run("a script whose --help fails", lambda: write(s, orig_s.replace("import sys", "import sys\nraise SystemExit(4)", 1)), lambda: write(s, orig_s), run_scripts=True)
    run("a missing script", lambda: os.rename(s, s + ".x"), lambda: os.rename(s + ".x", s))
    g = os.path.join(root, "scripts", "generate_redirects.py"); orig_g = io.open(g).read()
    run("a redirect generator without the homepage guard", lambda: write(g, orig_g.replace("homepage", "root").replace("Homepage", "Root")), lambda: write(g, orig_g))
    cm = os.path.join(root, "templates", "CLAUDE.md"); orig_cm = io.open(cm).read()
    run("CLAUDE.md missing a safety rule", lambda: write(cm, orig_cm.replace("Never redirect every missing page to the homepage", "Redirect carefully")), lambda: write(cm, orig_cm))
    run("CLAUDE.md missing the mail/DNS rule", lambda: write(cm, orig_cm.replace("Never treat a website migration", "Treat a migration")), lambda: write(cm, orig_cm))
    rm = os.path.join(root, "templates", "redirect-map.csv"); orig_rm = io.open(rm).read()
    run("a homepage-dump redirect sample", lambda: write(rm, "source_path,target_path,status\n/a,/,301\n/b,/,301\n/c,/,301\n"), lambda: write(rm, orig_rm))
    cfg = os.path.join(root, "templates", "migration-config.yaml"); orig_cfg = io.open(cfg).read()
    run("a credential field in the config template", lambda: write(cfg, orig_cfg + "\nhosting:\n  password: hunter2\n"), lambda: write(cfg, orig_cfg))
    run("a config template without a rollback block", lambda: write(cfg, orig_cfg.replace("rollback:", "undo:")), lambda: write(cfg, orig_cfg))
    ex = os.path.join(root, "examples", "wordpress-to-astro", "url-map.csv"); orig_ex = io.open(ex).read()
    run("a real host in the example", lambda: write(ex, orig_ex.replace("northwindsupply.example", "northwindsupply.co.uk")), lambda: write(ex, orig_ex))
    rep = os.path.join(root, "examples", "wordpress-to-astro", "post-migration-report.md"); orig_rep = io.open(rep).read()
    run("an unfilled placeholder in the example report", lambda: write(rep, orig_rep + "\n{owner}\n"), lambda: write(rep, orig_rep))
    au = os.path.join(root, "reports", "website-migration-audit.md"); orig_au = io.open(au).read()
    run("the master audit shape missing a scorecard line", lambda: write(au, orig_au.replace("Canonical Integrity", "Canonicals")), lambda: write(au, orig_au))
    sh = os.path.join(root, "START-HERE.md"); orig_sh = io.open(sh).read()
    run("a reference to a file that does not exist", lambda: write(sh, orig_sh + "\nSee `12-redirects/NOPE.md`.\n"), lambda: write(sh, orig_sh))
    run("a missing required file", lambda: os.rename(sh, sh + ".x"), lambda: os.rename(sh + ".x", sh))
    ck = os.path.join(root, "checklists", "rollback-checklist.md")
    run("a missing checklist", lambda: os.rename(ck, ck + ".x"), lambda: os.rename(ck + ".x", ck))
    pg = os.path.join(root, "20-platform-guides", "domain-migration.md"); orig_pg = io.open(pg).read()
    run("a platform guide missing 'What always breaks'", lambda: write(pg, orig_pg.replace("## What always breaks", "## Gotchas")), lambda: write(pg, orig_pg))
    art = os.path.join(root, ".DS_Store")
    run("a development artefact", lambda: write(art, "x"), lambda: os.remove(art))
    shutil.rmtree(tmp)
    print("self-test: %d failure(s)" % fails)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
