#!/usr/bin/env python3
"""Submit changed URLs to IndexNow.

IndexNow is a Bing/Yandex/Seznam/Naver protocol. Google has not adopted it --
Google discovery is handled through Search Console, not here.

Ownership is proved by a key file on the host. Shopify cannot serve an
arbitrary file at the site root, so the file is uploaded to Shopify Files and
a store URL redirect maps /<key>.txt onto it. That resolves 301 -> 200 with
the key as the body, which is what the protocol checks.

Usage: indexnow-submit.py <keyfile-path> <url> [<url> ...]
       indexnow-submit.py --key <key> <url> [<url> ...]
"""
import json
import os
import sys
import urllib.error
import urllib.request

HOST = "sitebuilderstack.com"
ORIGIN = "https://" + HOST
ENDPOINT = "https://api.indexnow.org/indexnow"

MEANING = {
    200: "OK -- URLs submitted and the key was accepted",
    202: "Accepted -- URLs received, key validation still pending",
    400: "Bad request -- malformed payload",
    403: "Forbidden -- the key file could not be validated",
    422: "Unprocessable -- URLs do not belong to the host, or the key does not match",
    429: "Too many requests -- rate limited",
}


def submit(key, urls, endpoint=ENDPOINT):
    payload = {
        "host": HOST,
        "key": key,
        "keyLocation": "%s/%s.txt" % (ORIGIN, key),
        "urlList": urls,
    }
    req = urllib.request.Request(
        endpoint, data=json.dumps(payload).encode(), method="POST",
        headers={"Content-Type": "application/json; charset=utf-8",
                 "User-Agent": "sbs-indexnow/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            return r.getcode(), r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")
    except urllib.error.URLError as e:
        return None, "URLError: %s" % e


def main():
    args = sys.argv[1:]
    if not args:
        raise SystemExit(__doc__)
    if args[0] == "--key":
        key, urls = args[1], args[2:]
    else:
        key = open(args[0], encoding="utf-8").read().strip()
        urls = args[1:]
    if not urls:
        raise SystemExit("no URLs given")

    bad = [u for u in urls if not u.startswith(ORIGIN + "/")]
    if bad:
        raise SystemExit("refusing: URLs outside %s: %s" % (ORIGIN, bad))

    print("host        %s" % HOST)
    print("keyLocation %s/%s.txt" % (ORIGIN, key[:4] + "…"))
    print("urls        %d" % len(urls))
    for u in urls:
        print("   %s" % u)

    code, body = submit(key, urls)
    print("\nPOST %s -> HTTP %s" % (ENDPOINT, code))
    print("  %s" % MEANING.get(code, "unrecognised status"))
    if body.strip():
        print("  body: %s" % body.strip()[:300])
    return 0 if code in (200, 202) else 1


if __name__ == "__main__":
    sys.exit(main())
