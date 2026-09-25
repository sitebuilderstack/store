#!/usr/bin/env python3
"""Render a static HTML approximation of the landing page for visual QA.

This is NOT a Liquid engine. It handles only the constructs used in our own
sbs-* sections, so it can turn templates/index.json + the section files into
something a browser can display. It exists because the storefront is
password-protected and cannot be rendered remotely.

Treat the output as a layout and design check, not as proof the Liquid renders
identically on Shopify. `shopify theme check` covers Liquid correctness.

Usage: render-preview.py <themeDir> <template.json> <out.html>
"""
import io
import json
import os
import re
import sys

THEME, TEMPLATE, OUT = sys.argv[1], sys.argv[2], sys.argv[3]

# Stand-in Shopify globals
CTX = {
    "shop.name": "Site Builder Stack",
    "routes.root_url": "/",
    "cart.currency.iso_code": "USD",
    "'now' | date: '%Y'": "2026",
}
PRODUCT = {
    "title": "The Claude Code Website Launch System",
    "price_money": "$19.99",
    "price_short": "$19.99",
    "vendor": "Site Builder Stack",
    "available": True,
}


def strip_schema(src):
    return re.sub(r"\{%\s*schema\s*%\}.*?\{%\s*endschema\s*%\}", "", src, flags=re.S)


def strip_comments(src):
    return re.sub(r"\{%-?\s*comment\s*-?%\}.*?\{%-?\s*endcomment\s*-?%\}", "", src, flags=re.S)


def val(settings, key, default=""):
    v = settings.get(key)
    return default if v in (None, "") else v


def resolve_expr(expr, settings, block=None, loop_index=None):
    """Resolve a {{ ... }} expression to a string."""
    # Strip Liquid whitespace-control markers: {{- ... -}}
    e = expr.strip().lstrip("-").rstrip("-").strip()

    # forloop counter used for 01, 02 …
    if e.startswith("forloop.index0"):
        return f"{(loop_index or 0) + 1:02d}"

    # default filter
    default = ""
    m = re.search(r"\|\s*default:\s*'([^']*)'", e) or \
        re.search(r'\|\s*default:\s*"([^"]*)"', e)
    if m:
        default = m.group(1)
    m = re.search(r"\|\s*default:\s*shop\.name", e)
    if m:
        default = PRODUCT["vendor"]

    base = e.split("|")[0].strip()

    if base.startswith("section.settings."):
        return str(val(settings, base.split("section.settings.")[1], default))
    if base.startswith("block.settings.") and block is not None:
        return str(val(block.get("settings", {}), base.split("block.settings.")[1], default))
    if base.startswith("form."):
        return ""
    if base.startswith("page."):
        return {"page.title": "Privacy Policy",
                "page.content": "<p>Sample page body used only for layout preview.</p>",
                "page.url": "/pages/privacy-policy"}.get(base, "")
    if base.startswith("product.featured_media") or "image_url" in e:
        return "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='1600' height='1200'%3E%3Crect width='100%25' height='100%25' fill='%23171B26'/%3E%3C/svg%3E"
    if base == "product.description":
        return "<p>Sample product description used only for layout preview.</p>"
    if base in ("product.title", "PRODUCT.title"):
        return PRODUCT["title"]
    if base == "product.vendor":
        return PRODUCT["vendor"]
    if "price | money_without_trailing_zeros" in e or "price_short" in e:
        return PRODUCT["price_short"]
    if "price | money" in e:
        return PRODUCT["price_money"]
    if base == "cart.currency.iso_code":
        return "USD"
    if base == "shop.name":
        return PRODUCT["vendor"]
    if "date: '%Y'" in e:
        return "2026"
    if base.endswith(".width"):
        return "1600"
    if base.endswith(".height"):
        return "1200"
    if base.startswith("routes."):
        return "/"
    if base == "block.id":
        return (block or {}).get("_id", "blk")
    if base.startswith("section.settings"):
        return default
    return default


