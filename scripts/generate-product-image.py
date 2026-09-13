#!/usr/bin/env python3
"""Generate a toolkit product image from the built bundle.

Same tokens, mark and grammar as scripts/generate-brand-assets.py, so the three
product images read as one family. Each depicts the actual module contents —
the directory names and their real file counts — rather than a box mockup,
because nothing about these products is physical and a rendered box would
imply otherwise.

Every number on the image is read from the bundle, not typed. An image is the
one place a stale count is invisible to every text-based check, so it is
counted here instead.

Usage: generate-product-image.py <cro|seo> <outputDir>
"""
import io
import os
import re
import sys
import importlib.util as _il

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

PRODUCTS = {
    "cro": {
        "bundle": "Claude-Code-Conversion-Revenue-Optimization-Toolkit",
        "title": ["Conversion & Revenue", "Optimization Toolkit"],
        "out": "product-cro-toolkit.png",
        "unit": "workflows",
        "hot": {"01 CORE", "COMMANDS"},
        "extras": [("COMMANDS", "{commands} commands"), ("CLAUDE.md", "2 files"),
                   ("EXAMPLES", "{examples} worked")],
        "template_dir": "13-",
        "template_noun": "templates",
    },
    "ops": {
        "bundle": "Claude-Code-Website-Operations-Maintenance-System",
        "title": ["Website Operations &", "Maintenance System"],
        "out": "product-ops-system.png",
        "unit": "files",
        "hot": {"14 MONTHLY", "COMMANDS", "SCRIPTS"},
        "extras": [("COMMANDS", "{commands} commands"), ("SCRIPTS", "{scripts} scripts"),
                   ("CHECKLISTS", "{checklists} checklists")],
        "template_dir": "15-",
        "template_noun": "templates",
        "validator": "validate-ops-system.py",
    },
    "seo": {
        "bundle": "Claude-Code-SEO-Website-Audit-Toolkit",
        "title": ["SEO & Website", "Audit Toolkit"],
        "out": "product-seo-toolkit.png",
        "unit": "files",
        "hot": {"01 TECHNICAL SEO", "PROMPTS"},
        "extras": [("PROMPTS", "{prompts} prompts"), ("TEMPLATES", "{templates} templates"),
                   ("CHECKLISTS", "{checklists} checklists")],
        "template_dir": None,
        "template_noun": None,
    },
}

if len(sys.argv) < 2 or sys.argv[1] not in PRODUCTS:
    raise SystemExit("usage: generate-product-image.py <%s> <outputDir>"
                     % "|".join(sorted(PRODUCTS)))
KEY = sys.argv[1]
P = PRODUCTS[KEY]
BUNDLE = os.path.join(ROOT, "product", P["bundle"])

_spec = _il.spec_from_file_location("vc", os.path.join(HERE, P.get("validator", "validate-cro-toolkit.py")))
_vc = _il.module_from_spec(_spec)
_spec.loader.exec_module(_vc)

OUT = sys.argv[2] if len(sys.argv) > 2 else "assets"
os.makedirs(OUT, exist_ok=True)

BG       = (11, 13, 18)
SURFACE2 = (23, 27, 38)
BORDER   = (35, 42, 56)
TEXT     = (233, 236, 243)
MUTED    = (167, 176, 192)
DIM      = (125, 135, 152)
ACCENT   = (138, 166, 255)

FDIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(os.path.join(FDIR, name), size)


SANS_B, MONO_B, MONO = "DejaVuSans-Bold.ttf", "DejaVuSansMono-Bold.ttf", "DejaVuSansMono.ttf"


def rr(draw, box, radius, fill=None, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def draw_mark(d, x, y, size, bar_colour, gap_ratio=0.20):
    bar_h = size * 0.19
    gap = size * gap_ratio
    top = y + (size - (3 * bar_h + 2 * gap)) / 2
    for i, wfrac in enumerate((1.0, 0.74, 0.48)):
        by = top + i * (bar_h + gap)
        rr(d, [x, by, x + size * wfrac, by + bar_h], radius=bar_h / 2.6, fill=bar_colour)


def module_counts():
    """(label, 'N <unit>') per numbered module, counted from the bundle."""
    out = []
    for name in sorted(os.listdir(BUNDLE)):
        if not re.match(r"^\d{2}-", name):
            continue
        path = os.path.join(BUNDLE, name)
        if not os.path.isdir(path):
            continue
        # The operations system's modules hold scripts, YAML and shell files
        # alongside the Markdown; "1 file" for a folder of five would be wrong.
        n = len([f for f in os.listdir(path)
                 if (KEY == "ops" or f.endswith(".md")) and f != "README.md"])
        pretty = name.split("-", 1)[1].replace("-", " ")
        noun = P["unit"]
        if P["template_dir"] and name.startswith(P["template_dir"]):
            noun = P["template_noun"]
        # "1 files" on a product image is the kind of small wrongness that
        # makes a buyer doubt the larger numbers.
        if n == 1 and noun.endswith("s"):
            noun = noun[:-1]
        out.append((name[:2] + " " + pretty.upper(), "%d %s" % (n, noun)))
    return out


def flat_counts():
    """Counts for the non-module directories each product uses on the image."""
    c = {}
    for d, key in (("commands", "commands"), ("prompts", "prompts"),
                   ("templates", "templates"), ("checklists", "checklists")):
        path = os.path.join(BUNDLE, d)
        c[key] = len([f for f in os.listdir(path)
                      if f.endswith(".md") and f not in ("README.md", "COMMANDS.md")]) if os.path.isdir(path) else 0
    # commands/ holds category files, not one file per command.
    n = 0
    cdir = os.path.join(BUNDLE, "commands")
    if os.path.isdir(cdir):
        for f in sorted(os.listdir(cdir)):
            if f.endswith(".md") and f != "COMMANDS.md":
                body = io.open(os.path.join(cdir, f), encoding="utf-8").read()
                n += len(re.findall(r"^## C-\d+", body, re.M))
    if n:
        c["commands"] = n
    sdir = os.path.join(BUNDLE, "scripts")
    c["scripts"] = len([f for f in os.listdir(sdir) if f.endswith(".py") and f != "_common.py"]) if os.path.isdir(sdir) else 0
    ex = os.path.join(BUNDLE, "examples")
    c["examples"] = len([f for f in os.listdir(ex)
                         if f.endswith(".md") and f != "README.md"]) if os.path.isdir(ex) else 0
    return c


counts = _vc.counts(BUNDLE)
flat = flat_counts()
MODULES = module_counts()
for label, meta in P["extras"]:
    MODULES.append((label, meta.format(**flat)))
HOT = P["hot"]

W, H = 1600, 1200
img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)

