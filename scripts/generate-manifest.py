#!/usr/bin/env python3
"""Generate PRODUCT-MANIFEST.md for the bundle.

Usage: generate-manifest.py <bundleDir> <version> <buildDate>

Counts are derived from the actual files — never hand-maintained, so the
numbers on the sales page can be checked against the shipped product.
The SHA-256 and archive size are filled in by build-product.sh once the
archive exists.
"""
import hashlib
import os
import re
import sys
from collections import OrderedDict

bundle, version, build_date = sys.argv[1], sys.argv[2], sys.argv[3]

MODULE_TITLES = OrderedDict([
    ("01-Master-System", "Master System"),
    ("02-Claude-Code-Configuration", "Claude Code Configuration"),
    ("03-SEO-System", "SEO System"),
    ("04-Shopify", "Shopify"),
    ("05-WordPress", "WordPress"),
    ("06-Astro", "Astro"),
    ("07-SaaS", "SaaS"),
    ("08-Landing-Pages", "Landing Pages"),
    ("09-GitHub", "GitHub"),
    ("10-Cloudflare", "Cloudflare"),
    ("11-Security", "Security"),
    ("12-Accessibility", "Accessibility"),
    ("13-Search-Engines", "Search Engines"),
    ("14-Checklists", "Checklists"),
    ("15-Claude-Code-Prompt-Library", "Claude Code Prompt Library"),
    ("16-Templates", "Templates"),
    ("17-Bonus", "Bonus"),
])

LIB_RE = re.compile(r"^## (DIS|PLN|DEV|DBG|SEO|SEC|A11Y|PERF|CNT|DEP|MNT)-\d+", re.M)


def files_in(path):
    out = []
    for dirpath, dirnames, filenames in os.walk(path):
        dirnames.sort()
        for name in sorted(filenames):
            out.append(os.path.join(dirpath, name))
    return out


all_files = files_in(bundle)
# Exclude the manifest itself from its own counts where it already exists.
all_files = [f for f in all_files if os.path.basename(f) != "PRODUCT-MANIFEST.md"]

total_files = len(all_files)
total_bytes = sum(os.path.getsize(f) for f in all_files)
total_dirs = sum(1 for _, d, _ in os.walk(bundle) for _ in d)

md_files = [f for f in all_files if f.endswith(".md")]
total_words = 0
for f in md_files:
    with open(f, encoding="utf-8") as fh:
        total_words += len(fh.read().split())

# Content digest: a deterministic SHA-256 over every file in the bundle except
# this manifest. Self-consistent, so it can live *inside* the manifest — unlike
# the archive's own checksum, which no file can contain.
digest_input = []
for f in sorted(all_files):
    with open(f, "rb") as fh:
        digest_input.append(
            f"{os.path.relpath(f, bundle)}  {hashlib.sha256(fh.read()).hexdigest()}\n"
        )
content_digest = hashlib.sha256("".join(digest_input).encode()).hexdigest()

names = [os.path.basename(f) for f in all_files]
prompt_docs = sum(1 for n in names if "PROMPT" in n)
checklists = sum(1 for n in names if "CHECKLIST" in n)
templates = sum(1 for n in names if "TEMPLATE" in n)
guides = sum(1 for n in names if "GUIDE" in n or "WORKFLOW" in n or "SYSTEM" in n)
workflow_yml = sum(1 for n in names if n.endswith(".yml"))

library_prompts = 0
lib_dir = os.path.join(bundle, "15-Claude-Code-Prompt-Library")
lib_breakdown = []
if os.path.isdir(lib_dir):
    for name in sorted(os.listdir(lib_dir)):
        if not name.endswith(".md"):
            continue
        with open(os.path.join(lib_dir, name), encoding="utf-8") as fh:
            n = len(LIB_RE.findall(fh.read()))
        if n:
            lib_breakdown.append((name.replace("-PROMPTS.md", "").title(), n))
            library_prompts += n

rows = []
for mod, title in MODULE_TITLES.items():
    path = os.path.join(bundle, mod)
    if not os.path.isdir(path):
        continue
    mf = files_in(path)
    rows.append((mod, title, len(mf), sum(os.path.getsize(f) for f in mf)))

root_files = [f for f in all_files if os.path.dirname(f) == bundle]

lines = []
w = lines.append

