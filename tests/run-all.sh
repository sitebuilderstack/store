#!/usr/bin/env bash
#
# Run every automated check in this repository.
#
#   ./tests/run-all.sh [--with-render]
#
# --with-render also runs the browser-based audits, which need Chrome and
# PUPPETEER_EXECUTABLE_PATH set.

set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PASS=0; FAIL=0; SKIP=0

# The public mirror of this repository excludes product/, because that is the
# thing customers pay for. Checks that read the bundle are skipped there rather
# than failed, so `./tests/run-all.sh` is meaningful on a clone. Nothing changes
# when the bundle is present.
BUNDLE="product/Claude-Code-Website-Launch-System"
run_if_bundle() {
  local name="$1"; shift
  if [ ! -d "$BUNDLE" ]; then
    printf '\n\033[1m▸ %s\033[0m\n' "$name"
    printf '  \033[33m- skipped\033[0m (no %s in this checkout)\n' "$BUNDLE"
    SKIP=$((SKIP+1)); return
  fi
  run "$name" "$@"
}
SEO_BUNDLE="product/Claude-Code-SEO-Website-Audit-Toolkit"
run_if_bundle_seo() {
  local name="$1"; shift
  if [ ! -d "$SEO_BUNDLE" ]; then
    printf '\n\033[1m▸ %s\033[0m\n' "$name"
    printf '  \033[33m- skipped\033[0m (no %s in this checkout)\n' "$SEO_BUNDLE"
    SKIP=$((SKIP+1)); return
  fi
  run "$name" "$@"
}
CRO_BUNDLE="product/Claude-Code-Conversion-Revenue-Optimization-Toolkit"
run_if_bundle_cro() {
  local name="$1"; shift
  if [ ! -d "$CRO_BUNDLE" ]; then
    printf '\n\033[1m▸ %s\033[0m\n' "$name"
    printf '  \033[33m- skipped\033[0m (no %s in this checkout)\n' "$CRO_BUNDLE"
    SKIP=$((SKIP+1)); return
  fi
  run "$name" "$@"
}
run() {
  local name="$1"; shift
  printf '\n\033[1m▸ %s\033[0m\n' "$name"
  if "$@" > /tmp/sbs-test.out 2>&1; then
    printf '  \033[32m✓ pass\033[0m\n'; PASS=$((PASS+1))
  else
    printf '  \033[31m✗ FAIL\033[0m\n'; tail -20 /tmp/sbs-test.out | sed 's/^/    /'
    FAIL=$((FAIL+1))
  fi
}

run_if_bundle "Product bundle validation" \
  python3 scripts/validate-product.py

run_if_bundle "Storefront claims match the bundle" \
  python3 scripts/audit-storefront-claims.py

# agents.md / llms.txt runs in a restricted Liquid context with no product
# object, so its price and counts are literals. This is what stops them drifting.
run_if_bundle "agents.md claims match the product" \
  python3 scripts/audit-agents-claims.py

# A skill with a typo'd frontmatter field or the wrong filename is silently
# ignored by Claude Code, which is worse than shipping no skill at all.
# The information architecture is data. A handle that does not resolve is a
# dead internal link on a live page, so the graph is checked against the
# manifests in both directions rather than reviewed by eye.
run "Content graph resolves" \
  python3 scripts/validate-graph.py

# The homepage selector recommends a route through the site. An invented URL
# there is a dead end on the most visited page.
run "Workflow selector URLs all exist" \
  python3 scripts/validate-selector.py

# The listing quotes the toolkit's counts. A bundle that drifts from them is
# the kind of thing only a customer notices.
run_if_bundle_seo "SEO toolkit bundle is valid" \
  python3 scripts/validate-toolkit.py

run_if_bundle_cro "Conversion toolkit bundle is valid" \
  python3 scripts/validate-cro-toolkit.py

# The conversion toolkit's central claim is that it never predicts a percentage
# lift and never recommends a manipulative tactic. Two of the validator's
# checks enforce exactly that, and a check nobody has watched fail is a line in
# a log that says PASS. The self-test breaks each one on purpose.
run_if_bundle_cro "Conversion toolkit validator detects every fault it claims to" \
  python3 scripts/validate-cro-toolkit.py --self-test

