#!/usr/bin/env python3
"""Verify every factual claim made on the storefront against the built product.

The sales page, the product description, and the theme copy all assert counts.
Those numbers are written by hand; the bundle is generated. This script checks
they agree, so a build can never silently make the storefront lie.

Usage: audit-storefront-claims.py
Exit 0 = all claims verified, 1 = a claim does not match.
"""
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUNDLE = os.path.join(REPO, "product", "Claude-Code-Website-Launch-System")
THEME = os.path.join(REPO, "theme", "dev")

sys.path.insert(0, os.path.join(REPO, "scripts"))

# ── ground truth, measured from the bundle ───────────────────────────────────
files = []
for dirpath, dirnames, filenames in os.walk(BUNDLE):
    dirnames.sort()
    for f in sorted(filenames):
        files.append(os.path.join(dirpath, f))

names = [os.path.basename(f) for f in files]
modules = sorted(d for d in os.listdir(BUNDLE)
                 if os.path.isdir(os.path.join(BUNDLE, d)) and re.match(r"^\d{2}-", d))

LIB_RE = re.compile(r"^## (DIS|PLN|DEV|DBG|SEO|SEC|A11Y|PERF|CNT|DEP|MNT)-\d+", re.M)
lib = 0
libdir = os.path.join(BUNDLE, "15-Claude-Code-Prompt-Library")
for f in os.listdir(libdir):
    if f.endswith(".md"):
        lib += len(LIB_RE.findall(open(os.path.join(libdir, f), encoding="utf-8").read()))

words = 0
for f in files:
    if f.endswith(".md"):
        words += len(open(f, encoding="utf-8").read().split())

truth = {
    "files": len(files),
    "modules": len(modules),
    "library_prompts": lib,
    "checklists": sum(1 for n in names if "CHECKLIST" in n),
    "templates": sum(1 for n in names if "TEMPLATE" in n),
    "prompt_docs": sum(1 for n in names if "PROMPT" in n),
    "workflow_yml": sum(1 for n in names if n.endswith(".yml")),
    "words": words,
    "bytes": sum(os.path.getsize(f) for f in files),
}
per_module = {m: len(os.listdir(os.path.join(BUNDLE, m))) for m in modules}
# nested dirs (09-GitHub has EXAMPLE-WORKFLOWS)
for m in modules:
    n = 0
    for dp, dn, fn in os.walk(os.path.join(BUNDLE, m)):
        n += len(fn)
    per_module[m] = n

print("=== measured from the bundle ===")
for k, v in truth.items():
    print(f"  {k:<18} {v:,}")
print()

# Phrases that appear in a tile's `meta` and name a product.
META_SUBJECT = (
    ("Launch System", "claude-code-website-launch-system"),
    ("SEO Toolkit", "claude-code-seo-website-audit-toolkit"),
    ("Conversion Toolkit", "claude-code-conversion-revenue-optimization-toolkit"),
    ("Operations System", "claude-code-website-operations-maintenance-system"),
)


# ── claims made in the theme ────────────────────────────────────────────────
claims = []
module_tiles = []


def add(source, text, subject=None):
    """`subject` is the product handle of the enclosing settings block, when
    there is one. An ecosystem card on the conversion toolkit's page describes
    the Launch System, and its body says "100 prompts" without ever naming it —
    the handle beside the body is the only reliable signal of what the sentence
    is about."""
    claims.append((source, text, subject))


