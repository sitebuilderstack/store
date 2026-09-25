#!/usr/bin/env python3
"""Generate theme/dev/snippets/sbs-lab-fixtures.liquid from content/labs/*.json.

Each lab is defined once, as data. This script writes the snippet the lab
section renders: for every lab, a JSON block the engine (assets/sbs-labs.js)
reads, and a complete static version of the same lab — scenario, evidence,
steps, options and answers — so the page is whole without JavaScript and is
never a thin fixture page. The generated file is committed; run this after
editing a lab and commit both.

    python3 scripts/build-labs.py          # write the snippet
    python3 scripts/build-labs.py --check  # exit 1 if the snippet is stale
"""
import glob
import html
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "theme", "dev", "snippets", "sbs-lab-fixtures.liquid")
INDEX = os.path.join(ROOT, "theme", "dev", "snippets", "sbs-labs-index.liquid")
REQUIRED = ("id", "handle", "title", "eyebrow", "short", "summary", "guide", "product",
            "module", "scenario", "sample", "starting", "evidence", "steps", "after", "closing")


def esc(s):
    return html.escape(str(s), quote=True)


def load_labs():
    labs = []
    for path in sorted(glob.glob(os.path.join(ROOT, "content", "labs", "*.json"))):
        with io.open(path, encoding="utf-8") as fh:
            lab = json.load(fh)
        validate(lab, os.path.basename(path))
        labs.append(lab)
    return labs


def validate(lab, name):
    """A lab that renders with a dangling evidence id or an answer that is
    not one of its options is broken in a way nobody notices until a reader
    clicks it. Refuse to build it."""
    for k in REQUIRED:
        if k not in lab:
            raise SystemExit("%s: missing %s" % (name, k))
    ids = {e["id"] for e in lab["evidence"]} | {e["id"] for e in lab["after"]}
    if len(ids) != len(lab["evidence"]) + len(lab["after"]):
        raise SystemExit("%s: duplicate evidence id" % name)
    if len(lab["steps"]) < 3:
        raise SystemExit("%s: fewer than 3 steps" % name)
    for s in lab["steps"]:
        for eid in s["evidence"]:
            if eid not in ids:
                raise SystemExit("%s: step %s references unknown evidence %s" % (name, s["id"], eid))
        d = s["decision"]
        opts = [o["id"] for o in d["options"]]
        if len(opts) < 2 or len(opts) != len(set(opts)):
            raise SystemExit("%s: step %s needs 2+ distinct options" % (name, s["id"]))
        if d["correct"] not in opts:
            raise SystemExit("%s: step %s correct answer %r is not an option" % (name, s["id"], d["correct"]))
        for o in opts:
            if o != d["correct"] and o not in d["explain"]["wrong"]:
                raise SystemExit("%s: step %s has no explanation for wrong answer %s" % (name, s["id"], o))
    if lab["handle"] != "lab-" + lab["id"]:
        raise SystemExit("%s: handle must be lab-<id>" % name)


def render_evidence(e):
    out = ['<figure class="sbs-lab__ev"><figcaption>%s</figcaption>' % esc(e["title"])]
    if e["kind"] == "table":
        out.append('<div class="sbs-lab__table"><table><thead><tr>%s</tr></thead><tbody>'
                   % "".join("<th>%s</th>" % esc(c) for c in e["columns"]))
        for row in e["rows"]:
            out.append("<tr>%s</tr>" % "".join("<td>%s</td>" % esc(c) for c in row))
        out.append("</tbody></table></div>")
    else:
        out.append('<pre class="sbs-lab__pre">%s</pre>' % esc(e["content"]))
    out.append("</figure>")
    return "".join(out)


def render_static(lab):
    """The whole lab as readable HTML: what a no-JS visitor and a crawler see."""
    ev = {e["id"]: e for e in lab["evidence"] + lab["after"]}
    o = []
    o.append('<div class="sbs-lab__static" data-lab-static>')
    o.append('<h2 id="lab-sample">%s</h2><p>%s</p>' % (esc(lab["sample"]["label"]), esc(lab["sample"]["note"])))
    dl = [a for a in lab["sample"]["artifacts"] if a.get("url")]
    if dl:
        o.append('<ul class="sbs-lab__downloads">%s</ul>' % "".join(
            '<li><a href="%s" download>%s</a></li>' % (esc(a["url"]), esc(a["label"])) for a in dl))
    o.append('<h2 id="lab-evidence">Evidence</h2>')
    for e in lab["evidence"]:
        o.append(render_evidence(e))
    o.append('<h2 id="lab-steps">Steps</h2>')
    for i, s in enumerate(lab["steps"], 1):
        o.append('<section class="sbs-lab__step"><h3>Step %d — %s</h3><p>%s</p>' % (i, esc(s["title"]), esc(s["instruction"])))
        o.append('<p class="sbs-lab__refs">Evidence: %s</p>' % ", ".join(esc(ev[x]["title"]) for x in s["evidence"]))
        d = s["decision"]
        o.append("<p><strong>%s</strong></p><ol class=\"sbs-lab__opts\">" % esc(d["question"]))
        for opt in d["options"]:
            o.append("<li>%s</li>" % esc(opt["label"]))
        o.append("</ol>")
        correct = [x for x in d["options"] if x["id"] == d["correct"]][0]
        o.append('<details class="sbs-lab__answer"><summary>Answer and explanation</summary><p><strong>%s</strong></p><p>%s</p></details>'
                 % (esc(correct["label"]), esc(d["explain"]["correct"])))
        o.append("</section>")
    o.append('<h2 id="lab-after">The corrected version</h2>')
    for e in lab["after"]:
        o.append(render_evidence(e))
    o.append("<p>%s</p>" % esc(lab["closing"]))
    o.append("</div>")
    o.append(render_walkthrough(lab))
    o.append(render_links(lab))
    return "\n".join(o)


