#!/usr/bin/env python3
"""Test downloads/website-migration-seo-kit/check_redirects.py against two
local fixture servers.

"Old" (port 8471) redirects; "new" (port 8472) serves pages. The map has a
correct move, a redirect that dumps on the homepage (right status, wrong
place), a two-hop chain, a loop, a page that should 200 but 404s, a wrong
identity, a REMOVE that should 410, and a source that never answers — so
every failure mode the article describes is shown to be detected, and the
correct rows are shown to pass. A malformed row is tested separately: it
must stop the run with exit 2 before any request is made.
"""
import http.server
import io
import os
import socketserver
import subprocess
import sys
import tempfile
import threading
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "downloads", "website-migration-seo-kit", "check_redirects.py")
# Ephemeral ports: the fixtures bind to port 0 and the map is built from
# whatever the OS handed out, so a previous run's TIME_WAIT sockets cannot
# make this test fail.
OLD = NEW = 0
NEW_BASE = ""
REDIRECTS = {}

PAGES = {
    "/": "<title>Harbourline Physio — Home</title><h1>Welcome</h1>",
    "/services/physiotherapy": "<title>Physiotherapy in Harbourline | Harbourline Physio</title>",
    "/about": "<title>About Harbourline Physio</title>",
    "/services/": "<title>Services</title>",
}
def build_redirects():
    REDIRECTS.update({
    "/physio": (301, NEW_BASE + "/services/physiotherapy"),   # correct
    "/team": (301, NEW_BASE + "/"),                             # homepage dump
    "/old-services": (301, "http://127.0.0.1:%d/services-2" % OLD),  # chain hop 1
    "/services-2": (301, NEW_BASE + "/services/"),             # chain hop 2
    "/loop-a": (301, "http://127.0.0.1:%d/loop-b" % OLD),
    "/loop-b": (301, "http://127.0.0.1:%d/loop-a" % OLD),
    "/temp": (302, NEW_BASE + "/about"),                        # wrong status
    "/gone": (410, None),
    "/news": (301, NEW_BASE + "/about"),                        # lands, wrong identity
    })


