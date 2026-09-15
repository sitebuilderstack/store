#!/usr/bin/env python3
"""Run every migration-system script against two local fixture sites, offline.

Two throwaway HTTP servers on 127.0.0.1 play the SOURCE (old) site and the
TARGET (new) site of a migration, with the failures the scripts exist to
find: a page missing on the target, a redirect that is missing, one that
loops, one that chains, one that lands on a 404, a canonical pointing at
the old host, a sitemap listing a staging URL, a target page that lost its
meta description, an image on the old domain, a form that disappeared, and
an analytics tag on some pages only. Each script runs as a subprocess the
way a customer runs it; the test asserts the documented exit code and the
specific finding. Nothing touches the network beyond localhost.
"""
import http.server
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "product", "Claude-Code-Website-Migration-Replatforming-System", "scripts")

GA = "<script async src='https://www.googletagmanager.com/gtag/js?id=G-TEST12345'></script>"


def page(title, body, desc=True, canonical=None, robots=None, ld=None, extra_head=""):
    head = "<title>%s</title>" % title
    if desc:
        head += "<meta name='description' content='%s description'>" % title
    if canonical:
        head += "<link rel='canonical' href='%s'>" % canonical
    if robots:
        head += "<meta name='robots' content='%s'>" % robots
    if ld:
        head += "<script type='application/ld+json'>%s</script>" % json.dumps(ld)
    return "<!doctype html><html><head>%s%s</head><body><h1>%s</h1>%s</body></html>" % (head, extra_head, title, body)


def source_pages(src, tgt):
    words = " ".join(["word"] * 120)
    return {
        "/": page("Old Home", "<a href='/about'>About</a> <a href='/blog/post-one'>Post</a> <a href='/blog/post-two'>Two</a> <a href='/contact'>Contact</a> <a href='/services'>Services</a> <a href='/gone'>Gone</a><img src='/img/hero.jpg' alt='hero'>" + words, canonical=src + "/", ld={"@type": "Organization"}, extra_head=GA),
        "/about": page("About Us", "<a href='/'>Home</a>" + words, canonical=src + "/about", extra_head=GA),
        "/blog/post-one": page("Post One", words + "<img src='/img/one.jpg'>", canonical=src + "/blog/post-one", ld={"@type": "Article"}, extra_head=GA),
        "/blog/post-two": page("Post Two", words, canonical=src + "/blog/post-two", ld={"@type": "Article"}, extra_head=GA),
        "/contact": page("Contact", "<form action='/submit'><input name='email'></form>" + words, canonical=src + "/contact", extra_head=GA),
        "/services": page("Services", words, canonical=src + "/services", extra_head=GA),
        "/gone": page("Gone Page", words, extra_head=GA),
        "/robots.txt": "User-agent: *\nAllow: /\nSitemap: %s/sitemap.xml\n" % src,
        "/sitemap.xml": "<?xml version='1.0'?><urlset xmlns='http://www.sitemaps.org/schemas/sitemap/0.9'>" + "".join("<url><loc>%s%s</loc></url>" % (src, p) for p in ("/", "/about", "/blog/post-one", "/blog/post-two", "/contact", "/services")) + "</urlset>",
        "/img/hero.jpg": "JPEGDATA", "/img/one.jpg": "JPEGDATA",
    }


def target_pages(src, tgt, staging):
    words = " ".join(["word"] * 120)
    return {
        "/": page("New Home", "<a href='/about'>About</a> <a href='/posts/post-one'>Post</a> <a href='/posts/post-two'>Two</a> <a href='/contact'>Contact</a> <a href='/services'>Services</a> <a href='/missing-link'>Broken</a> <a href='%s/about'>Old link</a><img src='%s/img/hero.jpg' alt='hero'>" % (src, src) + words, canonical=tgt + "/", ld={"@type": "Organization"}, extra_head=GA),
        "/about": page("About Us", "<a href='/'>Home</a>" + words, canonical=tgt + "/about", extra_head=GA),
        "/posts/post-one": page("Post One", words + "<img src='/img/one.jpg'>", desc=False, canonical=src + "/blog/post-one", ld={"@type": "Article"}),
        "/posts/post-two": page("Post Two", words, canonical=tgt + "/posts/post-two", ld={"@type": "BlogPosting"}, extra_head=GA),
        "/contact": page("Contact", words, canonical=tgt + "/contact", extra_head=GA),
        # /services is missing on the target (no page, no redirect)
        "/robots.txt": "User-agent: *\nDisallow: /admin\nSitemap: %s/sitemap.xml\n" % tgt,
        "/sitemap.xml": "<?xml version='1.0'?><urlset xmlns='http://www.sitemaps.org/schemas/sitemap/0.9'>" + "".join("<url><loc>%s%s</loc></url>" % (tgt, p) for p in ("/", "/about", "/posts/post-one", "/posts/post-two", "/contact")) + "<url><loc>%s/leftover</loc></url></urlset>" % staging,
        "/img/one.jpg": "JPEGDATA",
    }


