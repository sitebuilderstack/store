#!/usr/bin/env bash
#
# Build the distributable Conversion & Revenue Optimization Toolkit archive.
#
#   ./scripts/build-toolkit.sh [version]
#
# Reuses the same archive tooling as the other two products so all three are
# packaged identically: deterministic entry order, a round-trip verification,
# and a published SHA-256 alongside the download rather than inside the
# manifest — a file cannot contain its own hash.
#
# Exits non-zero on any failure.

set -euo pipefail

VERSION="${1:-1.0}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUNDLE="$ROOT/product/Claude-Code-Conversion-Revenue-Optimization-Toolkit"
DIST="$ROOT/dist"
NAME="claude-code-conversion-revenue-optimization-toolkit-v${VERSION}.zip"
ARCHIVE="$DIST/$NAME"

say() { printf '\n\033[1m▸ %s\033[0m\n' "$1"; }
ok()  { printf '  \033[32m✓\033[0m %s\n' "$1"; }
die() { printf '  \033[31m✗ %s\033[0m\n' "$1"; exit 1; }

mkdir -p "$DIST"

say "Validating the bundle"
python3 "$ROOT/scripts/validate-cro-toolkit.py" || die "validation failed"
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
    dns[:] = [d for d in dns if not d.startswith(".")]
    for fn in sorted(fns):
        files.append(os.path.relpath(os.path.join(dp, fn), bundle))
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

modules = sorted({r.split(os.sep)[0] for r in files
                  if os.sep in r and r.split(os.sep)[0][:2].isdigit()})
# Same definition as scripts/validate-cro-toolkit.py: a workflow is a Markdown
# file in one of the numbered modules 01- to 12-. If these two ever disagree,
# the product page ends up quoting a number nothing counted.
WORKFLOW_DIR = re.compile(r"^(0[1-9]|1[0-2])-[a-z-]+/[^/]+\.md$")
workflows = [r for r in files if WORKFLOW_DIR.match(r.replace(os.sep, "/"))]
templates = [r for r in files if r.startswith("13-templates" + os.sep)]
examples = [r for r in files if r.startswith("examples" + os.sep)
            and not r.endswith("README.md")]
commands = 0
for r in files:
    if r.startswith("commands" + os.sep) and not r.endswith("COMMANDS.md"):
        body = io.open(os.path.join(bundle, r), encoding="utf-8").read()
        commands += len(re.findall(r"^## C-\d+", body, re.M))

lines = [
  "# Product manifest",
  "",
  "**Claude Code Conversion & Revenue Optimization Toolkit** — version %s" % version,
  "",
  "Generated at build time from the bundle itself. Every number here was",
  "counted, not typed.",
  "",
  "| | |",
  "| --- | --- |",
  "| Files | %d |" % len(files),
  "| Modules | %d |" % len(modules),
  "| Workflows | %d |" % len(workflows),
  "| Commands | %d |" % commands,
  "| Templates | %d |" % len(templates),
  "| Worked examples | %d |" % len(examples),
  "| Words | %s |" % format(words, ","),
  "",
  "Content digest (SHA-256 over every file's path and contents, sorted):",
  "",
  "`%s`" % digest,
  "",
  "The archive's own SHA-256 is published alongside the download rather than",
  "here, because a file cannot contain its own hash.",
  "",
  "## Contents",
  "",
]
for r in files:
    lines.append("- `%s`" % r.replace(os.sep, "/"))
lines.append("")
io.open(manifest, "w", encoding="utf-8").write("\n".join(lines))
print("  files=%d modules=%d workflows=%d commands=%d words=%s"
      % (len(files), len(modules), len(workflows), commands, format(words, ",")))
PY
ok "manifest written"

say "Re-validating with the manifest present"
python3 "$ROOT/scripts/validate-cro-toolkit.py" || die "validation failed after manifest"
ok "still valid"

if [ -f "$ARCHIVE" ]; then
  mv "$ARCHIVE" "$ARCHIVE.$(date -u +%Y%m%d%H%M%S).bak"
  ok "existing archive moved aside"
fi

say "Creating the archive"
python3 "$ROOT/scripts/make-archive.py" "$BUNDLE" "$ARCHIVE" || die "archive creation failed"
ok "created $NAME"

say "Verifying the archive round-trips"
python3 "$ROOT/scripts/verify-archive.py" "$ARCHIVE" "$BUNDLE" || die "archive verification failed"
ok "archive verified"

say "Checksum"
( cd "$DIST" && sha256sum "$NAME" > "$NAME.sha256" )
SHA=$(cut -d' ' -f1 < "$ARCHIVE.sha256")
SIZE=$(stat -c%s "$ARCHIVE")
SIZE_H=$(numfmt --to=iec-i --suffix=B "$SIZE" 2>/dev/null || echo "${SIZE} bytes")
ok "SHA-256: $SHA"

printf '\n────────────────────────────────\n'
printf '  %s\n  %s (%s bytes)\n  %s\n' "$NAME" "$SIZE_H" "$SIZE" "$SHA"
printf '────────────────────────────────\n'