OPS_BUNDLE="product/Claude-Code-Website-Operations-Maintenance-System"
run_if_bundle_ops() {
  local name="$1"; shift
  if [ ! -d "$OPS_BUNDLE" ]; then
    printf '\n\033[1m▸ %s\033[0m\n' "$name"
    printf '  \033[33m- skipped\033[0m (no %s in this checkout)\n' "$OPS_BUNDLE"
    SKIP=$((SKIP+1)); return
  fi
  run "$name" "$@"
}

run_if_bundle_ops "Operations system bundle is valid" \
  python3 scripts/validate-ops-system.py

# The operations system ships working scripts and promises "standard library
# only, never a credential, never an attack tool". The validator enforces
# each; the self-test breaks each on purpose so the PASS line means something.
run_if_bundle_ops "Operations system validator detects every fault it claims to" \
  python3 scripts/validate-ops-system.py --self-test

# The scripts are the product. Each must run, against a fixture that needs no
# network, and exit with the documented code.
run_if_bundle_ops "Operations system scripts run offline and exit as documented" \
  python3 scripts/test-ops-scripts.py

# The listing states counts and a price; both are checked against the bundle
# and the specification before a publish is attempted.
run_if_bundle_ops "Operations system listing matches the bundle" \
  python3 scripts/publish-ops-system-product.py --check-only

SHOP_BUNDLE="product/Claude-Code-Shopify-Automation-Admin-API-Toolkit"
run_if_bundle_shop() {
  local name="$1"; shift
  if [ ! -d "$SHOP_BUNDLE" ]; then
    printf '\n\033[1m▸ %s\033[0m\n' "$name"
    printf '  \033[33m- skipped\033[0m (no %s in this checkout)\n' "$SHOP_BUNDLE"
    SKIP=$((SKIP+1)); return
  fi
  run "$name" "$@"
}

run_if_bundle_shop "Shopify toolkit bundle is valid" \
  python3 scripts/validate-shopify-toolkit.py

# The toolkit's first rule is that a token never leaves .env; its second is
# standard library only; its third is that every write is guarded. The
# validator enforces each and the self-test breaks each on purpose.
run_if_bundle_shop "Shopify toolkit validator detects every fault it claims to" \
  python3 scripts/validate-shopify-toolkit.py --self-test

# Every script against a mock Admin GraphQL API: retries, throttling,
# userErrors, dry runs that write nothing, writes that preview, back up and
# read back, and no output line that ever contains the token.
run_if_bundle_shop "Shopify toolkit scripts run against a mock Admin API" \
  python3 scripts/test-shopify-toolkit.py

run_if_bundle_shop "Shopify toolkit listing matches the bundle" \
  python3 scripts/publish-shopify-toolkit-product.py --check-only

MIG_BUNDLE="product/Claude-Code-Website-Migration-Replatforming-System"
run_if_bundle_migration() {
  local name="$1"; shift
  if [ ! -d "$MIG_BUNDLE" ]; then
    printf '\n\033[1m▸ %s\033[0m\n' "$name"
    printf '  \033[33m- skipped\033[0m (no %s in this checkout)\n' "$MIG_BUNDLE"
    SKIP=$((SKIP+1)); return
  fi
  run "$name" "$@"
}

run_if_bundle_migration "Migration system bundle is valid" \
  python3 scripts/validate-migration-system.py

# The product's rules: no credentials, standard library only, the ten safety
# rules in every command, no homepage-dump redirects, a fictional example, no
# ranking guarantees. The validator enforces each; the self-test breaks each.
run_if_bundle_migration "Migration system validator detects every fault it claims to" \
  python3 scripts/validate-migration-system.py --self-test

# Two local fixture sites (source and target) with the failures the scripts
# exist to find: a missing page, redirects that are valid / missing / loop /
# chain / dead, a canonical to the old host, a staging URL in the sitemap, a
# lost description, an image on the old domain, a vanished form.
run_if_bundle_migration "Migration system scripts run offline and exit as documented" \
  python3 scripts/test-migration-system.py

