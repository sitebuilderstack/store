#!/usr/bin/env python3
"""Generate featured images for the cornerstone guides.

One shared visual system: dark ground, faint grid, a coloured rail, the
"Claude Code Guides" eyebrow, the title, and a motif drawn from the
article's own subject. Each article gets a distinct hue and a distinct
motif so the five read as a set without looking interchangeable.

Colours are the tokens from assets/sbs.css. Nothing depicts a physical
object; these are diagrams, not product mockups.

Usage: generate-article-images.py <outputDir>
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

OUT = sys.argv[1] if len(sys.argv) > 1 else "brand/articles"
os.makedirs(OUT, exist_ok=True)

W, H = 1200, 630

BG       = (11, 13, 18)
SURFACE  = (18, 21, 29)
SURFACE2 = (23, 27, 38)
BORDER   = (35, 42, 56)
GRID     = (21, 25, 34)
TEXT     = (233, 236, 243)
MUTED    = (167, 176, 192)
DIM      = (108, 118, 136)

FDIR = "/usr/share/fonts/truetype/dejavu"
def font(name, size):
    return ImageFont.truetype(os.path.join(FDIR, name), size)

SANS_B = "DejaVuSans-Bold.ttf"
SANS   = "DejaVuSans.ttf"
MONO_B = "DejaVuSansMono-Bold.ttf"
MONO   = "DejaVuSansMono.ttf"


f_ = font


def mix(c, bg, a):
    """Composite c over bg at alpha a."""
    return tuple(int(round(bg[i] + (c[i] - bg[i]) * a)) for i in range(3))


def wrap(draw, text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- motifs
# Each motif is drawn inside a 380x380 box at (x, y). They share a visual
# language -- rounded rectangles, 2px strokes, the article's accent used
# sparingly for the one element that carries the meaning.

def motif_pages(d, x, y, acc):
    """Article 1: a page being assembled from blocks."""
    d.rounded_rectangle([x, y, x + 250, y + 330], 8, fill=SURFACE, outline=BORDER, width=2)
    d.rounded_rectangle([x + 20, y + 22, x + 230, y + 66], 4, fill=SURFACE2, outline=BORDER)
    d.rounded_rectangle([x + 20, y + 84, x + 230, y + 190], 4, fill=mix(acc, SURFACE, .14),
                        outline=acc, width=2)
    for i in range(3):
        cy = y + 208 + i * 40
        d.rounded_rectangle([x + 20, cy, x + 230, cy + 28], 4, fill=SURFACE2, outline=BORDER)
    # blocks queueing to join
    for i, off in enumerate((0, 62, 124)):
        bx = x + 285
        by = y + 40 + off
        d.rounded_rectangle([bx, by, bx + 86, by + 44], 6,
                            fill=SURFACE2, outline=acc if i == 0 else BORDER, width=2)
        d.line([bx - 26, by + 22, bx - 6, by + 22], fill=acc if i == 0 else DIM, width=2)


def motif_prompts(d, x, y, acc):
    """Article 2: stacked prompt lines, each with a caret."""
    rows = [(0, 200), (1, 258), (0, 168), (1, 232), (0, 210), (1, 150)]
    for i, (indent, wdt) in enumerate(rows):
        ry = y + 26 + i * 52
        rx = x + 14 + indent * 28
        d.rounded_rectangle([rx, ry, x + 344, ry + 38], 6,
                            fill=SURFACE if i else mix(acc, SURFACE, .16),
                            outline=acc if i == 0 else BORDER, width=2)
        d.text((rx + 14, ry + 9), ">", font=font(MONO_B, 20),
               fill=acc if i == 0 else DIM)
        d.rounded_rectangle([rx + 40, ry + 15, rx + 40 + wdt, ry + 23], 4,
                            fill=MUTED if i == 0 else BORDER)


def motif_doc(d, x, y, acc):
    """Article 3: a rules document with a folded corner and checked lines."""
    fold = 54
    d.polygon([(x + 30, y), (x + 300 - fold, y), (x + 300, y + fold),
               (x + 300, y + 340), (x + 30, y + 340)],
              fill=SURFACE, outline=BORDER)
    d.line([(x + 300 - fold, y), (x + 300 - fold, y + fold), (x + 300, y + fold)],
           fill=BORDER, width=2)
    d.text((x + 54, y + 34), "CLAUDE.md", font=font(MONO_B, 22), fill=acc)
    labels = [True, True, False, True, False, True]
    for i, checked in enumerate(labels):
        ly = y + 92 + i * 40
        if checked:
            d.line([(x + 56, ly + 10), (x + 64, ly + 18), (x + 80, ly - 2)],
                   fill=acc, width=3, joint="curve")
        else:
            d.ellipse([x + 58, ly + 2, x + 74, ly + 18], outline=DIM, width=2)
        d.rounded_rectangle([x + 96, ly + 5, x + 96 + (150 if i % 2 else 178), ly + 13],
                            4, fill=MUTED if checked else BORDER)


def motif_store(d, x, y, acc):
    """Article 4: a storefront grid with one item flowing out as a download."""
    d.rounded_rectangle([x, y, x + 300, y + 210], 8, fill=SURFACE, outline=BORDER, width=2)
    d.line([(x, y + 46), (x + 300, y + 46)], fill=BORDER, width=2)
    for i in range(3):
        d.ellipse([x + 20 + i * 20, y + 18, x + 30 + i * 20, y + 28], fill=BORDER)
    for r in range(2):
        for c in range(3):
            tx, ty = x + 22 + c * 90, y + 66 + r * 68
            on = (r == 0 and c == 1)
            d.rounded_rectangle([tx, ty, tx + 72, ty + 52], 5,
                                fill=mix(acc, SURFACE, .16) if on else SURFACE2,
                                outline=acc if on else BORDER, width=2)
    # download arrow to a file
    ax = x + 138
    d.line([(ax, y + 224), (ax, y + 276)], fill=acc, width=3)
    d.polygon([(ax - 11, y + 270), (ax + 11, y + 270), (ax, y + 288)], fill=acc)
    d.rounded_rectangle([x + 96, y + 300, x + 180, y + 344], 6,
                        fill=SURFACE2, outline=acc, width=2)
    d.text((x + 112, y + 312), ".zip", font=font(MONO_B, 19), fill=acc)


def motif_seo(d, x, y, acc):
    """Article 5: a crawl graph above a rising result."""
    nodes = [(x + 60, y + 34), (x + 60, y + 104), (x + 60, y + 174),
             (x + 176, y + 69), (x + 176, y + 139), (x + 292, y + 104)]
    edges = [(0, 3), (1, 3), (1, 4), (2, 4), (3, 5), (4, 5)]
    for a, b in edges:
        d.line([nodes[a], nodes[b]], fill=BORDER, width=2)
    for i, (nx, ny) in enumerate(nodes):
        last = (i == 5)
        r = 17 if last else 12
        d.ellipse([nx - r, ny - r, nx + r, ny + r],
                  fill=mix(acc, BG, .26) if last else SURFACE2,
                  outline=acc if last else BORDER, width=2)

    base = y + 352
    for i, h in enumerate((44, 74, 106, 144)):
        bx = x + 70 + i * 56
        d.rounded_rectangle([bx, base - h, bx + 40, base], 4,
                            fill=mix(acc, BG, .30) if i == 3 else SURFACE2,
                            outline=acc if i == 3 else BORDER, width=2)



def motif_delegate(d, x, y, acc):
    """Subagents: a main thread handing work to isolated contexts."""
    d.rounded_rectangle([x + 14, y + 150, x + 96, y + 232], 10,
                        fill=mix(acc, SURFACE, .18), outline=acc, width=3)
    d.text((x + 34, y + 182), "you", font=f_(SANS_B, 17), fill=acc)
    for i, oy in enumerate((22, 130, 238)):
        bx, by = x + 190, y + oy
        d.rounded_rectangle([bx, by, bx + 168, by + 112], 10,
                            fill=SURFACE2, outline=BORDER, width=2)
        d.line([(x + 100, y + 191), (bx - 12, by + 56)], fill=BORDER, width=2)
        d.ellipse([bx - 18, by + 50, bx - 6, by + 62], fill=acc)
        for r in range(3):
            d.rounded_rectangle([bx + 16, by + 26 + r * 24, bx + 16 + (110 - r * 26),
                                 by + 34 + r * 24], 4, fill=BORDER)


def motif_skillcards(d, x, y, acc):
    """Skills: a stack of slash commands."""
    for i in range(4):
        ox, oy = i * 10, i * 14
        d.rounded_rectangle([x + 20 + ox, y + 30 + oy, x + 300 + ox, y + 118 + oy], 10,
                            fill=mix(acc, SURFACE, .16) if i == 3 else SURFACE2,
                            outline=acc if i == 3 else BORDER, width=2)
    d.text((x + 68, y + 118), "/audit", font=f_(MONO_B, 26), fill=acc)
    d.rounded_rectangle([x + 20, y + 250, x + 340, y + 300], 8,
                        fill=SURFACE2, outline=BORDER, width=2)
    d.text((x + 40, y + 263), "SKILL.md", font=f_(MONO, 19), fill=MUTED)


def motif_package(d, x, y, acc):
    """Plugins: one package holding several component blocks."""
    d.rounded_rectangle([x + 10, y + 40, x + 350, y + 330], 14,
                        fill=SURFACE, outline=acc, width=3)
    labels = ["skills", "agents", "hooks", "mcp"]
    for i, lab in enumerate(labels):
        cx = x + 34 + (i % 2) * 168
        cy = y + 74 + (i // 2) * 122
        on = (i == 0)
        d.rounded_rectangle([cx, cy, cx + 144, cy + 96], 8,
                            fill=mix(acc, SURFACE, .16) if on else SURFACE2,
                            outline=acc if on else BORDER, width=2)
        d.text((cx + 16, cy + 36), lab, font=f_(MONO_B, 17),
               fill=TEXT if on else MUTED)


def motif_badge(d, x, y, acc):
    """Certification: a credential seal."""
    cx, cy = x + 180, y + 150
    for r, w in ((104, 3), (84, 2)):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=acc if r == 104 else BORDER, width=w)
    d.ellipse([cx - 62, cy - 62, cx + 62, cy + 62], fill=mix(acc, BG, .16), outline=acc, width=2)
    d.line([(cx - 28, cy + 2), (cx - 8, cy + 24), (cx + 30, cy - 26)],
           fill=acc, width=6, joint="curve")
    for sx in (-34, 34):
        d.polygon([(cx + sx - 18, cy + 96), (cx + sx + 18, cy + 96),
                   (cx + sx + 18, cy + 190), (cx + sx, cy + 166),
                   (cx + sx - 18, cy + 190)], fill=SURFACE2, outline=BORDER)


def motif_org(d, x, y, acc):
    """Enterprise: policy layers narrowing from org to project."""
    rows = [("organisation", 0), ("team", 34), ("project", 68), ("developer", 102)]
    for i, (lab, inset) in enumerate(rows):
        top = y + 24 + i * 86
        on = (i == 0)
        d.rounded_rectangle([x + 8 + inset, top, x + 352 - inset, top + 66], 8,
                            fill=mix(acc, SURFACE, .16) if on else SURFACE2,
                            outline=acc if on else BORDER, width=2)
        d.text((x + 30 + inset, top + 22), lab, font=f_(SANS_B, 16),
               fill=TEXT if on else MUTED)
        if i:
            d.line([(x + 180, top - 20), (x + 180, top)], fill=BORDER, width=2)


def motif_dial(d, x, y, acc):
    """Vibe coding: a dial between vibes and discipline."""
    track_y = y + 190
    d.rounded_rectangle([x + 20, track_y - 10, x + 340, track_y + 10], 10,
                        fill=SURFACE2, outline=BORDER, width=2)
    d.rounded_rectangle([x + 20, track_y - 10, x + 132, track_y + 10], 10,
                        fill=mix(acc, SURFACE, .34))
    d.ellipse([x + 108, track_y - 30, x + 156, track_y + 18], fill=BG, outline=acc, width=4)
    d.text((x + 20, track_y - 76), "vibes", font=f_(MONO_B, 18), fill=acc)
    tw = d.textlength("disciplined", font=f_(MONO_B, 18))
    d.text((x + 340 - tw, track_y - 76), "disciplined", font=f_(MONO_B, 18), fill=DIM)
    for i in range(9):
        tx = x + 20 + i * 40
        d.line([(tx, track_y + 30), (tx, track_y + 44)], fill=BORDER, width=2)



def motif_ci(d, x, y, acc):
    """GitHub Actions: a pipeline with a gate."""
    stages = ["push", "review", "merge"]
    for i, lab in enumerate(stages):
        bx = x + 12
        by = y + 20 + i * 116
        on = (i == 1)
        d.rounded_rectangle([bx, by, bx + 330, by + 84], 10,
                            fill=mix(acc, SURFACE, .16) if on else SURFACE2,
                            outline=acc if on else BORDER, width=2)
        d.ellipse([bx + 22, by + 28, bx + 50, by + 56],
                  fill=BG, outline=acc if on else DIM, width=3)
        d.text((bx + 70, by + 32), lab, font=f_(MONO_B, 18), fill=TEXT if on else MUTED)
        if on:
            d.text((bx + 210, by + 33), "@claude", font=f_(MONO_B, 16), fill=acc)
        if i < 2:
            d.line([(bx + 36, by + 84), (bx + 36, by + 116)], fill=BORDER, width=2)
            d.polygon([(bx + 31, by + 110), (bx + 41, by + 110), (bx + 36, by + 120)], fill=BORDER)


def motif_prompt(d, x, y, acc):
    """Terminal: a prompt line and a cursor."""
    d.rounded_rectangle([x + 10, y + 60, x + 350, y + 300], 10,
                        fill=SURFACE, outline=BORDER, width=2)
    d.line([(x + 10, y + 104), (x + 350, y + 104)], fill=BORDER, width=2)
    for i in range(3):
        d.ellipse([x + 32 + i * 22, y + 74, x + 44 + i * 22, y + 86], fill=BORDER)
    d.text((x + 36, y + 132), "$ claude", font=f_(MONO_B, 22), fill=acc)
    rows = [(200, MUTED), (260, BORDER), (150, BORDER)]
    for i, (w, col) in enumerate(rows):
        d.rounded_rectangle([x + 36, y + 182 + i * 30, x + 36 + w, y + 190 + i * 30], 4, fill=col)
    d.rounded_rectangle([x + 36, y + 274, x + 52, y + 292], 2, fill=acc)


def motif_connect(d, x, y, acc):
    """MCP: one hub wired to external systems."""
    cx, cy = x + 96, y + 170
    d.rounded_rectangle([cx - 60, cy - 46, cx + 60, cy + 46], 10,
                        fill=mix(acc, SURFACE, .18), outline=acc, width=3)
    d.text((cx - 26, cy - 12), "you", font=f_(SANS_B, 18), fill=acc)
    for i, oy in enumerate((14, 116, 218)):
        bx, by = x + 236, y + oy
        d.rounded_rectangle([bx, by, bx + 122, by + 84], 10, fill=SURFACE2,
                            outline=BORDER, width=2)
        d.line([(cx + 62, cy), (bx - 8, by + 42)], fill=acc if i == 1 else BORDER, width=2)
        d.ellipse([bx - 16, by + 34, bx - 4, by + 46], fill=acc if i == 1 else BORDER)
        for r in range(2):
            d.rounded_rectangle([bx + 20, by + 26 + r * 24, bx + 92 - r * 22, by + 34 + r * 24],
                                4, fill=BORDER)


def motif_gate(d, x, y, acc):
    """Hooks: a barrier that stops one thing and passes another."""
    gx = x + 190
    d.line([(gx, y + 26), (gx, y + 330)], fill=acc, width=4)
    for i, (oy, blocked) in enumerate(((44, False), (140, True), (236, False))):
        by = y + oy
        d.rounded_rectangle([x + 14, by, x + 132, by + 66], 8, fill=SURFACE2,
                            outline=BORDER, width=2)
        for r in range(2):
            d.rounded_rectangle([x + 32, by + 22 + r * 20, x + 112 - r * 26, by + 30 + r * 20],
                                4, fill=BORDER)
        if blocked:
            d.line([(x + 140, by + 33), (gx - 12, by + 33)], fill=BORDER, width=2)
            r = 15
            d.ellipse([gx - r + 2, by + 33 - r, gx + r + 2, by + 33 + r], outline=acc, width=3)
            d.line([(gx - 8, by + 25), (gx + 12, by + 41)], fill=acc, width=3)
        else:
            d.line([(x + 140, by + 33), (x + 330, by + 33)], fill=acc, width=2)
            d.polygon([(x + 322, by + 27), (x + 322, by + 39), (x + 338, by + 33)], fill=acc)


def motif_audit(d, x, y, acc):
    """Website audit: a page under a lens, with findings ranked beside it."""
    d.rounded_rectangle([x, y + 10, x + 214, y + 320], 8, fill=SURFACE, outline=BORDER, width=2)
    d.rounded_rectangle([x + 18, y + 30, x + 196, y + 66], 4, fill=SURFACE2, outline=BORDER)
    for i in range(5):
        ry = y + 84 + i * 34
        d.rounded_rectangle([x + 18, ry, x + 18 + (168 if i % 2 else 132), ry + 12],
                            4, fill=BORDER)
    # lens over the page
    cx, cy, r = x + 168, y + 216, 62
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=acc, width=4)
    d.line([(cx + 44, cy + 44), (cx + 92, cy + 92)], fill=acc, width=6)
    # findings, most severe first
    for i, w in enumerate((150, 120, 96)):
        fy = y + 40 + i * 62
        d.rounded_rectangle([x + 262, fy, x + 380, fy + 44], 6, fill=SURFACE2,
                            outline=acc if i == 0 else BORDER, width=2)
        d.rounded_rectangle([x + 276, fy + 18, x + 276 + min(w, 90), fy + 26], 4,
                            fill=MUTED if i == 0 else BORDER)


def motif_evidence(d, x, y, acc):
    """Technical SEO audit: checks that must be able to fail, not just pass."""
    for i, state in enumerate(("pass", "fail", "pass", "partial", "pass")):
        ry = y + 20 + i * 62
        d.rounded_rectangle([x + 60, ry, x + 380, ry + 46], 6, fill=SURFACE,
                            outline=acc if state != "pass" else BORDER, width=2)
        gx = x + 26
        gy = ry + 23
        if state == "pass":
            d.line([(gx - 12, gy), (gx - 3, gy + 10), (gx + 14, gy - 12)],
                   fill=DIM, width=3, joint="curve")
        elif state == "fail":
            d.line([(gx - 11, gy - 11), (gx + 12, gy + 12)], fill=acc, width=3)
            d.line([(gx + 12, gy - 11), (gx - 11, gy + 12)], fill=acc, width=3)
        else:
            d.ellipse([gx - 12, gy - 12, gx + 12, gy + 12], outline=acc, width=3)
            d.line([(gx, gy - 6), (gx, gy + 2)], fill=acc, width=3)
        d.rounded_rectangle([x + 78, ry + 19, x + 78 + (232 if i % 2 else 178), ry + 27],
                            4, fill=MUTED if state != "pass" else BORDER)


def motif_examples(d, x, y, acc):
    """CLAUDE.md examples: one file per project shape, stacked as a set."""
    labels = ("static site", "web app", "shopify theme", "monorepo")
    for i, lab in enumerate(labels):
        top = y + 4 + i * 96
        d.rounded_rectangle([x + 12, top, x + 356, top + 84], 8,
                            fill=mix(acc, SURFACE, .16) if i == 0 else SURFACE2,
                            outline=acc if i == 0 else BORDER, width=2)
        d.text((x + 32, top + 16), "CLAUDE.md", font=font(MONO_B, 18),
               fill=acc if i == 0 else DIM)
        d.text((x + 170, top + 18), lab, font=font(MONO, 14), fill=MUTED)
        for k in range(2):
            ly = top + 50 + k * 16
            d.rounded_rectangle([x + 32, ly, x + 32 + (300 if k else 236), ly + 7],
                                4, fill=BORDER)


def motif_storefront_seo(d, x, y, acc):
    """Shopify SEO: a catalogue whose URLs resolve to one canonical each."""
    for i in range(3):
        ty = y + 26 + i * 96
        d.rounded_rectangle([x, ty, x + 150, ty + 74], 6, fill=SURFACE,
                            outline=BORDER, width=2)
        d.rounded_rectangle([x + 16, ty + 16, x + 134, ty + 40], 4, fill=SURFACE2)
        d.rounded_rectangle([x + 16, ty + 50, x + 96, ty + 58], 4, fill=BORDER)
        # every variant collapses onto one canonical
        d.line([(x + 158, ty + 37), (x + 222, y + 170)], fill=DIM, width=2)
    d.rounded_rectangle([x + 230, y + 140, x + 380, y + 202], 8,
                        fill=mix(acc, SURFACE, .16), outline=acc, width=2)
    d.text((x + 248, y + 154), "canonical", font=font(MONO_B, 18), fill=acc)
    d.rounded_rectangle([x + 248, y + 182, x + 348, y + 190], 4, fill=MUTED)


def motif_shield(d, x, y, acc):
    """Security audit: layers of review, only some of which a tool can do."""
    cx = x + 190
    pts = [(cx, y + 8), (x + 340, y + 78), (x + 340, y + 210),
           (cx, y + 356), (x + 40, y + 210), (x + 40, y + 78)]
    d.polygon(pts, fill=SURFACE, outline=BORDER)
    d.line(pts + [pts[0]], fill=BORDER, width=2)
    for i, w in enumerate((150, 190, 160)):
        ly = y + 108 + i * 52
        d.rounded_rectangle([cx - w // 2, ly, cx + w // 2, ly + 24], 5,
                            fill=mix(acc, SURFACE, .18) if i == 1 else SURFACE2,
                            outline=acc if i == 1 else BORDER, width=2)
    # the part a scanner cannot reach, drawn open
    d.arc([cx - 46, y + 244, cx + 46, y + 320], 200, 340, fill=DIM, width=3)
    d.line([(cx - 30, y + 276), (cx + 30, y + 276)], fill=DIM, width=2)


def motif_console(d, x, y, acc):
    """Search Console: queries sorted into position bands."""
    bands = [(0, 3, 0.9), (1, 7, 0.55), (2, 12, 0.3), (3, 5, 0.15)]
    for i, (row, n, alpha) in enumerate(bands):
        by = y + 20 + row * 88
        d.rounded_rectangle([x, by, x + 380, by + 68], 8,
                            fill=mix(acc, SURFACE, .16) if row == 1 else SURFACE2,
                            outline=acc if row == 1 else BORDER, width=2)
        for k in range(n):
            bx = x + 22 + k * 26
            if bx > x + 350:
                break
            h = 10 + int(28 * alpha)
            d.rounded_rectangle([bx, by + 56 - h, bx + 16, by + 56], 3,
                                fill=acc if row == 1 else BORDER)


def motif_gauge(d, x, y, acc):
    """Performance: one metric moving, measured twice."""
    for i, (val, hot) in enumerate(((0.30, False), (0.72, True))):
        gx = x + 40 + i * 190
        gy = y + 120
        d.arc([gx, gy, gx + 150, gy + 150], 180, 360,
              fill=BORDER if not hot else mix(acc, SURFACE, .5), width=12)
        import math
        ang = math.pi + math.pi * val
        ex = gx + 75 + math.cos(ang) * 60
        ey = gy + 75 + math.sin(ang) * 60
        d.line([(gx + 75, gy + 75), (ex, ey)], fill=acc if hot else DIM, width=5)
        d.ellipse([gx + 68, gy + 68, gx + 82, gy + 82], fill=acc if hot else DIM)
        d.text((gx + 46, gy + 108), "before" if not hot else "after",
               font=font(MONO, 15), fill=MUTED if hot else DIM)
    d.line([(x + 200, y + 195), (x + 226, y + 195)], fill=acc, width=3)
    d.polygon([(x + 220, y + 189), (x + 220, y + 201), (x + 234, y + 195)], fill=acc)


def motif_a11y(d, x, y, acc):
    """Accessibility: what a scanner reaches, and what a person has to."""
    d.rounded_rectangle([x, y + 20, x + 380, y + 160], 8, fill=SURFACE2,
                        outline=BORDER, width=2)
    d.text((x + 22, y + 38), "automated", font=font(MONO_B, 16), fill=DIM)
    for k in range(4):
        d.rounded_rectangle([x + 22 + k * 88, y + 76, x + 90 + k * 88, y + 132], 6,
                            fill=SURFACE, outline=BORDER, width=2)
        d.line([(x + 40 + k * 88, y + 104), (x + 50 + k * 88, y + 114),
                (x + 72 + k * 88, y + 92)], fill=DIM, width=3, joint="curve")
    d.rounded_rectangle([x, y + 200, x + 380, y + 356], 8,
                        fill=mix(acc, SURFACE, .14), outline=acc, width=3)
    d.text((x + 22, y + 218), "requires a person", font=font(MONO_B, 16), fill=acc)
    labels = ("keyboard order", "screen reader", "does it make sense")
    for k, lab in enumerate(labels):
        ly = y + 254 + k * 32
        d.ellipse([x + 24, ly + 2, x + 38, ly + 16], outline=acc, width=2)
        d.text((x + 52, ly), lab, font=font(SANS, 15), fill=MUTED)


# The motif panel is drawn at [704, 96, 1144, 534] and motifs are called at
# (758, 148). That leaves 386 x 386 to draw in. Exceeding it clips silently —
# the drawing simply runs off the panel and nothing raises — so new motifs
# assert their own extent rather than being checked by eye.
MOTIF_W = 386
MOTIF_H = 386


def within(x0, y0, x1, y1, ox, oy, what):
    """Raise if a motif would draw outside its panel."""
    if x1 - ox > MOTIF_W or y1 - oy > MOTIF_H or x0 < ox or y0 < oy:
        raise ValueError(
            "%s draws outside the motif panel: (%d,%d)-(%d,%d) exceeds %dx%d"
            % (what, x0 - ox, y0 - oy, x1 - ox, y1 - oy, MOTIF_W, MOTIF_H))


def motif_layers(d, x, y, acc):
    """WordPress: three sources of truth resolving into one rendered page.

    Files, database rows and plugin filters as stacked plates converging on a
    single page — the article's thesis, and the reason two of the three are
    invisible to a tool that only reads files."""
    within(x, y, x + 366, y + 300, x, y, "motif_layers")
    for i, lab in enumerate(("files", "database", "plugins")):
        py = y + 24 + i * 84
        on = i == 1
        d.rounded_rectangle([x, py, x + 152, py + 60], 8, fill=SURFACE2,
                            outline=acc if on else BORDER, width=2)
        d.text((x + 18, py + 20), lab, font=font(MONO_B, 17),
               fill=acc if on else MUTED)
        d.line([(x + 164, py + 30), (x + 218, y + 156)],
               fill=acc if on else BORDER, width=2)
    d.rounded_rectangle([x + 228, y + 40, x + 366, y + 272], 8, fill=SURFACE,
                        outline=acc, width=3)
    d.text((x + 248, y + 62), "rendered", font=font(MONO_B, 16), fill=TEXT)
    d.text((x + 248, y + 84), "page", font=font(MONO_B, 16), fill=TEXT)
    for i in range(5):
        ly = y + 124 + i * 26
        d.rounded_rectangle([x + 248, ly, x + 248 + (98 if i % 2 else 74), ly + 8],
                            3, fill=SURFACE2, outline=BORDER)


def motif_split(d, x, y, acc):
    """Comparison: two panes with different centres of gravity.

    A terminal on one side, an editor buffer on the other — the architectural
    difference every other difference in the article follows from."""
    within(x, y, x + 366, y + 300, x, y, "motif_split")
    for i, (title, rows) in enumerate((("terminal", 6), ("editor", 6))):
        px = x + i * 190
        on = i == 0
        d.rounded_rectangle([px, y + 20, px + 176, y + 292], 8, fill=SURFACE,
                            outline=acc if on else BORDER, width=3 if on else 2)
        d.rounded_rectangle([px, y + 20, px + 176, y + 54], 8, fill=SURFACE2,
                            outline=acc if on else BORDER, width=2)
        d.text((px + 16, y + 29), title, font=font(MONO_B, 16),
               fill=acc if on else MUTED)
        for r in range(rows):
            ry = y + 74 + r * 34
            if on:
                d.text((px + 16, ry), "$", font=font(MONO_B, 14), fill=acc)
                d.rounded_rectangle([px + 34, ry + 5, px + 34 + 118 - r * 13, ry + 13],
                                    3, fill=SURFACE2, outline=BORDER)
            else:
                d.rounded_rectangle([px + 16, ry + 3, px + 30, ry + 15], 2,
                                    fill=SURFACE2, outline=BORDER)
                d.rounded_rectangle([px + 38, ry + 5, px + 38 + 112 - r * 11, ry + 13],
                                    3, fill=SURFACE2, outline=BORDER)


ARTICLES = [
    dict(slug="how-to-build-a-website-with-claude-code",
         eyebrow="COMPLETE GUIDE",
         title="How to Build a Website With Claude Code",
         kicker="Definition to deployment, in fifteen verifiable steps",
         accent=(138, 166, 255), motif=motif_pages),
    dict(slug="best-claude-code-prompts-for-web-development",
         eyebrow="PROMPT LIBRARY",
         title="Best Claude Code Prompts for Web Development",
         kicker="27 worked examples, and why each one works",
         accent=(94, 234, 212), motif=motif_prompts),
    dict(slug="production-claude-md-web-development",
         eyebrow="PROJECT CONTEXT",
         title="How to Create a Production CLAUDE.md",
         kicker="The rules worth writing down, and the ones that dilute them",
         accent=(196, 181, 253), motif=motif_doc),
    dict(slug="build-shopify-store-with-claude-code",
         eyebrow="PLATFORM WORKFLOW",
         title="How to Build a Shopify Store With Claude Code",
         kicker="Theme, catalogue, delivery, and the gotchas that cost hours",
         accent=(251, 191, 36), motif=motif_store),
    dict(slug="claude-code-seo-website-optimization",
         eyebrow="OPTIMIZATION WORKFLOW",
         title="Claude Code SEO: Complete Optimization Workflow",
         kicker="Thirteen audits, in the order that matters",
         accent=(134, 239, 172), motif=motif_seo),
    dict(slug="claude-code-subagents",
         eyebrow="AGENT WORKFLOWS",
         title="Claude Code Subagents: How to Use Them",
         kicker="Isolated context, locked-down tools, and the roster worth having",
         accent=(125, 211, 252), motif=motif_delegate),
    dict(slug="claude-code-skills",
         eyebrow="REUSABLE PROCEDURES",
         title="Claude Code Skills: Turn Repeated Work Into Commands",
         kicker="Why a skill costs nothing until the moment you use it",
         accent=(253, 164, 175), motif=motif_skillcards),
    dict(slug="claude-code-plugins",
         eyebrow="DISTRIBUTION",
         title="Claude Code Plugins: Build, Install, and Share",
         kicker="Package skills, agents, and hooks so a team installs them once",
         accent=(190, 242, 100), motif=motif_package),
    dict(slug="claude-code-certification",
         eyebrow="CREDENTIALS",
         title="Is There a Claude Code Certification?",
         kicker="What Anthropic actually certifies, and what proves competence",
         accent=(240, 171, 252), motif=motif_badge),
    dict(slug="claude-code-enterprise",
         eyebrow="TEAM DEPLOYMENT",
         title="Claude Code for Teams and Enterprise",
         kicker="Deployment, managed policy, cost control, and rollout",
         accent=(253, 224, 71), motif=motif_org),
    dict(slug="vibe-coding-tools",
         eyebrow="TOOL COMPARISON",
         title="Vibe Coding Tools and Platforms",
         kicker="Three categories, what each is for, and where each one fails",
         accent=(251, 146, 60), motif=motif_dial),
    dict(slug="claude-code-github-actions",
         eyebrow="CONTINUOUS INTEGRATION",
         title="Claude Code and GitHub: Actions, PR Review, CI",
         kicker="Respond to @claude, review every pull request, run on a schedule",
         accent=(147, 197, 253), motif=motif_ci),
    dict(slug="claude-code-terminal-setup",
         eyebrow="GETTING STARTED",
         title="Getting Started With Claude Code in the Terminal",
         kicker="Install, log in, first session, and the first week",
         accent=(216, 180, 254), motif=motif_prompt),
    dict(slug="claude-code-mcp",
         eyebrow="EXTERNAL TOOLS",
         title="Claude Code and MCP: Connecting External Tools",
         kicker="Transports, scopes, authentication, and the risk you take on",
         accent=(103, 232, 249), motif=motif_connect),
    dict(slug="claude-code-hooks",
         eyebrow="ENFORCEMENT",
         title="Claude Code Hooks: Enforce What You Shouldn't Have to Remember",
         kicker="Events, matchers, exit codes, and four hooks worth having",
         accent=(252, 165, 165), motif=motif_gate),
    dict(slug="claude-code-website-audit",
         eyebrow="PRODUCTION AUDIT",
         title="Claude Code Website Audit: The Complete Checklist",
         kicker="Fifteen areas, ranked by what actually costs you",
         accent=(153, 246, 228), motif=motif_audit),
    dict(slug="claude-code-technical-seo-audit",
         eyebrow="EVIDENCE, NOT OPINIONS",
         title="How to Run a Technical SEO Audit With Claude Code",
         kicker="Run it, prove it ran, and submit what changed",
         accent=(165, 180, 252), motif=motif_evidence),
    dict(slug="claude-md-examples-web-development",
         eyebrow="WORKED EXAMPLES",
         title="CLAUDE.md Examples for Production Web Development",
         kicker="Four complete files, and what changes between them",
         accent=(249, 168, 212), motif=motif_examples),
    dict(slug="shopify-seo-with-claude-code",
         eyebrow="PLATFORM SEO",
         title="Shopify SEO With Claude Code: Complete Workflow",
         kicker="What Shopify controls, what you control, and what to validate",
         accent=(254, 215, 170), motif=motif_storefront_seo),
    dict(slug="claude-code-website-security-audit",
         eyebrow="SECURITY REVIEW",
         title="Claude Code Website Security Audit",
         kicker="Fifteen passes, and the ones it cannot make for you",
         accent=(248, 113, 113), motif=motif_shield),
    dict(slug="google-search-console-claude-code",
         eyebrow="SEARCH DATA",
         title="Google Search Console With Claude Code",
         kicker="Turning real query data into a short list of work",
         accent=(96, 165, 250), motif=motif_console),
    dict(slug="claude-code-performance-core-web-vitals",
         eyebrow="CORE WEB VITALS",
         title="Claude Code Performance Optimization",
         kicker="Measure, change one thing, measure again",
         accent=(45, 212, 191), motif=motif_gauge),
    dict(slug="claude-code-accessibility-audit",
         eyebrow="WCAG 2.2 WORKFLOW",
         title="Claude Code Accessibility Audit",
         kicker="What a scanner reaches, and what only a person can",
         accent=(196, 181, 253), motif=motif_a11y),
]


def build(a):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    acc = a["accent"]

    # faint grid
    for gx in range(0, W, 40):
        d.line([(gx, 0), (gx, H)], fill=GRID)
    for gy in range(0, H, 40):
        d.line([(0, gy), (W, gy)], fill=GRID)

    # accent rail, fading down
    for i in range(H):
        d.line([(0, i), (7, i)], fill=mix(acc, BG, 1 - (i / H) * 0.72))

    # motif panel on the right
    d.rounded_rectangle([704, 96, 1144, 534], 16, fill=SURFACE, outline=BORDER, width=2)
    a["motif"](d, 758, 148, acc)

    x0 = 72
    d.text((x0, 96), a["eyebrow"], font=font(MONO_B, 17), fill=acc)
    d.line([(x0, 128), (x0 + 46, 128)], fill=acc, width=3)

    f_title = font(SANS_B, 50)
    lines = wrap(d, a["title"], f_title, 560)
    y = 168
    for ln in lines:
        d.text((x0, y), ln, font=f_title, fill=TEXT)
        y += 62

    f_kick = font(SANS, 22)
    y += 14
    for ln in wrap(d, a["kicker"], f_kick, 560):
        d.text((x0, y), ln, font=f_kick, fill=MUTED)
        y += 32

    # footer identity
    d.line([(x0, 500), (640, 500)], fill=BORDER, width=1)
    d.text((x0, 522), "Claude Code Guides", font=font(SANS_B, 19), fill=TEXT)
    d.text((x0, 550), "sitebuilderstack.com", font=font(MONO, 17), fill=DIM)

    p = os.path.join(OUT, "guide-%s.png" % a["slug"])
    img.save(p, "PNG", optimize=True)
    return p


ARTICLES += [
    dict(slug="claude-code-conversion-rate-optimization",
         eyebrow="CONVERSION WORKFLOW",
         title="Claude Code Conversion Rate Optimization",
         kicker="Measure, diagnose, prioritise, change, validate",
         accent=(244, 114, 182), motif=motif_dial),
    dict(slug="ai-website-conversion-audit",
         eyebrow="AUDIT METHOD",
         title="AI Website Conversion Audit",
         kicker="Four passes, an evidence standard, and where AI audits go wrong",
         accent=(134, 239, 172), motif=motif_seo),
    dict(slug="shopify-conversion-audit-claude-code",
         eyebrow="PLATFORM AUDIT",
         title="Shopify Conversion Audit With Claude Code",
         kicker="Duplicated events, the product page, and what checkout will not change",
         accent=(251, 191, 36), motif=motif_store),
    dict(slug="claude-code-landing-page-audit",
         eyebrow="CRO WORKFLOW",
         title="Claude Code Landing Page Audit",
         kicker="Message match, the measured fold, and the order to fix things in",
         accent=(138, 166, 255), motif=motif_pages),
    dict(slug="claude-code-cro-prompts",
         eyebrow="PROMPT LIBRARY",
         title="Claude Code CRO Prompts",
         kicker="Organised by stage, because the order is what makes them useful",
         accent=(167, 139, 250), motif=motif_prompts),
    dict(slug="shopify-admin-api-claude-code",
         eyebrow="PLATFORM AUTOMATION",
         title="Automating Shopify With the Admin API",
         kicker="GraphQL, userErrors, publications, and scripts you can run twice",
         accent=(244, 114, 182), motif=motif_connect),
    dict(slug="claude-code-wordpress",
         eyebrow="PLATFORM WORKFLOW",
         title="How to Build a WordPress Website With Claude Code",
         kicker="Three sources of truth, and only one of them is files",
         accent=(129, 199, 132), motif=motif_layers),
    dict(slug="claude-code-astro",
         eyebrow="PLATFORM WORKFLOW",
         title="How to Build an Astro Website With Claude Code",
         kicker="Content collections, islands, and a build that can fail",
         accent=(255, 167, 122), motif=motif_pages),
    dict(slug="claude-code-vs-cursor-web-development",
         eyebrow="HONEST COMPARISON",
         title="Claude Code vs Cursor for Web Development",
         kicker="No invented benchmarks, and a framework for choosing",
         accent=(196, 181, 253), motif=motif_split),
    dict(slug="claude-code-github-actions-cloudflare",
         eyebrow="CI/CD WORKFLOW",
         title="Deploy With GitHub Actions and Cloudflare",
         kicker="Gates that can fail, previews, smoke tests and rollback",
         accent=(94, 234, 212), motif=motif_gate),
]


if __name__ == "__main__":
    for a in ARTICLES:
        p = build(a)
        print("%-72s %7d bytes" % (p, os.path.getsize(p)))