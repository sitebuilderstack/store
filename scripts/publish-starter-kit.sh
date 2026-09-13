#!/usr/bin/env bash
#
# Publish the starter kit to github.com/sitebuilderstack/sitebuilderstack_store.
#
#   ./scripts/publish-starter-kit.sh            # build and verify only
#   ./scripts/publish-starter-kit.sh --push     # build, verify, then push
#
# The kit stands alone in its own repository so an awesome-list can link a repo
# root rather than a subdirectory. It is also mirrored inside the storefront
# repository at github/claude-code-website-starter-kit/, because that is where
# scripts/build-github-kit.sh regenerates it from resources/.
#
# Like the storefront mirror this is a SINGLE commit, rebuilt each time. The
# kit's real history lives in commits whose messages carry keyword demand data,
# ranking positions and pricing — none of which belongs in a public repository.

set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

REMOTE="git@github.com:sitebuilderstack/sitebuilderstack_store.git"
SRC="github/claude-code-website-starter-kit"
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT

[ -d "$SRC" ] || { echo "ABORT: $SRC missing" >&2; exit 1; }

# Skills that Claude Code would silently ignore are worse than no skills, so the
# validator gates the publish rather than only the test suite.
python3 scripts/validate-skills.py > /dev/null || { echo "ABORT: skill validation failed" >&2; exit 1; }

git ls-files "$SRC" | while read -r f; do
  rel="${f#"$SRC"/}"
  mkdir -p "$STAGE/$(dirname "$rel")"
  cp "$f" "$STAGE/$rel"
done

cd "$STAGE"

# The kit is public and this repository tracks the paid bundle. Nothing outside
# the kit directory should ever reach the payload.
if find . -maxdepth 1 -mindepth 1 -type d | sed 's|^\./||' | grep -qxE 'product|dist|freebie'; then
  echo "ABORT: an excluded directory is present in the payload" >&2; exit 1
fi
if grep -rIlE "AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{36}|shp(at|ss|ca|pa)_[0-9a-fA-F]{32}|AIza[0-9A-Za-z_-]{35}|-----BEGIN [A-Z ]*PRIVATE KEY-----" \
     . 2>/dev/null | grep -q .; then
  echo "ABORT: credential pattern found in the payload" >&2; exit 1
fi
[ -f README.md ] && [ -f LICENSE ] || { echo "ABORT: README.md or LICENSE missing" >&2; exit 1; }

n=$(find . -type f | wc -l)
echo "payload: $n files, $(du -sh . | cut -f1)"
echo "skills:               valid"
echo "excluded directories: absent"
echo "credential patterns:  none"
echo "README + LICENSE:     present"

if [ "${1:-}" != "--push" ]; then
  echo "not pushing (pass --push)"; exit 0
fi

git init -q -b main
git -c user.name="James Joyner IV" -c user.email="james.joyner.iv2@gmail.com" add -A
git -c user.name="James Joyner IV" -c user.email="james.joyner.iv2@gmail.com" \
    commit -q -m "Claude Code Website Starter Kit

A CLAUDE.md starter, four production checklists and five installable
Claude Code skills for building, launching and auditing websites.

MIT licensed. Rebuilt from the source tree on each publish."
git push -q --force "$REMOTE" main:main
echo "pushed $n files to $REMOTE"
