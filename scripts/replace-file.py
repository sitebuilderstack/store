#!/usr/bin/env python3
"""Replace a file in Shopify Files, keeping its filename.

Uploading a name that already exists makes Shopify append a UUID, so the
existing URL keeps serving the old asset. The only way to update in place is to
delete first and re-upload.

That leaves a short window where the URL 404s, so this verifies the new file
serves before reporting success, and refuses to start unless the local file
exists and the remote one was found.

Usage: replace-file.py <local-path> [<local-path> ...]
"""
import os
import subprocess
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from shopify_api import gql, check_user_errors  # noqa: E402

CDN = "https://cdn.shopify.com/s/files/1/0987/3925/7636/files/"


def find(name):
    d = gql("""query($q:String!){ files(first:20, query:$q) {
                 nodes { id alt preview { image { url } }
                   ... on GenericFile { url } ... on MediaImage { image { url } } } } }""",
            {"q": "filename:%s" % name})
    for n in d["files"]["nodes"]:
        url = n.get("url") or ((n.get("image") or {}).get("url"))
        if url and url.split("/")[-1].split("?")[0] == name:
            return n["id"], url
    return None, None


def main():
    paths = [a for a in sys.argv[1:] if not a.startswith("-")]
    if not paths:
        raise SystemExit(__doc__)
    for path in paths:
        name = os.path.basename(path)
        if not os.path.exists(path):
            raise SystemExit("no such local file: %s" % path)
        fid, url = find(name)
        if not fid:
            raise SystemExit("no remote file named %s — use upload-files.py instead" % name)

        d = gql("mutation($ids:[ID!]!){ fileDelete(fileIds:$ids){ deletedFileIds "
                "userErrors{ field message } } }", {"ids": [fid]})
        check_user_errors(d["fileDelete"], "fileDelete")
        print("%-44s deleted" % name)

        out = subprocess.run([sys.executable, os.path.join(HERE, "upload-files.py"), path],
                             capture_output=True, text=True)
        if out.returncode != 0:
            raise SystemExit("RE-UPLOAD FAILED for %s — the URL is now 404:\n%s"
                             % (name, out.stdout + out.stderr))
        if "_" in out.stdout.split(name)[-1][:40] and "?v=" not in out.stdout.split(name)[1][:4]:
            print("  warning: Shopify may have renamed it; check the URL above")

        # Confirm the canonical URL serves again before moving on.
        for attempt in range(8):
            try:
                r = urllib.request.urlopen(
                    urllib.request.Request(CDN + name, headers={"User-Agent": "sbs/1"}),
                    timeout=30)
                if r.status == 200:
                    print("%-44s replaced, %d bytes live" % (name, len(r.read())))
                    break
            except Exception:                          # noqa: BLE001
                time.sleep(2 + attempt)
        else:
            raise SystemExit("%s did not come back after re-upload" % name)


if __name__ == "__main__":
    main()
