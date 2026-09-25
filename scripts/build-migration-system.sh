#!/usr/bin/env bash
#
# Build the distributable Website Migration & Replatforming System archive.
#
#   ./scripts/build-migration-system.sh [version]
#
# Same shape as the other five product builds: validate, generate the
# manifest from the bundle itself, archive deterministically, verify the
# round-trip, publish the SHA-256 beside the download.
#
# Exits non-zero on any failure.

set -euo pipefail

VERSION="${1:-1.0}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUNDLE="$ROOT/product/Claude-Code-Website-Migration-Replatforming-System"
DIST="$ROOT/dist"
NAME="claude-code-website-migration-replatforming-system-v${VERSION}.zip"
ARCHIVE="$DIST/$NAME"

say() { printf '\n\033[1m▸ %s\033[0m\n' "$1"; }
ok()  { printf '  \033[32m✓\033[0m %s\n' "$1"; }
die() { printf '  \033[31m✗ %s\033[0m\n' "$1"; exit 1; }

mkdir -p "$DIST"
find "$BUNDLE" -name "__pycache__" -type d -prune -exec rm -rf {} + 2>/dev/null || true

say "Validating the bundle"
python3 "$ROOT/scripts/validate-migration-system.py" || die "validation failed"
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

# Same definitions as scripts/validate-migration-system.py. If they drift, the
# product page quotes a number nothing counted.
GUIDE_DOC = re.compile(r"^20-platform-guides/(?!README)[a-z-]+\.md$")
modules = sorted({r.split("/")[0] for r in files if re.match(r"^\d{2}-", r)})
docs = [r for r in files if re.match(r"^\d{2}-[a-z-]+/.*\.md$", r)]
guides = [r for r in files if GUIDE_DOC.match(r)]
commands = [r for r in files if r.startswith(".claude/commands/") and r != ".claude/commands/COMMANDS.md"]
scripts = [r for r in files if r.startswith("scripts/") and r.endswith(".py") and not r.split("/")[-1].startswith("_")]
templates = [r for r in files if r.startswith("templates/") and not r.endswith("README.md")]
reports = [r for r in files if r.startswith("reports/") and r != "reports/README.md"]
checklists = [r for r in files if r.startswith("checklists/") and r != "checklists/README.md"]
examples = [r for r in files if r.startswith("examples/")]

lines = [
  "# Product manifest", "",
  "**Claude Code Website Migration & Replatforming System** — version %s" % version, "",
  "Generated at build time from the bundle itself. Every number here was",
  "counted, not typed.", "",
  "| | |", "| --- | --- |",
  "| Files | %d |" % len(files),
  "| Modules | %d |" % len(modules),
  "| Module documents | %d |" % len(docs),
  "| Platform guides | %d |" % len(guides),
  "| Claude Code commands | %d |" % len(commands),
  "| Scripts | %d |" % len(scripts),
  "| Templates | %d |" % len(templates),
  "| Report templates | %d |" % len(reports),
  "| Checklists | %d |" % len(checklists),
  "| Example files | %d |" % len(examples),
  "| Words | %s |" % format(words, ","), "",
  "Content digest (SHA-256 over every file's path and contents, sorted):", "",
  "`%s`" % digest, "",
  "The archive's own SHA-256 is published alongside the download rather than",
  "here, because a file cannot contain its own hash.", "",
  "## Contents", "",
]
lines += ["- `%s`" % r for r in files] + [""]
io.open(manifest, "w", encoding="utf-8").write("\n".join(lines))
print("  files=%d modules=%d docs=%d guides=%d commands=%d scripts=%d templates=%d reports=%d checklists=%d examples=%d words=%s"
      % (len(files), len(modules), len(docs), len(guides), len(commands), len(scripts), len(templates), len(reports), len(checklists), len(examples), format(words, ",")))
PY
ok "manifest written"

say "Re-validating with the manifest present"
python3 "$ROOT/scripts/validate-migration-system.py" || die "validation failed after manifest"
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
       or n.endswith(".jsonl")]
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