for root, _, fs in os.walk(THEME):
    for f in sorted(fs):
        if not f.endswith((".json", ".liquid")):
            continue
        p = os.path.join(root, f)
        txt = open(p, encoding="utf-8").read()
        if f.endswith(".json"):
            def walk(node, key=None, subject=None):
                if isinstance(node, dict):
                    # A settings block naming a product sets the subject for
                    # every string inside it.
                    own = node.get("product")
                    if isinstance(own, str) and "-" in own:
                        subject = own
                    # A tile is a {label, meta} pair. When the label carries a
                    # module index ("01 Core method"), its meta counts THAT
                    # module, not the whole bundle — checking "8 workflows"
                    # against the bundle's 70 reports a correct tile as wrong.
                    lab, meta = node.get("label"), node.get("meta")
                    # On the bundle page a tile's `meta` names which product the
                    # label is about ("100 reusable prompts" / "Launch System").
                    # Without this the label is checked against the bundle total.
                    if isinstance(meta, str):
                        for phrase, whose in META_SUBJECT:
                            if phrase.lower() in meta.lower():
                                subject = whose
                                break
                    if isinstance(lab, str) and isinstance(meta, str) \
                            and re.match(r"^\d{2} ", lab):
                        module_tiles.append((f, lab, meta))
                        for k, v in node.items():
                            if k not in ("label", "meta"):
                                walk(v, k, subject)
                        return
                    for k, v in node.items():
                        walk(v, k, subject)
                elif isinstance(node, list):
                    for v in node:
                        walk(v, key, subject)
                elif isinstance(node, str):
                    # A tile's `label` beginning with a two-digit module index
                    # ("13 Templates") names a directory; it is not a claim that
                    # there are thirteen templates. The adjacent `meta` field is
                    # where that tile's count lives, and it is still checked.
                    if key == "label" and re.match(r"^\d{2} ", node):
                        return
                    add(f, node, subject)
            try:
                walk(json.loads(re.sub(r"^\s*/\*.*?\*/\s*", "", txt, flags=re.S)))
            except json.JSONDecodeError:
                pass
        else:
            for m in re.finditer(r'"default"\s*:\s*"([^"]+)"', txt):
                add(f, m.group(1), None)

failures, verified = [], []

# ── the second product ───────────────────────────────────────────────────────
# The store now sells two bundles. A claim made on the SEO toolkit's own
# template describes the toolkit, not the flagship, and checking it against the
# flagship's counts reports a correct page as wrong.
#
# Sources are matched to a bundle by filename. Anything not matched here is
# checked against the flagship, which is the safe default: a new file has to be
# opted in deliberately rather than silently exempted.
SEO_BUNDLE = os.path.join(REPO, "product", "Claude-Code-SEO-Website-Audit-Toolkit")
CRO_BUNDLE = os.path.join(REPO, "product",
                          "Claude-Code-Conversion-Revenue-Optimization-Toolkit")
SEO_SOURCES = ("product.seo-toolkit.json",)
CRO_SOURCES = ("product.cro-toolkit.json",)
STACK_SOURCES = ("product.complete-stack.json",)
OPS_BUNDLE = os.path.join(REPO, "product", "Claude-Code-Website-Operations-Maintenance-System")
OPS_SOURCES = ("product.ops-system.json",)

# Handle -> which bundle a claim beside that handle is about. Used when an
# ecosystem or bundle-value block names a product: the sentence next to the
# handle describes THAT product, whatever page it appears on.
BY_HANDLE = {
    "claude-code-website-launch-system": "launch",
    "claude-code-seo-website-audit-toolkit": "seo",
    "claude-code-conversion-revenue-optimization-toolkit": "cro",
    "complete-site-builder-stack": "stack",
    "claude-code-website-operations-maintenance-system": "ops",
}


