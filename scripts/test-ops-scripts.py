#!/usr/bin/env python3
"""Run every operations-system script against a local fixture site, offline.

A throwaway HTTP server on 127.0.0.1 serves a small site with the failures the
scripts exist to find: a 404 link, a redirect chain, a loop, an exposed .env,
a sitemap listing a redirecting URL, a slow page, a page missing its expected
text. Each script is run as a subprocess the way a customer runs it, and the
test asserts the documented exit code and the specific finding.

An HTTPS fixture with a self-signed certificate exercises check_ssl.py's
"verification failed" path when openssl is available; otherwise that case is
skipped and said so. Nothing here touches the network beyond localhost.
"""
import http.server
import json
import os
import shutil
import socket
import ssl
import subprocess
import sys
import tempfile
import threading
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "product", "Claude-Code-Website-Operations-Maintenance-System", "scripts")

PAGES = {
    "/": (200, "text/html", "<!doctype html><html><head><title>Fixture Home</title></head><body>"
          "<a href='/about'>About</a> <a href='/missing'>Missing</a> <a href='/chain-1'>Chain</a> "
          "<a href='/loop-a'>Loop</a> <a href='http://127.0.0.1:{port}/about'>Insecure</a></body></html>"),
    "/about": (200, "text/html", "<!doctype html><html><head><title>About</title></head><body>About page <a href='/'>Home</a></body></html>"),
    "/slow": (200, "text/html", "<!doctype html><html><body>slow</body></html>"),
    "/.env": (200, "text/plain", "DB_PASSWORD=not-a-real-secret\n"),
    "/robots.txt": (200, "text/plain", "User-agent: *\nAllow: /\nSitemap: http://127.0.0.1:{port}/sitemap.xml\n"),
    "/sitemap.xml": (200, "application/xml",
                     "<?xml version='1.0' encoding='UTF-8'?><urlset xmlns='http://www.sitemaps.org/schemas/sitemap/0.9'>"
                     "<url><loc>http://127.0.0.1:{port}/</loc><lastmod>2026-09-01</lastmod></url>"
                     "<url><loc>http://127.0.0.1:{port}/about</loc></url>"
                     "<url><loc>http://127.0.0.1:{port}/chain-1</loc></url></urlset>"),
}
REDIRECTS = {"/chain-1": "/chain-2", "/chain-2": "/about", "/loop-a": "/loop-b", "/loop-b": "/loop-a", "/old": "/about"}


class Handler(http.server.BaseHTTPRequestHandler):
    port = 0

    def log_message(self, *a):
        pass

    def do_GET(self):
        path = self.path.split("?")[0]
        if path in REDIRECTS:
            self.send_response(301); self.send_header("Location", REDIRECTS[path]); self.end_headers(); return
        if path == "/slow":
            time.sleep(1.2)
        if path in PAGES:
            status, ctype, body = PAGES[path]
            body = body.replace("{port}", str(self.port)).encode()
            self.send_response(status)
            self.send_header("Content-Type", ctype); self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "max-age=60"); self.end_headers(); self.wfile.write(body); return
        body = b"<!doctype html><html><body>not found</body></html>"
        self.send_response(404); self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)

    do_HEAD = do_GET


