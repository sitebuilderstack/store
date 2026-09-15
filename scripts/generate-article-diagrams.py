#!/usr/bin/env python3
"""Generate the in-article diagrams for the cornerstone guides.

Each diagram is original and specific to its article: no stock imagery,
no generic flowcharts. Same tokens as assets/sbs.css so they sit inside
the article body without looking pasted in.

Usage: generate-article-diagrams.py <outputDir>
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

OUT = sys.argv[1] if len(sys.argv) > 1 else "brand/articles"
os.makedirs(OUT, exist_ok=True)

W = 1000
BG       = (18, 21, 29)
SURFACE2 = (23, 27, 38)
BORDER   = (35, 42, 56)
TEXT     = (233, 236, 243)
MUTED    = (167, 176, 192)
DIM      = (118, 128, 146)

FDIR = "/usr/share/fonts/truetype/dejavu"
def f(name, size):
    return ImageFont.truetype(os.path.join(FDIR, name), size)

SANS_B = "DejaVuSans-Bold.ttf"
SANS   = "DejaVuSans.ttf"
MONO_B = "DejaVuSansMono-Bold.ttf"
MONO   = "DejaVuSansMono.ttf"


def mix(c, bg, a):
    return tuple(int(round(bg[i] + (c[i] - bg[i]) * a)) for i in range(3))


def canvas(h):
    img = Image.new("RGB", (W, h), BG)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, W - 1, h - 1], 12, outline=BORDER, width=2)
    return img, d


def head(d, title, sub, acc):
    # The subtitle is drawn on one line and is not wrapped, so a long one is
    # silently clipped at the canvas edge. Fail loudly instead.
    for label, text, fnt in (("title", title, f(SANS_B, 26)), ("subtitle", sub, f(SANS, 16))):
        if d.textlength(text, font=fnt) > W - 80:
            raise SystemExit("diagram %s too wide for the canvas (%d px > %d): %r"
                             % (label, d.textlength(text, font=fnt), W - 80, text[:70]))
    d.text((40, 34), title, font=f(SANS_B, 26), fill=TEXT)
    d.text((40, 72), sub, font=f(SANS, 16), fill=MUTED)
    d.line([(40, 106), (W - 40, 106)], fill=BORDER, width=1)
    d.line([(40, 106), (110, 106)], fill=acc, width=3)


def foot(d, h, text, fs=15):
    """Footer line, with the same width guard head() has.

    head() has checked its title and subtitle since the first diagram; the
    footers were drawn with a raw d.text() and were not checked, so a long one
    was clipped at the canvas edge with no error. That happened. Same rule for
    both now.
    """
    fnt = f(SANS, fs)
    if d.textlength(text, font=fnt) > W - 80:
        raise SystemExit("diagram footer too wide for the canvas (%d px > %d): %r"
                         % (d.textlength(text, font=fnt), W - 80, text[:70]))
    d.text((40, h - 58), text, font=fnt, fill=DIM)


def chip(d, x, y, label, acc, on=False, pad=14, fs=15, mono=False):
    fnt = f(MONO if mono else SANS, fs)
    w = d.textlength(label, font=fnt) + pad * 2
    d.rounded_rectangle([x, y, x + w, y + 32], 6,
                        fill=mix(acc, BG, .16) if on else SURFACE2,
                        outline=acc if on else BORDER, width=2)
    d.text((x + pad, y + 7), label, font=fnt, fill=TEXT if on else MUTED)
    return w


def save(img, name):
    p = os.path.join(OUT, name)
    img.save(p, "PNG", optimize=True)
    print("%-58s %6d bytes  %sx%s" % (p, os.path.getsize(p), img.width, img.height))


# ----------------------------------------------------------- diagram 1
def d1_workflow():
    ACC = (138, 166, 255)
    phases = [
        ("DEFINE",  ["1  Define the site"]),
        ("ORIENT",  ["2  Read the repo", "3  Plan first", "4  CLAUDE.md"]),
        ("DESIGN",  ["5  Information architecture", "6  Technical architecture"]),
        ("BUILD",   ["7  Small increments", "8  SEO", "9  Security",
                     "10  Accessibility", "11  Performance"]),
        ("SHIP",    ["12  Validate", "13  Deploy", "14  Get indexed"]),
        ("OPERATE", ["15  Monitor and improve"]),
    ]
    h = 130 + len(phases) * 74 + 46
    img, d = canvas(h)
    head(d, "The fifteen steps, grouped by phase",
         "Each phase produces something the next one depends on. "
         "Nothing moves forward on an unverified step.", ACC)

    y = 132
    for i, (name, steps) in enumerate(phases):
        d.line([(64, y + 6), (64, y + 64)], fill=BORDER, width=2)
        if i < len(phases) - 1:
            d.line([(64, y + 64), (64, y + 74)], fill=BORDER, width=2)
        d.ellipse([56, y + 18, 72, y + 34], fill=BG, outline=ACC, width=3)
        d.text((92, y + 18), name, font=f(MONO_B, 16), fill=ACC)
        x = 210
        for s in steps:
            w = chip(d, x, y + 12, s, ACC, on=(i == 3))
            x += w + 10
        y += 74

    d.text((40, h - 36), "Build is where most of the work is. Ship is where "
           "most of the risk is.", font=f(SANS, 15), fill=DIM)
    save(img, "diagram-build-workflow.png")


# ----------------------------------------------------------- diagram 2
def d2_anatomy():
    ACC = (94, 234, 212)
    parts = [
        ("CONTEXT",      "What this project is, and what already exists",
         "Code that ignores your conventions"),
        ("OBJECTIVE",    "The specific outcome, not the general area",
         "A good answer to a different question"),
        ("CONSTRAINTS",  "What must and must not happen",
         "Reasonable choices you did not want"),
        ("PROCESS",      "The order of work, and where to stop",
         "A twelve-file diff you cannot review"),
        ("VALIDATION",   "How to prove it worked",
         "“Done” meaning “I stopped writing”"),
        ("DELIVERABLES", "What you want back, and in what form",
         "Prose where you wanted a table"),
    ]
    h = 130 + len(parts) * 62 + 60
    img, d = canvas(h)
    head(d, "The six parts of a prompt that works",
         "Process and Validation are the two most often missing.", ACC)

    d.text((40, 122), "PART", font=f(MONO_B, 13), fill=DIM)
    d.text((222, 122), "WHAT IT DOES", font=f(MONO_B, 13), fill=DIM)
    d.text((622, 122), "WITHOUT IT", font=f(MONO_B, 13), fill=DIM)

    y = 146
    for i, (name, does, without) in enumerate(parts):
        key = name in ("PROCESS", "VALIDATION")
        d.rounded_rectangle([40, y, W - 40, y + 50], 8,
                            fill=mix(ACC, BG, .10) if key else SURFACE2,
                            outline=ACC if key else BORDER, width=2)
        d.text((58, y + 16), name, font=f(MONO_B, 15), fill=ACC if key else TEXT)
        d.text((222, y + 17), does, font=f(SANS, 14), fill=MUTED)
        d.text((622, y + 17), without, font=f(SANS, 14), fill=DIM)
        y += 62

    d.text((40, h - 44), "Highlighted: the two parts that turn a request into "
           "something you can check.", font=f(SANS, 15), fill=DIM)
    save(img, "diagram-prompt-anatomy.png")


# ----------------------------------------------------------- diagram 3
def d3_memory():
    ACC = (196, 181, 253)
    layers = [
        ("Enterprise policy", "managed system path", "Organisation-wide rules", False),
        ("Project", "./CLAUDE.md", "Team conventions — committed to git", True),
        ("User", "~/.claude/CLAUDE.md", "Your preferences, every project", False),
        ("Directory", "src/pkg/CLAUDE.md", "Loaded when work happens in that subtree", False),
    ]
    h = 132 + len(layers) * 78 + 66
    img, d = canvas(h)
    head(d, "Where memory comes from",
         "These combine rather than replace one another. Everything that "
         "applies is loaded into the same context.", ACC)

    y = 138
    for name, path, note, key in layers:
        d.rounded_rectangle([40, y, W - 260, y + 62], 8,
                            fill=mix(ACC, BG, .12) if key else SURFACE2,
                            outline=ACC if key else BORDER, width=2)
        d.text((60, y + 12), name, font=f(SANS_B, 17), fill=TEXT)
        d.text((60, y + 36), path, font=f(MONO, 14), fill=ACC if key else DIM)
        d.text((W - 240, y + 22), note, font=f(SANS, 14), fill=MUTED)
        y += 78

    ay = 138
    d.line([(24, ay + 20), (24, y - 36)], fill=BORDER, width=2)
    d.polygon([(19, y - 42), (29, y - 42), (24, y - 26)], fill=BORDER)
    d.text((40, h - 50), "Narrower scope loads later. The project file is the one "
           "your team shares — keep it under about 200 lines.",
           font=f(SANS, 15), fill=DIM)
    save(img, "diagram-memory-precedence.png")


# ----------------------------------------------------------- diagram 4
def d4_pushorder():
    ACC = (251, 191, 36)
    steps = [
        ("1", "assets/  layout/  snippets/  sections/",
         "Liquid and static files. Nothing references them yet."),
        ("2", "sections/*-group.json",
         "Section groups name sections by filename — they must exist first."),
        ("3", "templates/",
         "Templates reference sections and section groups."),
        ("4", "config/",
         "Settings last. Values must match their schema type."),
    ]
    h = 132 + len(steps) * 86 + 70
    img, d = canvas(h)
    head(d, "Theme push order, and why it is not arbitrary",
         "Every stage references the one before it. Push out of order and "
         "the push fails on an unknown section.", ACC)

    y = 138
    for i, (n, what, why) in enumerate(steps):
        d.rounded_rectangle([40, y, W - 40, y + 68], 8, fill=SURFACE2,
                            outline=BORDER, width=2)
        d.ellipse([58, y + 20, 92, y + 54], fill=mix(ACC, BG, .20),
                  outline=ACC, width=2)
        d.text((70, y + 27), n, font=f(MONO_B, 19), fill=ACC)
        d.text((112, y + 16), what, font=f(MONO_B, 16), fill=TEXT)
        d.text((112, y + 42), why, font=f(SANS, 14), fill=MUTED)
        if i < len(steps) - 1:
            cx = 75
            d.line([(cx, y + 68), (cx, y + 86)], fill=ACC, width=2)
            d.polygon([(cx - 5, y + 80), (cx + 5, y + 80), (cx, y + 88)], fill=ACC)
        y += 86

    d.text((40, h - 52), "Then fetch the preview URL and read the response body. "
           "A successful push is not evidence the page renders.",
           font=f(SANS, 15), fill=DIM)
    save(img, "diagram-theme-push-order.png")


# ----------------------------------------------------------- diagram 4b
def d4b_mutation():
    """The Admin API failure that returns HTTP 200.

    Drawn as two paths from one response because that is the shape of the
    mistake: both branches are a 200, and only one of them changed anything.
    """
    ACC = (244, 114, 182)
    h = 132 + 3 * 92 + 86
    img, d = canvas(h)
    head(d, "Why a Shopify mutation can succeed and change nothing",
         "A mutation that fails validation returns HTTP 200 with an empty "
         "result. Checking the status code reports success.", ACC)

    rows = [
        ("POST /admin/api/2025-07/graphql.json", "HTTP 200", TEXT,
         "The status code is the same either way."),
        ('"product": null,  "userErrors": [ ... ]', "CHANGED NOTHING", ACC,
         "Validation failed. The only signal is the array."),
        ('"product": { "id": ... },  "userErrors": []', "WROTE", MUTED,
         "The empty array is the success condition."),
    ]
    y = 138
    for i, (left, tag, tagcol, note) in enumerate(rows):
        d.rounded_rectangle([40, y, W - 40, y + 74], 8, fill=SURFACE2,
                            outline=ACC if i == 1 else BORDER, width=2)
        d.text((60, y + 14), left, font=f(MONO_B, 15), fill=TEXT)
        d.text((60, y + 44), note, font=f(SANS, 14), fill=MUTED)
        tw = d.textlength(tag, font=f(MONO_B, 14))
        d.rounded_rectangle([W - 60 - tw - 20, y + 18, W - 60, y + 46], 6,
                            fill=mix(tagcol, BG, .18), outline=tagcol, width=1)
        d.text((W - 60 - tw - 10, y + 24), tag, font=f(MONO_B, 14), fill=tagcol)
        if i == 0:
            cx = 78
            d.line([(cx, y + 74), (cx, y + 92)], fill=ACC, width=2)
            d.polygon([(cx - 5, y + 86), (cx + 5, y + 86), (cx, y + 94)], fill=ACC)
        y += 92

    foot(d, h, "Check userErrors in the shared client, not in each "
           "script. Then send an invalid mutation once and watch it stop.", 15)
    save(img, "diagram-shopify-mutation-errors.png")


# ----------------------------------------------------------- diagram 5
def d5_seo_order():
    ACC = (134, 239, 172)
    tiers = [
        ("Content worth ranking", "Does this help anyone?"),
        ("Experience", "Speed, mobile, accessibility"),
        ("Machine-readable layer", "Structured data"),
        ("Description", "Titles, meta descriptions, headings"),
        ("Discovery", "Sitemaps, internal links"),
        ("Canonicalisation", "Which URL is the real one"),
        ("URL behaviour", "Status codes, redirects, duplicates"),
        ("Crawlable and indexable", "Everything above is moot until this holds"),
    ]
    h = 132 + len(tiers) * 56 + 70
    img, d = canvas(h)
    head(d, "Audit order: work up from the foundation",
         "Each tier depends on the one below it. Optimising a title tag on a "
         "blocked page achieves nothing.", ACC)

    y = 138
    n = len(tiers)
    for i, (name, note) in enumerate(tiers):
        inset = (n - 1 - i) * 26
        base = (i == n - 1)
        d.rounded_rectangle([40 + inset, y, W - 40 - inset, y + 46], 8,
                            fill=mix(ACC, BG, .16) if base else SURFACE2,
                            outline=ACC if base else BORDER, width=2)
        d.text((60 + inset, y + 14), name, font=f(SANS_B, 15),
               fill=TEXT if base else MUTED)
        tw = d.textlength(note, font=f(SANS, 13))
        d.text((W - 60 - inset - tw, y + 16), note, font=f(SANS, 13), fill=DIM)
        y += 56

    d.text((40, h - 52), "Read bottom to top. Fix bottom to top.",
           font=f(SANS, 15), fill=DIM)
    save(img, "diagram-seo-audit-order.png")



# ----------------------------------------------------------- diagram 6
def d6_isolation():
    ACC = (125, 211, 252)
    h = 470
    img, d = canvas(h)
    head(d, "What a subagent keeps out of your context",
         "Only the summary returns. The files it read to produce that summary "
         "never enter your session.", ACC)

    d.rounded_rectangle([40, 150, 430, 300], 10, fill=SURFACE2, outline=ACC, width=3)
    d.text((60, 166), "YOUR SESSION", font=f(MONO_B, 14), fill=ACC)
    for i, t in enumerate(("the plan", "the decisions", "one summary back")):
        d.text((60, 198 + i * 30), "\u2022  " + t, font=f(SANS, 15), fill=TEXT)

    d.rounded_rectangle([570, 150, W - 40, 380], 10, fill=BG, outline=BORDER, width=2)
    d.text((590, 166), "SUBAGENT CONTEXT", font=f(MONO_B, 14), fill=DIM)
    for i, t in enumerate(("40 files read", "12 greps", "3 command runs",
                           "dead ends explored", "all discarded")):
        d.text((590, 198 + i * 30), "\u2022  " + t, font=f(SANS, 15), fill=DIM)

    d.line([(430, 200), (570, 200)], fill=ACC, width=2)
    d.polygon([(560, 194), (560, 206), (574, 200)], fill=ACC)
    d.text((444, 176), "task", font=f(MONO, 13), fill=DIM)
    d.line([(570, 262), (430, 262)], fill=ACC, width=2)
    d.polygon([(440, 256), (440, 268), (426, 262)], fill=ACC)
    d.text((452, 238), "summary only", font=f(MONO, 13), fill=ACC)

    d.text((40, h - 46), "This is why Explore is worth reaching for more often "
           "than feels natural.", font=f(SANS, 15), fill=DIM)
    save(img, "diagram-subagent-isolation.png")


# ----------------------------------------------------------- diagram 7
def d7_where():
    ACC = (253, 164, 175)
    rows = [
        ("CLAUDE.md", "Facts and rules that must always hold",
         "Every request, forever", True),
        ("Skill", "A procedure you run sometimes",
         "Only when used", False),
        ("Subagent", "Work needing its own context and tool limits",
         "Only when delegated", False),
    ]
    h = 132 + len(rows) * 88 + 66
    img, d = canvas(h)
    head(d, "Where a piece of knowledge belongs",
         "The test: would it be wrong for Claude not to know this right now?",
         ACC)
    d.text((60, 124), "PUT IT IN", font=f(MONO_B, 13), fill=DIM)
    d.text((260, 124), "WHEN IT IS", font=f(MONO_B, 13), fill=DIM)
    d.text((700, 124), "CONTEXT COST", font=f(MONO_B, 13), fill=DIM)
    y = 148
    for name, what, cost, hot in rows:
        d.rounded_rectangle([40, y, W - 40, y + 72], 8,
                            fill=mix(ACC, BG, .12) if hot else SURFACE2,
                            outline=ACC if hot else BORDER, width=2)
        d.text((60, y + 26), name, font=f(MONO_B, 17), fill=ACC if hot else TEXT)
        d.text((260, y + 27), what, font=f(SANS, 15), fill=MUTED)
        d.text((700, y + 27), cost, font=f(SANS, 15),
               fill=ACC if hot else DIM)
        y += 88
    d.text((40, h - 48), "Highlighted: the one you pay for on every single "
           "message, including the unrelated ones.", font=f(SANS, 15), fill=DIM)
    save(img, "diagram-skill-vs-claudemd.png")


# ----------------------------------------------------------- diagram 8
def d8_plugin_layout():
    ACC = (190, 242, 100)
    BAD = (255, 158, 150)
    h = 520
    img, d = canvas(h)
    head(d, "Plugin layout, and the one mistake that fails silently",
         "Only plugin.json goes inside .claude-plugin/. Everything else sits at "
         "the plugin root.", ACC)

    d.rounded_rectangle([40, 146, 470, 470], 10, fill=SURFACE2, outline=ACC, width=2)
    d.text((60, 162), "CORRECT", font=f(MONO_B, 14), fill=ACC)
    lines = ["my-plugin/", "  .claude-plugin/", "    plugin.json", "  skills/",
             "  agents/", "  hooks/", "  .mcp.json"]
    for i, t in enumerate(lines):
        col = ACC if "plugin.json" in t or ".claude-plugin" in t else TEXT
        d.text((62, 196 + i * 32), t, font=f(MONO, 17), fill=col)

    d.rounded_rectangle([530, 146, W - 40, 470], 10, fill=SURFACE2, outline=BAD, width=2)
    d.text((552, 162), "SILENTLY BROKEN", font=f(MONO_B, 14), fill=BAD)
    bad_lines = ["my-plugin/", "  .claude-plugin/", "    plugin.json",
                 "    skills/   \u2190 never found", "    agents/   \u2190 never found",
                 "", "no error, plugin does nothing"]
    for i, t in enumerate(bad_lines):
        col = BAD if "never found" in t or "does nothing" in t else TEXT
        fnt = f(SANS, 15) if "does nothing" in t else f(MONO, 17)
        d.text((554, 196 + i * 32), t, font=fnt, fill=col)
    save(img, "diagram-plugin-structure.png")


# ----------------------------------------------------------- diagram 9
def d9_certs():
    ACC = (240, 171, 252)
    GAP = (167, 176, 192)
    certs = [
        ("Claude Certified Associate: Foundations", "Everyday use of Claude", False),
        ("Claude Certified Developer: Foundations", "API, tool use, agent development", False),
        ("Claude Certified Architect: Foundations", "Designing agent systems", False),
        ("Claude Certified Architect: Professional", "Enterprise architecture and governance", False),
        ("A Claude Code certification", "Does not exist", True),
    ]
    h = 132 + len(certs) * 74 + 62
    img, d = canvas(h)
    head(d, "What Anthropic certifies",
         "Four role-based credentials, delivered through Pearson with Credly "
         "badges. None is specific to Claude Code.", ACC)
    y = 142
    for name, who, absent in certs:
        d.rounded_rectangle([40, y, W - 40, y + 58], 8,
                            fill=BG if absent else SURFACE2,
                            outline=GAP if absent else ACC, width=2)
        if absent:
            for dx in range(44, W - 44, 14):
                d.line([(dx, y + 58), (dx + 7, y + 58)], fill=GAP, width=2)
        d.text((62, y + 19), name, font=f(SANS_B, 16), fill=GAP if absent else TEXT)
        tw = d.textlength(who, font=f(SANS, 14))
        d.text((W - 62 - tw, y + 21), who, font=f(SANS, 14),
               fill=GAP if absent else MUTED)
        y += 74
    d.text((40, h - 44), "The closest overlap is Developer: Foundations \u2014 adjacent, "
           "not the same subject.", font=f(SANS, 15), fill=DIM)
    save(img, "diagram-claude-certifications.png")


# ---------------------------------------------------------- diagram 10
def d10_enforcement():
    ACC = (253, 224, 71)
    rows = [
        ("CLAUDE.md", "Instructions in context", "Followed, not guaranteed", False),
        ("Managed settings", "Permission rules and configuration", "Enforced by the tool", True),
        ("Hooks", "Shell commands on tool events", "Enforced by your own code", False),
    ]
    h = 132 + len(rows) * 86 + 66
    img, d = canvas(h)
    head(d, "Three ways to make a rule stick",
         "They differ in one respect that decides where each of your rules "
         "belongs: whether compliance is guaranteed.", ACC)
    d.text((60, 124), "MECHANISM", font=f(MONO_B, 13), fill=DIM)
    d.text((330, 124), "WHAT IT IS", font=f(MONO_B, 13), fill=DIM)
    d.text((700, 124), "ENFORCEMENT", font=f(MONO_B, 13), fill=DIM)
    y = 148
    for name, what, enf, hot in rows:
        d.rounded_rectangle([40, y, W - 40, y + 70], 8,
                            fill=mix(ACC, BG, .12) if hot else SURFACE2,
                            outline=ACC if hot else BORDER, width=2)
        d.text((60, y + 25), name, font=f(MONO_B, 16), fill=ACC if hot else TEXT)
        d.text((330, y + 26), what, font=f(SANS, 15), fill=MUTED)
        d.text((700, y + 26), enf, font=f(SANS, 15), fill=ACC if hot else DIM)
        y += 86
    d.text((40, h - 48), "If being missed would be serious, it belongs in the "
           "middle row \u2014 and keep the reason in the top one.",
           font=f(SANS, 15), fill=DIM)
    save(img, "diagram-enforcement-layers.png")


# ---------------------------------------------------------- diagram 11
def d11_dial():
    ACC = (251, 146, 60)
    h = 430
    img, d = canvas(h)
    head(d, "It is a dial, not a side",
         "You can move it per task. The skill worth developing is noticing "
         "which end you are on.", ACC)

    ty = 250
    d.rounded_rectangle([70, ty - 14, W - 70, ty + 14], 14, fill=SURFACE2,
                        outline=BORDER, width=2)
    stops = [(0.06, "layout\nprototype"), (0.30, "internal\ntool"),
             (0.62, "customer\nfeature"), (0.92, "auth and\npayments")]
    for frac, label in stops:
        x = 70 + (W - 140) * frac
        hot = frac > 0.5
        d.ellipse([x - 15, ty - 15, x + 15, ty + 15], fill=BG,
                  outline=ACC if hot else BORDER, width=3)
        for i, line in enumerate(label.split("\n")):
            tw = d.textlength(line, font=f(SANS, 14))
            d.text((x - tw / 2, ty + 34 + i * 20), line, font=f(SANS, 14),
                   fill=TEXT if hot else MUTED)
    d.text((70, ty - 66), "VIBES", font=f(MONO_B, 16), fill=ACC)
    tw = d.textlength("DISCIPLINED", font=f(MONO_B, 16))
    d.text((W - 70 - tw, ty - 66), "DISCIPLINED", font=f(MONO_B, 16), fill=TEXT)
    d.text((40, h - 46), "Read the structure, verify what fails silently, write "
           "the decisions down. About an hour.", font=f(SANS, 15), fill=DIM)
    save(img, "diagram-vibe-coding-dial.png")



# ---------------------------------------------------------- diagram 12
def d12_modes():
    ACC = (147, 197, 253)
    h = 470
    img, d = canvas(h)
    head(d, "The mode is decided by one input",
         "You do not choose it. The action infers it from whether you supplied a "
         "`prompt`.", ACC)
    cols = [
        ("INTERACTIVE", "no prompt input",
         ["triggered by @claude", "in a comment, review,", "or a new issue",
          "", "output: a comment on", "the issue or PR"], False),
        ("AUTOMATION", "prompt input present",
         ["triggered by any", "GitHub event \u2014 a PR,", "a cron schedule, a label",
          "", "output: the run log,", "unless the prompt says", "otherwise"], True),
    ]
    for i, (name, sub, lines, hot) in enumerate(cols):
        x0 = 40 + i * 470
        d.rounded_rectangle([x0, 140, x0 + 450, h - 70], 10,
                            fill=mix(ACC, BG, .12) if hot else SURFACE2,
                            outline=ACC if hot else BORDER, width=2)
        d.text((x0 + 24, 158), name, font=f(MONO_B, 15), fill=ACC if hot else TEXT)
        d.text((x0 + 24, 182), sub, font=f(MONO, 13), fill=DIM)
        for j, ln in enumerate(lines):
            d.text((x0 + 24, 216 + j * 26), ln, font=f(SANS, 15), fill=MUTED)
    d.text((40, h - 46), "The right-hand column is where the durable value is: a check "
           "nobody has to remember to ask for.", font=f(SANS, 15), fill=DIM)
    save(img, "diagram-action-modes.png")


# ---------------------------------------------------------- diagram 13
def d13_firstweek():
    ACC = (216, 180, 254)
    days = [
        ("Days 1-2", "Ask, do not tell", "Codebase questions. Zero risk, fast calibration."),
        ("Day 3", "Small verifiable changes", "A bug with a reproduction. \u201cDid it work\u201d has one answer."),
        ("Day 4", "Ask for a plan first", "Before anything touching more than one file."),
        ("Day 5", "Write a CLAUDE.md", "The moment you explain the same convention twice."),
        ("Rest", "Let it drive git", "Commits, branches, history. Low risk, recoverable."),
    ]
    h = 132 + len(days) * 74 + 60
    img, d = canvas(h)
    head(d, "A first week that builds judgement before dependency",
         "The order matters more than the speed.", ACC)
    y = 140
    for i, (when, what, why) in enumerate(days):
        d.line([(74, y - 6), (74, y + 62)], fill=BORDER, width=2)
        d.ellipse([66, y + 20, 82, y + 36], fill=BG, outline=ACC, width=3)
        d.text((40, y + 20), when, font=f(MONO_B, 13), fill=ACC)
        d.rounded_rectangle([160, y, W - 40, y + 56], 8, fill=SURFACE2,
                            outline=BORDER, width=2)
        d.text((180, y + 8), what, font=f(SANS_B, 16), fill=TEXT)
        d.text((180, y + 31), why, font=f(SANS, 14), fill=MUTED)
        y += 74
    d.text((40, h - 44), "Skipping to day 4 is the commonest reason people conclude the "
           "tool is unreliable.", font=f(SANS, 15), fill=DIM)
    save(img, "diagram-first-week.png")


# ---------------------------------------------------------- diagram 14
def d14_scopes():
    ACC = (103, 232, 249)
    rows = [
        ("Local", "~/.claude.json", "This project", "No", False),
        ("Project", ".mcp.json at the repo root", "This project", "YES \u2014 commit it", True),
        ("User", "~/.claude.json", "All your projects", "No", False),
    ]
    h = 132 + len(rows) * 82 + 62
    img, d = canvas(h)
    head(d, "Three MCP scopes, one of which is shareable",
         "Choosing the wrong one is why a colleague cannot see the server you added.",
         ACC)
    d.text((60, 124), "SCOPE", font=f(MONO_B, 13), fill=DIM)
    d.text((210, 124), "WRITTEN TO", font=f(MONO_B, 13), fill=DIM)
    d.text((580, 124), "LOADS IN", font=f(MONO_B, 13), fill=DIM)
    d.text((800, 124), "SHARED", font=f(MONO_B, 13), fill=DIM)
    y = 148
    for name, path, loads, shared, hot in rows:
        d.rounded_rectangle([40, y, W - 40, y + 66], 8,
                            fill=mix(ACC, BG, .12) if hot else SURFACE2,
                            outline=ACC if hot else BORDER, width=2)
        d.text((60, y + 23), name, font=f(SANS_B, 16), fill=ACC if hot else TEXT)
        d.text((210, y + 24), path, font=f(MONO, 14), fill=MUTED)
        d.text((580, y + 24), loads, font=f(SANS, 14), fill=MUTED)
        d.text((800, y + 24), shared, font=f(SANS_B if hot else SANS, 14),
               fill=ACC if hot else DIM)
        y += 82
    d.text((40, h - 44), "Local and User both land in ~/.claude.json. Neither travels with "
           "the repository.", font=f(SANS, 15), fill=DIM)
    save(img, "diagram-mcp-scopes.png")


# ---------------------------------------------------------- diagram 15
def d15_exit():
    ACC = (252, 165, 165)
    rows = [
        ("exit 0", "Success", "Stdout starting with { is parsed as JSON output", False),
        ("exit 2", "BLOCKS the action", "On capable events. Cannot be overridden, even by JSON", True),
        ("exit 1", "Nothing", "Ignored. Only JSON output controls the decision", False),
        ("other", "Nothing", "Same as exit 1. WorktreeCreate is the one exception", False),
    ]
    h = 132 + len(rows) * 76 + 66
    img, d = canvas(h)
    head(d, "Exit codes are not what you would assume",
         "A hook that fails with a normal error code lets the action straight through.",
         ACC)
    y = 142
    for code, effect, detail, hot in rows:
        d.rounded_rectangle([40, y, W - 40, y + 60], 8,
                            fill=mix(ACC, BG, .14) if hot else SURFACE2,
                            outline=ACC if hot else BORDER, width=3 if hot else 2)
        d.text((62, y + 20), code, font=f(MONO_B, 17), fill=ACC if hot else TEXT)
        d.text((190, y + 20), effect, font=f(SANS_B, 16), fill=ACC if hot else MUTED)
        d.text((420, y + 21), detail, font=f(SANS, 14), fill=MUTED if hot else DIM)
        y += 76
    d.text((40, h - 48), "If you want to stop something, you must exit 2. There is no "
           "other way.", font=f(SANS, 15), fill=DIM)
    save(img, "diagram-hook-exit-codes.png")


# ---------------------------------------------------------- diagram 16
def d16_audit_order():
    ACC = (153, 246, 228)
    steps = [
        ("1", "Crawl", "Status, title, description, canonical, word count — for every URL"),
        ("2", "Fetch rendered HTML", "One page per template. What ships, not what the template says"),
        ("3", "Use the site", "On a phone. Try to do the thing it wants you to do"),
        ("4", "Read the code", "Last. Now you know what to look for"),
    ]
    h = 132 + len(steps) * 74 + 74
    img, d = canvas(h)
    head(d, "Audit order: observe first, read the source last",
         "Read the source first and you see what the site is meant to do, "
         "not what it does.", ACC)
    y = 140
    for i, (n, name, note) in enumerate(steps):
        last = (i == len(steps) - 1)
        d.rounded_rectangle([40, y, W - 40, y + 58], 8,
                            fill=mix(ACC, BG, .14) if last else SURFACE2,
                            outline=ACC if last else BORDER, width=3 if last else 2)
        d.ellipse([62, y + 15, 90, y + 43], outline=ACC if last else DIM, width=2)
        d.text((71, y + 21), n, font=f(MONO_B, 15), fill=ACC if last else MUTED)
        d.text((112, y + 20), name, font=f(SANS_B, 16), fill=TEXT if last else MUTED)
        d.text((330, y + 21), note, font=f(SANS, 14), fill=MUTED if last else DIM)
        y += 74
    d.text((40, h - 54), "Steps 1 and 2 are machine work. Step 3 is the one nobody does. "
           "Step 4 is where the fix lives.", font=f(SANS, 15), fill=DIM)
    save(img, "diagram-audit-order.png")


# ---------------------------------------------------------- diagram 17
def d17_check_can_fail():
    ACC = (165, 180, 252)
    rows = [
        ("PASS", "The check ran and the condition held", "Evidence", False),
        ("PASS", "The check ran against the wrong thing", "Indistinguishable from the row above", True),
        ("PASS", "The check never ran at all", "Indistinguishable from the row above", True),
        ("FAIL", "The check ran and the condition broke", "Evidence, and the only proof the check works", False),
    ]
    h = 132 + len(rows) * 76 + 78
    img, d = canvas(h)
    head(d, "Three of these produce the same output",
         "A passing check is only evidence once you have watched the same check fail.",
         ACC)
    y = 142
    for verdict, what, meaning, hot in rows:
        d.rounded_rectangle([40, y, W - 40, y + 60], 8,
                            fill=mix(ACC, BG, .14) if hot else SURFACE2,
                            outline=ACC if hot else BORDER, width=3 if hot else 2)
        d.text((62, y + 21), verdict, font=f(MONO_B, 16), fill=ACC if hot else TEXT)
        d.text((150, y + 20), what, font=f(SANS_B, 15), fill=TEXT if hot else MUTED)
        tw = d.textlength(meaning, font=f(SANS, 13))
        d.text((W - 62 - tw, y + 22), meaning, font=f(SANS, 13), fill=ACC if hot else DIM)
        y += 76
    d.text((40, h - 56), "Break the thing on purpose. If the check stays green, it was "
           "never checking.", font=f(SANS, 15), fill=DIM)
    save(img, "diagram-check-can-fail.png")


# ---------------------------------------------------------- diagram 18
def d18_claudemd_by_project():
    ACC = (249, 168, 212)
    cols = ["static site", "web app", "shopify theme", "monorepo pkg"]
    rows = [
        ("Commands",        ["same", "same", "differs", "differs"]),
        ("Architecture",    ["differs", "differs", "differs", "differs"]),
        ("Testing",         ["light", "same", "differs", "same"]),
        ("Security",        ["light", "same", "differs", "light"]),
        ("Accessibility",   ["same", "same", "same", "omit"]),
        ("SEO",             ["same", "light", "same", "omit"]),
        ("Deployment",      ["differs", "differs", "differs", "omit"]),
        ("Do not",          ["same", "same", "differs", "same"]),
    ]
    x0, colw = 250, 176
    h = 132 + 44 + len(rows) * 46 + 70
    img, d = canvas(h)
    head(d, "What actually changes between CLAUDE.md files",
         "Most sections carry over unchanged. The ones that differ are the ones "
         "worth spending time on.", ACC)
    y = 142
    for i, c in enumerate(cols):
        cx = x0 + i * colw
        d.text((cx, y), c, font=f(MONO_B, 13), fill=MUTED)
    y += 32
    for name, cells in rows:
        d.line([(40, y - 8), (W - 40, y - 8)], fill=BORDER, width=1)
        d.text((56, y + 8), name, font=f(SANS_B, 14), fill=TEXT)
        for i, cell in enumerate(cells):
            cx = x0 + i * colw
            if cell == "differs":
                d.rounded_rectangle([cx, y + 4, cx + 84, y + 30], 5,
                                    fill=mix(ACC, BG, .18), outline=ACC, width=2)
                d.text((cx + 12, y + 10), "differs", font=f(SANS_B, 12), fill=ACC)
            elif cell == "omit":
                d.text((cx + 6, y + 9), "omit", font=f(SANS, 13), fill=DIM)
            elif cell == "light":
                d.text((cx + 6, y + 9), "trimmed", font=f(SANS, 13), fill=MUTED)
            else:
                d.text((cx + 6, y + 9), "as-is", font=f(SANS, 13), fill=DIM)
        y += 46
    d.text((40, h - 50), "Architecture and deployment carry nearly all of the difference. "
           "The rest is copied and trimmed.",
           font=f(SANS, 15), fill=DIM)
    save(img, "diagram-claude-md-by-project.png")


# ---------------------------------------------------------- diagram 19
def d19_shopify_urls():
    ACC = (254, 215, 170)
    variants = [
        ("/products/<handle>", "200", "canonical to itself"),
        ("/products/<handle>?variant=<id>", "200", "canonical strips the parameter"),
        ("/products/<handle>?utm_source=...", "200", "canonical strips the parameter"),
        ("/collections/<c>/products/<handle>", "200", "canonical points at /products/<handle>"),
        ("/collections/all/products/<handle>", "301", "redirects to /products/<handle>"),
    ]
    h = 132 + len(variants) * 68 + 82
    img, d = canvas(h)
    head(d, "One product, five URLs, one canonical",
         "Measured on a live storefront. Shopify resolves all of this; the job "
         "is to confirm it.", ACC)
    y = 140
    for url, code, note in variants:
        redir = code == "301"
        d.rounded_rectangle([40, y, W - 40, y + 54], 8,
                            fill=mix(ACC, BG, .12) if redir else SURFACE2,
                            outline=ACC if redir else BORDER, width=2)
        d.text((62, y + 19), url, font=f(MONO, 14), fill=TEXT)
        d.text((560, y + 19), code, font=f(MONO_B, 14), fill=ACC if redir else DIM)
        d.text((620, y + 20), note, font=f(SANS, 13), fill=MUTED if redir else DIM)
        y += 68
    d.text((40, h - 60), "Nothing here needed a theme change. Every line was verified by "
           "fetching the URL and reading",
           font=f(SANS, 15), fill=DIM)
    d.text((40, h - 38), "the canonical tag out of the response.",
           font=f(SANS, 15), fill=DIM)
    save(img, "diagram-shopify-url-variants.png")


# ---------------------------------------------------------- diagram 20
def d20_security_reach():
    ACC = (248, 113, 113)
    rows = [
        ("Source code", "Reads it all", "Secrets, injection, authorisation logic, unsafe DOM", True),
        ("Configuration", "Reads it all", "Headers, CSP, CI/CD, environment separation", True),
        ("Dependencies", "Runs the scanner", "Known CVEs in the lockfile", True),
        ("Deployed site", "Only what it requests", "Live headers, exposed paths, error pages", True),
        ("Running behaviour", "Cannot observe", "Race conditions, session handling under load", False),
        ("Adversarial testing", "Must not attempt", "Exploitation, chaining, privilege escalation", False),
        ("Threat modelling", "Cannot decide", "What matters, to whom, and how much", False),
    ]
    h = 132 + len(rows) * 62 + 72
    img, d = canvas(h)
    head(d, "What a security audit with an agent actually reaches",
         "The top four are where it earns its place. The bottom three are not a "
         "gap in the tooling — they are a different job.", ACC)
    y = 140
    for name, verdict, detail, reach in rows:
        d.rounded_rectangle([40, y, W - 40, y + 50], 8,
                            fill=SURFACE2 if reach else mix(ACC, BG, .12),
                            outline=BORDER if reach else ACC, width=2)
        gx, gy = 66, y + 25
        if reach:
            d.line([(gx - 10, gy), (gx - 2, gy + 9), (gx + 12, gy - 10)],
                   fill=MUTED, width=3, joint="curve")
        else:
            d.line([(gx - 9, gy - 9), (gx + 11, gy + 11)], fill=ACC, width=3)
            d.line([(gx + 11, gy - 9), (gx - 9, gy + 11)], fill=ACC, width=3)
        d.text((100, y + 16), name, font=f(SANS_B, 15), fill=TEXT if not reach else MUTED)
        d.text((280, y + 17), verdict, font=f(MONO, 13), fill=ACC if not reach else DIM)
        d.text((470, y + 17), detail, font=f(SANS, 13), fill=DIM)
        y += 62
    d.text((40, h - 52), "An audit that does not say which row it stopped at is not "
           "finished, it is unlabelled.", font=f(SANS, 15), fill=DIM)
    save(img, "diagram-security-audit-reach.png")


# ---------------------------------------------------------- diagram 21
def d21_position_tiers():
    ACC = (96, 165, 250)
    tiers = [
        ("1-3", "Leave alone", "Protect. Editing a page that ranks is how you lose it", False),
        ("4-10", "Optimise", "Metadata, intent match, internal links. Cheapest gains", True),
        ("11-20", "Strengthen", "A real gap in the page. Add the missing subtopic", True),
        ("21-40", "Read as signal", "Google associates you with this. Usually a content call", False),
        ("40+", "Ignore for now", "Not a ranking. On-page work will not move it", False),
    ]
    h = 132 + len(tiers) * 64 + 74
    img, d = canvas(h)
    head(d, "What to do at each position band",
         "The band decides the action. Treating every row the same is how a "
         "Search Console export becomes busywork.", ACC)
    y = 140
    for band, action, note, hot in tiers:
        d.rounded_rectangle([40, y, W - 40, y + 52], 8,
                            fill=mix(ACC, BG, .16) if hot else SURFACE2,
                            outline=ACC if hot else BORDER, width=3 if hot else 2)
        d.text((64, y + 17), band, font=f(MONO_B, 17), fill=ACC if hot else DIM)
        d.text((170, y + 17), action, font=f(SANS_B, 15), fill=TEXT if hot else MUTED)
        d.text((380, y + 18), note, font=f(SANS, 13), fill=MUTED if hot else DIM)
        y += 64
    d.text((40, h - 54), "Impressions decide whether a row is worth reading at all. "
           "Under about ten, the position is noise.", font=f(SANS, 15), fill=DIM)
    save(img, "diagram-gsc-position-tiers.png")


# ---------------------------------------------------------- diagram 22
def d22_perf_loop():
    ACC = (45, 212, 191)
    steps = [
        ("Measure", "Record the baseline. Field data if you have it, lab if you do not"),
        ("Locate", "Find the single largest contributor. Not a list of twelve"),
        ("Hypothesise", "Say what you expect to change, and by roughly how much"),
        ("Change ONE thing", "One variable. This is the whole discipline"),
        ("Measure again", "Same tool, same conditions, same page"),
        ("Keep or revert", "If it did not move, revert it. A neutral change is a cost"),
    ]
    h = 132 + len(steps) * 62 + 76
    img, d = canvas(h)
    head(d, "The loop, and the rule that makes it work",
         "Change five things at once and you have learned nothing about any of "
         "them, however much the score moved.", ACC)
    y = 140
    for i, (name, note) in enumerate(steps):
        hot = i == 3
        d.rounded_rectangle([40, y, W - 40, y + 50], 8,
                            fill=mix(ACC, BG, .16) if hot else SURFACE2,
                            outline=ACC if hot else BORDER, width=3 if hot else 2)
        d.ellipse([62, y + 13, 86, y + 37], outline=ACC if hot else DIM, width=2)
        d.text((70, y + 17), str(i + 1), font=f(MONO_B, 14), fill=ACC if hot else DIM)
        d.text((108, y + 16), name, font=f(SANS_B, 15), fill=TEXT if hot else MUTED)
        d.text((330, y + 17), note, font=f(SANS, 13), fill=MUTED if hot else DIM)
        if i < len(steps) - 1:
            d.line([(74, y + 50), (74, y + 62)], fill=BORDER, width=2)
        y += 62
    d.text((40, h - 56), "Step 6 is the one people skip. A change that did not help "
           "is still code you have to maintain.", font=f(SANS, 15), fill=DIM)
    save(img, "diagram-perf-loop.png")


# ---------------------------------------------------------- diagram 23
def d23_a11y_split():
    ACC = (196, 181, 253)
    left = ["Missing alt attribute", "Empty button", "Contrast ratio", "Missing form label",
            "Heading level skipped", "Duplicate id", "Missing lang", "Invalid ARIA value"]
    right = ["Is the alt text meaningful?", "Is the tab order logical?",
             "Is focus visible where it lands?", "Does the announcement make sense?",
             "Is the error recoverable?", "Is the shortcut discoverable?"]
    rows = max(len(left), len(right))
    h = 132 + 44 + rows * 34 + 76
    img, d = canvas(h)
    head(d, "What a scanner finds, and what it cannot",
         "W3C is explicit: \u201ctools can\u2019t do it all.\u201d Some checks cannot be "
         "automated at all.", ACC)
    mid = W // 2
    d.rounded_rectangle([40, 140, mid - 12, h - 60], 8, fill=SURFACE2, outline=BORDER, width=2)
    d.rounded_rectangle([mid + 12, 140, W - 40, h - 60], 8,
                        fill=mix(ACC, BG, .12), outline=ACC, width=3)
    d.text((64, 158), "A tool answers", font=f(SANS_B, 15), fill=MUTED)
    d.text((mid + 36, 158), "Only a person answers", font=f(SANS_B, 15), fill=ACC)
    for i, t in enumerate(left):
        d.text((64, 200 + i * 34), "\u00b7  " + t, font=f(SANS, 14), fill=DIM)
    for i, t in enumerate(right):
        d.text((mid + 36, 200 + i * 34), "\u00b7  " + t, font=f(SANS, 14), fill=MUTED)
    d.text((40, h - 46), "Zero errors on the left says nothing about the right.",
           font=f(SANS, 15), fill=DIM)
    save(img, "diagram-a11y-automated-vs-human.png")


# ----------------------------------------------------------- conversion set
def d24_modes():
    """The four modes, and the one boundary that matters."""
    ACC = (244, 114, 182)
    rows = [("AUDIT", "Reads. Changes nothing.", "Findings with evidence", True),
            ("PLAN", "Reads, and ranks what was found.", "An ordered list with reasons", False),
            ("IMPLEMENT", "Changes one agreed thing.", "A diff, and a way to check it", False),
            ("VALIDATE", "Measures what happened.", "A verdict, including 'cannot tell'", False)]
    h = 132 + len(rows) * 78 + 74
    img, d = canvas(h)
    head(d, "Four modes, and the boundary that matters",
         "An audit whose fixes land in the same run leaves a diff and no report.", ACC)
    y = 138
    for name, does, out, hot in rows:
        d.rounded_rectangle([40, y, W - 40, y + 62], 8, fill=SURFACE2,
                            outline=ACC if hot else BORDER, width=2 if hot else 1)
        d.text((60, y + 12), name, font=f(MONO_B, 17), fill=ACC if hot else TEXT)
        d.text((60, y + 38), does, font=f(SANS, 14), fill=MUTED)
        tw = d.textlength(out, font=f(MONO, 14))
        d.text((W - 60 - tw, y + 25), out, font=f(MONO, 14), fill=DIM)
        y += 78
    foot(d, h, "Say which mode the session is in before it starts.")
    save(img, "diagram-cro-modes.png")


def d25_labels():
    """The four honesty labels, by what you actually know."""
    ACC = (134, 239, 172)
    rows = [("Proven problem", "You reproduced it", "Fix it. No test needed."),
            ("Strong heuristic", "Well evidenced, observed here", "Usually not worth a test"),
            ("Experiment opportunity", "Plausible, genuinely unknown", "Test it, if you can power one"),
            ("Insufficient data", "You do not know", "Saying so IS the finding")]
    h = 132 + len(rows) * 74 + 74
    img, d = canvas(h)
    head(d, "Label every finding by what you actually know",
         "Without this everything arrives in the same confident register.", ACC)
    y = 138
    for name, means, act in rows:
        d.rounded_rectangle([40, y, W - 40, y + 58], 8, fill=SURFACE2, outline=BORDER, width=1)
        d.text((60, y + 10), name, font=f(MONO_B, 16), fill=ACC)
        d.text((60, y + 34), means, font=f(SANS, 14), fill=MUTED)
        tw = d.textlength(act, font=f(SANS, 14))
        d.text((W - 60 - tw, y + 22), act, font=f(SANS, 14), fill=DIM)
        y += 74
    foot(d, h, "Most reports cannot express the fourth, so everything reads as known.")
    save(img, "diagram-cro-labels.png")


def d26_shopify_events():
    """Where a Shopify store's conversion events come from."""
    ACC = (251, 191, 36)
    srcs = ["Shopify's own analytics", "Theme code", "A custom pixel",
            "Each installed app"]
    h = 132 + len(srcs) * 56 + 110
    img, d = canvas(h)
    head(d, "Why a Shopify conversion rate is exactly half",
         "Four independent things can fire a purchase event. Nothing warns you.", ACC)
    y = 138
    for sname in srcs:
        d.rounded_rectangle([40, y, 520, y + 44], 8, fill=SURFACE2, outline=BORDER, width=1)
        d.text((60, y + 13), sname, font=f(SANS, 15), fill=TEXT)
        d.line([(524, y + 22), (596, y + 22)], fill=ACC, width=2)
        y += 56
    box_y = 138 + (len(srcs) * 56) // 2 - 34
    d.rounded_rectangle([600, box_y, W - 40, box_y + 68], 8,
                        fill=mix(ACC, BG, .16), outline=ACC, width=2)
    d.text((622, box_y + 14), "purchase", font=f(MONO_B, 18), fill=ACC)
    d.text((622, box_y + 42), "counted once per source", font=f(SANS, 14), fill=MUTED)
    foot(d, h, "Complete one real transaction and count what actually fired.")
    save(img, "diagram-shopify-events.png")


