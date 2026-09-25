#!/usr/bin/env python3
"""Validate the Shopify Automation & Admin API Toolkit before packaging.

Structural checks — required files, every module document in the promised
shape, every command in the eight-section shape with a mode line, every
script runnable with --help, every GraphQL document taking variables — plus
the checks that would embarrass this product in particular:

  * A credential, a `.env`, or our own store's private hostnames anywhere in
    the bundle. The product's first rule is that tokens never leave `.env`.
  * A third-party import in a script ("standard library only").
  * A write script without the write guard (--confirm / --limit / dry run).
  * A REST Admin API call in a script or document (the product is GraphQL-first;
    REST may be mentioned, never used).
  * A price literal for this product that is not $39.99, or any of the
    forbidden neighbours.

Run with --self-test to prove every check fires.
"""
import io
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUNDLE = os.path.join(ROOT, "product", "Claude-Code-Shopify-Automation-Admin-API-Toolkit")

REQUIRED_FILES = ["START-HERE.md", "QUICK-START.md", "README.md", "LICENSE.md", "VERSION.md", "CHANGELOG.md",
                  "templates/.env.example", "templates/.gitignore", "templates/CLAUDE.md", "templates/product.yaml",
                  "templates/products.csv", "templates/product-seo.csv", "templates/metafields.csv", "templates/redirects.csv",
                  ".claude/commands/COMMANDS.md", "graphql/README.md", "scripts/README.md", "scripts/shopify_client.py",
                  "reference/api-version-upgrade.md", "reference/scopes.md", "reference/troubleshooting.md",
                  "examples/github-actions/shopify-weekly-audit.yml"]
REQUIRED_COMMANDS = ["shopify-connection-check", "shopify-store-discovery", "shopify-store-audit",
                     "shopify-product-audit", "shopify-product-export", "shopify-product-create", "shopify-product-update", "shopify-product-bulk-update",
                     "shopify-variant-audit", "shopify-sku-audit", "shopify-collection-audit", "shopify-collection-create", "shopify-collection-update",
                     "shopify-metafield-audit", "shopify-metafield-export", "shopify-metafield-update", "shopify-metaobject-audit",
                     "shopify-media-audit", "shopify-alt-text-audit", "shopify-seo-audit", "shopify-product-seo-audit", "shopify-collection-seo-audit",
                     "shopify-seo-export", "shopify-seo-import", "shopify-seo-update", "shopify-inventory-audit", "shopify-pricing-audit",
                     "shopify-redirect-audit", "shopify-redirect-create", "shopify-redirect-import",
                     "shopify-bulk-export", "shopify-bulk-import", "shopify-bulk-status", "shopify-bulk-cancel"]
COMMAND_SECTIONS = ["## Purpose", "## Inputs", "## Preconditions", "## Steps", "## Safety rules", "## Expected output", "## Validation", "**Required access:**"]
COMMAND_MODE = re.compile(r"^> \*\*MODE: (READ ONLY|WRITES TO SHOPIFY — REQUIRES EXPLICIT CONFIRMATION|STOPS A RUNNING JOB — REQUIRES EXPLICIT CONFIRMATION)\*\*", re.M)
REQUIRED_SCRIPTS = ["shopify_client.py", "connection_check.py", "store_discovery.py", "product_export.py", "product_audit.py", "product_create.py",
                    "product_update.py", "variant_audit.py", "pricing_audit.py", "collection_audit.py", "collection_write.py", "metafield_export.py",
                    "metafield_update.py", "metaobject_audit.py", "media_audit.py", "alt_text_update.py", "seo_audit.py", "seo_export.py", "seo_import.py",
                    "inventory_audit.py", "redirect_audit.py", "redirect_import.py", "bulk_query.py", "bulk_status.py", "bulk_cancel.py", "bulk_mutation.py",
                    "jsonl_to_csv.py", "csv_to_jsonl.py", "jsonl_summary.py", "jsonl_validate.py", "validate_graphql.py", "store_audit.py"]
