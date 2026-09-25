# Website migration SEO checklist

Companion to https://sitebuilderstack.com/blogs/guides/website-migration-seo-checklist-claude-code
Tick nothing you did not observe. Each line has an evidence column for a reason.

Kind of move (tick one): [ ] redesign, same URLs  [ ] URL structure change  [ ] platform change  [ ] domain change
Some sections only apply to some kinds; they say so.

## 1. Inventory (before anything is built)

| Check | Done | Evidence (file / URL / date) |
|---|---|---|
| Full crawl of the current site saved off-host (every URL, status, title, canonical, robots directive) | | |
| Sitemap URLs reconciled against the crawl (URLs in one but not the other listed) | | |
| Search Console: Pages report and Performance export (12 months) saved | | |
| Analytics: landing pages with sessions in the last 12 months saved | | |
| Existing redirects exported (server config, platform list, plugin) | | |
| Backlink sample: the pages with the most linking domains identified | | |
| Union of all of the above = the inventory; count recorded | | |

## 2. Baselines

| Check | Done | Evidence |
|---|---|---|
| Titles, descriptions, canonicals, H1s per URL saved (the crawl) | | |
| Structured data types per URL saved | | |
| Core Web Vitals / performance for the key pages recorded | | |
| Rankings for a fixed keyword set recorded with the date (if you track them) | | |

## 3. URL mapping (URL change, platform change, domain change)

| Check | Done | Evidence |
|---|---|---|
| One row per inventory URL with a disposition: KEEP / MOVE / MERGE / REMOVE | | |
| Zero rows still marked REVIEW before build starts | | |
| Every MOVE/MERGE target exists on the new site (staging 200) | | |
| No REMOVE row redirects to the homepage; each is 410 or a 301 to the closest page | | |
| Identity string filled for every MOVE/MERGE row (a word from the target's title) | | |
| Map stored with the project, not in someone's spreadsheet | | |

## 4. Redirects

| Check | Done | Evidence |
|---|---|---|
| Existing redirects merged into the new set, not dropped | | |
| Every redirect is a single hop (source → final), 301 or 308 | | |
| No chains, no loops (the checker reports both) | | |
| Redirects live at the server or platform layer, not in page JavaScript | | |
| Redirects planned to stay for at least a year (Google's guidance) | | |

## 5. Staging

| Check | Done | Evidence |
|---|---|---|
| Staging is noindexed (robots meta or X-Robots-Tag) and/or auth-protected | | |
| Canonicals on staging point at the PRODUCTION host, not staging | | |
| Every mapped target returns 200 on staging | | |
| Titles/descriptions compared page by page against the baseline; critical pages verbatim | | |
| Structured data on the key pages parses and matches the visible content | | |
| Internal links do not point at the old host or at staging | | |
| Forms tested with a marker on staging (mocked or sandbox delivery is fine — say which) | | |
| check_redirects.py run against staging with --host-rewrite: 0 failures | | |

## 6. Launch day

| Check | Done | Evidence |
|---|---|---|
| Domain change: DNS TTL lowered at least a week ahead; zone recorded incl. MX/SPF/DKIM/DMARC | | |
| Production is NOT noindexed; the staging block was removed | | |
| Canonicals on production self-reference on the production host | | |
| check_redirects.py run against the live origin: 0 failures | | |
| Sitemap on the new site lists the new URLs; submitted in Search Console | | |
| Domain change: Change of Address submitted in Search Console | | |
| Forms, tracking, and the key pages verified from outside (phone on mobile data) | | |
| Old hosting kept for at least 30 days as the rollback | | |

## 7. Monitoring (T+1 day, T+1 week, T+1 month)

| Check | Done | Evidence |
|---|---|---|
| Search Console: Pages report — "Not found (404)" and "Redirect error" lists reviewed | | |
| Server/platform 404 log reviewed; new 404s mapped or accepted | | |
| Performance report compared with the baseline for the key pages | | |
| check_redirects.py re-run (redirects have a way of being "cleaned up") | | |
| Old-host traffic trending to zero before it is switched off | | |

## Not checked (and why)

Write here what you could not verify, so nobody reads a blank as a pass.