ASSIGN_RE = re.compile(r"\{%-?\s*assign\s+(\w+)\s*=\s*(.+?)\s*-?%\}")


def apply_assigns(text, settings, block):
    """Resolve {% assign x = ... %} then substitute {{ x }} occurrences."""
    vars_ = {}

    def collect(m):
        name, expr = m.group(1), m.group(2)
        # 'literal' | append: block.id   →  literal + block id
        parts = [p.strip() for p in expr.split("|")]
        out = ""
        first = parts[0]
        if first.startswith("'") and first.endswith("'"):
            out = first[1:-1]
        else:
            out = resolve_expr(first, settings, block)
        for f in parts[1:]:
            am = re.match(r"append:\s*(.+)", f)
            if am:
                a = am.group(1).strip()
                out += (a[1:-1] if a.startswith("'") else resolve_expr(a, settings, block))
        vars_[name] = out
        return ""

    text = ASSIGN_RE.sub(collect, text)
    for name, v in vars_.items():
        text = re.sub(r"\{\{-?\s*" + re.escape(name) + r"\s*-?\}\}", v, text)
    return text


def render(src, settings, blocks):
    src = strip_schema(strip_comments(src))

    # for-loops over section.blocks
    def do_for(m):
        body = m.group(1)
        out = []
        for i, b in enumerate(blocks):
            chunk = body
            chunk = apply_assigns(chunk, settings, b)
            # nested if inside the loop
            chunk = resolve_ifs(chunk, settings, b)
            chunk = re.sub(r"\{\{(.*?)\}\}",
                           lambda mm: resolve_expr(mm.group(1), settings, b, i), chunk)
            chunk = chunk.replace("{{ block.shopify_attributes }}", "")
            out.append(chunk)
        return "".join(out)

    src = re.sub(r"\{%-?\s*for block in section\.blocks\s*-?%\}(.*?)\{%-?\s*endfor\s*-?%\}",
                 do_for, src, flags=re.S)

    src = apply_assigns(src, settings, None)
    src = resolve_ifs(src, settings, None)
    src = re.sub(r"\{\{(.*?)\}\}", lambda m: resolve_expr(m.group(1), settings), src)
    # anything left over
    src = re.sub(r"\{%-?.*?-?%\}", "", src, flags=re.S)
    return src


def resolve_ifs(src, settings, block):
    """Handle {% if X != blank %} / {% if X %} / {% unless %} for our patterns."""
    # Match INNERMOST if-blocks only (body contains no further {% if %}), then
    # loop until stable. Without this, an outer {% if %} pairs with an inner
    # {% endif %} and the markup is shredded.
    NOIF = r"(?:(?!\{%-?\s*if\b).)*?"
    pattern = re.compile(
        r"\{%-?\s*if\s+((?:(?!-?%\}).)+?)\s*-?%\}(" + NOIF + r")"
        r"(?:\{%-?\s*else\s*-?%\}(" + NOIF + r"))?"
        r"\{%-?\s*endif\s*-?%\}",
        re.S)

    def once(text):
        def rep(m):
            cond, yes, no = m.group(1), m.group(2), m.group(3) or ""
            neg = "!=" in cond and "blank" in cond
            base = cond.split("!=")[0].split("==")[0].strip()
            if base.startswith("section.settings."):
                v = val(settings, base.split("section.settings.")[1])
            elif base.startswith("block.settings.") and block:
                v = val(block.get("settings", {}), base.split("block.settings.")[1])
            elif base.startswith("form.") or "form.errors" in cond:
                v = False          # unsubmitted form: no success, no errors
            elif "product" in base:
                v = True
            elif "available" in cond:
                v = PRODUCT["available"]
            elif "section.blocks.size" in cond:
                v = True
            else:
                v = True
            truthy = bool(v) if not neg else bool(v)
            return yes if truthy else no
        return pattern.sub(rep, text)

    prev = None
    while prev != src:
        prev, src = src, once(src)
    return src


