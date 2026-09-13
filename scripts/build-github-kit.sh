#!/usr/bin/env bash
# Rebuild github/claude-code-website-starter-kit from resources/, which is the
# single source of truth for the checklists. README.md and LICENSE are authored
# in the kit itself and are left alone.
#
# Site-relative links only resolve on the storefront, so they are rewritten to
# absolute sitebuilderstack.com URLs for the GitHub copy.
set -euo pipefail
cd "$(dirname "$0")/.."

KIT=github/claude-code-website-starter-kit
mkdir -p "$KIT"

cp resources/production-claude-md-starter/CLAUDE.md "$KIT/CLAUDE.md"

rewrite() {
  python3 - "$1" "$2" <<'PY'
import io, re, sys
src, dst = sys.argv[1], sys.argv[2]
s = io.open(src, encoding="utf-8").read()
s = re.sub(r"\]\((/(?:blogs|pages|products)/[^)]+)\)",
           r"](https://sitebuilderstack.com\1)", s)
io.open(dst, "w", encoding="utf-8").write(s)
print("  %-32s -> %s" % (src, dst))
PY
}

rewrite resources/claude-code-launch-checklist.md        "$KIT/LAUNCH-CHECKLIST.md"
rewrite resources/claude-code-seo-checklist.md           "$KIT/SEO-CHECKLIST.md"
rewrite resources/claude-code-security-checklist.md      "$KIT/SECURITY-CHECKLIST.md"
rewrite resources/claude-code-website-audit-checklist.md "$KIT/WEBSITE-AUDIT-CHECKLIST.md"

# The skills are authored in the kit rather than generated from resources/, so
# they are only validated here, not rewritten.
echo
echo "Validating the skills:"
python3 scripts/validate-skills.py

echo
echo "No relative links should remain in the kit:"
if grep -rn "](/" "$KIT" --include="*.md" | grep -v "](/#"; then
  echo "FAIL: relative links found above" >&2
  exit 1
fi
echo "  none found"
