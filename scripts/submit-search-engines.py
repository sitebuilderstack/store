#!/usr/bin/env python3
"""Submit the sitemap to Google and Bing, and ping IndexNow with changed URLs.

  submit-search-engines.py --status              report state, submit nothing
  submit-search-engines.py --sitemaps            (re)submit the sitemap to both
  submit-search-engines.py --urls <url> [...]    IndexNow + Bing URL submission

Credentials are read at runtime from paths outside this repository. Nothing
here holds a secret, and each client redacts its own before printing.

Google does not participate in IndexNow -- Google discovery happens through
the Search Console sitemap submission above.
"""
import argparse
import datetime
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bing_webmaster as bing            # noqa: E402
import google_search_console as gsc      # noqa: E402
import importlib.util                    # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "indexnow", os.path.join(os.path.dirname(os.path.abspath(__file__)), "indexnow-submit.py"))
indexnow = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(indexnow)

ORIGIN = "https://sitebuilderstack.com"
SITEMAP = ORIGIN + "/sitemap.xml"
GSC_SITE = "sc-domain:sitebuilderstack.com"
BING_SITE = ORIGIN + "/"
INDEXNOW_KEY_PATH = os.environ.get("INDEXNOW_KEY_PATH", "/opt/indexnow-key.txt")


def _dt(v):
    m = re.search(r"-?\d+", v or "")
    if not m:
        return v or "—"
    ms = int(m.group())
    if ms < 0:
        return "never"
    return datetime.datetime.fromtimestamp(ms / 1000, datetime.timezone.utc) \
                            .strftime("%Y-%m-%d %H:%M:%SZ")


def status():
    print("── Google Search Console " + "─" * 40)
    code, d = gsc.get_sitemaps(GSC_SITE)
    print("  HTTP %s" % code)
    for s in d.get("sitemap", []) or [{}]:
        if not s:
            print("  no sitemap registered")
            break
        print("  %-16s %s" % ("path", s.get("path")))
        print("  %-16s %s" % ("pending", s.get("isPending")))
        print("  %-16s %s" % ("lastSubmitted", s.get("lastSubmitted")))
        print("  %-16s %s" % ("lastDownloaded", s.get("lastDownloaded", "not yet fetched")))
        print("  %-16s %s errors, %s warnings" % ("health", s.get("errors"), s.get("warnings")))

    print("\n── Bing Webmaster Tools " + "─" * 41)
    code, d = bing.get_feeds(BING_SITE)
    print("  HTTP %s" % code)
    for f in d.get("d", []) or [{}]:
        if not f:
            print("  no feed registered")
            break
        print("  %-16s %s" % ("url", f.get("Url")))
        print("  %-16s %s" % ("status", f.get("Status")))
        print("  %-16s %s" % ("submitted", _dt(f.get("Submitted"))))
        print("  %-16s %s" % ("lastCrawled", _dt(f.get("LastCrawled"))))
        print("  %-16s %s" % ("urlCount", f.get("UrlCount")))
    code, q = bing.call("GET", "GetUrlSubmissionQuota", siteUrl=BING_SITE)
    qq = q.get("d", {}) if isinstance(q, dict) else {}
    print("  %-16s daily %s/100, monthly %s/500 remaining"
          % ("quota", qq.get("DailyQuota"), qq.get("MonthlyQuota")))

    print("\n── IndexNow " + "─" * 53)
    if not os.path.exists(INDEXNOW_KEY_PATH):
        print("  no key file at %s" % INDEXNOW_KEY_PATH)
        return
    key = open(INDEXNOW_KEY_PATH, encoding="utf-8").read().strip()
    import urllib.request
    url = "%s/%s.txt" % (ORIGIN, key)
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            body = r.read().decode().strip()
        print("  %-16s HTTP %s, body matches key: %s" % ("key file", r.getcode(), body == key))
    except Exception as e:
        print("  %-16s unreachable: %s" % ("key file", e))
    print("  %-16s %s.txt" % ("keyLocation", ORIGIN + "/" + key[:4] + "…"))


def submit_sitemaps():
    print("── Google Search Console " + "─" * 40)
    code, d = gsc.submit_sitemap(GSC_SITE, SITEMAP)
    print("  PUT sitemap -> HTTP %s  %s" % (code, "accepted" if code in (200, 204) else gsc.redact(json.dumps(d))[:200]))

    print("\n── Bing Webmaster Tools " + "─" * 41)
    code, d = bing.submit_feed(BING_SITE, SITEMAP)
    print("  SubmitFeed -> HTTP %s  %s" % (code, "accepted" if code == 200 else bing.redact(json.dumps(d))[:200]))
    print("\nIndexNow does not take sitemaps -- use --urls for changed pages.")


def submit_urls(urls):
    bad = [u for u in urls if not u.startswith(ORIGIN + "/")]
    if bad:
        raise SystemExit("refusing URLs outside %s: %s" % (ORIGIN, bad))

    print("── IndexNow (Bing, Yandex, Seznam, Naver; not Google) " + "─" * 12)
    key = open(INDEXNOW_KEY_PATH, encoding="utf-8").read().strip()
    code, body = indexnow.submit(key, urls)
    print("  POST -> HTTP %s  %s" % (code, indexnow.MEANING.get(code, "unrecognised")))

    print("\n── Bing URL submission (authenticated, no key file needed) " + "─" * 6)
    code, d = bing.call("GET", "GetUrlSubmissionQuota", siteUrl=BING_SITE)
    before = (d.get("d") or {}).get("DailyQuota")
    code, d = bing.submit_url_batch(BING_SITE, urls)
    print("  SubmitUrlbatch -> HTTP %s" % code)
    code, d = bing.call("GET", "GetUrlSubmissionQuota", siteUrl=BING_SITE)
    after = (d.get("d") or {}).get("DailyQuota")
    print("  daily quota %s -> %s (%s URLs consumed)"
          % (before, after, (before - after) if None not in (before, after) else "?"))

    print("\nGoogle: no per-URL push. Discovery is via the submitted sitemap.")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--sitemaps", action="store_true")
    ap.add_argument("--urls", nargs="+")
    a = ap.parse_args()
    if a.sitemaps:
        submit_sitemaps()
    elif a.urls:
        submit_urls(a.urls)
    else:
        status()


if __name__ == "__main__":
    main()
