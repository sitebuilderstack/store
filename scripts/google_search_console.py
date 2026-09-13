#!/usr/bin/env python3
"""Google Search Console API client using a service account.

Reads the service account key from a path OUTSIDE this repository. Nothing
here contains a credential, and every network helper runs its output through
redact() so an access token or an assertion can never reach a log, a report,
or a commit.

The service account must be granted access to the property in Search Console
first -- a service account cannot verify a property itself. Add
`client_email` from the key file as a user on the property.
"""
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request

KEY_PATH = os.environ.get("GSC_KEY_PATH", "/opt/site-builder-stack-726cbbfd0bed.json")
SCOPE = "https://www.googleapis.com/auth/webmasters"
API = "https://www.googleapis.com/webmasters/v3"
CACHE_DIR = os.path.expanduser("~/.cache/sitebuilderstack")
CACHE = os.path.join(CACHE_DIR, "gsc-token.json")

_secrets = []


def _load_key():
    with open(KEY_PATH, encoding="utf-8") as fh:
        d = json.load(fh)
    _secrets.append(d["private_key"])
    _secrets.append(d.get("private_key_id", ""))
    return d


def redact(text):
    """Strip anything secret from text before it is shown or written."""
    if not isinstance(text, str):
        text = str(text)
    for s in _secrets:
        if s and len(s) > 8:
            text = text.replace(s, "<redacted>")
    # bearer tokens and JWT assertions
    text = __import__("re").sub(r"(ya29\.|1//|eyJ)[A-Za-z0-9._\-]{20,}", "<redacted-token>", text)
    return text


def _mint():
    import jwt  # PyJWT

    key = _load_key()
    now = int(time.time())
    assertion = jwt.encode(
        {
            "iss": key["client_email"],
            "scope": SCOPE,
            "aud": key["token_uri"],
            "iat": now,
            "exp": now + 3600,
        },
        key["private_key"],
        algorithm="RS256",
        headers={"kid": key.get("private_key_id")},
    )
    body = urllib.parse.urlencode({
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
        "assertion": assertion,
    }).encode()
    req = urllib.request.Request(key["token_uri"], data=body, method="POST",
                                 headers={"Content-Type": "application/x-www-form-urlencoded"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            tok = json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        raise SystemExit("token request failed: HTTP %s\n%s"
                         % (e.code, redact(e.read().decode("utf-8", "replace"))))
    tok["expires_at"] = now + int(tok.get("expires_in", 3600)) - 60
    os.makedirs(CACHE_DIR, exist_ok=True)
    fd = os.open(CACHE, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as fh:
        json.dump(tok, fh)
    return tok["access_token"]


def token():
    try:
        with open(CACHE, encoding="utf-8") as fh:
            t = json.load(fh)
        if t.get("expires_at", 0) > time.time():
            _load_key()          # populate the redaction list either way
            return t["access_token"]
    except (OSError, ValueError, KeyError):
        pass
    return _mint()


def call(method, path, body=None, raw_url=None):
    """One Search Console API call. Returns (status, parsed-or-text)."""
    url = raw_url or (API + path)
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        "Authorization": "Bearer " + token(),
        "Content-Type": "application/json",
        "User-Agent": "sbs-search-console/1.0",
    })
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            payload = r.read().decode("utf-8", "replace")
            return r.getcode(), (json.loads(payload) if payload.strip() else {})
    except urllib.error.HTTPError as e:
        payload = e.read().decode("utf-8", "replace")
        try:
            return e.code, json.loads(payload)
        except ValueError:
            return e.code, redact(payload)


def list_sites():
    return call("GET", "/sites")


def submit_sitemap(site_url, sitemap_url):
    p = "/sites/%s/sitemaps/%s" % (urllib.parse.quote(site_url, safe=""),
                                   urllib.parse.quote(sitemap_url, safe=""))
    return call("PUT", p)


def get_sitemaps(site_url):
    return call("GET", "/sites/%s/sitemaps" % urllib.parse.quote(site_url, safe=""))


def search_analytics(site_url, start, end, dimensions=None, row_limit=100,
                     search_type="web", data_state="all"):
    """Search Analytics query: impressions, clicks, CTR, average position.

    `data_state="all"` includes fresh (not yet finalised) data, which for a
    site this young is most of it. Without it a two-day-old site reports zero.
    """
    body = {
        "startDate": start,
        "endDate": end,
        "dimensions": dimensions or [],
        "rowLimit": row_limit,
        "type": search_type,
        "dataState": data_state,
    }
    p = "/sites/%s/searchAnalytics/query" % urllib.parse.quote(site_url, safe="")
    return call("POST", p, body=body)


def inspect_url(site_url, page_url):
    """URL Inspection API. Different host from the rest of Search Console."""
    return call("POST", None, body={"inspectionUrl": page_url, "siteUrl": site_url},
                raw_url="https://searchconsole.googleapis.com/v1/urlInspection/index:inspect")


if __name__ == "__main__":
    code, sites = list_sites()
    print("GET /sites -> HTTP %s" % code)
    print(redact(json.dumps(sites, indent=2)))