def d27_landing_order():
    """The order to fix a landing page in."""
    ACC = (138, 166, 255)
    steps = [("1", "Anything broken", "Forms that drop submissions, controls that cannot be operated"),
             ("2", "Anything unmeasured", "If the event does not fire once, the rest is guesswork"),
             ("3", "Message match", "Usually the largest effect, and among the cheapest changes"),
             ("4", "The first screen and the action", "Measured at 375px, not eyeballed"),
             ("5", "Everything else", "Only if you can tell whether it worked")]
    h = 132 + len(steps) * 80 + 70
    img, d = canvas(h)
    head(d, "The order to fix a landing page in",
         "Most audits invert this and start at five, which is why they produce a redesign.", ACC)
    y = 138
    for i, (n, what, why) in enumerate(steps):
        d.rounded_rectangle([40, y, W - 40, y + 64], 8, fill=SURFACE2, outline=BORDER, width=1)
        d.ellipse([58, y + 18, 90, y + 50], fill=mix(ACC, BG, .20), outline=ACC, width=2)
        d.text((70, y + 24), n, font=f(MONO_B, 18), fill=ACC)
        d.text((110, y + 14), what, font=f(MONO_B, 16), fill=TEXT)
        d.text((110, y + 38), why, font=f(SANS, 14), fill=MUTED)
        if i < len(steps) - 1:
            cx = 74
            d.line([(cx, y + 64), (cx, y + 80)], fill=ACC, width=2)
        y += 80
    foot(d, h, "Steps one and two are certainties. The rest need measurement.")
    save(img, "diagram-landing-order.png")


