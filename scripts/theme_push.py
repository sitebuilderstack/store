#!/usr/bin/env python3
"""Push local theme files to a Shopify theme via the Admin GraphQL API.

Usage:
    theme_push.py <themeId> <localDir> [relativePath ...]

With no relative paths, every file under localDir is pushed.
Text files are sent as UTF-8; anything else as base64.

Refuses to push to the published theme unless SBS_ALLOW_LIVE=1 is set —
development happens on an unpublished theme.
"""
import base64
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shopify_api import gql, redact  # noqa: E402

TEXT_EXT = {".liquid", ".json", ".css", ".js", ".svg", ".txt", ".md", ".map"}
BATCH = 10


def theme_role(tid):
    d = gql("query($id:ID!){ theme(id:$id){ id name role } }", {"id": tid})
    return d["theme"]


def upsert(tid, entries):
    q = """mutation($themeId:ID!,$files:[OnlineStoreThemeFilesUpsertFileInput!]!){
      themeFilesUpsert(themeId:$themeId, files:$files){
        upsertedThemeFiles{ filename }
        userErrors{ filename code message }
      }
    }"""
    d = gql(q, {"themeId": tid, "files": entries})
    payload = d["themeFilesUpsert"]
    errs = payload.get("userErrors") or []
    if errs:
        for e in errs:
            print(f"  ERROR {e.get('filename')}: {e.get('code')} {e.get('message')}")
        raise SystemExit("themeFilesUpsert reported errors")
    return [f["filename"] for f in payload["upsertedThemeFiles"]]


def main():
    tid = sys.argv[1]
    local = sys.argv[2].rstrip("/")
    only = sys.argv[3:]
    if not tid.startswith("gid://"):
        tid = f"gid://shopify/OnlineStoreTheme/{tid}"

    info = theme_role(tid)
    if info["role"] == "MAIN" and os.environ.get("SBS_ALLOW_LIVE") != "1":
        raise SystemExit(
            f"Refusing to push to the PUBLISHED theme {info['name']!r}. "
            "Work on a development theme. Set SBS_ALLOW_LIVE=1 to override."
        )
    print(f"theme: {info['name']} ({info['role']})")

    paths = []
    if only:
        paths = [os.path.join(local, p) for p in only]
    else:
        for dirpath, dirnames, filenames in os.walk(local):
            dirnames.sort()
            for name in sorted(filenames):
                paths.append(os.path.join(dirpath, name))
    paths = [p for p in sorted(paths) if os.path.isfile(p)]
    if not paths:
        raise SystemExit("nothing to push")

    entries = []
    for p in paths:
        rel = os.path.relpath(p, local).replace(os.sep, "/")
        ext = os.path.splitext(p)[1].lower()
        if ext in TEXT_EXT:
            with open(p, encoding="utf-8") as fh:
                entries.append({"filename": rel, "body": {"type": "TEXT", "value": fh.read()}})
        else:
            with open(p, "rb") as fh:
                entries.append({
                    "filename": rel,
                    "body": {"type": "BASE64", "value": base64.b64encode(fh.read()).decode()},
                })

    pushed = []
    for i in range(0, len(entries), BATCH):
        chunk = entries[i : i + BATCH]
        pushed += upsert(tid, chunk)
        for name in (e["filename"] for e in chunk):
            print(f"  ✓ {name}")

    print(f"\npushed {len(pushed)} file(s) to {info['name']}")


if __name__ == "__main__":
    main()
