#!/usr/bin/env bash
#
# Build the distributable Shopify Automation & Admin API Toolkit archive.
#
#   ./scripts/build-ops-system.sh [version]
#
# Same shape as the other four product builds: validate, generate the
# manifest from the bundle itself, archive deterministically, verify the
# round-trip, publish the SHA-256 beside the download.
#
# Exits non-zero on any failure.

set -euo pipefail

VERSION="${1:-1.0}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUNDLE="$ROOT/product/Claude-Code-Shopify-Automation-Admin-API-Toolkit"
DIST="$ROOT/dist"
NAME="claude-code-shopify-automation-admin-api-toolkit-v${VERSION}.zip"
ARCHIVE="$DIST/$NAME"

say() { printf '\n\033[1m▸ %s\033[0m\n' "$1"; }
ok()  { printf '  \033[32m✓\033[0m %s\n' "$1"; }
die() { printf '  \033[31m✗ %s\033[0m\n' "$1"; exit 1; }

mkdir -p "$DIST"
find "$BUNDLE" -name "__pycache__" -type d -prune -exec rm -rf {} + 2>/dev/null || true

say "Validating the bundle"
python3 "$ROOT/scripts/validate-shopify-toolkit.py" || die "validation failed"
ok "bundle valid"

say "Generating PRODUCT-MANIFEST.md"
python3 - "$BUNDLE" "$VERSION" <<'PY' || die "manifest generation failed"
import hashlib, io, os, re, sys
bundle, version = sys.argv[1], sys.argv[2]
manifest = os.path.join(bundle, "PRODUCT-MANIFEST.md")
if os.path.exists(manifest):
    os.remove(manifest)   # never let a previous manifest count itself

files = []
for dp, dns, fns in os.walk(bundle):
    dns[:] = [d for d in dns if (not d.startswith(".") or d == ".claude") and d != "__pycache__"]
    for fn in sorted(fns):
        files.append(os.path.relpath(os.path.join(dp, fn), bundle).replace(os.sep, "/"))
files.sort()

words = 0
h = hashlib.sha256()
for r in files:
    raw = io.open(os.path.join(bundle, r), "rb").read()
    h.update(r.encode("utf-8")); h.update(raw)
    try:
        words += len(raw.decode("utf-8").split())
    except UnicodeDecodeError:
        pass
digest = h.hexdigest()

# Same definitions as scripts/validate-shopify-toolkit.py. If they drift, the
# product page quotes a number nothing counted.
MODULE_DOC = re.compile(r"^(0[1-9]|1[0-9])-[a-z-]+/[^/]+\.md$")
modules = sorted({r.split("/")[0] for r in files if re.match(r"^\d{2}-", r)})
docs = [r for r in files if MODULE_DOC.match(r)]
commands = [r for r in files if r.startswith(".claude/commands/") and r != ".claude/commands/COMMANDS.md"]
scripts = [r for r in files if r.startswith("scripts/") and r.endswith(".py") and not r.endswith("_lib.py")]
graphql = [r for r in files if r.startswith("graphql/") and r.endswith(".graphql")]
templates = [r for r in files if r.startswith("templates/")]
reports = [r for r in files if r.startswith("reports/")]
checklists = [r for r in files if r.startswith("checklists/") and r != "checklists/README.md"]
examples = [r for r in files if r.startswith("examples/") and r.endswith(".md") and r != "examples/README.md"]
automation = [r for r in files if r.startswith("examples/") and not r.endswith(".md")]

lines = [
  "# Product manifest", "",
  "**Claude Code Shopify Automation & Admin API Toolkit** — version %s" % version, "",
  "Generated at build time from the bundle itself. Every number here was",
  "counted, not typed.", "",
  "| | |", "| --- | --- |",
  "| Files | %d |" % len(files),
  "| Modules | %d |" % len(modules),
  "| Module documents | %d |" % len(docs),
  "| Claude Code commands | %d |" % len(commands),
  "| Scripts | %d |" % len(scripts),
  "| GraphQL documents | %d |" % len(graphql),
  "| Templates | %d |" % len(templates),
  "| Report templates | %d |" % len(reports),
  "| Checklists | %d |" % len(checklists),
  "| Worked examples | %d |" % len(examples),
  "| Automation samples | %d |" % len(automation),
  "| Words | %s |" % format(words, ","), "",
  "Content digest (SHA-256 over every file's path and contents, sorted):", "",
  "`%s`" % digest, "",
  "The archive's own SHA-256 is published alongside the download rather than",
  "here, because a file cannot contain its own hash.", "",
  "## Contents", "",
]
lines += ["- `%s`" % r for r in files] + [""]
io.open(manifest, "w", encoding="utf-8").write("\n".join(lines))
print("  files=%d modules=%d docs=%d commands=%d scripts=%d graphql=%d templates=%d reports=%d checklists=%d words=%s"
      % (len(files), len(modules), len(docs), len(commands), len(scripts), len(graphql), len(templates), len(reports), len(checklists), format(words, ",")))
PY
ok "manifest written"

say "Re-validating with the manifest present"
python3 "$ROOT/scripts/validate-shopify-toolkit.py" || die "validation failed after manifest"
ok "still valid"

if [ -f "$ARCHIVE" ]; then
  mv "$ARCHIVE" "$ARCHIVE.$(date -u +%Y%m%d%H%M%S).bak"
  ok "existing archive moved aside"
fi

find "$BUNDLE" -name "__pycache__" -type d -prune -exec rm -rf {} + 2>/dev/null || true

say "Creating the archive"
python3 "$ROOT/scripts/make-archive.py" "$BUNDLE" "$ARCHIVE" || die "archive creation failed"
ok "created $NAME"

say "Verifying the archive round-trips"
python3 "$ROOT/scripts/verify-archive.py" "$ARCHIVE" "$BUNDLE" || die "archive verification failed"
ok "archive verified"

say "Checking the archive for what must not be in it"
python3 - "$ARCHIVE" <<'PY' || die "archive content check failed"
import re, sys, zipfile
z = zipfile.ZipFile(sys.argv[1])
names = z.namelist()
bad = [n for n in names if "__pycache__" in n or n.endswith((".pyc", ".DS_Store")) or n.endswith("/.env") or ".env." in n and not n.endswith(".env.example")
       or (n.endswith(".jsonl") and "examples/" not in n)]
if bad:
    print("  unwanted entries:", bad); sys.exit(1)
secret = re.compile(rb"shp(at|ss|ca|pa|ut)_[0-9a-fA-F]{32}|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{36}|kjhvcj-yi\.myshopify\.com|site-builder-stack\.myshopify\.com")
for n in names:
    if secret.search(z.read(n)):
        print("  credential-shaped content in", n); sys.exit(1)
print("  %d entries, no artefacts, no credential patterns" % len(names))
PY
ok "archive clean"

say "Checksum"
( cd "$DIST" && sha256sum "$NAME" > "$NAME.sha256" )
SHA=$(cut -d' ' -f1 < "$ARCHIVE.sha256")
SIZE=$(stat -c%s "$ARCHIVE")
SIZE_H=$(numfmt --to=iec-i --suffix=B "$SIZE" 2>/dev/null || echo "${SIZE} bytes")
ok "SHA-256: $SHA"

printf '\n────────────────────────────────\n'
printf '  %s\n  %s (%s bytes)\n  %s\n' "$NAME" "$SIZE_H" "$SIZE" "$SHA"
printf '────────────────────────────────\n'
