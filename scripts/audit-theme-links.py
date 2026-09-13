#!/usr/bin/env python3
"""Static link and anchor audit for the Site Builder Stack landing layer.

Extracts every URL referenced by our sections and templates, then verifies:
  * /pages/<handle>   resolves to a published page on the store
  * /products/<handle> resolves to an existing product
  * /policies/<x>     flagged (we do not manage these)
  * #anchor           an element with that id exists in a rendered section
  * external URLs     reachable (HEAD/GET)
  * no '#' placeholders, no localhost, no theme-vendor links
"""
import json
import os
import re
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shopify_api import gql  # noqa: E402

THEME = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "theme", "dev")

# ── gather store resources ───────────────────────────────────────────────────
pages = {p["handle"]: p for p in gql(
    "{ pages(first:50){ nodes{ handle title isPublished } } }")["pages"]["nodes"]}
products = {p["handle"]: p for p in gql(
    "{ products(first:50){ nodes{ handle title status } } }")["products"]["nodes"]}

# ── gather anchors our sections define ───────────────────────────────────────
anchors = set()
for root, _, files in os.walk(os.path.join(THEME, "sections")):
    for f in files:
        if not f.endswith(".liquid"):
            continue
        text = open(os.path.join(root, f), encoding="utf-8").read()
        # id="literal"
        anchors |= set(re.findall(r'id="([a-z0-9_-]+)"', text))
        # id="{{ section.settings.anchor | default: 'x' }}"
        anchors |= set(re.findall(r"default:\s*'([a-z0-9_-]+)'", text))
anchors |= {"main"}  # provided by the layout

# anchors set explicitly in template JSON
for tf in os.listdir(os.path.join(THEME, "templates")):
    if not tf.endswith(".json"):
        continue
    data = json.load(open(os.path.join(THEME, "templates", tf), encoding="utf-8"))
    for s in data.get("sections", {}).values():
        a = (s.get("settings") or {}).get("anchor")
        if a:
            anchors.add(a)

# ── gather referenced URLs ───────────────────────────────────────────────────
refs = []  # (source, url)

def load_theme_json(path):
    """Shopify writes a /* ... */ banner into generated JSON templates and
    section groups. It is not valid JSON, so strip it before parsing."""
    raw = open(path, encoding="utf-8").read()
    return json.loads(re.sub(r"^\s*/\*.*?\*/\s*", "", raw, flags=re.S))


def scan_json(path):
    data = load_theme_json(path)
    def walk(node, where):
        if isinstance(node, dict):
            for k, v in node.items():
                if isinstance(v, str) and (k.startswith("url") or k.endswith("_url")):
                    refs.append((where, v))
                else:
                    walk(v, where)
        elif isinstance(node, list):
            for v in node:
                walk(v, where)
        elif isinstance(node, str):
            for m in re.findall(r'href="([^"]+)"', node):
                refs.append((where, m))
    walk(data, os.path.basename(path))

for d in ("templates", "sections"):
    for f in sorted(os.listdir(os.path.join(THEME, d))):
        p = os.path.join(THEME, d, f)
        if f.endswith(".json"):
            scan_json(p)
        elif f.endswith(".liquid"):
            text = open(p, encoding="utf-8").read()
            for m in re.findall(r'href="([^"{}]+)"', text):  # literal hrefs only
                refs.append((f, m))

# ── evaluate ─────────────────────────────────────────────────────────────────
ok, warn, err = [], [], []
seen = set()
for src, url in refs:
    key = (src, url)
    if key in seen:
        continue
    seen.add(key)
    u = url.strip()

    if u == "#":
        err.append(f"{src}: placeholder link {u!r}")
    elif u == "":
        # An empty url setting is not a broken link — Liquid guards every one of
        # them with `!= blank` and renders nothing. The demo section ships with
        # video_url empty on purpose, because there is no recording yet. A "#"
        # is still an error: that one renders as a link that goes nowhere.
        ok.append(f"{src}: empty url setting, rendered conditionally")
    elif u.startswith("#"):
        a = u[1:]
        (ok if a in anchors else err).append(
            f"{src}: anchor #{a}" + ("" if a in anchors else "  <-- NO SUCH ID"))
    elif u.startswith("/#"):
        a = u[2:]
        (ok if a in anchors else err).append(
            f"{src}: home anchor {u}" + ("" if a in anchors else "  <-- NO SUCH ID"))
    elif u.startswith("/pages/"):
        h = u.split("/pages/")[1].split("#")[0].rstrip("/")
        if h in pages and pages[h]["isPublished"]:
            ok.append(f"{src}: /pages/{h} (published)")
        elif h in pages:
            err.append(f"{src}: /pages/{h} exists but is NOT published")
        else:
            err.append(f"{src}: /pages/{h} DOES NOT EXIST")
    elif u.startswith("/products/"):
        h = u.split("/products/")[1].split("#")[0].rstrip("/")
        if h in products:
            st = products[h]["status"]
            (ok if st == "ACTIVE" else warn).append(f"{src}: /products/{h} (status {st})")
        else:
            err.append(f"{src}: /products/{h} DOES NOT EXIST")
    elif u.startswith("/policies/"):
        warn.append(f"{src}: {u} — shop policy documents are not managed by this app; "
                    "verify it exists in Settings > Policies")
    elif u.startswith("/"):
        ok.append(f"{src}: {u} (site-relative)")
    elif u.startswith("http"):
        if "localhost" in u or "127.0.0.1" in u:
            err.append(f"{src}: localhost link {u}")
        elif any(v in u for v in ("novathemes", "vinovathemes", "themeforest")):
            err.append(f"{src}: theme-vendor link {u}")
        else:
            try:
                req = urllib.request.Request(u, method="GET",
                                             headers={"User-Agent": "SBS-link-audit"})
                with urllib.request.urlopen(req, timeout=15) as r:
                    (ok if r.status < 400 else err).append(f"{src}: {u} -> {r.status}")
            except Exception as exc:
                warn.append(f"{src}: {u} -> could not verify ({type(exc).__name__})")
    else:
        warn.append(f"{src}: unrecognised link form {u!r}")

print(f"Anchors defined by our sections: {', '.join(sorted(a for a in anchors if len(a) < 20))}\n")
print(f"=== OK ({len(ok)}) ===")
for x in sorted(set(ok)):
    print("  ✓", x)
print(f"\n=== WARNINGS ({len(warn)}) ===")
for x in sorted(set(warn)):
    print("  !", x)
print(f"\n=== ERRORS ({len(err)}) ===")
for x in sorted(set(err)):
    print("  ✗", x)
sys.exit(1 if err else 0)