run_if_bundle_migration "Migration system listing matches the bundle" \
  python3 scripts/publish-migration-system-product.py --check-only

AGENCY_BUNDLE="product/Claude-Code-Agency-Client-Delivery-System"
run_if_bundle_agency() {
  local name="$1"; shift
  if [ ! -d "$AGENCY_BUNDLE" ]; then
    printf '\n\033[1m▸ %s\033[0m\n' "$name"
    printf '  \033[33m- skipped\033[0m (no %s in this checkout)\n' "$AGENCY_BUNDLE"
    SKIP=$((SKIP+1)); return
  fi
  run "$name" "$@"
}

run_if_bundle_agency "Agency system bundle is valid" \
  python3 scripts/validate-agency-system.py

# No credentials anywhere, no plaintext credential template, no invented metric
# in the example, no legal or guarantee language, the ten rules in every
# command, every CSV/YAML/JSON parseable. The self-test breaks each on purpose.
run_if_bundle_agency "Agency system validator detects every fault it claims to" \
  python3 scripts/validate-agency-system.py --self-test

# The four scripts against a temp workspace and the example project: creation
# that refuses to overwrite, the status block from the files, the estimate as a
# range, and the client-project validation that fails on a .env or a credential.
run_if_bundle_agency "Agency system scripts run offline and exit as documented" \
  python3 scripts/test-agency-system.py

run_if_bundle_agency "Agency system listing matches the bundle" \
  python3 scripts/publish-agency-system-product.py --check-only

# Plausible is rendered from one snippet into all three layout heads (landing,
# the policy branch, the ONE fallback); a page type that lost it would be
# invisible in the dashboard rather than broken.
run "Plausible snippet is rendered in every layout head" \
  bash -c "[ \"\$(cat theme/dev/layout/landing.liquid theme/dev/layout/theme.liquid | grep -c \"render 'sbs-plausible'\")\" = 3 ] && grep -q 'plausible.io/js/pa-z2VuG5J4PEn80otsE-Ymx.js' theme/dev/snippets/sbs-plausible.liquid"

# Each of these audits decides what work happens next, so a rule that quietly
# stopped firing would not show up as a failure — it would show up as a clean
# report. Every self-test breaks each rule on purpose and then proves it stays
# silent on a correct case, which is the half that catches an over-eager rule.
# ---- engagement layer: Try-this modules, labs, My Projects, Weekly Fix ----
# The graph validator now covers modules, labs and challenges (dangling ids,
# next-step destinations, the Thursday cadence); the generated Liquid must
# match its JSON sources; the storage core, the generators, the analytics
# allowlist and the lab scoring have offline tests; the free downloads' two
# scripts are exercised against local fixtures with a planted failure each.
run "Content graph engagement rules fire and stay silent" \
  python3 scripts/validate-graph.py --self-test

run "Lab snippets are generated from content/labs" \
  python3 scripts/build-labs.py --check

run "Weekly Fix schedule snippet is generated from the graph" \
  python3 scripts/build-weekly.py --check

run "My Projects storage core (persistence, migration, imports, limits)" \
  node scripts/test-projects-store.js

run "Try-this generators, analytics allowlist, lab scoring" \
  node scripts/test-engagement.js

run "Redirect checker detects every planted fault on local fixtures" \
  python3 scripts/test-redirect-checker.py

run "Weekly maintenance checker fails on the broken fixture, passes when repaired" \
  python3 scripts/test-weekly-check.py

# The four monetization paths: no page may assert an affiliate relationship the
# register does not record, publish a price the owner has not approved, carry
# purchasable-offer schema on an inquiry, or let a visitor's text reach an
# analytics payload. Each of those is a claim, and each is checked here.
run "Monetization offers: disclosure, pricing, schema and analytics honesty" \
  node scripts/test-monetization.js

