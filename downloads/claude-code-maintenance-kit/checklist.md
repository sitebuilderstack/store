# Website maintenance checklist — daily / weekly / monthly

Companion to https://sitebuilderstack.com/blogs/guides/claude-code-website-maintenance
A starting cadence, not a rule: move items as your site's risk changes. Items
marked (host) are handled by a hosted platform (Shopify, managed WordPress,
Webflow, Squarespace) — listed so you know they are not yours to run, and so
you can still verify the parts that are.

## Daily — 2 minutes, or automated

- [ ] Homepage and the one page that earns money return 200 from outside (a phone on mobile data, or an uptime monitor)
- [ ] No incident overnight (monitor / status page)

## Weekly — 15 to 30 minutes

- [ ] Every form that matters: one marked test submission, confirmed in the inbox or system a human reads; send and arrival times recorded
- [ ] Navigation and footer links resolve to the page their label names (weekly_check.py covers "resolves"; the label check is yours)
- [ ] Broken links on the key pages; 404 log reviewed for new entries
- [ ] TLS certificate valid with more than 14 days to expiry (host)
- [ ] Security headers unchanged from the baseline (host)
- [ ] Analytics still receiving events (real-time view)
- [ ] weekly_check.py run; report saved with the date

## Monthly — 1 to 2 hours

- [ ] Dependencies: platform, plugins/packages, theme — reviewed; updates applied on staging first, then production, with a rollback point (host: apps list reviewed instead; leftovers removed)
- [ ] Configuration drift: settings, redirects, DNS records compared with the recorded baseline
- [ ] Backup: restore one backup somewhere and open it. "Job succeeded" is not this item. (host: verify an export instead — theme download, data CSVs — and that you can open them)
- [ ] Rollback readiness: the previous release/theme still exists and the steps are written down
- [ ] Performance on the key pages compared with last month
- [ ] Certificate renewal log reviewed if you run your own (a failing auto-renew looks like "enabled")
- [ ] Report written from evidence (report-template.md)

## Quarterly

- [ ] Access review: who can deploy, who can publish, who has admin; remove leavers
- [ ] Secrets rotated where policy requires; none in the repository
- [ ] The checklist itself reviewed: what failed this quarter that was not on it?
