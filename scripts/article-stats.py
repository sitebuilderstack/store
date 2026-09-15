#!/usr/bin/env python3
"""Report word count and link/structure stats for article HTML files."""
import html
import re
import sys

for path in sys.argv[1:]:
    s = open(path, encoding="utf-8").read()
    text = html.unescape(re.sub(r"<[^>]+>", " ", s))
    words = len(text.split())
    print(f"  {path}")
    print(f"      words={words:,}  bytes={len(s):,}")
    print(f"      h2={len(re.findall(r'<h2', s))}  h3={len(re.findall(r'<h3', s))}"
          f"  pre={len(re.findall(r'<pre', s))}  tables={len(re.findall(r'<table', s))}")
    print(f"      internal links={len(re.findall(r'href=\"/', s))}"
          f"  external={len(re.findall(r'href=\"http', s))}"
          f"  anchors={len(re.findall(r'href=\"#', s))}")