run "Workflow Club pilot scripts (capture and compare) self-test" \
  bash -c "python3 content/membership/pilot-01/capture.py --self-test >/dev/null && python3 content/membership/pilot-01/compare.py --self-test >/dev/null"

run "SEO Audit Navigator: analytics modules, session model, attribution link, data" \
  node scripts/test-navigator-analytics.js

run "Launch Readiness Analyzer: scoring, scoping, risks, plan, mapping, analytics" \
  node scripts/test-launch-analyzer.js

run "SEO Audit Navigator: artifact files parse" \
  bash -c "for f in artifacts/seo-audit-navigator/*.js artifacts/seo-audit-navigator/analytics/*.js; do node --check \$f || exit 1; done"

run "Engagement bundles parse and are registered in the layout" \
  bash -c "node --check theme/dev/assets/sbs-projects.js && node --check theme/dev/assets/sbs-engage.js && node --check theme/dev/assets/sbs-labs.js && node --check theme/dev/assets/sbs-workspace.js && grep -q 'id=\"sbs-assets\"' theme/dev/layout/landing.liquid"

run "Cannibalisation classifier fires and stays silent" \
  python3 scripts/audit-cannibalization.py --self-test

run "Internal-linking extractors are correct" \
  python3 scripts/audit-internal-linking.py --self-test

run "Indexation rules fire and stay silent" \
  python3 scripts/audit-indexation.py --self-test

run "Benchmark harness refuses invalid trials" \
  python3 scripts/benchmark-harness.py --self-test

# The benchmark page must be incapable of implying a result it does not have.
# The empty and partial states are generated by the same code path as a full
# one, and this proves both withhold rather than improvise.
run "Benchmark analysis withholds what it cannot show" \
  python3 scripts/benchmark-analyse.py --self-test

run "Benchmark dataset carries no unbacked rows" \
  bash -c 'f=research/benchmark/results.csv;
    [ -f "$f" ] || { echo "missing $f"; exit 1; };
    rows=$(( $(wc -l < "$f") - 1 ));
    nd=research/benchmark/results.ndjson;
    have=0; [ -f "$nd" ] && have=$(grep -c . "$nd" || true);
    echo "csv rows=$rows ndjson rows=$have";
    [ "$rows" -le "$have" ] || { echo "the published CSV has rows the raw store does not"; exit 1; }'

# The pixel, the collector and the events documentation are three lists that
# must agree and live in three files. An event documented but not subscribed is
# uncollected; one forwarded but not in the collector's allowlist is dropped on
# arrival. Both look correct in isolation.
run "Pixel, collector and events documentation agree" \
  python3 scripts/validate-pixel.py

run "Pixel checks fire on a crafted mismatch" \
  python3 scripts/validate-pixel.py --self-test

# The recommendation table is the commercially load-bearing part of the
# picker: a quiz sold by the shop that breaks ties towards the most expensive
# answer is not a recommendation. Tested without a browser so every branch is
# covered, including the case the brief singles out.
run "Product picker recommends what the answers say" \
  node scripts/test-picker-logic.js

run "Free tool pages are wired" \
  python3 scripts/validate-tool-pages.py

run "Starter kit skills are valid" \
  python3 scripts/validate-skills.py

run "Theme links and anchors resolve" \
  python3 scripts/audit-theme-links.py

# The layout noindexes a blog page number past the end of the list, and it has
# to know the page size to work out where the end is. If these two ever drift,
# a real paginated page gets dropped from the index silently.
run "Blog page size matches the layout constant" \
  bash -c 'sec=$(grep -oE "paginate blog\.articles by [0-9]+" theme/dev/sections/sbs-blog.liquid | grep -oE "[0-9]+");
    lay=$(grep -oE "assign BLOG_PER_PAGE = [0-9]+" theme/dev/layout/landing.liquid | grep -oE "[0-9]+");
    echo "section=$sec layout=$lay";
    [ -n "$sec" ] && [ -n "$lay" ] && [ "$sec" = "$lay" ]'

