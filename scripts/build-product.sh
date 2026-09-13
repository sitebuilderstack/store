#!/usr/bin/env bash
#
# Build the distributable product archive.
#
#   ./scripts/build-product.sh [version]
#
# Steps:
#   1. Check required files are present
#   2. Run the validation suite (secrets, links, duplicates, structure)
#   3. Verify the prompt library meets its minimum count
#   4. Generate PRODUCT-MANIFEST.md (with a self-consistent content digest)
#   5. Create the ZIP deterministically
#   6. Verify the archive round-trips
#   7. Generate the SHA-256 checksum for publication
#
# Note on checksums: the archive's SHA-256 is published *alongside* the download
# (in dist/*.sha256 and in the release notes) and deliberately not inside the
# manifest — a file cannot contain its own hash. The manifest instead carries a
# content digest over the extracted files, which is self-consistent.
#
# Exits non-zero on any failure.

set -euo pipefail

VERSION="${1:-1.0}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUNDLE_DIR="$REPO_ROOT/product/Claude-Code-Website-Launch-System"
DIST_DIR="$REPO_ROOT/dist"
ARCHIVE_NAME="claude-code-website-launch-system-v${VERSION}.zip"
ARCHIVE_PATH="$DIST_DIR/$ARCHIVE_NAME"
BUILD_DATE="${BUILD_DATE:-$(date -u +%Y-%m-%d)}"

say()  { printf '\n\033[1m▸ %s\033[0m\n' "$*"; }
ok()   { printf '  \033[32m✓\033[0m %s\n' "$*"; }
fail() { printf '  \033[31m✗\033[0m %s\n' "$*" >&2; exit 1; }

# ── 1. required files ────────────────────────────────────────────────────────
say "Checking required files"

REQUIRED=(
  "START-HERE.md" "README.md" "LICENSE.md" "VERSION.md"
  "01-Master-System/MASTER-WEBSITE-BUILDER-PROMPT.md"
  "01-Master-System/WEBSITE-LAUNCH-WORKFLOW.md"
  "02-Claude-Code-Configuration/PRODUCTION-CLAUDE.md"
  "02-Claude-Code-Configuration/CLAUDE-MD-GUIDE.md"
  "03-SEO-System/SEO-ARCHITECTURE-PROMPT.md"
  "03-SEO-System/TECHNICAL-SEO-AUDIT-PROMPT.md"
  "03-SEO-System/CONTENT-CLUSTER-SYSTEM.md"
  "04-Shopify/SHOPIFY-MASTER-BUILD-PROMPT.md"
  "05-WordPress/WORDPRESS-MASTER-BUILD-PROMPT.md"
  "06-Astro/ASTRO-MASTER-BUILD-PROMPT.md"
  "07-SaaS/SAAS-APPLICATION-BUILD-PROMPT.md"
  "08-Landing-Pages/HIGH-CONVERTING-LANDING-PAGE-PROMPT.md"
  "09-GitHub/GITHUB-DEPLOYMENT-WORKFLOW.md"
  "10-Cloudflare/CLOUDFLARE-DEPLOYMENT-GUIDE.md"
  "11-Security/WEBSITE-SECURITY-AUDIT-PROMPT.md"
  "11-Security/SECRET-SCANNING-PROMPT.md"
  "12-Accessibility/ACCESSIBILITY-AUDIT-PROMPT.md"
  "13-Search-Engines/GOOGLE-SEARCH-CONSOLE-WORKFLOW.md"
  "13-Search-Engines/BING-WEBMASTER-TOOLS-WORKFLOW.md"
  "13-Search-Engines/INDEXNOW-WORKFLOW.md"
  "14-Checklists/PRE-LAUNCH-CHECKLIST.md"
  "14-Checklists/POST-LAUNCH-CHECKLIST.md"
  "15-Claude-Code-Prompt-Library/README.md"
  "16-Templates/QA-REPORT-TEMPLATE.md"
  "17-Bonus/WEBSITE-RESCUE-PROMPT.md"
)

MISSING=0
for f in "${REQUIRED[@]}"; do
  [ -f "$BUNDLE_DIR/$f" ] || { printf '  \033[31m✗\033[0m missing: %s\n' "$f" >&2; MISSING=1; }