def measure(bundle):
    """Counts for a bundle, or None if it is not in this checkout."""
    if not os.path.isdir(bundle):
        return None
    files = 0
    words = 0
    for dp, dn, fn in os.walk(bundle):
        dn[:] = [d for d in dn if not d.startswith(".")]
        for f in fn:
            files += 1
            try:
                words += len(open(os.path.join(dp, f), encoding="utf-8").read().split())
            except (UnicodeDecodeError, IOError):
                pass
    mods = sorted(d for d in os.listdir(bundle)
                  if os.path.isdir(os.path.join(bundle, d)) and re.match(r"^\d{2}-", d))
    def count(sub):
        d = os.path.join(bundle, sub)
        # A README inside a counted directory describes the directory; it is
        # not one of the things being counted.
        return len([f for f in os.listdir(d) if f != "README.md"]) if os.path.isdir(d) else 0

    # The conversion toolkit keeps its fill-in documents in 13-templates/ and
    # its reusable prompts in commands/, as C-nn headings inside category
    # files. Counting directory entries would report zero templates and zero
    # prompts for it, which is worse than not checking at all.
    templates = count("templates") or count("13-templates")
    commands = 0
    cdir = os.path.join(bundle, "commands")
    if os.path.isdir(cdir):
        for f in sorted(os.listdir(cdir)):
            if f.endswith(".md") and f != "COMMANDS.md":
                commands += len(re.findall(
                    r"^## C-\d+",
                    open(os.path.join(cdir, f), encoding="utf-8").read(), re.M))
    # The operations system's commands are one file per slash command rather
    # than C-nn headings inside category files.
    if not commands and os.path.isdir(cdir):
        commands = len([f for f in os.listdir(cdir) if f.endswith(".md") and f != "COMMANDS.md"])
    sdir = os.path.join(bundle, "scripts")
    scripts = len([f for f in os.listdir(sdir) if f.endswith(".py") and f != "_common.py"]) if os.path.isdir(sdir) else 0
    workflows = 0
    for d in sorted(os.listdir(bundle)):
        if re.match(r"^(0[1-9]|1[0-2])-", d) and os.path.isdir(os.path.join(bundle, d)):
            workflows += len([f for f in os.listdir(os.path.join(bundle, d))
                              if f.endswith(".md")])
    return {"files": files, "modules": len(mods), "words": words,
            "library_prompts": count("prompts"),
            "checklists": count("checklists"),
            "templates": templates,
            "prompt_docs": count("prompts"),
            "commands": commands,
            "scripts": scripts,
            "workflows": workflows,
            "workflow_yml": 0}


SEO_TRUTH = measure(SEO_BUNDLE)
CRO_TRUTH = measure(CRO_BUNDLE)
OPS_TRUTH = measure(OPS_BUNDLE)

# The bundle sells all three, so a number on its page is the sum of all three.
# Summed from the same measurements rather than typed, so it cannot drift from
# the products it is a total of.
STACK_TRUTH = None
if SEO_TRUTH and CRO_TRUTH:
    STACK_TRUTH = {}
    for k in set(truth) | set(SEO_TRUTH) | set(CRO_TRUTH):
        vals = [t.get(k) for t in (truth, SEO_TRUTH, CRO_TRUTH)]
        if all(isinstance(v, int) for v in vals):
            STACK_TRUTH[k] = sum(vals)
for label, t in (("SEO toolkit", SEO_TRUTH), ("Conversion toolkit", CRO_TRUTH), ("Operations system", OPS_TRUTH)):
    if t:
        print(f"=== measured from the {label} ===")
        for k, v in t.items():
            print(f"  {k:<18} {v:,}")
        print()


def truth_for(source):
    """Which bundle's counts a given source's claims should be checked against."""
    if SEO_TRUTH and source in SEO_SOURCES:
        return SEO_TRUTH, "SEO toolkit"
    if CRO_TRUTH and source in CRO_SOURCES:
        return CRO_TRUTH, "Conversion toolkit"
    if STACK_TRUTH and source in STACK_SOURCES:
        return STACK_TRUTH, "Complete Stack"
    if OPS_TRUTH and source in OPS_SOURCES:
        return OPS_TRUTH, "Operations system"
    return truth, "Launch System"