def load_section(name):
    p = os.path.join(THEME, "sections", f"{name}.liquid")
    return open(p, encoding="utf-8").read()


tpl = json.load(open(TEMPLATE, encoding="utf-8"))
css = open(os.path.join(THEME, "assets", "sbs.css"), encoding="utf-8").read()
js = open(os.path.join(THEME, "assets", "sbs.js"), encoding="utf-8").read()

def load_theme_json(path):
    """Parse a Shopify theme JSON file, tolerating its comment banner.

    Shopify writes a /* ... */ header into section-group files it manages, and
    plain json.load rejects it. This renderer used to call json.load directly,
    which meant it raised on every run — so the rendered accessibility and
    overflow checks behind --with-render never executed at all. They reported
    nothing, which read as nothing being wrong.
    """
    raw = io.open(path, encoding="utf-8").read()
    return json.loads(re.sub(r"^\s*/\*.*?\*/\s*", "", raw, flags=re.S))


groups = {}
for g in ("sbs-header-group", "sbs-footer-group"):
    gp = os.path.join(THEME, "sections", f"{g}.json")
    if os.path.exists(gp):
        groups[g] = load_theme_json(gp)

body = []


def schema_defaults(section_src):
    """Default values declared in a section's own {% schema %}.

    Shopify falls back to these for any setting the template does not name.
    This renderer used to emit an empty string instead, which produced markup
    the live site never serves — an unlabelled input and an empty button on the
    opt-in form, reported by the accessibility audit as two real failures that
    do not exist. A checker that invents findings gets ignored, so the renderer
    has to match the platform here.

    Block settings are handled the same way, keyed by block type.
    """
    m = re.search(r"\{%\s*schema\s*%\}(.*?)\{%\s*endschema\s*%\}", section_src, re.S)
    if not m:
        return {}, {}
    try:
        sch = json.loads(m.group(1))
    except ValueError:
        return {}, {}
    sec = {s["id"]: s["default"] for s in sch.get("settings", [])
           if isinstance(s, dict) and "id" in s and "default" in s}
    blk = {}
    for b in sch.get("blocks", []):
        blk[b.get("type")] = {s["id"]: s["default"] for s in b.get("settings", [])
                              if isinstance(s, dict) and "id" in s and "default" in s}
    return sec, blk


def emit(sdef):
    stype = sdef["type"]
    try:
        src = load_section(stype)
    except FileNotFoundError:
        body.append(f"<!-- missing section {stype} -->")
        return
    sec_defaults, blk_defaults = schema_defaults(src)

    settings = dict(sec_defaults)
    settings.update(sdef.get("settings", {}))

    blocks = []
    for bid in sdef.get("block_order", []):
        b = dict(sdef["blocks"][bid])
        merged = dict(blk_defaults.get(b.get("type"), {}))
        merged.update(b.get("settings", {}))
        b["settings"] = merged
        b["_id"] = bid
        blocks.append(b)
    body.append(render(src, settings, blocks))


for g in ("sbs-header-group",):
    if g in groups:
        for sid in groups[g]["order"]:
            emit(groups[g]["sections"][sid])

body.append('<main id="main" tabindex="-1">')
for sid in tpl["order"]:
    emit(tpl["sections"][sid])
body.append("</main>")

for g in ("sbs-footer-group",):
    if g in groups:
        for sid in groups[g]["order"]:
            emit(groups[g]["sections"][sid])

html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Preview — {PRODUCT['vendor']}</title>
<style>{css}</style>
</head>
<body class="sbs">
<a class="sbs-skip" href="#main">Skip to content</a>
{''.join(body)}
<script>{js}</script>
</body></html>"""

open(OUT, "w", encoding="utf-8").write(html)
print(f"  wrote {OUT} ({len(html):,} bytes)")
leftover = len(re.findall(r"\{\{|\{%", html))
print(f"  unresolved liquid tags remaining: {leftover}")
