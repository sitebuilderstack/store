#!/usr/bin/env python3
"""Every tool page declares a tool the section can actually render.

A page whose `sbs.tool` metafield names something the section has no branch for
renders a heading, some prose, and no form — with no error anywhere. This is the
check for that.
"""
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    src = io.open(os.path.join(ROOT, "scripts", "publish-tools.py"), encoding="utf-8").read()
    tools = re.findall(r'"tool":\s*"([a-z-]+)"', src)
    liquid = io.open(os.path.join(ROOT, "theme", "dev", "sections", "sbs-tool.liquid"),
                     encoding="utf-8").read()
    renderable = set(re.findall(r"tool == '([a-z-]+)'", liquid))
    missing = [t for t in tools if t not in renderable]
    orphan = [t for t in sorted(renderable) if t not in tools]
    for t in missing:
        print("  FAIL the section cannot render tool %r" % t)
    for t in orphan:
        print("  FAIL the section renders %r but no page declares it" % t)
    print("%d tool page(s), %d renderable branch(es), %d failure(s)"
          % (len(tools), len(renderable), len(missing) + len(orphan)))
    return 1 if (missing or orphan) else 0


if __name__ == "__main__":
    sys.exit(main())
