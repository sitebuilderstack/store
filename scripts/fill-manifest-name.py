#!/usr/bin/env python3
"""Substitute the archive filename placeholder in the generated manifest.

Usage: fill-manifest-name.py <manifestPath> <archiveName>
"""
import sys

manifest, name = sys.argv[1], sys.argv[2]
with open(manifest, encoding="utf-8") as fh:
    text = fh.read()

text = text.replace("{{ARCHIVE_NAME}}", name)

leftover = [tok for tok in ("{{SHA256}}", "{{ARCHIVE_SIZE}}", "{{ARCHIVE_NAME}}")
            if tok in text]
if leftover:
    sys.exit(f"unfilled placeholders remain in manifest: {leftover}")

with open(manifest, "w", encoding="utf-8") as fh:
    fh.write(text)
