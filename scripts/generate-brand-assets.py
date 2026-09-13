#!/usr/bin/env python3
"""Generate Site Builder Stack brand assets.

  favicon.png        512x512  browser tab / app icon
  logo.png           600x600  Organization schema logo (square, safe margins)
  product-bundle.png 1600x1200 product image — depicts the ACTUAL module
                              contents, never a physical box mockup
  og-share.png       1200x630  Open Graph / Twitter card

Colours are the same tokens as assets/sbs.css. Nothing here implies a
physical product.

Usage: generate-brand-assets.py <outputDir>
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

OUT = sys.argv[1] if len(sys.argv) > 1 else "assets"
os.makedirs(OUT, exist_ok=True)

BG       = (11, 13, 18)
SURFACE  = (18, 21, 29)
SURFACE2 = (23, 27, 38)
BORDER   = (35, 42, 56)
TEXT     = (233, 236, 243)
MUTED    = (167, 176, 192)
DIM      = (125, 135, 152)
ACCENT   = (138, 166, 255)
INK      = (11, 13, 18)
TEAL     = (94, 234, 212)

FDIR = "/usr/share/fonts/truetype/dejavu"
def font(name, size):
    return ImageFont.truetype(os.path.join(FDIR, name), size)

SANS_B = "DejaVuSans-Bold.ttf"
SANS   = "DejaVuSans.ttf"
MONO_B = "DejaVuSansMono-Bold.ttf"
MONO   = "DejaVuSansMono.ttf"


def rr(draw, box, radius, fill=None, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


# ── the mark: three offset bars, a "stack" ──────────────────────────────────
def draw_mark(d, x, y, size, bar_colour, gap_ratio=0.20):
    """Three stacked bars of decreasing width. Reads clearly at 32px."""
    bar_h = size * 0.19
    gap = size * gap_ratio
    widths = (1.0, 0.74, 0.48)
    top = y + (size - (3 * bar_h + 2 * gap)) / 2
    for i, wfrac in enumerate(widths):
        by = top + i * (bar_h + gap)
        rr(d, [x, by, x + size * wfrac, by + bar_h], radius=bar_h / 2.6, fill=bar_colour)


# ── 1. favicon ──────────────────────────────────────────────────────────────
S = 512
img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
d = ImageDraw.Draw(img)
rr(d, [0, 0, S - 1, S - 1], radius=S * 0.22, fill=ACCENT)
draw_mark(d, S * 0.24, S * 0.24, S * 0.52, INK)
img.save(os.path.join(OUT, "favicon.png"))
print(f"  favicon.png        {S}x{S}")

# ── 1b. Organization logo ───────────────────────────────────────────────────
# Distinct from the favicon and from og-share.png, and it exists because the
# Organization schema needs a LOGO rather than a social card. The schema pointed
# at og-share.png, a 1200x630 landscape image with marketing copy on it —
# usable as an Open Graph image and wrong as a logo.
#
# Square, on the brand ink rather than transparent (Google renders the logo on
# an unknown background, and a transparent dark mark disappears on dark), with
# generous margins so it survives being cropped to a circle.
L = 600
img = Image.new("RGB", (L, L), INK)
d = ImageDraw.Draw(img)
# The mark's bars decrease in width, so its visual mass sits left. Centring the
# wordmark under it reads as a misalignment; sharing a left edge reads as the
# lockup it is, and matches how the header sets mark-then-wordmark.
_mx, _msize = L * 0.27, L * 0.46
draw_mark(d, _mx, L * 0.20, _msize, ACCENT)
_wm = font(MONO_B, 52)
d.text((_mx, L * 0.66), "SBS", font=_wm, fill=TEXT)
img.save(os.path.join(OUT, "logo.png"))
print(f"  logo.png           {L}x{L}")

# ── 2. product bundle image ─────────────────────────────────────────────────
W, H = 1600, 1200
img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)

# soft accent glow, top-left
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

d.text((PAD, PAD + 96), "The Claude Code", font=font(SANS_B, 76), fill=TEXT)
d.text((PAD, PAD + 182), "Website Launch System", font=font(SANS_B, 76), fill=TEXT)
d.text((PAD, PAD + 292),
       "17 modules  ·  113 files  ·  100 reusable prompts",
       font=font(MONO, 30), fill=ACCENT)

MODULES = [
    ("MASTER PROMPT",   "15 phases",     True),
    ("CLAUDE.md",       "production",    False),
    ("SEO SYSTEM",      "10 files",      False),
    ("CONTENT CLUSTERS","briefs",        False),
    ("SHOPIFY",         "7 files",       False),
    ("WORDPRESS",       "5 files",       False),
    ("ASTRO",           "5 files",       False),
    ("SAAS",            "6 files",       False),
    ("LANDING PAGES",   "5 files",       False),
    ("SECURITY",        "6 files",       False),
    ("ACCESSIBILITY",   "5 files",       False),
    ("DEPLOYMENT",      "GitHub + CF",   False),
    ("SEARCH ENGINES",  "GSC · Bing",    False),
    ("100 PROMPTS",     "11 categories", True),
    ("CHECKLISTS",      "11 files",      False),
    ("TEMPLATES",       "10 files",      False),
]
COLS, ROWS = 4, 4
GRID_TOP = PAD + 372
GRID_W = W - PAD * 2
GAP = 20
CW = (GRID_W - GAP * (COLS - 1)) / COLS
CH = 128

for i, (label, meta, hot) in enumerate(MODULES[: COLS * ROWS]):
    cx = PAD + (i % COLS) * (CW + GAP)
    cy = GRID_TOP + (i // COLS) * (CH + GAP)
    rr(d, [cx, cy, cx + CW, cy + CH], radius=14,
       fill=(24, 30, 48) if hot else SURFACE2,
       outline=ACCENT if hot else BORDER, width=2 if hot else 1)
    d.text((cx + 20, cy + 26), label, font=font(MONO_B, 21), fill=TEXT if hot else TEXT)
    d.text((cx + 20, cy + 62), meta, font=font(MONO, 19), fill=ACCENT if hot else DIM)
    d.text((cx + 20, cy + 92), f"{i + 1:02d}", font=font(MONO, 16), fill=DIM)

d.text((PAD, H - 92), "Digital download  ·  Markdown  ·  no installation, no dependencies",
       font=font(MONO, 24), fill=DIM)
img.save(os.path.join(OUT, "product-bundle.png"))
print(f"  product-bundle.png {W}x{H}")

# ── 3. Open Graph image ─────────────────────────────────────────────────────
W, H = 1200, 630
img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)
d.rectangle([0, 0, W, 6], fill=ACCENT)

PAD = 72
draw_mark(d, PAD, PAD - 2, 44, ACCENT)
d.text((PAD + 64, PAD + 4), "SITE BUILDER STACK", font=font(MONO_B, 22), fill=MUTED)

d.text((PAD, PAD + 88),  "Build production-ready", font=font(SANS_B, 62), fill=TEXT)
d.text((PAD, PAD + 158), "websites with Claude Code", font=font(SANS_B, 62), fill=TEXT)

d.text((PAD, PAD + 262),
       "Prompts, CLAUDE.md templates, SEO workflows, deployment",
       font=font(SANS, 27), fill=MUTED)
d.text((PAD, PAD + 302),
       "guides, security and accessibility audits, launch checklists.",
       font=font(SANS, 27), fill=MUTED)

chips = [("17 modules", ACCENT), ("113 files", TEAL), ("100 prompts", ACCENT)]
x = PAD
for label, col in chips:
    f = font(MONO_B, 22)
    tw = d.textlength(label, font=f)
    rr(d, [x, PAD + 372, x + tw + 40, PAD + 424], radius=26, outline=col, width=2)
    d.text((x + 20, PAD + 386), label, font=f, fill=col)
    x += tw + 40 + 16

d.text((PAD, H - 74), "sitebuilderstack.com", font=font(MONO, 24), fill=DIM)
img.save(os.path.join(OUT, "og-share.png"))
print(f"  og-share.png       {W}x{H}")

print("\nBrand assets written to", os.path.abspath(OUT))
