#!/usr/bin/env python3
"""Bing Webmaster Tools API client.

Reads the API key from a path OUTSIDE this repository. The key travels in the
query string, so every URL and every error body is passed through redact()
before it is printed or written anywhere.
"""
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request

KEY_PATH = os.environ.get("BING_KEY_PATH", "/opt/bing-webmaster-tools-api-key.txt")
BASE = "https://ssl.bing.com/webmaster/api.svc/json"

_key = None


def key():
    global _key
    if _key is None:
        with open(KEY_PATH, encoding="utf-8") as fh:
            _key = fh.read().strip()
    return _key


def redact(text):
    """Strip the API key, and the per-site verification codes the API returns
    for every property on the account -- this key can see domains that have
    nothing to do with this project, and none of that belongs in our output."""
    if not isinstance(text, str):
        text = str(text)
    text = re.sub(r'("(?:AuthenticationCode|DnsVerificationCode)"\s*:\s*")[^"]*(")',
                  r"\1<redacted>\2", text)
    k = key()
    if k:
        text = text.replace(k, "<redacted-apikey>")
        text = text.replace(urllib.parse.quote(k, safe=""), "<redacted-apikey>")
    return re.sub(r"(?i)(apikey=)[^&\s\"']+", r"\1<redacted>", text)


def call(method, op, body=None, **params):
    q = dict(params)
    q["apikey"] = key()
    url = "%s/%s?%s" % (BASE, op, urllib.parse.urlencode(q))
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        "Content-Type": "application/json; charset=utf-8",
        "User-Agent": "sbs-bing-webmaster/1.0",
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            payload = r.read().decode("utf-8", "replace")
            try:
                return r.getcode(), json.loads(payload) if payload.strip() else {}
            except ValueError:
                return r.getcode(), redact(payload)
    except urllib.error.HTTPError as e:
        payload = e.read().decode("utf-8", "replace")
        try:
            return e.code, json.loads(payload)
        except ValueError:
            return e.code, redact(payload)
    except urllib.error.URLError as e:
        return None, redact("URLError: %s" % e)


def get_user_sites():
    return call("GET", "GetUserSites")


def submit_feed(site_url, feed_url):
    return call("POST", "SubmitFeed", body={"siteUrl": site_url, "feedUrl": feed_url})


def get_feeds(site_url):
    return call("GET", "GetFeeds", siteUrl=site_url)


def submit_url_batch(site_url, urls):
    return call("POST", "SubmitUrlbatch", body={"siteUrl": site_url, "urlList": urls})


def get_rank_and_traffic(site_url):
    """Impressions and clicks per day, as Bing reports them."""
    return call("GET", "GetRankAndTrafficStats", siteUrl=site_url)


def get_query_stats(site_url):
    return call("GET", "GetQueryStats", siteUrl=site_url)


def get_crawl_stats(site_url):
    return call("GET", "GetCrawlStats", siteUrl=site_url)


def get_url_traffic(site_url, url):
    return call("GET", "GetUrlTrafficInfo", siteUrl=site_url, url=url)


def get_page_stats(site_url):
    return call("GET", "GetPageStats", siteUrl=site_url)


def get_url_submission_quota(site_url):
    return call("GET", "GetUrlSubmissionQuota", siteUrl=site_url)


def get_children_url_info(site_url, url, page=0):
    return call("GET", "GetChildrenUrlInfo", siteUrl=site_url, url=url,
                page=page, pageSize=100)


def find_site(url_prefix):
    """Return the verified site entry matching url_prefix, or None."""
    code, d = get_user_sites()
    if code != 200:
        return None
    for s in d.get("d", []):
        if s.get("Url", "").rstrip("/") == url_prefix.rstrip("/"):
            return s
    return None


if __name__ == "__main__":
    code, d = get_user_sites()
    print("GetUserSites -> HTTP %s" % code)
    sites = d.get("d", []) if isinstance(d, dict) else []
    print("  %d properties on this account" % len(sites))
    for s in sites:
        u = s.get("Url", "")
        mine = "sitebuilderstack.com" in u
        print("   %-40s verified=%-5s %s"
              % (u, s.get("IsVerified"), "<-- ours" if mine else ""))