def d28_prompt_stages():
    """CRO prompts, organised by stage rather than by page type."""
    ACC = (167, 139, 250)
    stages = ["Discovery", "Analytics", "Funnel", "Pages", "Forms", "Copy",
              "Experiments", "Validation"]
    h = 132 + 200
    img, d = canvas(h)
    head(d, "Prompts by stage, not by page type",
         "The order is what makes them useful. Each one states its mode.", ACC)
    x, y = 40, 150
    for i, st in enumerate(stages):
        wbox = 218
        if x + wbox > W - 40:
            x = 40
            y += 66
        d.rounded_rectangle([x, y, x + wbox, y + 50], 8, fill=SURFACE2,
                            outline=ACC if i < 2 else BORDER, width=2 if i < 2 else 1)
        d.text((x + 18, y + 16), "%d. %s" % (i + 1, st), font=f(MONO_B, 15),
               fill=ACC if i < 2 else TEXT)
        x += wbox + 14
    foot(d, h, "An unverified event makes every later number a guess.")
    save(img, "diagram-cro-stages.png")


if __name__ == "__main__":
    d1_workflow(); d2_anatomy(); d3_memory(); d4_pushorder(); d5_seo_order()
    d6_isolation(); d7_where(); d8_plugin_layout(); d9_certs()
    d10_enforcement(); d11_dial()
    d12_modes(); d13_firstweek(); d14_scopes(); d15_exit()
    d16_audit_order(); d17_check_can_fail(); d18_claudemd_by_project()
    d19_shopify_urls()
    d20_security_reach(); d21_position_tiers()
    d22_perf_loop(); d23_a11y_split()
    d4b_mutation()
    d24_modes(); d25_labels(); d26_shopify_events()
    d27_landing_order(); d28_prompt_stages()