glow = Image.new("RGB", (W, H), BG)
gd = ImageDraw.Draw(glow)
for r in range(700, 0, -14):
    a = int(16 * (1 - r / 700))
    gd.ellipse([160 - r, -220 - r, 160 + r, -220 + r],
               fill=(BG[0] + a, BG[1] + a, min(255, BG[2] + int(a * 2.2))))
img = Image.blend(img, glow, 0.85)
d = ImageDraw.Draw(img)

PAD = 84
draw_mark(d, PAD, PAD + 6, 54, ACCENT)
d.text((PAD + 78, PAD + 14), "SITE BUILDER STACK", font=font(MONO_B, 26), fill=MUTED)

d.text((PAD, PAD + 96), P["title"][0], font=font(SANS_B, 76), fill=TEXT)
d.text((PAD, PAD + 182), P["title"][1], font=font(SANS_B, 76), fill=TEXT)
if KEY == "cro":
    strap = ("%d modules  ·  %d workflows  ·  %d reusable commands"
             % (counts["modules"], counts["workflows"], flat["commands"]))
elif KEY == "ops":
    strap = "OPERATE  ·  Monitor • Diagnose • Maintain • Protect"
else:
    strap = ("%d modules  ·  %d prompts  ·  %d files"
             % (counts["modules"], flat["prompts"], counts["files"]))
d.text((PAD, PAD + 292), strap, font=font(MONO, 30), fill=ACCENT)

# Rows adapt to the module count rather than truncating at sixteen. The SEO
# bundle has seventeen entries; a fixed 4x4 grid silently dropped the last one,
# which is exactly the kind of omission nobody notices in an image.
COLS = 4
GAP = 20
ROWS = -(-len(MODULES) // COLS)
GRID_TOP = PAD + 372
CW = (W - PAD * 2 - GAP * (COLS - 1)) / COLS
FOOT = H - 92
CH = min(116, ((FOOT - 28) - GRID_TOP - GAP * (ROWS - 1)) / ROWS)

for i, (label, meta) in enumerate(MODULES):
    hot = label in HOT
    cx = PAD + (i % COLS) * (CW + GAP)
    cy = GRID_TOP + (i // COLS) * (CH + GAP)
    rr(d, [cx, cy, cx + CW, cy + CH], radius=14,
       fill=(24, 30, 48) if hot else SURFACE2,
       outline=ACCENT if hot else BORDER, width=2 if hot else 1)
    # The longest label is "10 PERFORMANCE ACCESSIBILITY"; shrink to fit rather
    # than truncate, so no tile ships a half-word.
    size = 21
    while d.textlength(label, font=font(MONO_B, size)) > CW - 40 and size > 12:
        size -= 1
    d.text((cx + 20, cy + 26), label, font=font(MONO_B, size), fill=TEXT)
    # No index number under the meta line. The flagship image needs one because
    # its labels are unnumbered; here every module label already begins with
    # its number, and repeating it read as a second, different count.
    d.text((cx + 20, cy + 70), meta, font=font(MONO, 19), fill=ACCENT if hot else DIM)

foot = "Digital download  ·  Markdown  ·  no installation, no dependencies"
if KEY == "ops":
    foot = ("%d modules  ·  %d commands  ·  %d scripts  ·  Python 3 standard library only"
            % (counts["modules"], flat["commands"], flat["scripts"]))
d.text((PAD, H - 92), foot, font=font(MONO, 24), fill=DIM)

path = os.path.join(OUT, P["out"])
img.save(path)
print("  %s  %dx%d  -> %s" % (P["out"], W, H, os.path.abspath(path)))
print("  counted: %d modules, %d files, %s" % (counts["modules"], counts["files"], flat))