done
[ "$MISSING" -eq 0 ] || fail "required files are missing"
ok "all ${#REQUIRED[@]} required files present"

# ── 2. validation ────────────────────────────────────────────────────────────
say "Running validation suite"
python3 "$REPO_ROOT/scripts/validate-product.py" "$BUNDLE_DIR" \
  || fail "validation failed — fix the errors above before building"

# ── 3. prompt library count ──────────────────────────────────────────────────
say "Verifying prompt library"
LIB_COUNT=$(grep -hcE '^## (DIS|PLN|DEV|DBG|SEO|SEC|A11Y|PERF|CNT|DEP|MNT)-[0-9]+' \
  "$BUNDLE_DIR"/15-Claude-Code-Prompt-Library/*.md | paste -sd+ | bc)
[ "$LIB_COUNT" -ge 75 ] || fail "prompt library has only $LIB_COUNT prompts (minimum 75)"
ok "$LIB_COUNT reusable prompts in the library"

# ── 4. manifest ──────────────────────────────────────────────────────────────
say "Generating manifest"
python3 "$REPO_ROOT/scripts/generate-manifest.py" "$BUNDLE_DIR" "$VERSION" "$BUILD_DATE" \
  || fail "manifest generation failed"

python3 "$REPO_ROOT/scripts/fill-manifest-name.py" \
  "$BUNDLE_DIR/PRODUCT-MANIFEST.md" "$ARCHIVE_NAME" || fail "manifest finalisation failed"
ok "PRODUCT-MANIFEST.md written and finalised"

# ── 5. archive ───────────────────────────────────────────────────────────────
say "Building archive"
mkdir -p "$DIST_DIR"

if [ -f "$ARCHIVE_PATH" ]; then
  mv "$ARCHIVE_PATH" "$ARCHIVE_PATH.$(date -u +%Y%m%d%H%M%S).bak"
  ok "existing archive moved aside"
fi

# Python's zipfile rather than the `zip` binary: always available, and it lets
# us write entries in a deterministic sorted order.
python3 "$REPO_ROOT/scripts/make-archive.py" "$BUNDLE_DIR" "$ARCHIVE_PATH" \
  || fail "archive creation failed"
ok "archive created: $ARCHIVE_NAME"

# ── 6. verify ────────────────────────────────────────────────────────────────
say "Verifying archive integrity"
python3 "$REPO_ROOT/scripts/verify-archive.py" "$ARCHIVE_PATH" "$BUNDLE_DIR" \
  || fail "archive verification failed"
ok "archive verified"

# ── 7. checksum ──────────────────────────────────────────────────────────────
say "Generating checksum"
( cd "$DIST_DIR" && sha256sum "$ARCHIVE_NAME" > "$ARCHIVE_NAME.sha256" )
SHA=$(cut -d' ' -f1 < "$ARCHIVE_PATH.sha256")
SIZE=$(stat -c%s "$ARCHIVE_PATH")
SIZE_H=$(numfmt --to=iec-i --suffix=B "$SIZE" 2>/dev/null || echo "${SIZE} bytes")
DIGEST=$(grep -m1 'Content digest' "$BUNDLE_DIR/PRODUCT-MANIFEST.md" | sed 's/.*`\(.*\)`.*/\1/')
ok "SHA-256: $SHA"

FILE_COUNT=$(find "$BUNDLE_DIR" -type f | wc -l)
DIR_COUNT=$(find "$BUNDLE_DIR" -type d | wc -l)

cat <<REPORT

┌──────────────────────────────────────────────────────────────────────────┐
  BUILD COMPLETE

  Product          The Claude Code Website Launch System
  Version          $VERSION
  Built            $BUILD_DATE

  Archive          $ARCHIVE_PATH
  Size             $SIZE_H ($SIZE bytes)
  Archive SHA-256  $SHA
  Content digest   $DIGEST

  Files            $FILE_COUNT
  Directories      $DIR_COUNT
  Library prompts  $LIB_COUNT
└──────────────────────────────────────────────────────────────────────────┘

Publish the archive SHA-256 with the download. See docs/RELEASE-PROCESS.md.
REPORT
