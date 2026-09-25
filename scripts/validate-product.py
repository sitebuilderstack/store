#!/usr/bin/env python3
"""
Validate the Claude Code Website Launch System bundle before packaging.

Checks, per the release process in docs/RELEASE-PROCESS.md:
  * no empty or near-empty files
  * no placeholder / lorem ipsum text
  * no leaked credentials of any known shape
  * no machine-local absolute paths that should not ship
  * no broken internal markdown links
  * no unintended TODO / FIXME markers
  * no duplicate files (byte-identical) masquerading as distinct content
  * no near-duplicate prompts
  * balanced markdown fences and well-formed tables
  * consistent naming
  * required files present

Exit code 0 = clean, 1 = errors found. Warnings never fail the build.
"""
import hashlib
import os
import re
import sys
from collections import defaultdict

ROOT = sys.argv[1] if len(sys.argv) > 1 else "product/Claude-Code-Website-Launch-System"

errors: list = []
warnings: list = []


def err(path, msg):
    errors.append(f"{path}: {msg}")


def warn(path, msg):
    warnings.append(f"{path}: {msg}")


# ── credential shapes ────────────────────────────────────────────────────────
# Deliberately broad. These must not appear as *real values* anywhere.
SECRET_PATTERNS = [
    (r"AKIA[0-9A-Z]{16}", "AWS access key id"),
    (r"ASIA[0-9A-Z]{16}", "AWS temporary key"),
    (r"ghp_[A-Za-z0-9]{36}", "GitHub personal token"),
    (r"gho_[A-Za-z0-9]{36}", "GitHub OAuth token"),
    (r"github_pat_[A-Za-z0-9_]{22,}", "GitHub fine-grained PAT"),
    (r"shp(at|ss|ca|pa|ut)_[0-9a-fA-F]{32}", "Shopify token"),
    (r"xox[baprs]-[0-9A-Za-z]{8,}-[0-9A-Za-z-]{8,}", "Slack token"),
    (r"-----BEGIN [A-Z ]*PRIVATE KEY-----", "private key"),
    (r"AIza[0-9A-Za-z_-]{35}", "Google API key"),
    (r"\bsk-[A-Za-z0-9]{32,}\b", "provider secret key"),
    (r"[a-z][a-z0-9+.-]*://[^/\s:@\"']+:[^/\s:@\"']+@", "credentials in a URL"),
]

# Local paths that must never ship inside the customer bundle.
LOCAL_PATH_PATTERNS = [
    (r"/opt/sitebuilderstack", "build machine path"),
    (r"/opt/shopify-(client-id|secret)", "credential file path"),
    (r"/Users/[a-z]", "macOS home path"),
    (r"/home/(?!user\b)[a-z]+/", "Linux home path"),
    (r"C:\\\\Users\\\\(?!YourName)", "Windows home path"),
    (r"/tmp/claude-", "scratchpad path"),
]

PLACEHOLDER_PATTERNS = [
    (r"\blorem ipsum\b", "lorem ipsum"),
    (r"\bdolor sit amet\b", "lorem ipsum"),
    (r"\bXXXX+\b", "XXXX placeholder"),
    (r"\bFILL ?ME\b", "FILLME marker"),
    (r"\bINSERT[_ ]HERE\b", "INSERT HERE marker"),
    (r"\bplaceholder text\b", "literal 'placeholder text'"),
    (r"\bTBD\b", "TBD marker"),
    (r"\bcoming soon\b", "'coming soon'"),
]

# TODO markers are allowed only where the surrounding text is clearly *about*
# TODO markers (e.g. advice to remove them).
TODO_RE = re.compile(r"\b(TODO|FIXME|HACK|XXX)\b")
TODO_CONTEXT = re.compile(
    r"TODO and FIXME|TODO or FIXME|`TODO`|TODO/FIXME|no `?TODO|TODO markers|"
    r"TODO` requires|TODO and FIXME markers|commented-out code",
    re.I,
)

REQUIRED_ROOT = ["START-HERE.md", "README.md", "LICENSE.md", "VERSION.md"]

MIN_BYTES = 400  # anything smaller than this is suspicious for this bundle


def walk():
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames.sort()
        for name in sorted(filenames):
            yield os.path.join(dirpath, name)


def rel(path):
    return os.path.relpath(path, ROOT)


# ── 1. presence and structure ────────────────────────────────────────────────
if not os.path.isdir(ROOT):
    print(f"FATAL: bundle root not found: {ROOT}")
    sys.exit(1)

for required in REQUIRED_ROOT:
    if not os.path.isfile(os.path.join(ROOT, required)):
        err(required, "required root file missing")

files = list(walk())
if not files:
    print("FATAL: bundle is empty")
    sys.exit(1)

# ── 2. per-file checks ───────────────────────────────────────────────────────
hashes = defaultdict(list)
md_files = []

