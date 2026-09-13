#!/usr/bin/env python3
"""Check the literal numbers in agents.md.liquid against reality.

templates/agents.md.liquid runs in a RESTRICTED Liquid context: only `request`
and `agents` exist, so there is no product object and no price. Anything not
exposed by `agents` has to be written out literally — which means it can drift
silently from the product it describes.

This asserts the literal claims still hold:
  * the price against the live product variant
  * file, module and prompt counts against the shipped bundle
  * the stated word floor against the real word count
  * every guide and page URL against what is actually published

Usage: audit-agents-claims.py
"""
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from shopify_api import gql  # noqa: E402

ROOT = os.path.dirname(HERE)
TPL = os.path.join(ROOT, "theme", "dev", "templates", "agents.md.liquid")
BUNDLE = os.path.join(ROOT, "product", "Claude-Code-Website-Launch-System")
SEO_BUNDLE = os.path.join(ROOT, "product", "Claude-Code-SEO-Website-Audit-Toolkit")
OPS_BUNDLE = os.path.join(ROOT, "product", "Claude-Code-Website-Operations-Maintenance-System")
# What the Complete Site Builder Stack actually contains. The operations system
# is sold on its own, so it is deliberately not a component: if it were summed
# in, the file's "bought separately" total would claim the bundle holds it.
BUNDLE_COMPONENTS = ("claude-code-website-launch-system",
                     "claude-code-seo-website-audit-toolkit",
                     "claude-code-conversion-revenue-optimization-toolkit")
CRO_BUNDLE = os.path.join(ROOT, "product",
                          "Claude-Code-Conversion-Revenue-Optimization-Toolkit")

fail = []


def check(cond, msg):
    print("  %-58s %s" % (msg, "ok" if cond else "FAIL"))
    if not cond:
        fail.append(msg)