WRITE_SCRIPTS = ["product_create.py", "product_update.py", "collection_write.py", "metafield_update.py", "alt_text_update.py", "seo_import.py", "redirect_import.py", "bulk_mutation.py"]
REQUIRED_GRAPHQL = ["shop", "products", "product-by-handle", "collections", "metafields", "metaobjects", "inventory", "product-update", "collection-update", "bulk-products"]
CLAUDE_MD_KEYS = ["STORE_NAME=", "SHOPIFY_STORE_DOMAIN=", "SHOPIFY_API_VERSION=", "DEFAULT_OPERATION_MODE=READ_ONLY"]
CLAUDE_MD_RULES = ["Default to read-only", "Never expose access tokens", "Never commit credentials", "Preview all writes", "Do not delete products",
                   "Do not modify prices", "Do not modify inventory quantities", "Do not publish or unpublish", "Export affected data before bulk writes",
                   "Validate every mutation by reading the resource back", "Report Shopify `userErrors`", "Stop bulk operations if unexpected scope or volume"]

MODULE_DOC = re.compile(r"^(0[1-9]|1[0-9])-[a-z-]+/[^/]+\.md$")
REQUIRED_SECTIONS = ["## Goal", "## Common mistakes"]
MODE = re.compile(r"^> \*\*Mode: (READ ONLY|WRITES TO SHOPIFY|SETUP|REFERENCE)", re.M)

FORBIDDEN_NAMES = (".DS_Store", "Thumbs.db", ".gitkeep", "__MACOSX", ".env")
SECRET = re.compile(r"shp(?:at|ss|ca|pa|ut)_[0-9a-fA-F]{32}|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{36}|-----BEGIN [A-Z ]*PRIVATE KEY-----|xox[bap]-[0-9A-Za-z-]{10,}")
PRIVATE_HOSTS = re.compile(r"kjhvcj-yi\.myshopify\.com|site-builder-stack\.myshopify\.com|/opt/shopify-(client-id|secret)|SBS_TOKEN_CACHE|shopify_api\.py")
REST_CALL = re.compile(r"/admin/api/[\d-]+/(products|collections|variants|metafields|redirects|inventory_levels)[\w/]*\.json")
ATTACK_TOOLS = re.compile(r"\b(sqlmap|nikto|hydra|metasploit|msfconsole|gobuster|ffuf|wfuzz)\b", re.I)
PRICE = re.compile(r"\$(\d+(?:\.\d+)?)")
# A predicted percentage improvement. The toolkit never promises a lift; neither may its listing.
PREDICTED_LIFT = re.compile(
    r"(?:will|should|can|could|expect(?:\s+a)?|projected?(?:\s+to)?|estimated?(?:\s+to)?)\s+(?:\w+\s+){0,3}?"
    r"(?:increase|improve|boost|lift|raise|grow|reduce|cut)\s+(?:\w+\s+){0,3}?"
    r"by\s+(?:approximately\s+|around\s+|about\s+|roughly\s+)?\d+(?:\.\d+)?\s*%", re.I)
NEGATION = re.compile(r"\b(?:not|never|no|nor|avoid|refuse|prohibit\w*|exclude\w*|without|instead of|rather than|cannot|can't|don't|doesn't|won't|stop)\b", re.I)


def negated(body, start):
    window = re.split(r"[.!?\n]", body[max(0, start - 160):start])[-1]
    if NEGATION.search(window):
        return True
    prev = body[max(0, start - 160):start].rsplit("\n", 2)
    return len(prev) > 1 and bool(NEGATION.search(prev[-2]))
FORBIDDEN_PRICES = {"39", "39.00", "39.95", "49", "59", "69", "79"}
STDLIB = set(sys.stdlib_module_names) if hasattr(sys, "stdlib_module_names") else set()
IMPORT = re.compile(r"^\s*(?:from\s+([A-Za-z_][\w.]*)\s+import|import\s+([A-Za-z_][\w.]*))", re.M)
LOCAL_MODULES = {"_lib", "shopify_client", "bulk_query", "redirect_audit", "product_audit", "seo_audit", "media_audit", "variant_audit",
                 "pricing_audit", "collection_audit", "inventory_audit"}