class Old(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/slow":
            time.sleep(3)
        r = REDIRECTS.get(self.path)
        if not r:
            self.send_response(404); self.end_headers(); return
        self.send_response(r[0])
        if r[1]:
            self.send_header("Location", r[1])
        self.end_headers()
    def log_message(self, *a): pass


class New(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        body = PAGES.get(self.path)
        if body is None:
            self.send_response(404); self.end_headers(); return
        self.send_response(200); self.send_header("Content-Type", "text/html"); self.end_headers()
        self.wfile.write(body.encode())
    def log_message(self, *a): pass


def serve(handler):
    s = socketserver.TCPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=s.serve_forever, daemon=True).start()
    return s


def run(csv_text, *extra):
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8") as fh:
        fh.write(csv_text); path = fh.name
    p = subprocess.run([sys.executable, SCRIPT, path, "--timeout", "1", "--max-hops", "3", *extra], capture_output=True, text=True)
    os.unlink(path)
    return p


def main():
    failures = 0
    def check(name, ok, detail=""):
        nonlocal failures
        if not ok: failures += 1
        print("  %s  %s%s" % ("PASS" if ok else "FAIL", name, ("  -> " + detail[:200]) if detail and not ok else ""))

    global OLD, NEW, NEW_BASE
    old = serve(Old); new = serve(New)
    OLD, NEW = old.server_address[1], new.server_address[1]
    NEW_BASE = "http://127.0.0.1:%d" % NEW
    build_redirects()
    try:
        O = "http://127.0.0.1:%d" % OLD
        rows = ["source_url,target_url,expected_status,identity,notes",
                "%s/physio,%s/services/physiotherapy,301,Physiotherapy,correct move" % (O, NEW_BASE),
                "%s/team,%s/team,301,Team,homepage dump" % (O, NEW_BASE),
                "%s/old-services,%s/services/,301,Services,chain" % (O, NEW_BASE),
                "%s/loop-a,%s/about,301,,loop" % (O, NEW_BASE),
                "%s/temp,%s/about,301,About,302 instead of 301" % (O, NEW_BASE),
                "%s/gone,,410,,removed" % O,
                "%s/news,%s/about,301,News,lands but wrong identity" % (O, NEW_BASE),
                "%s/about,,200,About,page that must stay" % NEW_BASE,
                "%s/missing,,200,,should 200 but 404s" % NEW_BASE,
                "%s/slow,%s/about,301,,times out" % (O, NEW_BASE)]
        p = run("\n".join(rows) + "\n")
        out = p.stdout
        check("exit status 1 when any row fails", p.returncode == 1, str(p.returncode) + p.stderr)
        def row(n): return [l for l in out.splitlines() if l.startswith("| %d |" % n)]
        check("correct 301 to the mapped page with matching identity passes", row(2) and "PASS" in row(2)[0], out)
        check("homepage dump fails on destination even though status is 301", row(3) and "FAIL" in row(3)[0] and "landed on" in row(3)[0], out)
        check("two-hop chain fails on hop count", row(4) and "FAIL" in row(4)[0] and "2 hops" in row(4)[0], out)
        check("loop is detected and reported", row(5) and "FAIL" in row(5)[0] and "loop" in row(5)[0], out)
        check("302 where 301 expected fails", row(6) and "FAIL" in row(6)[0] and "returned 302" in row(6)[0], out)
        check("410 for a removed page passes", row(7) and "PASS" in row(7)[0], out)
        check("lands on the right URL but wrong page identity fails", row(8) and "FAIL" in row(8)[0] and "identity" in row(8)[0], out)
        check("page that must stay and 200s passes", row(9) and "PASS" in row(9)[0], out)
        check("page that should 200 but 404s fails", row(10) and "FAIL" in row(10)[0] and "404" in row(10)[0], out)
        check("a source that never answers fails with a timeout, not a hang", row(11) and "FAIL" in row(11)[0] and "request failed" in row(11)[0], out)
        check("summary line counts rows, passes and failures", "Rows checked: 10 · passed: 3 · failed: 7" in out, out.splitlines()[2] if len(out.splitlines()) > 2 else out)

        # malformed row: stops before any request
        p = run("source_url,target_url,expected_status\n/relative,%s/about,301\n" % NEW_BASE)
        check("malformed row (relative source) stops the run with exit 2", p.returncode == 2 and "STOP" in p.stderr, p.stderr)
        p = run("source_url,target_url,expected_status\n%s/physio,%s/x,999\n" % (O, NEW_BASE))
        check("unknown expected_status stops the run with exit 2", p.returncode == 2 and "expected_status" in p.stderr, p.stderr)
        p = run("foo,bar\n1,2\n")
        check("missing columns are refused with exit 2", p.returncode == 2 and "CSV needs columns" in p.stderr, p.stderr)
        # limit
        many = "source_url,target_url,expected_status\n" + "".join("%s/physio,%s/services/physiotherapy,301\n" % (O, NEW_BASE) for _ in range(5))
        p = run(many, "--limit", "2")
        check("--limit bounds the run and says so", p.returncode == 0 and "checking the first 2" in p.stdout and "Rows checked: 2" in p.stdout, p.stdout[:200])
        # host rewrite: a map written for a production host tested against local
        p = run("source_url,target_url,expected_status,identity\nhttp://old.example/physio,http://new.example/services/physiotherapy,301,Physiotherapy\n",
                "--host-rewrite", "old.example=127.0.0.1:%d" % OLD, "--host-rewrite", "new.example=127.0.0.1:%d" % NEW)
        check("--host-rewrite requests the local copies and the production-host map row passes", p.returncode == 0 and "| 2 |" in p.stdout and "PASS" in p.stdout, p.stdout[:300] + p.stderr[:200])
        # report file
        with tempfile.TemporaryDirectory() as d:
            rp = os.path.join(d, "r.md")
            p = run("\n".join(rows[:2]) + "\n", "--report", rp)
            check("--report writes the Markdown report", p.returncode == 0 and os.path.exists(rp) and "# Redirect check" in io.open(rp).read())
    finally:
        old.shutdown(); new.shutdown()
    print("\n%d failure(s)" % failures)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