for path in files:
    r = rel(path)
    size = os.path.getsize(path)

    if size == 0:
        err(r, "file is empty")
        continue
    if size < MIN_BYTES and not r.endswith((".yml", ".txt")):
        warn(r, f"unusually small ({size} bytes) — check it is complete")

    try:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
    except UnicodeDecodeError as exc:
        err(r, f"not valid UTF-8: {exc}")
        continue

    hashes[hashlib.sha256(text.encode()).hexdigest()].append(r)

    # naming
    base = os.path.basename(path)
    if " " in base:
        err(r, "filename contains a space")
    if base != base.strip():
        err(r, "filename has leading/trailing whitespace")

    lowered = text.lower()

    for pattern, label in SECRET_PATTERNS:
        for m in re.finditer(pattern, text):
            line = text[: m.start()].count("\n") + 1
            snippet = m.group(0)[:6] + "…"
            err(r, f"line {line}: possible {label} ({snippet})")

    for pattern, label in LOCAL_PATH_PATTERNS:
        for m in re.finditer(pattern, text):
            line = text[: m.start()].count("\n") + 1
            err(r, f"line {line}: {label} leaked: {m.group(0)!r}")

    for pattern, label in PLACEHOLDER_PATTERNS:
        for m in re.finditer(pattern, text, re.I):
            line = text[: m.start()].count("\n") + 1
            # These words legitimately appear when the text is warning against them.
            context = text[max(0, m.start() - 160) : m.end() + 160].lower()
            if any(
                cue in context
                for cue in (
                    "no lorem", "lorem ipsum anywhere", "placeholder text\n",
                    "no placeholder", "remove", "avoid", "never", "check for",
                    "look for", "flag", "must not", "do not", "without",
                )
            ):
                continue
            warn(r, f"line {line}: {label}")

    for m in TODO_RE.finditer(text):
        line = text[: m.start()].count("\n") + 1
        context = text[max(0, m.start() - 200) : m.end() + 200]
        if TODO_CONTEXT.search(context):
            continue
        err(r, f"line {line}: unintended {m.group(0)} marker")

    if path.endswith(".md"):
        md_files.append((path, r, text))

        # fenced code blocks must balance
        fences = re.findall(r"^```", text, re.M)
        if len(fences) % 2 != 0:
            err(r, f"unbalanced code fences ({len(fences)} found)")

        # must start with an h1
        first = next((ln for ln in text.splitlines() if ln.strip()), "")
        if not (first.startswith("# ") or first.startswith("<!--")):
            warn(r, f"does not begin with an H1 (starts: {first[:50]!r})")

        # tables should have consistent column counts
        for block in re.findall(r"(?:^\|.*\|\s*$\n?)+", text, re.M):
            rows = [ln for ln in block.strip().split("\n") if ln.strip().startswith("|")]
            if len(rows) < 2:
                continue
            widths = {len(re.findall(r"(?<!\\)\|", row)) for row in rows}
            if len(widths) > 1:
                line = text[: text.index(block)].count("\n") + 1
                warn(r, f"line {line}: table has inconsistent column counts {sorted(widths)}")

# ── 3. duplicate files ───────────────────────────────────────────────────────
for digest, paths in hashes.items():
    if len(paths) > 1:
        err(paths[0], f"byte-identical duplicate of: {', '.join(paths[1:])}")

# ── 4. internal link resolution ──────────────────────────────────────────────
# Links inside fenced blocks or inline code spans are illustrations of syntax,
# not real links. Blank them out (preserving offsets so line numbers stay
# correct) before scanning.
FENCE_RE = re.compile(r"^```.*?^```", re.M | re.S)
SPAN_RE = re.compile(r"`[^`\n]*`")


def strip_code(text):
    def blank(m):
        return re.sub(r"[^\n]", " ", m.group(0))

    return SPAN_RE.sub(blank, FENCE_RE.sub(blank, text))


LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
for path, r, text in md_files:
    base_dir = os.path.dirname(path)
    prose = strip_code(text)
    for m in LINK_RE.finditer(prose):
        target = m.group(1)
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        target = target.split("#", 1)[0]
        if not target:
            continue
        resolved = os.path.normpath(os.path.join(base_dir, target))
        if not os.path.exists(resolved):
            line = prose[: m.start()].count("\n") + 1
            err(r, f"line {line}: broken internal link -> {target}")

# ── 5. cross-references to bundle paths mentioned in prose ───────────────────
# e.g. `11-Security/SECRET-SCANNING-PROMPT.md` inside backticks
XREF_RE = re.compile(r"`(\d{2}-[A-Za-z-]+/[A-Za-z0-9./-]+\.md)`")
for path, r, text in md_files:
    for m in XREF_RE.finditer(text):
        target = m.group(1)
        if not os.path.exists(os.path.join(ROOT, target)):
            line = text[: m.start()].count("\n") + 1
            err(r, f"line {line}: cross-reference to a file that does not exist -> {target}")

# ── 6. near-duplicate prompt detection ───────────────────────────────────────
def shingles(text, k=8):
    words = re.findall(r"[a-z']+", text.lower())
    return {" ".join(words[i : i + k]) for i in range(max(0, len(words) - k + 1))}


prompt_files = [(r, t) for _, r, t in md_files if len(t) > 2000]
sets = {r: shingles(t) for r, t in prompt_files}
names = sorted(sets)
for i, a in enumerate(names):
    for b in names[i + 1 :]:
        sa, sb = sets[a], sets[b]
        if not sa or not sb:
            continue
        jac = len(sa & sb) / len(sa | sb)
        if jac > 0.45:
            err(a, f"near-duplicate content with {b} (similarity {jac:.0%})")
        elif jac > 0.30:
            warn(a, f"notable overlap with {b} (similarity {jac:.0%})")

# ── report ───────────────────────────────────────────────────────────────────
print(f"Validated {len(files)} files under {ROOT}\n")

if warnings:
    print(f"WARNINGS ({len(warnings)}):")
    for w in warnings:
        print(f"  ! {w}")
    print()

if errors:
    print(f"ERRORS ({len(errors)}):")
    for e in errors:
        print(f"  ✗ {e}")
    print(f"\nFAILED — {len(errors)} error(s)")
    sys.exit(1)

print("PASSED — no errors")
sys.exit(0)
