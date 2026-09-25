#!/usr/bin/env python3
"""Assemble each guide tool into one self-contained artifact page.

    python3 build.py

Each tool is <name>/body.html plus <name>/app.js. The shared tokens in
_tokens.css are inlined into every one, so a published page depends on
nothing being served beside it.
"""
import pathlib, sys

HERE = pathlib.Path(__file__).resolve().parent
TOKENS = (HERE / "_tokens.css").read_text(encoding="utf-8")

TOOLS = {
    "seo-review": "Shopify SEO Review Worksheet",
    "product-page": "Digital Product Page Builder",
    "scope-builder": "Website Scope Builder",
    "aeo-checker": "Answer Engine Readiness",
}

SHELL = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<style>:root{color-scheme:light dark;padding-top:env(safe-area-inset-top,0px);
padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0;font:14px system-ui,sans-serif;
background:#faf9f5}img{max-width:100%}[hidden]{display:none!important}</style>
</head><body>
"""


def build(name: str, title: str) -> int:
    d = HERE / name
    body = (d / "body.html").read_text(encoding="utf-8")
    app = (d / "app.js").read_text(encoding="utf-8")
    page = (f"<title>{title}</title>\n"
            f"<style>\n{TOKENS}\n{(d / 'style.css').read_text(encoding='utf-8') if (d / 'style.css').exists() else ''}\n</style>\n\n"
            f"{body}\n\n<script>\n{app}\n</script>\n")
    (d / "index.html").write_text(page, encoding="utf-8")
    (d / "preview.html").write_text(SHELL + page + "\n</body></html>\n", encoding="utf-8")
    n = len(page.encode("utf-8"))
    print(f"{name:16s} index.html {n:>8,} bytes")
    return 1 if n > 16 * 1024 * 1024 else 0


if __name__ == "__main__":
    bad = 0
    for k, v in TOOLS.items():
        if (HERE / k / "body.html").exists():
            bad += build(k, v)
    raise SystemExit(bad)
