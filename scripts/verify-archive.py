#!/usr/bin/env python3
"""Verify the built archive against the source bundle.

Usage: verify-archive.py <archive> <bundleDir>

Checks CRCs, entry count, a single top-level directory, required files, and
that no credential-shaped string made it into any entry.
"""
import os
import re
import sys
import zipfile

archive, bundle = sys.argv[1], sys.argv[2]
top_name = os.path.basename(os.path.normpath(bundle))

SECRET_RE = re.compile(
    rb"AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{36}|shp(at|ss|ca|pa)_[0-9a-fA-F]{32}"
    rb"|-----BEGIN [A-Z ]*PRIVATE KEY-----|AIza[0-9A-Za-z_-]{35}"
)

with zipfile.ZipFile(archive) as zf:
    bad = zf.testzip()
    if bad:
        sys.exit(f"  corrupt entry: {bad}")

    names = zf.namelist()
    on_disk = sum(len(f) for _, _, f in os.walk(bundle))
    if len(names) != on_disk:
        sys.exit(f"  entry count mismatch: archive {len(names)} vs disk {on_disk}")

    tops = {n.split("/")[0] for n in names}
    if tops != {top_name}:
        sys.exit(f"  unexpected top-level entries: {sorted(tops)}")

    for required in ("START-HERE.md", "README.md", "LICENSE.md",
                     "VERSION.md", "PRODUCT-MANIFEST.md"):
        if f"{top_name}/{required}" not in names:
            sys.exit(f"  missing from archive: {required}")

    for name in names:
        data = zf.read(name)
        if not data:
            sys.exit(f"  empty entry in archive: {name}")
        m = SECRET_RE.search(data)
        if m:
            sys.exit(f"  credential-shaped string in archive entry: {name}")

print(f"  {len(names)} entries verified: CRCs valid, no empty entries, "
      f"no credential patterns, single top-level directory")
