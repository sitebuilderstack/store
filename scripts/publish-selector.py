#!/usr/bin/env python3
"""Write the learning-path engine's blocks into theme/dev/templates/index.json.

The roadmaps live in content/workflow-selector.json so they can be validated.
This turns that file into the section blocks the theme renders, and refuses to
run if validation fails — an invented URL cannot reach a template.

The section keeps whatever position the theme editor gave it; only the blocks
and their settings are rewritten.

Usage: publish-selector.py [--dry-run]
"""
import collections
import io
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TEMPLATE = os.path.join(ROOT, "theme", "dev", "templates", "index.json")
CONFIG = os.path.join(ROOT, "content", "workflow-selector.json")
SECTION_ID = "selector"
LEVELS = ("beginner", "intermediate", "experienced")


def main():
    if subprocess.call([sys.executable, os.path.join(HERE, "validate-selector.py")],
                       stdout=subprocess.DEVNULL):
        raise SystemExit("validate-selector.py failed; not writing the template")

    cfg = json.load(io.open(CONFIG, encoding="utf-8"))
    tpl = json.loads(io.open(TEMPLATE, encoding="utf-8").read(),
                     object_pairs_hook=collections.OrderedDict)
    products = cfg["products"]

    blocks, order = collections.OrderedDict(), []
    for i, g in enumerate(cfg["goals"], 1):
        bid = "g%d" % i
        s = collections.OrderedDict()
        s["goal_value"] = g["value"]
        s["goal_label"] = g["label"]
        for lv in LEVELS:
            s["start_%s_url" % lv] = g["start"][lv]["url"]
            s["start_%s_label" % lv] = g["start"][lv]["label"]
        for n, st in enumerate(g["steps"], 1):
            s["step%d_kind" % n] = st["kind"]
            s["step%d_url" % n] = st["url"]
            s["step%d_label" % n] = st["label"]
            s["step%d_note" % n] = st.get("note", "")
        s["hub_url"] = g["hub"]["url"]
        s["hub_label"] = g["hub"]["label"]
        p = products[g["product"]]
        s["product_handle"] = p["handle"]
        s["product_note"] = p["note"]
        blocks[bid] = collections.OrderedDict([("type", "goal"), ("settings", s)])
        order.append(bid)

    existing = tpl["sections"].get(SECTION_ID, {})
    settings = existing.get("settings") or collections.OrderedDict([
        ("anchor", "start"),
        ("eyebrow", "Find your route"),
        ("heading", "What are you trying to build?"),
        ("intro", "Three questions, then a seven-step route through the free guides "
                  "for exactly that job. Tick steps off as you go — your progress is "
                  "saved in this browser, with no account."),
        ("browse_heading", "Or browse by topic"),
    ])
    # The heading and intro describe an engine that now asks three questions.
    settings["heading"] = "What are you trying to build?"
    settings["intro"] = ("Three questions, then a seven-step route through the free "
                         "guides for exactly that job. Tick steps off as you go — your "
                         "progress is saved in this browser, with no account.")

    tpl["sections"][SECTION_ID] = collections.OrderedDict([
        ("type", "sbs-selector"),
        ("blocks", blocks),
        ("block_order", order),
        ("settings", settings),
    ])
    if SECTION_ID not in tpl["order"]:
        pos = tpl["order"].index("hero") + 1 if "hero" in tpl["order"] else 0
        tpl["order"].insert(pos, SECTION_ID)

    out = json.dumps(tpl, indent=2, ensure_ascii=False) + "\n"
    if "--dry-run" in sys.argv:
        print("would write %d goal block(s)" % len(order))
        return 0
    io.open(TEMPLATE, "w", encoding="utf-8").write(out)
    print("wrote %d goal block(s) into index.json" % len(order))
    print("homepage order: %s" % " -> ".join(tpl["order"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
