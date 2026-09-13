#!/usr/bin/env python3
"""Attach a local PNG to a product as its featured image.

    attach-product-image.py <handle> <png> "<alt text>"

Uses a staged upload (the same helpers as upload-files.py) and
productCreateMedia. Refuses anything that is not an image, so it cannot be
used to put an archive on the CDN. If the product already has media, the new
image is added and the operator is told; nothing is deleted.
"""
import importlib.util
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from shopify_api import gql, check_user_errors  # noqa: E402

_spec = importlib.util.spec_from_file_location("uf", os.path.join(HERE, "upload-files.py"))
_uf = importlib.util.module_from_spec(_spec)
sys.argv_backup, sys.argv = sys.argv, [sys.argv[0]]   # upload-files parses argv at import
_spec.loader.exec_module(_uf)
sys.argv = sys.argv_backup


def main():
    if len(sys.argv) != 4:
        raise SystemExit(__doc__)
    handle, path, alt = sys.argv[1:4]
    if not path.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
        raise SystemExit("refusing: only images can be attached")
    d = gql("query($q:String!){ products(first:5, query:$q){ nodes{ id handle media(first:5){ nodes{ id alt } } } } }",
            {"q": "handle:%s" % handle})
    prod = next((p for p in d["products"]["nodes"] if p["handle"] == handle), None)
    if not prod:
        raise SystemExit("no product with handle %s" % handle)
    if prod["media"]["nodes"]:
        print("  product already has %d media item(s); adding another" % len(prod["media"]["nodes"]))
    target, _ = _uf.staged_target(path)
    _uf.post_multipart(target, path)
    m = gql("""mutation($pid:ID!,$media:[CreateMediaInput!]!){
                 productCreateMedia(productId:$pid, media:$media){
                   media{ id alt status ... on MediaImage { image{ url width height } } }
                   mediaUserErrors{ field message } } }""",
            {"pid": prod["id"], "media": [{"originalSource": target["resourceUrl"], "alt": alt, "mediaContentType": "IMAGE"}]})
    errs = m["productCreateMedia"]["mediaUserErrors"]
    if errs:
        raise SystemExit("productCreateMedia: %s" % errs)
    mid = m["productCreateMedia"]["media"][0]["id"]
    for _ in range(30):
        n = gql("query($id:ID!){ node(id:$id){ ... on MediaImage { id status alt image{ url width height } } } }", {"id": mid})["node"]
        if n and n.get("status") == "READY":
            print("  attached %s  %sx%s  alt=%r" % (n["image"]["url"], n["image"]["width"], n["image"]["height"], n["alt"]))
            return 0
        time.sleep(2)
    raise SystemExit("media did not become READY: %s" % n)


if __name__ == "__main__":
    sys.exit(main())