def walk(root):
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in ("__pycache__", ".git") and not d.startswith(".") or d == ".claude"]
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
        if base.endswith((".pyc", ".tmp", ".bak", ".orig", ".swp", ".jsonl")) and "examples" not in r:
            bad.append("temporary or data file: %s" % r)
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
        if r.endswith((".py", ".graphql")) and REST_CALL.search(body):
            bad.append("%s: uses the REST Admin API" % r)
        for m in PRICE.finditer(body):
            if m.group(1) in FORBIDDEN_PRICES:
                bad.append("%s: forbidden price literal $%s" % (r, m.group(1)))
        if r.endswith(".md"):
            for m in PREDICTED_LIFT.finditer(body):
                if not negated(body, m.start()):
                    bad.append("%s: predicted percentage improvement: %r" % (r, m.group(0)))

    for name in REQUIRED_FILES:
        if name not in known:
            bad.append("missing required file: %s" % name)
    if "templates/.env.example" in bodies:
        ex = bodies["templates/.env.example"]
        if not re.search(r"^SHOPIFY_ADMIN_ACCESS_TOKEN=\s*$", ex, re.M):
            bad.append("templates/.env.example must leave SHOPIFY_ADMIN_ACCESS_TOKEN empty")
        for k in ("SHOPIFY_STORE_DOMAIN=", "SHOPIFY_API_VERSION="):
            if k not in ex:
                bad.append("templates/.env.example missing %s" % k)
    if "templates/.gitignore" in bodies and not re.search(r"^\.env$", bodies["templates/.gitignore"], re.M):
        bad.append("templates/.gitignore must ignore .env")

    modules = sorted({r.split("/")[0] for r in rel if re.match(r"^\d{2}-", r)})
    if len(modules) != 19:
        bad.append("expected 19 numbered modules, found %d" % len(modules))
    for r in [x for x in rel if MODULE_DOC.match(x)]:
        body = bodies.get(r, "")
        for h in REQUIRED_SECTIONS:
            if h not in body:
                bad.append("%s: missing section %r" % (r, h))
        if not MODE.search(body):
            bad.append("%s: no mode declared" % r)
        if len(body.split()) < 300:
            bad.append("%s: only %d words, too thin to be useful" % (r, len(body.split())))

    for name in REQUIRED_COMMANDS:
        r = ".claude/commands/%s.md" % name
        if r not in known:
            bad.append("missing command: %s" % r); continue
        body = bodies[r]
        for h in COMMAND_SECTIONS:
            if h not in body:
                bad.append("%s: missing %r" % (r, h))
        if not COMMAND_MODE.search(body):
            bad.append("%s: no READ ONLY / WRITES TO SHOPIFY mode line" % r)
        if "# /%s" % name not in body:
            bad.append("%s: heading does not name the slash command" % r)
    cmd_files = [r for r in rel if r.startswith(".claude/commands/") and r != ".claude/commands/COMMANDS.md"]
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
        body = bodies[r]
        for m in IMPORT.finditer(body):
            mod = (m.group(1) or m.group(2)).split(".")[0]
            if mod in LOCAL_MODULES or mod in STDLIB or not STDLIB:
                continue
            bad.append("%s: non-standard-library import %r" % (r, mod))
        base = r.split("/")[-1]
        if base in WRITE_SCRIPTS:
            if "write=True" not in body or "write_mode(" not in body:
                bad.append("%s: write script without the write guard" % r)
            if "WRITES with --confirm" not in body:
                bad.append("%s: docstring does not say it writes" % r)
        if base != "_lib.py" and 'if __name__ == "__main__"' not in body:
            bad.append("%s: not runnable" % r)
        if run_scripts and base != "_lib.py":
            p = subprocess.run([sys.executable, os.path.join(root, r), "--help"], capture_output=True, text=True, timeout=30,
                               env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
            if p.returncode != 0 or "usage" not in (p.stdout + p.stderr).lower():
                bad.append("%s: --help failed (exit %d)" % (r, p.returncode))
    if "scripts/shopify_client.py" in bodies:
        versions = re.findall(r'DEFAULT_API_VERSION = "(\d{4}-\d{2})"', bodies["scripts/shopify_client.py"])
        if len(versions) != 1:
            bad.append("shopify_client.py must define DEFAULT_API_VERSION exactly once")
        for r in [x for x in rel if x.startswith("scripts/") and x.endswith(".py") and x != "scripts/shopify_client.py"]:
            if re.search(r"/admin/api/\d{4}-\d{2}/", bodies[r]):
                bad.append("%s: hard-codes an API version; the client owns it" % r)

    for name in REQUIRED_GRAPHQL:
        r = "graphql/%s.graphql" % name
        if r not in known:
            bad.append("missing GraphQL document: %s" % r); continue
        body = re.sub(r"#.*", "", bodies[r])
        if re.search(r'\b(handle|id|query):\s*"', body) and "bulk-products" not in r:
            bad.append("%s: interpolated literal where a variable belongs" % r)
    cm = bodies.get("templates/CLAUDE.md", "")
    for k in CLAUDE_MD_KEYS:
        if k not in cm:
            bad.append("templates/CLAUDE.md missing %s" % k)
    for rule in CLAUDE_MD_RULES:
        if rule not in cm:
            bad.append("templates/CLAUDE.md missing operating rule %r" % rule)
    for r, body in bodies.items():
        if r.startswith(("examples/github-actions/", "examples/cron/")) and re.search(r"SHOPIFY_ADMIN_ACCESS_TOKEN\s*[:=]\s*['\"]?shp", body):
            bad.append("%s: a token in an automation sample" % r)

    dirs = {os.path.dirname(r) + "/" for r in rel if os.path.dirname(r)}
    external = {"CLAUDE.md", "changes/", "exports/", "backups/", "reports/"}
    for r, body in bodies.items():
        if not r.endswith(".md"):
            continue
        here = os.path.dirname(r)
        resolve = lambda ref: os.path.normpath(os.path.join(here, ref)).replace(os.sep, "/")
        for ref in re.findall(r"`((?:[0-9]{2}-[a-z-]+|\.claude/commands|examples|templates|checklists|scripts|graphql|reference|reports)/[0-9A-Za-z_./<>-]+\.(?:md|py|yml|txt|csv|json|graphql|yaml|cron|example))`", body):
            if "<" in ref or ref.split("/")[0] in ("reports", "changes", "exports", "backups") and ref not in known and resolve(ref) not in known:
                # reports/*.md are the toolkit's templates only when they exist; other reports/… paths are user output
                if ref.startswith("reports/") and (ref in known or resolve(ref) in known):
                    continue
                if ref.split("/")[0] == "reports" and not ref.endswith("-template.md") and ref != "reports/bulk-operation-report.md":
                    continue
            if resolve(ref) not in known and ref not in known and "<" not in ref and not ref.startswith(("changes/", "exports/", "backups/")):
                if ref.startswith("reports/") and not (ref.endswith("-template.md") or ref == "reports/bulk-operation-report.md"):
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
            "docs": len([r for r in rel if MODULE_DOC.match(r)]),
            "commands": len([r for r in rel if r.startswith(".claude/commands/") and r != ".claude/commands/COMMANDS.md"]),
            "scripts": len([r for r in rel if r.startswith("scripts/") and r.endswith(".py") and not r.endswith("_lib.py")]),
            "graphql": len([r for r in rel if r.startswith("graphql/") and r.endswith(".graphql")]),
            "templates": len([r for r in rel if r.startswith("templates/")]),
            "reports": len([r for r in rel if r.startswith("reports/")]),
            "checklists": len([r for r in rel if r.startswith("checklists/") and r != "checklists/README.md"]),
            "examples": len([r for r in rel if r.startswith("examples/") and r.endswith(".md") and r != "examples/README.md"]),
            "words": words}


