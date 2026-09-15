#!/usr/bin/env bash
#
# Finish the starter-kit repository rename.
#
#   ./scripts/rename-kit-repo.sh              # check the gate, show what would change
#   ./scripts/rename-kit-repo.sh --apply      # rewrite refs, push theme, republish, submit
#
# Renaming a GitHub repository needs the REST API or the web UI. Only an SSH key
# is available here, so the rename itself is done by hand at
#   https://github.com/sitebuilderstack/sitebuilderstack_store/settings
# and this script does everything that follows it.
#
# Order matters. GitHub redirects the OLD name to the new one, so links written
# against the old name keep working after the rename — but a link written
# against the new name 404s before it. That is why this refuses to run until
# the rename is actually live.

set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# This script rewrites every match under $ROOT. If ROOT is ever wrong, that is
# a filesystem-wide search-and-replace, so refuse to run outside this repository.
for marker in content/articles.json scripts/publish-starter-kit.sh theme/dev; do
  [ -e "$marker" ] || { echo "ABORT: $ROOT is not the sitebuilderstack repository (no $marker)" >&2; exit 1; }
done

OLD="sitebuilderstack/sitebuilderstack_store"
NEW="sitebuilderstack/claude-code-website-starter-kit"
APPLY="${1:-}"

# The gate: the new name must resolve to a repository whose canonical full_name
# is the new name. Note that the API does NOT report a rename through the old
# name — GET /repos/<old> answers 301 with {"message":"Moved Permanently"} and
# no full_name unless the redirect is followed. So this asks for the new name
# directly, which only answers 200 once the rename has actually happened.
# -L is set so the check still reads correctly if these names are ever swapped.
live="$(curl -sfL "https://api.github.com/repos/$NEW" \
        | python3 -c 'import json,sys; print(json.load(sys.stdin).get("full_name",""))' 2>/dev/null || true)"
if [ "$live" != "$NEW" ]; then
  echo "NOT RENAMED YET — $NEW does not resolve (got: ${live:-404})."
  echo
  echo "Rename it first:"
  echo "  https://github.com/$OLD/settings"
  echo "  Repository name -> claude-code-website-starter-kit -> Rename"
  echo
  echo "Then run: ./scripts/rename-kit-repo.sh --apply"
  exit 1
fi
echo "gate: $NEW is live"

files=$(grep -rl "$OLD" --exclude-dir=.git --exclude-dir=node_modules . \
        | grep -vE '^\./(product|dist)/' | sed 's|^\./||' | sort)
if [ -z "$files" ]; then
  echo "nothing left to rewrite"
else
  echo "files holding the old path:"; echo "$files" | sed 's/^/  /'
fi

if [ "$APPLY" != "--apply" ]; then
  echo "not applying (pass --apply)"; exit 0
fi

# Replace the full owner/repo path only. The storefront mirror is
# sitebuilderstack/store, which this string cannot match.
for f in $files; do
  python3 - "$f" "$OLD" "$NEW" <<'PY'
import io, sys
p, old, new = sys.argv[1], sys.argv[2], sys.argv[3]
s = io.open(p, encoding="utf-8").read()
io.open(p, "w", encoding="utf-8").write(s.replace(old, new))
PY
done
echo "rewrote $(echo "$files" | wc -w) file(s)"

left=$(grep -rl "$OLD" --exclude-dir=.git --exclude-dir=node_modules . \
       | grep -vE '^\./(product|dist)/' || true)
[ -z "$left" ] || { echo "ABORT: old path still present in: $left" >&2; exit 1; }

echo
echo "── pushing the shared agents.md / llms.txt template ──"
python3 scripts/theme_push.py 191811453220 theme/dev templates/agents.md.liquid | tail -2
SBS_ALLOW_LIVE=1 python3 scripts/theme_push.py 191797854500 theme/dev templates/agents.md.liquid | tail -2

echo "── republishing the two pages that quote the URL ──"
python3 scripts/publish-articles.py claude-code-skills | tail -2
python3 scripts/publish-resources.py | tail -6

echo "── telling the search engines ──"
python3 scripts/indexnow-submit.py /opt/indexnow-key.txt \
  https://sitebuilderstack.com/blogs/guides/claude-code-skills \
  https://sitebuilderstack.com/pages/resources | tail -2

echo
echo "── verifying the live site ──"
fail=0
for u in /blogs/guides/claude-code-skills /pages/resources /agents.md /llms.txt; do
  body="$(curl -s -L --max-time 25 "https://sitebuilderstack.com$u")"
  n=$(printf '%s' "$body" | grep -c "$NEW" || true)
  o=$(printf '%s' "$body" | grep -c "$OLD" || true)
  printf '  %-42s new=%s old=%s\n' "$u" "$n" "$o"
  { [ "$n" -ge 1 ] && [ "$o" -eq 0 ]; } || fail=1
done
code=$(curl -s -o /dev/null -L -w '%{http_code}' "https://github.com/$NEW")
printf '  %-42s %s\n' "github.com/$NEW" "$code"
[ "$code" = "200" ] || fail=1
[ "$fail" -eq 0 ] && echo "all surfaces updated" || { echo "VERIFICATION FAILED" >&2; exit 1; }

echo
echo "Remaining by hand: the repository description and topics are in docs/PUBLIC-MIRROR.md."
