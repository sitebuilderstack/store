# Claude Code website maintenance kit

Companion download for
https://sitebuilderstack.com/blogs/guides/claude-code-website-maintenance

- `checklist.md` — daily / weekly / monthly / quarterly checklist, with the
  items a hosted platform handles marked.
- `report-template.md` — the report, with an evidence column and a
  "not checked" section.
- `prompts.md` — the read-only inspection prompt and the separate
  one-finding remediation prompt.
- `weekly_check.py` — a read-only outside-in check (Python 3.8+, standard
  library): page status, expected content, certificate days to expiry,
  same-host links (bounded). Writes a Markdown report. Copy
  `check.example.json`, put your own URLs in, and run:

      python3 weekly_check.py check.json --report reports/$(date +%F).md

The script cannot tell you whether a form delivers or a backup restores; the
checklist keeps those as manual items and the report template has a row for
each.