def main():
    if "--self-test" in sys.argv:
        return self_test()
    bad = check(BUNDLE)
    for b in bad:
        print("  FAIL %s" % b)
    c = counts(BUNDLE)
    print("%d file(s), %d module(s), %d document(s), %d command(s), %d script(s), %d GraphQL document(s), %d template(s), "
          "%d report template(s), %d checklist(s), %d example(s), %s words, %d failure(s)"
          % (c["files"], c["modules"], c["docs"], c["commands"], c["scripts"], c["graphql"], c["templates"], c["reports"],
             c["checklists"], c["examples"], format(c["words"], ","), len(bad)))
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
    w = os.path.join(root, "04-products", "PRODUCT-AUDIT.md")
    original = io.open(w, encoding="utf-8").read()
    restore = lambda: write(w, original)
    run("a module missing a required section", lambda: write(w, original.replace("## Common mistakes", "## Gotchas")), restore)
    run("a module with no mode declared", lambda: write(w, original.replace("> **Mode: READ ONLY**", "Analysis only.")), restore)
    run("a credential pattern", lambda: write(w, original + "\ntoken shpat_" + "a" * 32 + "\n"), restore)
    run("our private store hostname", lambda: write(w, original + "\nsee kjhvcj-yi.myshopify.com\n"), restore)
    run("a forbidden price literal", lambda: write(w, original + "\nOnly $39.95.\n"), restore)
    run("an attack tool", lambda: write(w, original + "\nRun sqlmap first.\n"), restore)
    run("a predicted percentage improvement", lambda: write(w, original + "\nThis will increase sales by 20%.\n"), restore)
    env = os.path.join(root, ".env")
    run("a .env file in the bundle", lambda: write(env, "SHOPIFY_ADMIN_ACCESS_TOKEN=x\n"), lambda: os.remove(env))
    ex = os.path.join(root, "templates", ".env.example"); orig_ex = io.open(ex).read()
    run("a token value in .env.example", lambda: write(ex, orig_ex.replace("SHOPIFY_ADMIN_ACCESS_TOKEN=", "SHOPIFY_ADMIN_ACCESS_TOKEN=abc")), lambda: write(ex, orig_ex))
    gi = os.path.join(root, "templates", ".gitignore"); orig_gi = io.open(gi).read()
    run(".gitignore that does not ignore .env", lambda: write(gi, orig_gi.replace(".env\n", "", 1)), lambda: write(gi, orig_gi))
    c = os.path.join(root, ".claude", "commands", "shopify-seo-import.md"); orig_c = io.open(c).read()
    run("a command missing its mode line", lambda: write(c, orig_c.replace("> **MODE: WRITES TO SHOPIFY — REQUIRES EXPLICIT CONFIRMATION**", "> writes")), lambda: write(c, orig_c))
    run("a command missing a section", lambda: write(c, orig_c.replace("## Safety rules", "## Rules")), lambda: write(c, orig_c))
    run("a missing command", lambda: os.rename(c, c + ".x"), lambda: os.rename(c + ".x", c))
    idx = os.path.join(root, ".claude", "commands", "COMMANDS.md"); orig_idx = io.open(idx).read()
    run("an index count that is no longer true", lambda: write(idx, orig_idx.replace("34 slash commands", "40 slash commands")), lambda: write(idx, orig_idx))
    s = os.path.join(root, "scripts", "product_update.py"); orig_s = io.open(s).read()
    run("a third-party import", lambda: write(s, "import requests\n" + orig_s), lambda: write(s, orig_s))
    run("a write script without the write guard", lambda: write(s, orig_s.replace("write=True", "write=False").replace("write_mode(", "wm(")), lambda: write(s, orig_s))
    run("a REST Admin API call", lambda: write(s, orig_s + "\nURL = 'https://x.myshopify.com/admin/api/2026-07/products.json'\n"), lambda: write(s, orig_s))
    run("a hard-coded API version outside the client", lambda: write(s, orig_s + "\nU = '/admin/api/2026-07/graphql.json'\n"), lambda: write(s, orig_s))
    run("a script whose --help fails", lambda: write(s, orig_s.replace("import sys", "import sys\nraise SystemExit(4)", 1)), lambda: write(s, orig_s), run_scripts=True)
    run("a missing script", lambda: os.rename(s, s + ".x"), lambda: os.rename(s + ".x", s))
    cl = os.path.join(root, "scripts", "shopify_client.py"); orig_cl = io.open(cl).read()
    run("two API version constants", lambda: write(cl, orig_cl + '\nDEFAULT_API_VERSION = "2025-10"\n'), lambda: write(cl, orig_cl))
    g = os.path.join(root, "graphql", "product-by-handle.graphql"); orig_g = io.open(g).read()
    run("a GraphQL document with an interpolated literal", lambda: write(g, orig_g.replace("handle: $handle", 'handle: "x"')), lambda: write(g, orig_g))
    run("a missing GraphQL document", lambda: os.rename(g, g + ".x"), lambda: os.rename(g + ".x", g))
    cm = os.path.join(root, "templates", "CLAUDE.md"); orig_cm = io.open(cm).read()
    run("CLAUDE.md missing an operating rule", lambda: write(cm, orig_cm.replace("Do not modify prices", "Prices")), lambda: write(cm, orig_cm))
    gh = os.path.join(root, "examples", "github-actions", "shopify-weekly-audit.yml"); orig_gh = io.open(gh).read()
    run("a token in the Actions sample", lambda: write(gh, orig_gh + "\n      SHOPIFY_ADMIN_ACCESS_TOKEN: shpat_abc\n"), lambda: write(gh, orig_gh))
    sh = os.path.join(root, "START-HERE.md"); orig_sh = io.open(sh).read()
    run("a reference to a file that does not exist", lambda: write(sh, orig_sh + "\nSee `04-products/NOPE.md`.\n"), lambda: write(sh, orig_sh))
    run("a missing required file", lambda: os.rename(sh, sh + ".x"), lambda: os.rename(sh + ".x", sh))
    art = os.path.join(root, ".DS_Store")
    run("a development artefact", lambda: write(art, "x"), lambda: os.remove(art))
    run("windows line endings", lambda: write(w, original.replace("\n", "\r\n")), restore)
    shutil.rmtree(tmp)
    print("self-test: %d failure(s)" % fails)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
