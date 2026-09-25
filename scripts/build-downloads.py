#!/usr/bin/env python3
"""Build the free download archives for the engagement cycle into dist/free/.

- downloads/<kit>/ → dist/free/<kit>.zip (node_modules, test results and
  reports excluded; the archive is what a reader unzips and runs).
- content/labs/<id>.json → dist/free/lab-<id>-fixture.zip: every evidence
  item written as a file, plus a README that declares the whole bundle as
  sample data written for the lab.

Deterministic: fixed timestamps, sorted entries, so rebuilding without a
change produces byte-identical archives. Upload with
scripts/upload-files.py --allow-archive (these are free; the paid products
are refused by that script by name).
"""
import glob
import io
import json
import os
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "dist", "free")
KITS = ["claude-code-maintenance-kit", "website-migration-seo-kit", "playwright-website-tests",
        "shopify-seo-review-worksheet", "digital-product-page-template",
        "website-scope-of-work-kit", "answer-engine-readiness-kit"]
EXCLUDE_DIRS = {"node_modules", "test-results", "playwright-report", ".git"}
EXCLUDE_FILES = {".last-run.json", ".DS_Store"}
STAMP = (2026, 9, 17, 0, 0, 0)


def add(z, arcname, data):
    info = zipfile.ZipInfo(arcname, date_time=STAMP)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    z.writestr(info, data)


def build_kit(name):
    src = os.path.join(ROOT, "downloads", name)
    files = []
    for dp, dn, fn in os.walk(src):
        dn[:] = sorted(d for d in dn if d not in EXCLUDE_DIRS)
        for f in sorted(fn):
            if f in EXCLUDE_FILES:
                continue
            files.append(os.path.join(dp, f))
    path = os.path.join(OUT, name + ".zip")
    with zipfile.ZipFile(path, "w") as z:
        for f in files:
            add(z, name + "/" + os.path.relpath(f, src).replace(os.sep, "/"), open(f, "rb").read())
    return path, len(files)


def ext_for(e):
    return {"html": ".html", "table": ".csv", "text": ".txt"}.get(e["kind"], ".txt")


def build_lab(path):
    lab = json.load(io.open(path, encoding="utf-8"))
    name = "lab-%s-fixture" % lab["id"]
    out = os.path.join(OUT, name + ".zip")
    with zipfile.ZipFile(out, "w") as z:
        readme = ["# %s — fixture files" % lab["title"], "",
                  "Sample data written for the lab at https://sitebuilderstack.com/pages/%s" % lab["handle"], "",
                  lab["sample"]["note"], "", "## Files", ""]
        for e in lab["evidence"] + lab["after"]:
            fn = e["id"] + ext_for(e)
            if e["kind"] == "table":
                body = ",".join(e["columns"]) + "\n" + "\n".join(",".join(r) for r in e["rows"]) + "\n"
            else:
                body = e["content"] + "\n"
            add(z, "%s/%s" % (name, fn), body.encode("utf-8"))
            readme.append("- `%s` — %s" % (fn, e["title"]))
        readme += ["", "## Scenario", "", lab["scenario"], "", "_Nothing here describes a real business, host or service._", ""]
        add(z, "%s/README.md" % name, "\n".join(readme).encode("utf-8"))
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    for k in KITS:
        p, n = build_kit(k)
        print("  %-52s %6d bytes  %d files" % (os.path.relpath(p, ROOT), os.path.getsize(p), n))
    for lab in sorted(glob.glob(os.path.join(ROOT, "content", "labs", "*.json"))):
        p = build_lab(lab)
        print("  %-52s %6d bytes" % (os.path.relpath(p, ROOT), os.path.getsize(p)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
