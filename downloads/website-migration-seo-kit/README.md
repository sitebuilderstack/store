# Website migration SEO kit

Companion download for
https://sitebuilderstack.com/blogs/guides/website-migration-seo-checklist-claude-code

- `migration-checklist.md` — the checklist from the guide, with an evidence
  column per line and a "not checked" section.
- `url-map-sample.csv` — the URL map format the checker reads, with example
  rows for MOVE, MERGE, REMOVE and KEEP.
- `check_redirects.py` — a bounded, read-only redirect validator (Python 3.8+,
  standard library, no dependencies). For every row it requests the source URL
  without following redirects, walks the chain hop by hop, and checks status,
  hop count, final destination and page identity. It stops on the first
  malformed row, times out per request, and caps the number of rows.

      python3 check_redirects.py url-map-sample.csv --report report.md
      python3 check_redirects.py url-map.csv --host-rewrite new.example=staging.new.example

The example rows point at `old.example` / `new.example`, which do not exist;
replace them with your own map. The checker never writes anything but the
report and never sends credentials.
