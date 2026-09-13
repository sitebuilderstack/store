#!/usr/bin/env bash
#
# Publish the public mirror of this repository to github.com/sitebuilderstack/store.
#
#   ./scripts/publish-public-mirror.sh            # build and verify only
#   ./scripts/publish-public-mirror.sh --push     # build, verify, then push
#
# The mirror is always a SINGLE commit built from the current working tree.
# History is deliberately not exported: every commit in this repository has
# product/ in its tree, so pushing history would make the paid bundle
# recoverable. Rebuilding from scratch each time is what keeps that true.

set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

REMOTE="git@github.com:sitebuilderstack/store.git"
EXCLUDE='^(product|dist|freebie)/'
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT

git ls-files | grep -vE "$EXCLUDE" | while read -r f; do
  mkdir -p "$STAGE/$(dirname "$f")"
  cp "$f" "$STAGE/$f"
done

cd "$STAGE"

# Refuse to publish if anything from an excluded top-level directory survived.
if find . -maxdepth 1 -mindepth 1 -type d | sed 's|^\./||' | grep -qE "${EXCLUDE%/}$"; then
  echo "ABORT: an excluded directory is present in the payload" >&2; exit 1
fi

# Refuse to publish if a live credential is anywhere in the payload. This is
# the same pattern set tests/run-all.sh uses, run over the payload rather than
# the tracked tree, so a file added outside git cannot slip through.
if grep -rIlE "AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{36}|shp(at|ss|ca|pa)_[0-9a-fA-F]{32}|AIza[0-9A-Za-z_-]{35}|-----BEGIN [A-Z ]*PRIVATE KEY-----" \
     --exclude="*.md" . 2>/dev/null | grep -q .; then
  echo "ABORT: credential pattern found in the payload" >&2; exit 1
fi

n=$(find . -type f | wc -l)
echo "payload: $n files, $(du -sh . | cut -f1)"
echo "excluded directories: absent"
echo "credential patterns:  none"

if [ "${1:-}" != "--push" ]; then
  echo "not pushing (pass --push)"; exit 0
fi

git init -q -b main
git -c user.name="James Joyner IV" -c user.email="james.joyner.iv2@gmail.com" add -A
git -c user.name="James Joyner IV" -c user.email="james.joyner.iv2@gmail.com" \
    commit -q -m "Publish the SiteBuilderStack storefront source

Rebuilt from the working tree. product/, dist/ and freebie/ are excluded."
git push -q --force "$REMOTE" main:main
echo "pushed $n files to $REMOTE"
