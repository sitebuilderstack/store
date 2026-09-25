#!/usr/bin/env bash
# Every check for the Website Action Planner, in dependency order.
#
#   bash tests/run.sh            offline only (rules + browser)
#   bash tests/run.sh --links    also check every outbound URL against the live site
set -u
cd "$(dirname "$0")/.."

fail=0
run() { echo; echo "=== $1 ==="; shift; "$@" || fail=1; }

run "build (index.html must be current)" python3 build.py
if ! git diff --quiet -- index.html 2>/dev/null; then
  echo "NOTE: index.html changed — a source file was edited without rebuilding. Commit the rebuilt file."
fi
run "decision engine" node tests/test-rules.js
run "published page in a browser" env PUPPETEER_EXECUTABLE_PATH="${PUPPETEER_EXECUTABLE_PATH:-/usr/bin/chromium-browser}" node tests/test-browser.js
if [ "${1:-}" = "--links" ]; then
  run "outbound links (live)" node tests/test-links.js
  run "catalogue against the storefront (live)" python3 refresh-catalogue.py
fi

echo
if [ "$fail" -eq 0 ]; then echo "ALL CHECKS PASSED"; else echo "FAILURES ABOVE"; fi
exit $fail