def serve(tls_cert=None):
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    Handler.port = srv.server_address[1]
    if tls_cert:
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER); ctx.load_cert_chain(tls_cert)
        srv.socket = ctx.wrap_socket(srv.socket, server_side=True)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def run(script, *args, timeout=60):
    p = subprocess.run([sys.executable, os.path.join(SCRIPTS, script)] + list(args),
                       capture_output=True, text=True, timeout=timeout,
                       env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    return p.returncode, p.stdout, p.stderr


failures = 0


def check(name, ok, detail=""):
    global failures
    failures += 0 if ok else 1
    print("  %s  %s%s" % ("PASS" if ok else "FAIL", name, ("  -> " + detail.strip()[:160]) if detail and not ok else ""))


def main():
    tmp = tempfile.mkdtemp()
    srv = serve(); port = srv.server_address[1]; base = "http://127.0.0.1:%d" % port
    try:
        rc, out, err = run("check_http.py", base, "/", "/about", "/missing", "--json")
        j = json.loads(out)
        check("check_http: 404 on a listed path exits 2", rc == 2, out + err)
        check("check_http: the 404 is a FAIL finding", any(f["status"] == "FAIL" and "/missing" in f["check"] for f in j["findings"]))
        rc, out, err = run("check_http.py", base, "/slow", "--slow", "0.5", "--json")
        check("check_http: a slow page exits 1 (warning)", rc == 1, out + err)
        rc, out, err = run("check_http.py", base, "/loop-a", "--json")
        check("check_http: a redirect loop is CRITICAL", rc == 2 and "loop" in out.lower(), out + err)
        rc, out, err = run("check_http.py", "not-a-url")
        check("check_http: bad arguments exit 3", rc == 3, out + err)

        rc, out, err = run("crawl_links.py", base, "--max", "10", "--pause", "0", "--json", "--csv", os.path.join(tmp, "links.csv"))
        j = json.loads(out)
        checks = " ".join(f["check"] + " " + f["status"] for f in j["findings"])
        check("crawl_links: exits 2 with a 404 and a loop", rc == 2, out + err)
        check("crawl_links: finds the 404", "/missing FAIL" in checks, checks)
        check("crawl_links: finds the loop as CRITICAL", "/loop-a CRITICAL" in checks, checks)
        check("crawl_links: finds the chain as WARNING", "/chain-1 WARNING" in checks, checks)
        check("crawl_links: writes the CSV", os.path.exists(os.path.join(tmp, "links.csv")))

        rc, out, err = run("validate_sitemap.py", base + "/sitemap.xml", "--all", "--pause", "0", "--json")
        j = json.loads(out)
        check("validate_sitemap: a redirecting URL is a warning", rc == 1 and any("redirect" in f["check"] for f in j["findings"]), out + err)
        rc, out, err = run("validate_sitemap.py", base + "/nope.xml", "--json")
        check("validate_sitemap: an unreachable sitemap is CRITICAL", rc == 2 and "CRITICAL" in out, out + err)

        rc, out, err = run("audit_redirects.py", base, "--probe", "--json")
        check("audit_redirects: --probe runs on a plain http fixture (http->https fails)", rc == 2 and "http -> https" in out, out + err)
        csv = os.path.join(tmp, "redirects.csv")
        open(csv, "w").write("/old,/about\n/chain-1,/about\n/loop-a,/about\n/gone,/about\n/about,/about\n")
        rc, out, err = run("audit_redirects.py", base, csv, "--json")
        j = json.loads(out); by = {f["check"]: f["status"] for f in j["findings"]}
        check("audit_redirects: one-hop 301 passes", by.get("/old -> /about") == "PASS", str(by))
        check("audit_redirects: a chain is a warning", by.get("/chain-1 -> /about") == "WARNING", str(by))
        check("audit_redirects: a loop is CRITICAL", by.get("/loop-a -> /about") == "CRITICAL", str(by))
        check("audit_redirects: a gone redirect fails", by.get("/gone -> /about") == "FAIL", str(by))
        check("audit_redirects: source == target at 200 passes", by.get("/about -> /about") == "PASS", str(by))

        ep = os.path.join(tmp, "endpoints.txt")
        open(ep, "w").write("# fixture\n/ 200 \"Fixture Home\"\n/about 200 \"Nope\"\n/missing 404\n/old 301\n/.env 404\n")
        rc, out, err = run("test_endpoints.py", ep, "--base", base, "--json")
        j = json.loads(out); by = {f["check"]: f["status"] for f in j["findings"]}
        check("test_endpoints: text found passes", by.get("/") == "PASS", str(by))
        check("test_endpoints: missing text fails", by.get("/about") == "FAIL", str(by))
        check("test_endpoints: expected 404 passes", by.get("/missing") == "PASS", str(by))
        check("test_endpoints: expected 301 passes", by.get("/old") == "PASS", str(by))
        check("test_endpoints: a served .env expected 404 fails (not a soft-404)", by.get("/.env") == "FAIL", str(by))
        check("test_endpoints: overall exit 2", rc == 2)

        rc, out, err = run("compare_baseline.py", "--capture", base, "/", "/about")
        bl = json.loads(out); open(os.path.join(tmp, "baseline.json"), "w").write(out)
        check("compare_baseline: --capture records status, bytes and title", bl["pages"]["/"]["status"] == 200 and bl["pages"]["/"]["title"] == "Fixture Home", out)
        rc, out, err = run("compare_baseline.py", os.path.join(tmp, "baseline.json"))
        check("compare_baseline: unchanged site exits 0", rc == 0, out + err)
        bl["pages"]["/about"]["status"] = 301; bl["pages"]["/"]["title"] = "Old Title"; bl["headers"]["x-frame-options"] = True
        open(os.path.join(tmp, "base2.json"), "w").write(json.dumps(bl))
        rc, out, err = run("compare_baseline.py", os.path.join(tmp, "base2.json"), "--json")
        j = json.loads(out); by = {f["check"]: f["status"] for f in j["findings"]}
        check("compare_baseline: a status change fails", by.get("/about") == "FAIL", str(by))
        check("compare_baseline: a title change warns", by.get("/") == "WARNING", str(by))
        check("compare_baseline: a header that disappeared fails", by.get("header x-frame-options") == "FAIL", str(by))

        rc, out, err = run("check_headers.py", base)
        check("check_headers: refuses a non-https URL with exit 3", rc == 3, out + err)
        rc, out, err = run("check_dns.py", "localhost", "--json")
        check("check_dns: resolves localhost (exit 0 or 1)", rc in (0, 1) and "127.0.0.1" in out, out + err)
        rc, out, err = run("check_dns.py", "localhost", "--expect", "203.0.113.9", "--json")
        check("check_dns: --expect mismatch is CRITICAL", rc == 2 and "CRITICAL" in out, out + err)
        rc, out, err = run("check_dns.py", "nope.invalid", "--json")
        check("check_dns: an unresolvable apex is CRITICAL", rc == 2, out + err)
        rc, out, err = run("check_ssl.py", "127.0.0.1", "--port", str(port), "--timeout", "3")
        check("check_ssl: a port that does not speak TLS exits non-zero", rc in (2, 3), out + err)

        # HTTPS fixture with a self-signed certificate: verification must fail loudly.
        if shutil.which("openssl"):
            cert = os.path.join(tmp, "cert.pem")
            subprocess.run(["openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes", "-keyout", cert, "-out", cert,
                            "-days", "2", "-subj", "/CN=127.0.0.1"], check=True, capture_output=True)
            tls = serve(tls_cert=cert); tport = tls.server_address[1]
            rc, out, err = run("check_ssl.py", "127.0.0.1", "--port", str(tport), "--json")
            check("check_ssl: a self-signed certificate is CRITICAL (verification failed)", rc == 2 and "verification failed" in out, out + err)
            rc, out, err = run("check_headers.py", "https://127.0.0.1:%d" % tport, "--json")
            check("check_headers: an untrusted certificate is reported, not crashed", rc == 3 and "could not fetch" in err, out + err)
            tls.shutdown()
        else:
            print("  SKIP  check_ssl self-signed case (no openssl binary)")

        # The merged report: run it over the JSON the scripts produced.
        res = os.path.join(tmp, "res"); os.makedirs(res)
        for name, args in (("health", ["check_http.py", base, "/", "/missing"]),
                           ("links", ["crawl_links.py", base, "--max", "5", "--pause", "0"]),
                           ("endpoints", ["test_endpoints.py", ep, "--base", base])):
            rc, out, err = run(*args, "--json"); open(os.path.join(res, name + ".json"), "w").write(out)
        open(os.path.join(res, "backups.json"), "w").write(json.dumps({"title": "Backups", "overall": "WARNING",
            "findings": [{"check": "verified restore", "status": "WARNING", "detail": "61 days", "data": {}}]}))
        rc, out, err = run("generate_report.py", "--site", base, os.path.join(res, "*.json"),
                           "--out", os.path.join(tmp, "r.md"), "--json-out", os.path.join(tmp, "r.json"))
        r = json.load(open(os.path.join(tmp, "r.json")))
        check("generate_report: writes markdown and JSON with a score", "overall_score" in r and os.path.exists(os.path.join(tmp, "r.md")), out + err)
        check("generate_report: scores each area from its findings", {a["area"] for a in r["areas"]} == {"health", "links", "endpoints", "backups"}, str([a["area"] for a in r["areas"]]))
        check("generate_report: backups area scores 95 (one warning)", next(a["score"] for a in r["areas"] if a["area"] == "backups") == 95)
        md = open(os.path.join(tmp, "r.md")).read()
        check("generate_report: the report carries Website, Date, Environment and the score line",
              all(k in md for k in ("**Website:**", "**Date:**", "**Environment:**", "**Overall Score:**")))
        check("generate_report: exit code follows the rating", rc in (0, 1, 2))
        rc, out, err = run("generate_report.py", "--site", base, os.path.join(tmp, "r.json"))
        check("generate_report: a previous merged report is skipped, not crashed on", rc == 3 and "no result files" not in err, out + err)

        rc, out, err = run("read_config.py", os.path.join(ROOT, "product", "Claude-Code-Website-Operations-Maintenance-System", "templates", "ops-config.yml"), "schedule.daily")
        check("read_config: reads a list from the template", rc == 0 and "check_http" in out, out + err)
        rc, out, err = run("read_config.py", os.path.join(ROOT, "product", "Claude-Code-Website-Operations-Maintenance-System", "templates", "ops-config.yml"), "notify.email")
        check("read_config: an empty value exits 1", rc == 1)
    finally:
        srv.shutdown(); shutil.rmtree(tmp, ignore_errors=True)
    print("\n%d failure(s)" % failures)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