run_if_bundle "Prompt library has at least 75 prompts" \
  bash -c 'n=$(grep -hcE "^## (DIS|PLN|DEV|DBG|SEO|SEC|A11Y|PERF|CNT|DEP|MNT)-[0-9]+" \
    product/Claude-Code-Website-Launch-System/15-Claude-Code-Prompt-Library/*.md \
    | paste -sd+ | bc); echo "$n prompts"; [ "$n" -ge 75 ]'

run "No credentials anywhere in the tracked tree" \
  bash -c '
    ! grep -rIlE "AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{36}|shp(at|ss|ca|pa)_[0-9a-fA-F]{32}|AIza[0-9A-Za-z_-]{35}|-----BEGIN [A-Z ]*PRIVATE KEY-----" \
      --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=dev-full --exclude-dir=one-live \
      --exclude="*.md" . 2>/dev/null | grep -q .'

# .env.example is the one .env-named file that may be tracked: it ships in the
# Shopify toolkit with an empty token, and validate-shopify-toolkit.py asserts
# the token line stays empty. Every other .env variant is a secret.
run "No secret file is tracked by git" \
  bash -c '! git ls-files | grep -vE "\.env\.example$" | grep -qE "(^|/)\.env($|\.)|\.pem$|\.key$|-token\.json$|shopify-(client-id|secret)\.txt$"'

run "Theme JSON is valid" \
  bash -c 'for f in theme/dev/templates/*.json theme/dev/sections/*.json theme/dev/config/*.json; do
             python3 -c "import json,re,sys;json.loads(re.sub(r\"^\s*/\*.*?\*/\s*\",\"\",open(sys.argv[1],encoding=\"utf-8\").read(),flags=re.S))" "$f" || exit 1
           done'

run_if_bundle "Example GitHub Actions workflows parse" \
  bash -c 'python3 -c "