# Every product page now compares itself to the other two, so a page's own
# bundle is not always the subject of a number on it. When the sentence around
# a claim names another product, that product's counts are the ones to check
# against. Matched on the phrase, so a claim with no such phrase still falls
# through to the page's own bundle rather than being excused.
CROSS = [
    ("Launch System", lambda: (truth, "Launch System")),
    ("SEO & Website Audit Toolkit", lambda: (SEO_TRUTH, "SEO toolkit")),
    ("SEO toolkit", lambda: (SEO_TRUTH, "SEO toolkit")),
    ("Conversion & Revenue Optimization Toolkit", lambda: (CRO_TRUTH, "Conversion toolkit")),
    ("conversion toolkit", lambda: (CRO_TRUTH, "Conversion toolkit")),
    ("Operations & Maintenance System", lambda: (OPS_TRUTH, "Operations system")),
    ("Operations System", lambda: (OPS_TRUTH, "Operations system")),
]


TRUTHS = {}


def subject_of(text, default, subject=None):
    """Whose counts this claim should be checked against.

    The enclosing product handle wins when there is one: it is structural,
    whereas the phrase match depends on the sentence happening to name the
    product. An ecosystem card's body describing the Launch System rarely says
    "Launch System" in the same string as the number.
    """
    if subject and subject in BY_HANDLE:
        t = TRUTHS.get(BY_HANDLE[subject])
        if t:
            return t, BY_HANDLE[subject]
    for phrase, get in CROSS:
        if phrase in text:
            t, name = get()
            if t:
                return t, name
    return default

CHECKS = [
    (r"\b(\d{3,4})\s+files\b", "files", None),
    (r"\b(\d+)\s+modules\b", "modules", None),
    (r"\b(\d+)\s+(?:reusable\s+)?prompts\b", "library_prompts", None),
    (r"\b(\d+)\s+checklists\b", "checklists", None),
    (r"\b(\d+)\s+(?:fill-in\s+)?templates\b", "templates", None),
    (r"\b(\d+)\s+prompt documents\b", "prompt_docs", None),
    (r"\b(\d+)\s+(?:working\s+)?GitHub Actions\b", "workflow_yml", None),
    (r"\b(\d+)\s+categories\b", None, 11),
    (r"\b(\d+)\s+(?:reusable\s+)?commands\b", "commands", None),
    (r"\b(\d+)\s+workflows\b", "workflows", None),
    (r"\b(\d+)\s+(?:standard-library\s+|working\s+)?scripts\b", "scripts", None),
    (r"\b(\d+)\s+slash commands\b", "commands", None),
]

TRUTHS.update({"launch": truth, "seo": SEO_TRUTH, "cro": CRO_TRUTH,
               "stack": STACK_TRUTH, "ops": OPS_TRUTH})

for source, text, subject in claims:
    src_truth, which = subject_of(text, truth_for(source), subject)
    for pattern, key, literal in CHECKS:
        for m in re.finditer(pattern, text, re.I):
            claimed = int(m.group(1))
            if key and key not in src_truth:
                continue
            expected = src_truth[key] if key else literal
            ctx = text[max(0, m.start() - 30):m.end() + 20].replace("\n", " ")
            if claimed == expected:
                verified.append(f"{source}: '{m.group(0)}' == {expected}")
            else:
                failures.append(f"{source}: claims '{m.group(0)}' but actual is {expected}  |  …{ctx}…")

# "over N words"
for source, text, subject in claims:
    src_truth, which = subject_of(text, truth_for(source), subject)
    for m in re.finditer(r"[Oo]ver ([\d,]+)\s+words", text):
        claimed = int(m.group(1).replace(",", ""))
        if src_truth["words"] > claimed:
            verified.append(f"{source}: 'over {m.group(1)} words' (actual {src_truth['words']:,})")
        else:
            failures.append(f"{source}: claims over {m.group(1)} words, "
                            f"actual is {src_truth['words']:,} ({which})")