def main():
    src = io.open(TPL, encoding="utf-8").read()

    # ---- prices ---------------------------------------------------------
    # The store sells more than one product. Every price literal in the file
    # must match some live product's price, and every live product's price must
    # appear — a product added to the catalogue and not to this file is exactly
    # the drift this check exists to catch.
    d = gql("""{ products(first:20){ nodes{ handle status
                 variants(first:1){ nodes{ price } } } } }""")
    live = {p["handle"]: p["variants"]["nodes"][0]["price"]
            for p in d["products"]["nodes"] if p["status"] == "ACTIVE"}
    live_prices = {float(v) for v in live.values()}
    stated = {float(v) for v in re.findall(r"\$(\d+(?:\.\d+)?)", src)}

    # The bundle entry legitimately states a total as well as a price: "bought
    # separately the three cost $197". That is not a product price, so it is
    # allowed only when it is exactly the sum of the non-bundle products'
    # live prices. If any component price changed, the stated total would stop
    # matching and this check would fail -- which is the behaviour wanted, and
    # the reason for computing it rather than adding 197.0 to an exempt list.
    components = {h: float(v) for h, v in live.items() if h in BUNDLE_COMPONENTS}
    allowed = set(live_prices) | {round(sum(components.values()), 2)}
    unknown = sorted(stated - allowed)
    missing = sorted(live_prices - stated)
    check(bool(stated) and not unknown and not missing,
          "price literals %s match the live products %s%s%s"
          % (sorted(stated), sorted(live_prices),
             "" if not unknown else "  [not a live price: %s]" % unknown,
             "" if not missing else "  [live price not stated: %s]" % missing))

    # Every active product must be linked from this file.
    for handle in sorted(live):
        check("/products/" + handle in src, "product is listed: %s" % handle)

    # ---- bundle counts --------------------------------------------------
    files = sum(len(f) for _, _, f in os.walk(BUNDLE))
    modules = len([d for d in os.listdir(BUNDLE)
                   if re.match(r"^\d\d-", d) and os.path.isdir(os.path.join(BUNDLE, d))])
    words = 0
    for root, _, fs in os.walk(BUNDLE):
        for f in fs:
            if f.endswith(".md"):
                words += len(io.open(os.path.join(root, f), encoding="utf-8",
                                     errors="replace").read().split())
    lib = os.path.join(BUNDLE, "15-Claude-Code-Prompt-Library")
    prompts = 0
    for f in os.listdir(lib):
        if f.endswith("-PROMPTS.md"):
            body = io.open(os.path.join(lib, f), encoding="utf-8").read()
            prompts += len([h for h in re.findall(r"^## (.+)$", body, re.M)
                            if h.strip().lower() not in ("the index", "index")])

    m = re.search(r"(\d+) files across (\d+) modules", src)
    check(m and int(m.group(1)) == files, "stated file count matches the bundle (%d)" % files)
    check(m and int(m.group(2)) == modules, "stated module count matches the bundle (%d)" % modules)

    mp = re.search(r"(\d+) reusable prompts", src)
    check(mp and int(mp.group(1)) == prompts, "stated prompt count matches the library (%d)" % prompts)

    # The other two products state their own counts in this file. They were
    # unchecked while only the flagship's were asserted, which is precisely how
    # the flagship's got checked in the first place: a number written once and
    # never compared to anything.
    def count_files(root):
        return sum(len(f) for _, _, f in os.walk(root))

    def count_modules(root):
        return len([d for d in os.listdir(root)
                    if re.match(r"^\d\d-", d) and os.path.isdir(os.path.join(root, d))])

    seo_files, seo_modules = count_files(SEO_BUNDLE), count_modules(SEO_BUNDLE)
    seo_prompts = len([f for f in os.listdir(os.path.join(SEO_BUNDLE, "prompts"))
                       if f.endswith(".md")])
    ms = re.search(r"(\d+) files across (\d+) modules\n  - (\d+) audit prompts", src)
    check(ms and int(ms.group(1)) == seo_files,
          "SEO toolkit file count matches its bundle (%d)" % seo_files)
    check(ms and int(ms.group(2)) == seo_modules,
          "SEO toolkit module count matches its bundle (%d)" % seo_modules)
    check(ms and int(ms.group(3)) == seo_prompts,
          "SEO toolkit prompt count matches its bundle (%d)" % seo_prompts)

    cro_files, cro_modules = count_files(CRO_BUNDLE), count_modules(CRO_BUNDLE)
    cro_workflows = len([1 for d in sorted(os.listdir(CRO_BUNDLE))
                         if re.match(r"^(0[1-9]|1[0-2])-", d)
                         and os.path.isdir(os.path.join(CRO_BUNDLE, d))
                         for f in os.listdir(os.path.join(CRO_BUNDLE, d))
                         if f.endswith(".md")])
    cro_commands = 0
    cdir = os.path.join(CRO_BUNDLE, "commands")
    for f in sorted(os.listdir(cdir)):
        if f.endswith(".md") and f != "COMMANDS.md":
            cro_commands += len(re.findall(
                r"^## C-\d+", io.open(os.path.join(cdir, f), encoding="utf-8").read(), re.M))
    ops_files, ops_modules = count_files(OPS_BUNDLE), count_modules(OPS_BUNDLE)
    ops_commands = len([f for f in os.listdir(os.path.join(OPS_BUNDLE, "commands"))
                        if f.endswith(".md") and f != "COMMANDS.md"])
    ops_scripts = len([f for f in os.listdir(os.path.join(OPS_BUNDLE, "scripts"))
                       if f.endswith(".py") and f != "_common.py"])
    mo = re.search(r"(\d+) files across (\d+) modules\n  - (\d+) slash commands", src)
    check(mo and int(mo.group(1)) == ops_files,
          "Operations system file count matches its bundle (%d)" % ops_files)
    check(mo and int(mo.group(2)) == ops_modules,
          "Operations system module count matches its bundle (%d)" % ops_modules)
    check(mo and int(mo.group(3)) == ops_commands,
          "Operations system command count matches its bundle (%d)" % ops_commands)
    mo2 = re.search(r"(\d+) Python scripts", src)
    check(mo2 and int(mo2.group(1)) == ops_scripts,
          "Operations system script count matches its bundle (%d)" % ops_scripts)
    mc = re.search(r"(\d+) files across (\d+) modules\n  - (\d+) workflows", src)
    check(mc and int(mc.group(1)) == cro_files,
          "CRO toolkit file count matches its bundle (%d)" % cro_files)
    check(mc and int(mc.group(2)) == cro_modules,
          "CRO toolkit module count matches its bundle (%d)" % cro_modules)
    check(mc and int(mc.group(3)) == cro_workflows,
          "CRO toolkit workflow count matches its bundle (%d)" % cro_workflows)
    mcc = re.search(r"(\d+) reusable commands across", src)
    check(mcc and int(mcc.group(1)) == cro_commands,
          "CRO toolkit command count matches its bundle (%d)" % cro_commands)

    mw = re.search(r"More than ([\d,]+) words", src)
    floor = int(mw.group(1).replace(",", "")) if mw else 0
    check(mw and floor <= words,
          "stated word floor %s is still true (actual %d)" % (mw.group(1) if mw else "?", words))

    # ---- every URL it advertises still exists ---------------------------
    handles = set(re.findall(r"/blogs/guides/([a-z0-9-]+)", src))
    pages = set(re.findall(r"/pages/([a-z0-9-]+)", src))
    d = gql("""{ blogs(first:5){ nodes{ articles(first:100){ nodes{ handle } } } }
                pages(first:100){ nodes{ handle } } }""")
    live_articles = {a["handle"] for b in d["blogs"]["nodes"] for a in b["articles"]["nodes"]}
    live_pages = {p["handle"] for p in d["pages"]["nodes"]}
    check(not (handles - live_articles),
          "every guide URL exists (%d listed)" % len(handles))
    if handles - live_articles:
        print("      dangling:", sorted(handles - live_articles))
    check(not (pages - live_pages), "every page URL exists (%d listed)" % len(pages))
    if pages - live_pages:
        print("      dangling:", sorted(pages - live_pages))

    # ---- and every published guide is advertised ------------------------
    missing = live_articles - handles
    check(not missing, "every published guide is listed (%d live)" % len(live_articles))
    if missing:
        print("      not listed:", sorted(missing))

    print()
    print("%d failure(s)" % len(fail))
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
