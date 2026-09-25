#!/usr/bin/env python3
"""Test downloads/claude-code-maintenance-kit/weekly_check.py against a local
fixture site: a homepage with navigation, a contact page with a form, and —
in the "broken" state — a navigation link to a page that 404s and a contact
page whose form is missing. The check must fail on both, and pass once the
fixture is repaired. Also: absolute-URL config validation, the link budget,
and that http hosts skip the certificate check rather than failing it.
"""
import http.server
import io
import json
import os
import socketserver
import subprocess
import sys
import tempfile
import threading

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "downloads", "claude-code-maintenance-kit", "weekly_check.py")
STATE = {"broken": True}


class Site(http.server.BaseHTTPRequestHandler):
    def _page(self, body):
        self.send_response(200); self.send_header("Content-Type", "text/html"); self.end_headers()
        if self.command == "GET":
            self.wfile.write(body.encode())
    def do_HEAD(self): self.do_GET()
    def do_GET(self):
        p = self.path
        if p == "/":
            nav = '<a href="/services">Services</a> <a href="/contact">Contact</a>' + (' <a href="/team">Team</a>' if STATE["broken"] else "")
            return self._page("<title>Harbourline Physio</title><nav>%s</nav>" % nav)
        if p == "/services":
            return self._page("<title>Services</title>")
        if p == "/contact":
            return self._page("<title>Contact</title>" + ("" if STATE["broken"] else "<form action='/submit'><input name='email'></form>"))
        self.send_response(404); self.end_headers()
    def log_message(self, *a): pass


def run(cfg, *extra):
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
        json.dump(cfg, fh); path = fh.name
    p = subprocess.run([sys.executable, SCRIPT, path, *extra], capture_output=True, text=True)
    os.unlink(path)
    return p


def main():
    failures = 0
    def check(name, ok, detail=""):
        nonlocal failures
        if not ok: failures += 1
        print("  %s  %s%s" % ("PASS" if ok else "FAIL", name, ("  -> " + detail[:240]) if detail and not ok else ""))

    srv = socketserver.TCPServer(("127.0.0.1", 0), Site)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = "http://127.0.0.1:%d" % srv.server_address[1]
    cfg = {"pages": [{"url": base + "/", "expect": "Harbourline"}, {"url": base + "/contact", "expect": "<form"}], "timeout": 2}
    try:
        p = run(cfg)
        check("broken fixture: exit 1", p.returncode == 1, p.stdout[-300:] + p.stderr)
        check("broken fixture: the 404 navigation link is reported as FAIL", "| link resolves | %s/team | FAIL | 404" % base in p.stdout, p.stdout)
        check("broken fixture: the missing form is reported as FAIL", "| page contains '<form' | %s/contact | FAIL" % base in p.stdout, p.stdout)
        check("http host: certificate check is skipped, not failed", "| certificate | 127.0.0.1 | PASS | skipped (http)" in p.stdout, p.stdout)
        check("report lists what the script does not check", "Forms deliver" in p.stdout and "Backups restore" in p.stdout)
        STATE["broken"] = False
        with tempfile.TemporaryDirectory() as d:
            rp = os.path.join(d, "r.md")
            p = run(cfg, "--report", rp)
            check("repaired fixture: exit 0, every check PASS", p.returncode == 0 and "failed: 0" in p.stdout, p.stdout[-300:])
            check("--report writes the Markdown report", os.path.exists(rp) and "# Weekly check" in io.open(rp).read())
        p = run({"pages": [{"url": "/relative"}]})
        check("relative URL in config is refused with exit 2", p.returncode == 2 and "absolute" in p.stderr, p.stderr)
        p = run({"pages": "nope"})
        check("bad config shape is refused with exit 2", p.returncode == 2)
        p = run({"pages": [{"url": base + "/"}], "max_links": 1, "timeout": 2})
        check("link budget bounds the crawl and says so", "link budget of 1 reached" in p.stdout, p.stdout)
    finally:
        srv.shutdown()
    print("\n%d failure(s)" % failures)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