def make_handler(pages, redirects):
    class H(http.server.BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_GET(self):
            path = self.path.split("?")[0]
            if path in redirects:
                code, loc = redirects[path]
                self.send_response(code); self.send_header("Location", loc); self.end_headers(); return
            if path in pages:
                body = pages[path].encode()
                ctype = "text/html" if path.endswith((".jpg", ".txt", ".xml")) is False else "image/jpeg" if path.endswith(".jpg") else "text/plain" if path.endswith(".txt") else "application/xml"
                self.send_response(200); self.send_header("Content-Type", ctype + ("; charset=utf-8" if ctype.startswith("text") else ""))
                self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body); return
            body = b"<!doctype html><html><head><title>Not found</title></head><body>not found</body></html>"
            self.send_response(404); self.send_header("Content-Type", "text/html"); self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)

        do_HEAD = do_GET
    return H


def serve(handler):
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def run(script, *args, cwd=None, timeout=120):
    p = subprocess.run([sys.executable, os.path.join(SCRIPTS, script)] + [str(x) for x in args], capture_output=True, text=True, timeout=timeout, cwd=cwd,
                       env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    return p.returncode, p.stdout, p.stderr


failures = 0


def check(name, ok, detail=""):
    global failures
    failures += 0 if ok else 1
    print("  %s  %s%s" % ("PASS" if ok else "FAIL", name, ("  -> " + detail.strip()[-300:]) if detail and not ok else ""))


def csv_rows(path):
    import csv
    return list(csv.DictReader(open(path, newline="", encoding="utf-8-sig")))


def main():
    tmp = tempfile.mkdtemp(); work = os.path.join(tmp, "migration"); os.makedirs(work)
    # two servers: we need the target port before building the source pages, so bind first
    tsrv = serve(make_handler({}, {})); tport = tsrv.server_address[1]; tsrv.shutdown(); tsrv.server_close()
    ssrv0 = serve(make_handler({}, {})); sport = ssrv0.server_address[1]; ssrv0.shutdown(); ssrv0.server_close()
    src, tgt = "http://127.0.0.1:%d" % sport, "http://127.0.0.1:%d" % tport
    staging = "http://staging.127.0.0.1.invalid"
    # source: after cutover it serves redirects into the target (the domain-change case)
    src_redirects = {"/blog/post-one": (301, tgt + "/posts/post-one"), "/blog/post-two": (301, tgt + "/posts/post-two"),
                     "/chain": (301, src + "/chain-2"), "/chain-2": (301, tgt + "/about"), "/loop-a": (301, src + "/loop-b"), "/loop-b": (301, src + "/loop-a"),
                     "/to-404": (301, tgt + "/nowhere"), "/temp": (302, tgt + "/about")}
    tgt_redirects = {"/old-about": (301, "/about")}
    live_src_redirects = {}  # empty during the baseline crawl; filled after "cutover"
    ssrv = http.server.ThreadingHTTPServer(("127.0.0.1", sport), make_handler(source_pages(src, tgt), live_src_redirects)); threading.Thread(target=ssrv.serve_forever, daemon=True).start()
    tsrv = http.server.ThreadingHTTPServer(("127.0.0.1", tport), make_handler(target_pages(src, tgt, staging), tgt_redirects)); threading.Thread(target=tsrv.serve_forever, daemon=True).start()
    try:
        cwd = work
        # ---- crawler
        rc, out, err = run("crawl_site.py", src, "--out", "source-url-inventory.csv", "--delay", "0", "--seed", "sitemap", cwd=cwd)
        rows = csv_rows(os.path.join(work, "source-url-inventory.csv")); by = {r["url"].replace(src, ""): r for r in rows}
        check("crawl_site: crawls the source (exit 0)", rc == 0, out + err)
        check("crawl_site: finds every page incl. the sitemap-only ones", all(p in by for p in ("/", "/about", "/blog/post-one", "/contact", "/services", "/gone")), str(sorted(by)))
        check("crawl_site: captures title, canonical, jsonld and word count", by["/"]["title"] == "Old Home" and by["/"]["canonical"] == src + "/" and "Organization" in by["/"]["jsonld_types"] and int(by["/"]["word_count"]) > 100, str(by["/"]))
        check("crawl_site: counts forms", by["/contact"]["forms"] == "1", str(by["/contact"]))
        check("crawl_site: /gone has no canonical, indexable", by["/gone"]["indexability"] == "INDEXABLE", str(by["/gone"]))
        rc, out, err = run("crawl_site.py", tgt, "--out", "target-url-inventory.csv", "--delay", "0", "--list", os.path.join(work, "_t.txt"), cwd=cwd) if open(os.path.join(work, "_t.txt"), "w").write(tgt + "/services\n") is not None else (None, "", "")
        trows = csv_rows(os.path.join(work, "target-url-inventory.csv")); tby = {r["url"].replace(tgt, ""): r for r in trows}
        check("crawl_site: target crawl records the 404 from --list", tby.get("/services", {}).get("status") == "404", str(sorted(tby)))
        check("crawl_site: target exits 1 with a 404 in the inventory", rc == 1, "rc=%s %s" % (rc, err))
        check("crawl_site: canonical to the old host is CANONICALISED", tby["/posts/post-one"]["indexability"] == "CANONICALISED", str(tby["/posts/post-one"]))

        live_src_redirects.update(src_redirects)  # cutover: the old host now redirects
        # ---- url map + comparison
        rc, out, err = run("url_map.py", "--source", "source-url-inventory.csv", "--target", "target-url-inventory.csv", "--target-origin", tgt, "--rule", r"^/blog/(.*)=/posts/\1", "--out", "url-map.csv", cwd=cwd)
        m = {r["source_url"].replace(src, ""): r for r in csv_rows(os.path.join(work, "url-map.csv"))}
        check("url_map: rule maps /blog/ to /posts/ as MOVE", m["/blog/post-one"]["migration_action"] == "MOVE" and m["/blog/post-one"]["target_url"].endswith("/posts/post-one"), str(m.get("/blog/post-one")))
        check("url_map: unchanged paths are KEEP", m["/about"]["migration_action"] == "KEEP", str(m.get("/about")))
        # a person decides /gone is removed and /services is ... forgotten (stays REVIEW → becomes the gap)
        import csv as _csv
        rows = csv_rows(os.path.join(work, "url-map.csv"))
        for r in rows:
            if r["source_url"].endswith("/gone"):
                r.update(migration_action="REMOVE", target_url="", redirect_required="false", notes="retired")
            if r["source_url"].endswith("/services"):
                r.update(migration_action="KEEP", target_url=tgt + "/services", redirect_required="false")
        with open(os.path.join(work, "url-map.csv"), "w", newline="") as fh:
            w = _csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
        rc, out, err = run("compare_urls.py", "--source", "source-url-inventory.csv", "--target", "target-url-inventory.csv", "--map", "url-map.csv", "--out", "coverage-report.csv", cwd=cwd)
        cov = {r["source_url"].replace(src, ""): r for r in csv_rows(os.path.join(work, "coverage-report.csv"))}
        check("compare_urls: exits 2 with a missing page", rc == 2, out + err)
        check("compare_urls: /services is MISSING (KEEP but 404 on target)", cov["/services"]["result"] in ("MISSING", "BROKEN"), str(cov.get("/services")))
        check("compare_urls: /about UNCHANGED", cov["/about"]["result"] == "UNCHANGED", str(cov.get("/about")))
        check("compare_urls: moved post is REDIRECTED/UNCHANGED via the map", cov["/blog/post-one"]["result"] in ("REDIRECTED", "UNCHANGED"), str(cov.get("/blog/post-one")))
        check("compare_urls: /gone is REMOVED (intentional)", cov["/gone"]["result"] == "REMOVED", str(cov.get("/gone")))

        # ---- redirects: valid / missing / loop / chain / 404 target / wrong code
        rmap = os.path.join(work, "redirect-map.csv")
        open(rmap, "w").write("source_path,target_path,status\n/blog/post-one,/posts/post-one,301\n/blog/post-two,/posts/post-two,301\n/services,/services-new,301\n/loop-a,/about,301\n/chain,/about,301\n/to-404,/nowhere,301\n/temp,/about,301\n")
        rc, out, err = run("test_redirects.py", rmap, "--origin", src, "--target-origin", tgt, "--out", "redirect-results.csv", "--delay", "0", cwd=cwd)
        rr = {r["source"]: r["result"] for r in csv_rows(os.path.join(work, "redirect-results.csv"))}
        check("test_redirects: valid redirect PASS", rr.get("/blog/post-one") == "PASS", str(rr))
        check("test_redirects: missing redirect MISSING", rr.get("/services") == "MISSING", str(rr))
        check("test_redirects: loop LOOP", rr.get("/loop-a") == "LOOP", str(rr))
        check("test_redirects: chain CHAIN", rr.get("/chain") == "CHAIN", str(rr))
        check("test_redirects: redirect to a 404 is DEAD", rr.get("/to-404") == "DEAD", str(rr))
        check("test_redirects: 302 where 301 expected is WRONG-CODE", rr.get("/temp") == "WRONG-CODE", str(rr))
        check("test_redirects: exit 2", rc == 2, out + err)
        for fmt, needle in (("nginx", "return 301"), ("apache", "Redirect 301"), ("netlify", "301"), ("vercel", '"permanent": true'), ("shopify", "Redirect from,Redirect to"), ("cloudflare", "source_url,target_url")):
            rc, out, err = run("generate_redirects.py", rmap, "--format", fmt, "--origin", src, "--force", cwd=cwd)
            check("generate_redirects: %s config emitted" % fmt, rc in (0, 1) and needle in out, out[:300] + err)
        bad = os.path.join(work, "bad-map.csv"); open(bad, "w").write("source_path,target_path,status\n/a,/b,301\n/b,/a,301\n/x,/,301\n")
        rc, out, err = run("generate_redirects.py", bad, "--format", "nginx", cwd=cwd)
        check("generate_redirects: refuses a map with a loop/homepage-dump without --force", rc == 2, out + err)

        # ---- metadata / schema
        rc, out, err = run("compare_metadata.py", "--source", "source-url-inventory.csv", "--target", "target-url-inventory.csv", "--map", "url-map.csv", "--out", "metadata-compare.csv", cwd=cwd)
        md = csv_rows(os.path.join(work, "metadata-compare.csv"))
        lost = [r for r in md if r["url"].endswith("/blog/post-one") and r["field"] == "meta_description"]
        check("compare_metadata: lost description on the moved post is MISSING", lost and lost[0]["status"] == "MISSING", str(lost))
        check("compare_metadata: canonical to old host on that page is REVIEW", any(r["url"].endswith("/blog/post-one") and r["field"] == "canonical" and r["status"] == "REVIEW" for r in md), str([r for r in md if r["field"] == "canonical"]))
        check("compare_metadata: unchanged /about title MATCH", any(r["url"].endswith("/about") and r["field"] == "title" and r["status"] == "MATCH" for r in md))
        check("compare_metadata: exit 2", rc == 2, out + err)
        rc, out, err = run("schema_compare.py", "--source", "source-url-inventory.csv", "--target", "target-url-inventory.csv", "--map", "url-map.csv", "--out", "schema-compare.csv", cwd=cwd)
        sc = csv_rows(os.path.join(work, "schema-compare.csv"))
        check("schema_compare: Article→BlogPosting change is reported", any("post-two" in r.get("url", "") and r.get("status") in ("CHANGED", "REVIEW", "MISSING") for r in sc), str(sc))

        # ---- canonicals, robots, sitemap
        rc, out, err = run("check_canonicals.py", "--inventory", "target-url-inventory.csv", "--domain", "127.0.0.1:%d" % tport, "--old", "127.0.0.1:%d" % sport, "--json", cwd=cwd)
        j = json.loads(out[out.index("{"):])
        check("check_canonicals: a canonical to the old host is CRITICAL/FAIL", rc == 2 and any(f["status"] in ("CRITICAL", "FAIL") and "old" in (f["check"] + f["detail"]).lower() for f in j["findings"]), out + err)
        rc, out, err = run("check_robots.py", tgt, "--json", cwd=cwd)
        check("check_robots: production robots allows crawling (not exit 2)", rc < 2, out + err)
        rc, out, err = run("check_robots.py", tgt, "--staging", "--json", cwd=cwd)
        check("check_robots: the same file on --staging is a failure (open to crawlers)", rc == 2, out + err)
        rc, out, err = run("validate_sitemap.py", tgt + "/sitemap.xml", "--domain", "127.0.0.1:%d" % tport, "--staging", "staging.127.0.0.1.invalid", "--all", "--json", cwd=cwd)
        j = json.loads(out[out.index("{"):])
        check("validate_sitemap: a staging URL in the sitemap is CRITICAL", rc == 2 and any("staging" in (f["check"] + f["detail"]).lower() and f["status"] == "CRITICAL" for f in j["findings"]), out + err)
        rc, out, err = run("validate_sitemap.py", src + "/sitemap.xml", "--domain", "127.0.0.1:%d" % sport, "--all", "--json", cwd=cwd)
        check("validate_sitemap: a clean sitemap passes (exit 0/1)", rc < 2, out + err)

        # ---- links, media, old-domain, tracking, critical pages
        rc, out, err = run("internal_link_audit.py", tgt, "--old", "127.0.0.1:%d" % sport, "--out", "internal-links.csv", "--json", "internal-links.json", "--delay", "0", cwd=cwd)
        j = json.load(open(os.path.join(work, "internal-links.json")))
        check("internal_link_audit: finds the broken link", j["counts"].get("BROKEN", 0) >= 1, out + err)
        check("internal_link_audit: finds the link to the old domain", j["counts"].get("OLD-DOMAIN", 0) >= 1, json.dumps(j["counts"]))
        check("internal_link_audit: exit 2", rc == 2)
        rc, out, err = run("media_inventory.py", "--inventory", "target-url-inventory.csv", "--old", "127.0.0.1:%d" % sport, "--check", "--out", "media-validation.csv", "--delay", "0", cwd=cwd)
        mv = csv_rows(os.path.join(work, "media-validation.csv"))
        check("media_inventory: hero on the old domain flagged OLD-DOMAIN", any("OLD-DOMAIN" in r["problem"] for r in mv), str(mv))
        check("media_inventory: image without alt flagged", any("MISSING-ALT" in r["problem"] for r in mv), str(mv))
        repo = os.path.join(tmp, "repo"); os.makedirs(os.path.join(repo, "src")); os.makedirs(os.path.join(repo, "node_modules", "x"))
        open(os.path.join(repo, "src", "Footer.astro"), "w").write("<a href='%s/about'>old</a>\n<a href='https://staging.example.com/x'>staging</a>\n" % src)
        open(os.path.join(repo, "node_modules", "x", "i.js"), "w").write("'%s'\n" % src)
        open(os.path.join(work, "migration.yaml"), "w").write("migration:\n  name: Fixture migration\nsource:\n  url: %s\n  platform: wordpress\ntarget:\n  url: %s\n  platform: astro\n  staging_url: https://staging.example.com\nanalytics:\n  expected_ids:\n    - G-TEST12345\nrollback:\n  source_preserved: true\n  backup_verified: true\n  backup_path: backup\n  backup_restore_tested: true\n  dns_recorded: true\n  owner_named: true\n  owner: Fixture Owner\n  window: 48h\n  dns_ttl_lowered: true\n" % (src, tgt))
        rc, out, err = run("find_old_domain_refs.py", "--config", "migration.yaml", "--dir", repo, "--pages", "target-url-inventory.csv", "--out", "old-domain-refs.csv", cwd=cwd)
        od = csv_rows(os.path.join(work, "old-domain-refs.csv"))
        check("find_old_domain_refs: finds the old-host link in the repo", any("Footer.astro" in r["where"] for r in od), str(od))
        check("find_old_domain_refs: finds the staging host", any("staging" in r["match"] for r in od), str(od))
        check("find_old_domain_refs: skips node_modules", not any("node_modules" in r["where"] for r in od), str(od))
        check("find_old_domain_refs: finds refs in rendered target pages", any(r["where"].startswith("http") for r in od), str(od))
        check("find_old_domain_refs: exit 2", rc == 2, out + err)
        rc, out, err = run("tracking_check.py", "--inventory", "target-url-inventory.csv", "--expect", "G-TEST12345", "--json", "tracking.json", "--delay", "0", cwd=cwd)
        tj = json.load(open(os.path.join(work, "tracking.json")))
        check("tracking_check: the ID is missing on one page → not on every page", tj["expected"]["G-TEST12345"] < tj["checked"] and rc >= 1, json.dumps(tj))
        open(os.path.join(work, "critical-pages.csv"), "w").write("url,priority,reason,expect_text,expect_form\n/,P0,homepage,,\n/contact,P0,lead form,,yes\n/blog/post-one,P1,top article,,\n/services,P0,revenue page,,\n")
        rc, out, err = run("critical_pages.py", "critical-pages.csv", "--origin", tgt, "--map", "url-map.csv", "--source-origin", src, "--out", "critical-pages-results.csv", "--delay", "0", cwd=cwd)
        cp = {r["source_url"]: r for r in csv_rows(os.path.join(work, "critical-pages-results.csv"))}
        check("critical_pages: homepage PASS", cp["/"]["result"] == "PASS", str(cp["/"]))
        check("critical_pages: lost form fails", cp["/contact"]["result"] == "FAIL" and "form" in cp["/contact"]["problems"], str(cp["/contact"]))
        check("critical_pages: moved post checked at the mapped target and the source redirect verified", cp["/blog/post-one"]["target_url"].endswith("/posts/post-one") and "301" in cp["/blog/post-one"]["redirect"], str(cp["/blog/post-one"]))
        check("critical_pages: missing /services fails with status 404", cp["/services"]["result"] == "FAIL" and "404" in cp["/services"]["problems"], str(cp["/services"]))

        # ---- baselines, dns, performance, rollback, plan, audit
        rc, out, err = run("seo_baseline.py", "source-url-inventory.csv", "--out", "seo-baseline", cwd=cwd)
        check("seo_baseline: writes csv/json/report", rc == 0 and os.path.exists(os.path.join(work, "seo-baseline.csv")) and os.path.exists(os.path.join(work, "seo-baseline-report.md")), out + err)
        rc, out, err = run("content_inventory.py", "source-url-inventory.csv", "--out", "content-inventory.csv", "--rule", "/blog/=post", cwd=cwd)
        ci = {r["url"].replace(src, ""): r for r in csv_rows(os.path.join(work, "content-inventory.csv"))}
        check("content_inventory: classifies by rule", ci["/blog/post-one"]["content_type"] == "post", str(ci.get("/blog/post-one")))
        check("content_inventory: /gone is an ORPHAN? no — linked from home; /services is linked too", "ORPHAN" not in ci["/about"].get("flags", ""), str(ci["/about"]))
        dig = os.path.join(work, "dig.txt"); open(dig, "w").write("example.com. 300 IN A 203.0.113.10\nexample.com. 3600 IN MX 10 mail.example.com.\nexample.com. 3600 IN TXT \"v=spf1 include:_spf.example.com ~all\"\nwww.example.com. 300 IN CNAME example.com.\n_dmarc.example.com. 3600 IN TXT \"v=DMARC1; p=none\"\n")
        rc, out, err = run("dns_inventory.py", "example.com", "--dig", dig, "--out", "dns-before.csv", cwd=cwd)
        dn = csv_rows(os.path.join(work, "dns-before.csv"))
        check("dns_inventory: parses dig output with purposes", rc == 0 and any(r["type"] == "MX" for r in dn) and any("mail" in r.get("purpose", "").lower() for r in dn), out + err + str(dn))
        dig2 = os.path.join(work, "dig2.txt"); open(dig2, "w").write("example.com. 300 IN A 198.51.100.7\nwww.example.com. 300 IN CNAME new.example.net.\n")
        rc, out, err = run("dns_inventory.py", "example.com", "--dig", dig2, "--out", "dns-after.csv", cwd=cwd)
        rc, out, err = run("dns_inventory.py", "--compare", "dns-before.csv", "dns-after.csv", cwd=cwd)
        check("dns_inventory: --compare exits 2 when MX/SPF/DMARC vanish", rc == 2 and "MX" in out, out + err)
        rc, out, err = run("performance_baseline.py", "--capture", src, "--paths", "/", "/about", "--out", "perf-source.json", cwd=cwd)
        rc2, out2, err2 = run("performance_baseline.py", "--capture", tgt, "--paths", "/", "/about", "--out", "perf-target.json", cwd=cwd)
        rc3, out3, err3 = run("performance_baseline.py", "--compare", "perf-source.json", "perf-target.json", "--tolerance", "10000", cwd=cwd)
        check("performance_baseline: capture + compare run (exit 0/1)", rc == 0 and rc2 == 0 and rc3 < 2, out + err + out2 + err2 + out3 + err3)
        os.makedirs(os.path.join(work, "backup")); open(os.path.join(work, "backup", "db.sql"), "w").write("-- fixture\n")
        rc, out, err = run("rollback_readiness.py", "--config", "migration.yaml", "--dir", work, "--json", cwd=cwd)
        j = json.loads(out[out.index("{"):])
        check("rollback_readiness: ready when source answers, backup exists, DNS recorded", rc < 2, out + err)
        os.rename(os.path.join(work, "dns-before.csv"), os.path.join(work, "dns-before.bak"))
        rc, out, err = run("rollback_readiness.py", "--config", "migration.yaml", "--dir", work, cwd=cwd)
        check("rollback_readiness: missing dns-before.csv is a FAIL", rc == 2 and "dns-before.csv missing" in out, out + err)
        os.rename(os.path.join(work, "dns-before.bak"), os.path.join(work, "dns-before.csv"))
        rc, out, err = run("migration_plan.py", "--config", "migration.yaml", "--dir", work, cwd=cwd)
        plan = open(os.path.join(work, "migration-plan.md")).read()
        check("migration_plan: writes a plan with the type and the three classes", rc == 0 and "WordPress → Astro" in plan and "AUTOMATABLE" in plan and "MANUAL" in plan and os.path.exists(os.path.join(work, "migration-risk-register.csv")), out + err)
        rc, out, err = run("migration_audit.py", "--config", "migration.yaml", "--dir", work, "--report", cwd=cwd)
        j = json.load(open(os.path.join(work, "migration-audit.json"))); md = open(os.path.join(work, "migration-audit.md")).read()
        check("migration_audit: NO-GO with a failing critical page", rc == 2 and j["recommendation"] == "NO-GO", out + err)
        check("migration_audit: blockers name the critical page and the canonical", any("critical page" in b for b in j["blockers"]) and any("canonical" in b for b in j["blockers"]), str(j["blockers"]))
        check("migration_audit: scorecard has the six percentages and an overall", all(isinstance(j["scores"].get(k), int) for k in ("url_coverage", "redirect_integrity", "metadata_preservation", "canonical_integrity", "internal_links", "media_integrity")) and "Overall Migration Health:" in md, json.dumps(j["scores"]))
        check("migration_audit: report written", os.path.exists(os.path.join(work, "migration-report.md")))
        # audit --run end-to-end against the fixtures (re-crawls the target)
        for f in ("target-url-inventory.csv", "coverage-report.csv", "internal-links.json", "media-validation.csv", "critical-pages-results.csv", "tracking.json"):
            os.remove(os.path.join(work, f))
        rc, out, err = run("migration_audit.py", "--config", "migration.yaml", "--dir", work, "--run", cwd=cwd, timeout=300)
        j = json.load(open(os.path.join(work, "migration-audit.json")))
        check("migration_audit --run: regenerates every file and still says NO-GO", rc == 2 and j["recommendation"] == "NO-GO" and all(os.path.exists(os.path.join(work, f)) for f in ("target-url-inventory.csv", "coverage-report.csv", "internal-links.json", "critical-pages-results.csv")), out + err)
        rc, out, err = run("staging_validation.py", tgt, "--dir", work, "--production-domain", "127.0.0.1:%d" % tport, "--max", "50", cwd=cwd, timeout=300)
        sv = open(os.path.join(work, "staging-validation.md")).read()
        check("staging_validation: runs the bundle and writes the report", os.path.exists(os.path.join(work, "staging-url-inventory.csv")) and "STAGING VALIDATION" in sv and rc == 2, out + err)

        # ---- content utilities
        html_dir = os.path.join(tmp, "html"); os.makedirs(html_dir)
        open(os.path.join(html_dir, "post.html"), "w").write("<html><head><title>Hello &amp; World</title><meta name='description' content='d'><link rel='canonical' href='https://old.example.com/blog/hello'></head><body><nav>skip</nav><article><h1>Hello</h1><p>First <strong>bold</strong> and <a href='/x'>link</a>.</p><h2>Sub</h2><ul><li>one</li><li>two</li></ul><pre><code>x = 1</code></pre><img src='/wp-content/uploads/2024/01/a.jpg' alt='A'><iframe src='https://www.youtube.com/embed/abc'></iframe><table><tr><td>t</td></tr></table>[gallery ids='1,2']</article></body></html>")
        rc, out, err = run("html_to_markdown.py", html_dir, "--out", os.path.join(tmp, "md"), "--select", "article", cwd=cwd)
        mdt = open(os.path.join(tmp, "md", "post.md")).read()
        check("html_to_markdown: converts headings, lists, links, code, images", rc in (0, 1) and "# Hello" in mdt and "- one" in mdt and "[link](/x)" in mdt and "```" in mdt and "![A](/wp-content/uploads/2024/01/a.jpg)" in mdt and "**bold**" in mdt, mdt + err)
        check("html_to_markdown: frontmatter carries title/canonical and review flag for the iframe/table", mdt.startswith("---") and "Hello & World" in mdt and "review: true" in mdt and "canonical" in mdt, mdt)
        check("html_to_markdown: nav stripped by --select", "skip" not in mdt, mdt)
        rc, out, err = run("normalize_content.py", os.path.join(tmp, "md"), "--image-prefix", "/images/", "--report", os.path.join(tmp, "norm.csv"), cwd=cwd)
        mdt2 = open(os.path.join(tmp, "md", "post.md")).read()
        check("normalize_content: shifts H1 to H2, comments the shortcode, rewrites uploads path", "## Hello" in mdt2 and "# Hello\n" not in mdt2.replace("## Hello", "") and "shortcode removed" in mdt2 and "/images/a.jpg" in mdt2, mdt2 + err)
        rc, out, err = run("validate_frontmatter.py", os.path.join(tmp, "md"), "--require", "title", "--require", "slug", cwd=cwd)
        check("validate_frontmatter: reports the missing required key", rc == 2 and "slug" in out, out + err)
        rc, out, err = run("slug_mapper.py", "source-url-inventory.csv", "--rule", r"^/blog/(.*)=/posts/\1", "--out", os.path.join(tmp, "slugs.csv"), cwd=cwd)
        check("slug_mapper: runs and writes a map", rc in (0, 1, 2) and os.path.exists(os.path.join(tmp, "slugs.csv")), out + err)
        rc, out, err = run("merge_inventories.py", "source-url-inventory.csv", "target-url-inventory.csv", "--csv", "--out", "merged.csv", cwd=cwd)
        check("merge_inventories: merges two inventories", rc == 0 and len(csv_rows(os.path.join(work, "merged.csv"))) >= len(csv_rows(os.path.join(work, "source-url-inventory.csv"))), out + err)
        # help for every script
        for f in sorted(os.listdir(SCRIPTS)):
            if f.endswith(".py") and not f.startswith("_"):
                rc, out, err = run(f, "--help")
                check("%s --help" % f, rc == 0 and "usage" in out.lower(), err)
    finally:
        ssrv.shutdown(); tsrv.shutdown(); shutil.rmtree(tmp, ignore_errors=True)
    print("\n%d failure(s)" % failures)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
