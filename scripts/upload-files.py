#!/usr/bin/env python3
"""Upload local files to Shopify Files via staged uploads.

Usage: upload-files.py [--allow-archive] <file> [<file> ...]

Prints the resulting CDN URL and resource id for each.

NOTE: files uploaded here are served from a PUBLIC CDN URL. The paid product
archive is refused unconditionally, with no override — a public URL bypasses
checkout. Other archives need --allow-archive, so putting a download on the
public CDN is always a deliberate act.
"""
import mimetypes
import os
import sys
import time
import urllib.request
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shopify_api import gql, check_user_errors, SHOP  # noqa: E402

ALLOW_ARCHIVE = "--allow-archive" in sys.argv

# Files uploaded here get a PUBLIC CDN URL, so a paid archive uploaded by
# mistake is given away. These substrings are refused unconditionally and there
# is no flag to override them. Every paid product's slug belongs on this list;
# it only had the flagship's while the flagship was the only paid product.
BLOCKED = (
    "claude-code-website-launch-system",
    "claude-code-seo-website-audit-toolkit",
    "claude-code-conversion-revenue-optimization-toolkit",
    "complete-site-builder-stack",
    "claude-code-website-operations-maintenance-system",
)

# Any other archive is refused too, but deliberately rather than absolutely:
# a genuinely free download (a lead magnet) belongs on the public CDN. Passing
# --allow-archive makes that a conscious act instead of an accident.
ARCHIVE_EXT = (".zip", ".tar", ".tgz", ".gz", ".7z", ".rar")


def staged_target(path):
    name = os.path.basename(path)
    mime = mimetypes.guess_type(name)[0] or "application/octet-stream"
    size = str(os.path.getsize(path))
    q = """mutation($input:[StagedUploadInput!]!){
      stagedUploadsCreate(input:$input){
        stagedTargets{ url resourceUrl parameters{ name value } }
        userErrors{ field message }
      }
    }"""
    d = gql(q, {"input": [{
        "filename": name, "mimeType": mime, "resource": "FILE",
        "fileSize": size, "httpMethod": "POST",
    }]})
    check_user_errors(d["stagedUploadsCreate"], "stagedUploadsCreate")
    return d["stagedUploadsCreate"]["stagedTargets"][0], mime


def post_multipart(target, path):
    boundary = uuid.uuid4().hex
    body = bytearray()
    for p in target["parameters"]:
        body += (f'--{boundary}\r\nContent-Disposition: form-data; name="{p["name"]}"'
                 f'\r\n\r\n{p["value"]}\r\n').encode()
    with open(path, "rb") as fh:
        content = fh.read()
    body += (f'--{boundary}\r\nContent-Disposition: form-data; name="file"; '
             f'filename="{os.path.basename(path)}"\r\n'
             f'Content-Type: application/octet-stream\r\n\r\n').encode()
    body += content + f"\r\n--{boundary}--\r\n".encode()

    req = urllib.request.Request(
        target["url"], data=bytes(body), method="POST",
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    with urllib.request.urlopen(req, timeout=120) as r:
        if r.status not in (200, 201, 204):
            raise SystemExit(f"staged upload failed: HTTP {r.status}")


def create_file(resource_url, alt, is_image):
    q = """mutation($files:[FileCreateInput!]!){
      fileCreate(files:$files){
        files{ id fileStatus alt
               ... on MediaImage { image{ url width height } }
               ... on GenericFile { url } }
        userErrors{ field message }
      }
    }"""
    d = gql(q, {"files": [{
        "originalSource": resource_url,
        "alt": alt,
        "contentType": "IMAGE" if is_image else "FILE",
    }]})
    check_user_errors(d["fileCreate"], "fileCreate")
    return d["fileCreate"]["files"][0]


def poll(file_id, tries=30):
    q = """query($id:ID!){ node(id:$id){
      ... on MediaImage { id fileStatus image{ url width height } }
      ... on GenericFile { id fileStatus url }
    } }"""
    for _ in range(tries):
        n = gql(q, {"id": file_id})["node"]
        if n and n.get("fileStatus") == "READY":
            return n
        time.sleep(2)
    return n


if __name__ == "__main__":
    for path in [a for a in sys.argv[1:] if not a.startswith("--")]:
        base = os.path.basename(path).lower()
        if any(b in base for b in BLOCKED):
            raise SystemExit(
                "refusing %s: this is the paid product. A public CDN URL "
                "bypasses checkout. There is no override." % base)
        if base.lower().endswith(ARCHIVE_EXT) and not ALLOW_ARCHIVE:
            raise SystemExit(
                "refusing %s: archives get a public CDN URL. If this file is "
                "genuinely free to give away, re-run with --allow-archive." % base)
        if False:
            print(f"  REFUSED {base}: product archives must not be uploaded to public Files")
            continue
        alt = os.path.splitext(base)[0].replace("-", " ")
        is_image = base.endswith((".png", ".jpg", ".jpeg", ".gif", ".webp"))
        target, mime = staged_target(path)
        post_multipart(target, path)
        f = create_file(target["resourceUrl"], alt, is_image)
        f = poll(f["id"])
        url = (f.get("image") or {}).get("url") or f.get("url")
        print(f"  uploaded {base:<22} status={f.get('fileStatus')} id={f['id'].split('/')[-1]}")
        print(f"           {url}")