w("# Product Manifest")
w("")
w("**The Claude Code Website Launch System**")
w("")
w("Generated automatically at build time from the actual contents of the")
w("bundle. Every number here is counted, not asserted — you can verify any of")
w("them against the files you received.")
w("")
w("---")
w("")
w("## Package")
w("")
w("| | |")
w("| --- | --- |")
w(f"| **Product** | The Claude Code Website Launch System |")
w(f"| **Version** | {version} |")
w(f"| **Build date** | {build_date} |")
w(f"| **Publisher** | Site Builder Stack — sitebuilderstack.com |")
w(f"| **Archive** | `{{{{ARCHIVE_NAME}}}}` |")
w(f"| **Content digest** | `{content_digest}` |")
w("")
w("### Verifying what you received")
w("")
w("Two different checksums are involved, and they answer different questions.")
w("")
w("**1. The archive checksum** verifies that the ZIP you downloaded arrived")
w("intact. It is published alongside the download, in the accompanying")
w("`.sha256` file and in the release notes — it cannot be printed inside this")
w("file, because a file cannot contain its own hash.")
w("")
w("```bash")
w("# macOS / Linux")
w("shasum -a 256 {{ARCHIVE_NAME}}")
w("")
w("# Windows PowerShell")
w("(Get-FileHash {{ARCHIVE_NAME}} -Algorithm SHA256).Hash.ToLower()")
w("```")
w("")
w("**2. The content digest above** verifies the extracted files. It is a")
w("SHA-256 over the name and hash of every file in this bundle except this")
w("manifest, so you can confirm the contents even after extraction. Run this")
w("from inside the `Claude-Code-Website-Launch-System` directory:")
w("")
w("```bash")
w("find . -type f ! -name PRODUCT-MANIFEST.md | LC_ALL=C sort | while read -r f; do")
w("  printf '%s  %s\\n' \"${f#./}\" \"$(sha256sum \"$f\" | cut -d\" \" -f1)\"")
w("done | sha256sum")
w("```")
w("")
w("If either check does not match, download the file again.")
w("")
w("---")
w("")
w("## Contents")
w("")
w("| | |")
w("| --- | --- |")
w(f"| **Total files** | {total_files} |")
w(f"| **Directories** | {total_dirs} |")
w(f"| **Total size, uncompressed** | {total_bytes:,} bytes |")
w(f"| **Words of documentation** | approximately {total_words:,} |")
w("")
w("### By document type")
w("")
w("| Type | Count |")
w("| --- | --- |")
w(f"| Structured prompt documents | {prompt_docs} |")
w(f"| Reusable prompts in the library | {library_prompts} |")
w(f"| Checklists | {checklists} |")
w(f"| Fill-in templates | {templates} |")
w(f"| Guides, workflows, and systems | {guides} |")
w(f"| Working GitHub Actions workflow files | {workflow_yml} |")
w("")
w("Some files count in more than one row — a launch checklist is both a")
w("checklist and part of a platform module. The totals are file counts, not")
w("sums of these rows.")
w("")
w("---")
w("")
w("## Modules")
w("")
w("| # | Module | Files | Size |")
w("| --- | --- | --- | --- |")
for mod, title, n, b in rows:
    num = mod.split("-")[0]
    w(f"| {num} | {title} | {n} | {b:,} bytes |")
w(f"| — | Root documents | {len(root_files)} | {sum(os.path.getsize(f) for f in root_files):,} bytes |")
w("")
w("---")
w("")
w("## Prompt library breakdown")
w("")
w("| Category | Prompts |")
w("| --- | --- |")
for name, n in lib_breakdown:
    w(f"| {name} | {n} |")
w(f"| **Total** | **{library_prompts}** |")
w("")
w("---")
w("")
w("## Supported platforms and topics")
w("")
w("Platform-specific build systems are included for:")
w("")
w("- Shopify — themes, Liquid, Online Store 2.0, metafields, launch")
w("- WordPress — themes, block themes, plugins, security, launch")
w("- Astro — architecture, content collections, SEO, deployment")
w("- SaaS applications — architecture, auth, database, production readiness")
w("- Landing pages — conversion structure, SaaS, digital product, lead generation")
w("")
w("Platform-agnostic systems cover: search architecture and content clusters,")
w("GitHub deployment and CI/CD, Cloudflare DNS and hosting, application")
w("security, WCAG 2.2 accessibility, search engine submission, and the full")
w("launch checklist sequence.")
w("")
w("This is not a claim of universal compatibility. The master prompt and the")
w("audit, security, accessibility, and checklist material apply to any stack;")
w("the platform modules apply to the platforms named above.")
w("")
w("---")
w("")
w("## Integrity statement")
w("")
w("This package was validated before release. The validation suite checks for:")
w("")
w("- Empty or truncated files")
w("- Placeholder and lorem ipsum text")
w("- Credentials of any known shape")
w("- Machine-local absolute paths")
w("- Broken internal links and cross-references")
w("- Unintended TODO and FIXME markers")
w("- Byte-identical duplicate files")
w("- Near-duplicate content between documents")
w("- Unbalanced code fences and malformed tables")
w("- Inconsistent naming")
w("")
w("**No API credentials, access tokens, private keys, or customer data are")
w("included in this package.**")
w("")
w("---")
w("")
w(f"*Manifest generated {build_date} for version {version}.*")

with open(os.path.join(bundle, "PRODUCT-MANIFEST.md"), "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines) + "\n")

print(f"  manifest: {total_files} files, {total_bytes:,} bytes, {library_prompts} library prompts")
