#!/usr/bin/env python3
"""Assemble the self-contained artifact page.

The published artifact must not depend on anything being served beside it,
so every source file in this folder is inlined into one HTML file.

    python3 build.py

Writes:
    index.html          the file that is published (no <html>/<head>/<body>:
                        the Artifact runtime wraps it)
    tests/preview.html  the same page inside a document shell that matches
                        the runtime's, for local browser tests
"""
from __future__ import annotations

import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE / "src"

TITLE = "SiteBuilderStack Website Action Planner"

def read(p: pathlib.Path) -> str:
    return p.read_text(encoding="utf-8")

def js_json(obj) -> str:
    # `</script` can never appear in this data, but escaping `<` makes that
    # structural rather than a thing to remember.
    return json.dumps(obj, ensure_ascii=False).replace("<", "\\u003c")

def build() -> str:
    products = json.loads(read(HERE / "products.json"))
    css = read(SRC / "styles.css")
    rules = read(HERE / "recommendation-rules.js")
    analytics = read(SRC / "analytics.js")
    config = read(SRC / "config.js")
    app = read(SRC / "app.js")

    brand_href = (
        "https://sitebuilderstack.com/?utm_source=claude_artifact"
        "&amp;utm_medium=interactive_tool&amp;utm_campaign=website_action_planner"
        "&amp;utm_content=header_brand"
    )

    return f"""<title>{TITLE}</title>
<meta name="description" content="Answer a few questions and get a practical website action plan, a starter Claude Code prompt and a matched toolkit recommendation.">
<style>
{css}
</style>

<header class="topbar">
  <div class="wrap wrap--wide topbar__in">
    <a class="brand" href="{brand_href}" target="_blank" rel="noopener">
      <span class="brand__mark" aria-hidden="true">S</span>
      <span>SiteBuilderStack</span>
      <span class="brand__sub">Website Action Planner</span>
    </a>
    <div class="topbar__acts">
      <a class="btn btn--quiet btn--sm" href="{brand_href}" target="_blank" rel="noopener">sitebuilderstack.com &#8599;</a>
    </div>
  </div>
</header>

<main id="main">
  <div id="app"></div>
</main>

<script>
window.SBS_PRODUCTS = {js_json(products)};
</script>
<script>
{rules}
</script>
<script>
{analytics}
</script>
<script>
{config}
</script>
<script>
{app}
</script>
"""

SHELL_HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<style>
  :root { color-scheme: light dark; padding-top: env(safe-area-inset-top, 0px); padding-bottom: env(safe-area-inset-bottom, 0px); }
  body { margin: 0; font: 14px system-ui, sans-serif; background: #fafaf9; }
  img { max-width: 100%; }
  [hidden] { display: none !important; }
</style>
</head>
<body>
"""

def main() -> int:
    page = build()
    (HERE / "index.html").write_text(page, encoding="utf-8")
    (HERE / "tests").mkdir(exist_ok=True)
    (HERE / "tests" / "preview.html").write_text(SHELL_HEAD + page + "\n</body>\n</html>\n", encoding="utf-8")
    size = len(page.encode("utf-8"))
    print(f"index.html        {size:>8,} bytes  ({size / 1048576:.2f} MiB of the 16 MiB limit)")
    print(f"tests/preview.html written")
    if size > 16 * 1024 * 1024:
        print("ERROR: over the 16 MiB rendered-page limit", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