import glob,sys
try: import yaml
except ImportError: sys.exit(0)
for f in glob.glob(\"product/Claude-Code-Website-Launch-System/09-GitHub/EXAMPLE-WORKFLOWS/*.yml\"):
    yaml.safe_load(open(f))
"'

run "Structured data produces valid JSON" \
  bash -c 'python3 - <<PY
import re, json
src = open("theme/dev/snippets/sbs-schema.liquid", encoding="utf-8").read()
blocks = re.findall(r"<script type=\"application/ld\+json\">(.*?)</script>", src, re.S)
want = {"Organization", "WebSite", "Product", "BreadcrumbList", "BlogPosting"}
found = set()
for b in blocks:
    found |= set(re.findall(r"\"@type\"\s*:\s*\"(\w+)\"", b))
missing = want - found
assert not missing, f"missing schema types: {sorted(missing)}"
stripped = re.sub(r"\{%-?\s*comment\s*-?%\}.*?\{%-?\s*endcomment\s*-?%\}", "", src, flags=re.S)
for bad in ("aggregateRating", "ratingValue", "reviewCount"):
    assert bad not in stripped, f"fabricated review markup: {bad}"
print(f"{len(blocks)} blocks, types {sorted(found)}, no review/rating markup")
PY'

if [ "${1:-}" = "--with-render" ]; then
  # Behavioural tests against the live site. These need a browser and the
  # network, which is why they sit behind --with-render rather than in the
  # default run: a suite that fails when the machine is offline stops being
  # trusted. Each drives real interactions and asserts what is painted, not
  # what a DOM attribute claims.
  SBS_SITE="${SBS_SITE:-https://sitebuilderstack.com}"
  run "Guide library filters (browser)" \
    node scripts/test-library-filter.js "$SBS_SITE/blogs/guides"
  run "Learning-path engine (browser)" \
    node scripts/test-route-engine.js "$SBS_SITE/"
  run "Header products menu (browser)" \
    node scripts/test-nav-menu.js "$SBS_SITE/"
  run "Mobile navigation panel (browser)" \
    node scripts/test-mobile-menu.js "$SBS_SITE/"
  run "Interactive checklist (browser)" \
    node scripts/test-checklist.js "$SBS_SITE/pages/claude-code-launch-checklist"
  run "Copy buttons (browser)" \
    node scripts/test-copy-buttons.js \
      "$SBS_SITE/blogs/guides/claude-md-examples-web-development" \
      "$SBS_SITE/blogs/guides/best-claude-code-prompts-for-web-development"
  run "Engagement events publish (browser)" \
    node scripts/test-analytics-events.js
  # The site-wide SEO crawl was never in the suite, so its entity-leak rule —
  # the one that should have caught a double-escaped meta description — only ran
  # when someone remembered to. It runs here now.
  run "Live SEO crawl finds nothing (browser-free)" \
    python3 scripts/audit-seo-site.py
  run "SEO crawl rules can all go red" \
    python3 scripts/audit-seo-site.py --self-test
  run "Free tools generate and recommend (browser)" \
    node scripts/test-tools.js
  run "Engagement journey: module → save → My Projects → lab → challenge (browser)" \
    node scripts/test-engagement-browser.js
  # Progress that appears without being set, or survives a reset, is worse than
  # no progress feature. This asserts both directions on all three surfaces.
  run "Learning progress persists and resets (browser)" \
    node scripts/test-learning.js
  # The header carried position:sticky from launch and never stuck once,
  # because Shopify's generated section wrapper gave it nowhere to travel.
  # Nothing caught it because nothing scrolled the page and looked.
  run "Guide reading experience (browser)" \
    node scripts/test-article-ux.js
  run "Product picker (browser)" \
    node scripts/test-picker.js

  # The local renderer is a smoke test that the landing layer renders at all,
  # with every Liquid tag resolved. It is deliberately NOT the source for the
  # accessibility and overflow assertions any more: it is a partial
  # reimplementation of Liquid, and its fidelity gaps produce findings the live
  # site does not have. One (settings not falling back to schema defaults) was
  # fixed after it reported an unlabelled input and an empty button that exist
  # only in the preview. Another, in the outcomes grid, still reports a 320px
  # overflow the live page does not have. Auditing the real page removes the
  # whole class, and tests what visitors actually receive.
  run "Landing layer renders with no unresolved Liquid" \
    bash -c 'out=$(python3 scripts/render-preview.py theme/dev theme/dev/templates/index.json /tmp/sbs-pv.html) || exit 1;
      echo "$out"; echo "$out" | grep -q "unresolved liquid tags remaining: 0"'

  # Twenty-five rendered audits plus six browser tests is roughly thirty page
  # loads in a burst, which is enough to trip Shopify's rate limiting. A
  # throttled response renders an error page with none of the markup these
  # checks look for, so the run reports findings that describe the throttle
  # rather than the site. Pace it.
  for u in "/" "/blogs/guides" "/pages/claude-code-seo" \
           "/pages/claude-code-launch-checklist" "/blogs/guides/claude-code-skills" \
           "/blogs/guides/shopify-admin-api-claude-code" \
           "/pages/build-rank-convert" \
           "/blogs/guides/claude-code-conversion-rate-optimization" \
           "/products/claude-code-conversion-revenue-optimization-toolkit" \
           "/products/complete-site-builder-stack" \
           "/products/claude-code-website-operations-maintenance-system" \
           "/products/claude-code-shopify-automation-admin-api-toolkit" \
           "/products/claude-code-website-migration-replatforming-system" \
           "/products/claude-code-agency-client-delivery-system" \
           "/pages/my-learning" \
           "/pages/claude-code-website-development-benchmark-2026" \
           "/collections/all"; do
    for w in 320 375 768 1024 1440; do
      sleep 2
      run "a11y + overflow ${u} @ ${w}px" \
        bash -c "node scripts/audit-rendered-a11y.js '${SBS_SITE}${u}' ${w} | python3 scripts/check-a11y-json.py"
    done
  done
fi

printf '\n────────────────────────────────\n'
if [ "$SKIP" -gt 0 ]; then
  printf '  passed: %d   failed: %d   skipped: %d\n' "$PASS" "$FAIL" "$SKIP"
else
  printf '  passed: %d   failed: %d\n' "$PASS" "$FAIL"
fi
printf '────────────────────────────────\n'
[ "$FAIL" -eq 0 ]
