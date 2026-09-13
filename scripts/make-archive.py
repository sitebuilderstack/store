#!/usr/bin/env python3
"""Create the distribution ZIP deterministically.

Usage: make-archive.py <bundleDir> <outputZip>

Entries are written in sorted order under a single top-level directory so the
customer always extracts to a predictable folder.
"""
import os
import sys
import zipfile

bundle, out = sys.argv[1], sys.argv[2]
root = os.path.dirname(os.path.normpath(bundle))

paths = []
for dirpath, dirnames, filenames in os.walk(bundle):
    dirnames.sort()
    for name in sorted(filenames):
        paths.append(os.path.join(dirpath, name))
paths.sort()

if not paths:
    sys.exit("bundle contains no files")

with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
    for p in paths:
        zf.write(p, os.path.relpath(p, root))

print(f"  wrote {len(paths)} entries")