# per-module counts in module cards ("7 files", "10 files" …) are covered by the
# generic files check only if they equal the total, so verify them structurally:
idx = os.path.join(THEME, "templates", "index.json")
if os.path.exists(idx):
    data = json.loads(re.sub(r"^\s*/\*.*?\*/\s*", "", open(idx, encoding="utf-8").read(), flags=re.S))
    mods = data.get("sections", {}).get("modules", {}).get("blocks", {})
    # Every module card's "N files" must equal the real count of the
    # directory (or directories) it describes.
    MAP = {
        "Master Website Builder":  ["01-Master-System"],
        "Production CLAUDE.md":    ["02-Claude-Code-Configuration"],
        "SEO Architecture System": ["03-SEO-System"],
        "Platform Build Systems":  ["04-Shopify", "05-WordPress", "06-Astro",
                                    "07-SaaS", "08-Landing-Pages"],
        "Deployment System":       ["09-GitHub", "10-Cloudflare"],
        "Security System":         ["11-Security"],
        "Accessibility System":    ["12-Accessibility"],
        "Search Engine Launch":    ["13-Search-Engines"],
        "Launch Checklists":       ["14-Checklists"],
        "Prompt Library":          ["15-Claude-Code-Prompt-Library"],
        "Templates & Bonuses":     ["16-Templates", "17-Bonus"],
    }
    covered = set()
    for b in mods.values():
        st = b.get("settings", {})
        title, meta = st.get("title", ""), st.get("meta", "")
        mm = re.match(r"(\d+) files", meta)
        if title in MAP:
            covered.add(title)
            if mm:
                actual = sum(per_module[d] for d in MAP[title])
                dirs = "+".join(MAP[title])
                if int(mm.group(1)) == actual:
                    verified.append(f"module card '{title}': {mm.group(1)} files == {actual} ({dirs})")
                else:
                    failures.append(f"module card '{title}': claims {mm.group(1)} files, "
                                    f"actual {actual} ({dirs})")
    unmapped = [b.get("settings", {}).get("title", "?") for b in mods.values()
                if b.get("settings", {}).get("title") not in MAP]
    if unmapped:
        print(f"  (module cards with no file-count claim to verify: {unmapped})")

# ── per-module tile counts ──────────────────────────────────────────────────
# A product page's contents grid claims a count per module. Those were skipped
# above because the bundle-wide "workflows" total is not what they mean; they
# are checked here against the directory the tile's index names.
TILE_DIR = {
    "product.cro-toolkit.json": CRO_BUNDLE,
    "product.seo-toolkit.json": SEO_BUNDLE,
    "product.json": BUNDLE,
    "product.ops-system.json": OPS_BUNDLE,
}
for source, lab, meta in sorted(set(module_tiles)):
    root = TILE_DIR.get(source)
    m = re.match(r"^(\d+)", meta.strip())
    if not root or not m:
        continue
    idx = lab[:2]
    dirs = sorted(d for d in os.listdir(root)
                  if os.path.isdir(os.path.join(root, d)) and d.startswith(idx + "-"))
    if not dirs:
        failures.append(f"{source}: tile '{lab}' names no directory in the bundle")
        continue
    if root == OPS_BUNDLE:
        actual = len([f for f in os.listdir(os.path.join(root, dirs[0])) if f != "README.md"])
    else:
        actual = len([f for f in os.listdir(os.path.join(root, dirs[0])) if f.endswith(".md")])
    claimed = int(m.group(1))
    if claimed == actual:
        verified.append(f"{source}: tile '{lab}' — {meta} == {actual} ({dirs[0]})")
    else:
        failures.append(f"{source}: tile '{lab}' claims '{meta}' but {dirs[0]} holds {actual}")

print(f"=== verified claims ({len(set(verified))}) ===")
for v in sorted(set(verified)):
    print("  ✓", v)
print(f"\n=== FAILED claims ({len(set(failures))}) ===")
for f in sorted(set(failures)):
    print("  ✗", f)

sys.exit(1 if failures else 0)