def render_walkthrough(lab):
    """An accessible screenshot walkthrough: real captures of this lab's four
    states (scripts/screenshot-engagement.js), each with an alt text that
    describes what is on screen and a caption. Shown to everyone, below the
    lab; there is no video and nothing pretending to be one."""
    frames = lab.get("walkthrough") or []
    if not frames:
        return ""
    o = ['<section class="sbs-lab__walk" aria-labelledby="lab-walk-h"><h2 id="lab-walk-h">Walkthrough</h2>',
         '<p>Four screenshots of this lab, taken from the published page: the start, a deliberately wrong answer, the matching answer, and the corrected version. Every screen is described in the image text.</p><ol class="sbs-lab__frames">']
    for i, fr in enumerate(frames, 1):
        o.append('<li><figure><img src="%s" alt="%s" width="%d" height="%d" loading="lazy" decoding="async"><figcaption>%d. %s</figcaption></figure></li>'
                 % (esc(fr["image"]), esc(fr["alt"]), fr["width"], fr["height"], i, esc(fr["caption"])))
    o.append("</ol></section>")
    return "".join(o)


def render_links(lab):
    """Guide, module, checklist, then product — after the lab, in that order.
    Always rendered (the engine shows the same product link on completion)."""
    o = ['<section class="sbs-lab__links" aria-labelledby="lab-links-h"><h2 id="lab-links-h">Take it to your own site</h2><ul class="sbs-lab__linklist">']
    o.append('<li><a href="%s">%s</a> — the guide this lab is drawn from</li>' % (esc(lab["guide"]["url"]), esc(lab["guide"]["title"])))
    o.append('<li><a href="%s">%s</a></li>' % (esc(lab["module"]["url"]), esc(lab["module"]["title"])))
    if lab.get("resource"):
        o.append('<li><a href="%s">%s</a></li>' % (esc(lab["resource"]["url"]), esc(lab["resource"]["title"])))
    o.append('<li><a href="/products/%s" data-sbs-track="related_product_clicked" data-sbs-product="%s" data-sbs-source="lab">%s</a> — %s</li>'
             % (esc(lab["product"]["handle"]), esc(lab["product"]["handle"]), esc(lab["product"]["label"]), esc(lab["product"]["note"])))
    o.append("</ul></section>")
    return "".join(o)


def build(labs):
    out = ["{%- comment -%}",
           "  GENERATED by scripts/build-labs.py from content/labs/*.json — do not edit.",
           "  Renders, for the lab named by `lab`: the JSON the engine reads and a",
           "  complete static version of the same lab for no-JS visitors and crawlers.",
           "{%- endcomment -%}",
           "{%- case lab -%}"]
    for lab in labs:
        data = json.dumps(lab, ensure_ascii=False, separators=(",", ":"))
        data = data.replace("</", "<\\/")  # never close the script element early
        out.append("{%%- when '%s' -%%}" % lab["id"])
        out.append("{% raw %}")
        out.append('<script type="application/json" data-lab-fixture>%s</script>' % data)
        out.append(render_static(lab))
        out.append("{% endraw %}")
    out.append("{%- endcase -%}")
    return "\n".join(out) + "\n"


def build_index(labs):
    """The hub's cards, in lab order A-D (eyebrow order), each linking to
    its page. Static markup: the hub needs no JavaScript at all."""
    out = ["{%- comment -%}",
           "  GENERATED by scripts/build-labs.py from content/labs/*.json — do not edit.",
           "{%- endcomment -%}",
           '<div class="sbs-labs__grid">']
    for lab in sorted(labs, key=lambda l: l["eyebrow"]):
        out.append('<article class="sbs-card sbs-labs__card">'
                   '<p class="sbs-eyebrow">%s</p><h2>%s</h2><p><strong>%s</strong></p><p>%s</p>'
                   '<a class="sbs-btn sbs-btn--primary" href="/pages/%s">Start the lab</a></article>'
                   % (esc(lab["eyebrow"]), esc(lab["title"]), esc(lab["short"]), esc(lab["summary"]), esc(lab["handle"])))
    out.append("</div>")
    return "\n".join(out) + "\n"


def main():
    labs = load_labs()
    outputs = [(OUT, build(labs)), (INDEX, build_index(labs))]
    if "--check" in sys.argv:
        for path, text in outputs:
            cur = io.open(path, encoding="utf-8").read() if os.path.exists(path) else ""
            if cur != text:
                print("%s is stale: run python3 scripts/build-labs.py" % os.path.basename(path))
                return 1
        print("lab snippets are current (%d labs)" % len(labs))
        return 0
    for path, text in outputs:
        with io.open(path, "w", encoding="utf-8") as fh:
            fh.write(text)
        print("wrote %s (%d bytes)" % (os.path.relpath(path, ROOT), len(text)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
