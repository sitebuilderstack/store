#!/usr/bin/env python3
"""Run the Shopify toolkit's scripts against a mock Admin GraphQL API, offline.

A local HTTP server impersonates https://<store>/admin/api/<version>/graphql.json
well enough for every script: it answers by inspecting the operation, serves
a fixture catalogue with the defects the audits exist to find, records every
mutation, throttles the first two requests (HTTP 429, then a THROTTLED
GraphQL error) to prove the client retries, and serves a bulk-operation
JSONL file. The client is pointed at it with SHOPIFY_API_URL, which exists
for exactly this.

Asserts documented exit codes, that dry runs write nothing, that writes are
previewed and read back, that validation rejects what it should, and that
no output line ever contains the token.
"""
import http.server
import json
import os
import re
import subprocess
import sys
import tempfile
import threading

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUNDLE = os.path.join(ROOT, "product", "Claude-Code-Shopify-Automation-Admin-API-Toolkit")
SCRIPTS = os.path.join(BUNDLE, "scripts")
TOKEN = "shpat_" + "f" * 32
DOMAIN = "fixture-store.myshopify.com"


def gid(t, n):
    return "gid://shopify/%s/%d" % (t, n)


def product(n, **kw):
    p = {"id": gid("Product", n), "handle": "product-%d" % n, "title": "Product %d" % n, "status": "ACTIVE", "vendor": "Northwind",
         "productType": "Jackets", "tags": ["a"], "createdAt": "2026-01-01T00:00:00Z", "updatedAt": "2026-09-01T00:00:00Z", "publishedAt": "2026-01-02T00:00:00Z",
         "descriptionHtml": "<p>" + " ".join(["word"] * 60) + "</p>", "onlineStoreUrl": "https://fixture.example/products/product-%d" % n, "totalInventory": 5,
         "seo": {"title": "Product %d | Northwind" % n, "description": "A good description of product %d that is long enough to pass the seventy character floor." % n},
         "featuredMedia": {"id": gid("MediaImage", n * 10)},
         "media": {"nodes": [{"id": gid("MediaImage", n * 10), "alt": "Olive jacket %d front" % n, "mediaContentType": "IMAGE", "image": {"url": "https://cdn.example/%d.jpg" % n, "width": 1600, "height": 1600}}]},
         "options": [{"name": "Size", "values": ["M"]}],
         "variants": {"nodes": [{"id": gid("ProductVariant", n * 100), "title": "M", "sku": "NW-%03d" % n, "barcode": "123", "price": "49.00", "compareAtPrice": None,
                                 "inventoryQuantity": 5, "inventoryPolicy": "DENY", "selectedOptions": [{"name": "Size", "value": "M"}], "inventoryItem": {"id": gid("InventoryItem", n * 100), "tracked": True}}]},
         "collections": {"nodes": [{"id": gid("Collection", 1), "handle": "jackets", "title": "Jackets"}]}}
    for k, v in kw.items():
        p[k] = v
    return p


PRODUCTS = [
    product(1),
    product(2, descriptionHtml="", media={"nodes": []}, seo={"title": "", "description": ""}, collections={"nodes": []}),           # missing description, no media, no SEO, no collection
    product(3, title="Product 1", variants={"nodes": [dict(product(3)["variants"]["nodes"][0], sku="NW-001", price="0.00")]}),       # duplicate title, duplicate SKU, zero price
    product(4, publishedAt=None, onlineStoreUrl=None, tags=[]),                                                                      # active but unpublished, untagged
    product(5, status="DRAFT", vendor="northwind", media={"nodes": [{"id": gid("MediaImage", 50), "alt": "", "mediaContentType": "IMAGE", "image": {"url": "https://cdn.example/5.jpg", "width": 400, "height": 400}}]}),  # draft, vendor case variant, no alt, small image
    product(6, variants={"nodes": [dict(product(6)["variants"]["nodes"][0], price="10.00", compareAtPrice="8.00", sku="")]}),        # compare-at below price, missing SKU
    product(7, seo={"title": "Product 1 | Northwind", "description": "short"}),                                                       # duplicate SEO title, short description
    product(8, handle="copy-of-product-8"),                                                                                            # handle quality
]
COLLECTIONS = [
    {"id": gid("Collection", 1), "handle": "jackets", "title": "Jackets", "updatedAt": "2026-09-01T00:00:00Z", "sortOrder": "BEST_SELLING", "descriptionHtml": "<p>Jackets.</p>", "image": {"id": "x", "altText": "Jackets"},
     "seo": {"title": "Jackets | Northwind", "description": "All the jackets we make, from waxed cotton to wool, in every size we cut."}, "productsCount": {"count": 7},
     "sources": [{"id": gid("CollectionConditionsSource", 1), "inclusion": {"conditions": [{"__typename": "CollectionSourceInclusionConditionProductType"}], "selections": {"nodes": []}}}], "resourcePublicationsCount": {"count": 1}},
    {"id": gid("Collection", 2), "handle": "empty-test", "title": "Test 2", "updatedAt": "2026-09-01T00:00:00Z", "sortOrder": "MANUAL", "descriptionHtml": "", "image": None,
     "seo": {"title": "", "description": ""}, "productsCount": {"count": 0}, "sources": [{"id": gid("CollectionConditionsSource", 2), "inclusion": {"conditions": [], "selections": {"nodes": []}}}], "resourcePublicationsCount": {"count": 0}},
]
REDIRECTS = [{"id": gid("UrlRedirect", 1), "path": "/old-a", "target": "/old-b"}, {"id": gid("UrlRedirect", 2), "path": "/old-b", "target": "/old-a"},
             {"id": gid("UrlRedirect", 3), "path": "/old-c", "target": "/collections/jackets"}, {"id": gid("UrlRedirect", 4), "path": "/deep/path/here", "target": "/"}]
LOCATIONS = [{"id": gid("Location", 1), "name": "Warehouse", "isActive": True, "fulfillsOnlineOrders": True}]
STATE = {"calls": 0, "mutations": [], "bulk_phase": 0}


class Mock(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _json(self, obj, status=200, headers=None):
        body = json.dumps(obj).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json"); self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Shopify-API-Version", "2026-07")
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        self.end_headers(); self.wfile.write(body)

    def do_GET(self):
        if self.path.startswith("/bulk.jsonl"):
            lines = [json.dumps({"id": p["id"], "handle": p["handle"], "title": p["title"]}) for p in PRODUCTS]
            for p in PRODUCTS:
                for v in p["variants"]["nodes"]:
                    lines.append(json.dumps({"id": v["id"], "sku": v["sku"], "price": v["price"], "__parentId": p["id"]}))
            body = ("\n".join(lines) + "\n").encode()
            self.send_response(200); self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body); return
        self.send_response(404); self.end_headers()

    def do_POST(self):
        if self.path.startswith("/upload"):
            self.rfile.read(int(self.headers.get("Content-Length") or 0)); self.send_response(201); self.end_headers(); return
        if self.headers.get("X-Shopify-Access-Token") != TOKEN:
            self._json({"errors": "[API] Invalid API key or access token"}, 401); return
        req = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        q, v = req.get("query", ""), req.get("variables") or {}
        STATE["calls"] += 1
        if STATE["calls"] == 1:
            self._json({"errors": [{"message": "Throttled"}]}, 429, {"Retry-After": "0"}); return
        if STATE["calls"] == 2:
            self._json({"errors": [{"message": "Throttled", "extensions": {"code": "THROTTLED"}}], "extensions": {"cost": {"requestedQueryCost": 10, "throttleStatus": {"maximumAvailable": 1000, "currentlyAvailable": 0, "restoreRate": 500}}}}); return
        self._json({"data": self.dispatch(q, v), "extensions": {"cost": {"requestedQueryCost": 10, "actualQueryCost": 10, "throttleStatus": {"maximumAvailable": 1000, "currentlyAvailable": 990, "restoreRate": 50}}}})

    def dispatch(self, q, v):
        base = "http://%s:%d" % self.server.server_address
        d = {}
        if re.search(r"__type\s*\(", q):
            return {"__type": {"name": "Mutation", "fields": []}}
        if re.search(r"\bshop\s*\{", q):
            d["shop"] = {"name": "Fixture Store", "myshopifyDomain": DOMAIN, "primaryDomain": {"host": "fixture.example", "url": "https://fixture.example"},
                         "plan": {"publicDisplayName": "Basic"}, "currencyCode": "USD", "ianaTimezone": "UTC", "email": "x@example.com", "contactEmail": "x@example.com"}
        if "currentAppInstallation" in q:
            d["currentAppInstallation"] = {"accessScopes": [{"handle": s} for s in ("read_products", "write_products", "read_content", "read_inventory", "read_locations", "read_online_store_navigation", "read_metaobject_definitions", "read_metaobjects")]}
        if "productsCount" in q:
            d.update({"productsCount": {"count": len(PRODUCTS)}, "active": {"count": 7}, "draft": {"count": 1}, "archived": {"count": 0}, "collectionsCount": {"count": 2}, "smart": {"count": 1},
                      "locations": {"nodes": [dict(l, address={"city": "X", "countryCode": "US"}) for l in LOCATIONS]}, "publications": {"nodes": [{"id": "p1", "catalog": {"title": "Online Store"}}]},
                      "metafieldDefinitions": {"nodes": [{"namespace": "custom", "key": "material", "type": {"name": "single_line_text_field"}}]}, "collectionDefs": {"nodes": []},
                      "metaobjectDefinitions": {"nodes": []}, "urlRedirectsCount": {"count": len(REDIRECTS)}, "productTypes": {"nodes": ["Jackets"]}, "productVendors": {"nodes": ["Northwind"]}, "productTags": {"nodes": ["a"]}})
        if "productByIdentifier" in q:
            h = (v.get("handle") or "")
            p = next((p for p in PRODUCTS if p["handle"] == h), None)
            d["productByIdentifier"] = dict(p, metafields={"nodes": []}) if p else None
        elif re.search(r"\bproducts\s*\(", q):
            qf = v.get("q") or v.get("query") or ""
            m = re.search(r"handle:(\S+)", qf)
            items = [p for p in PRODUCTS if p["handle"] == m.group(1)] if m else list(PRODUCTS)
            if "metafields(" in q:
                items = [{"id": p["id"], "handle": p["handle"], "metafields": {"nodes": [{"namespace": "custom", "key": "material", "type": "single_line_text_field", "value": "Waxed cotton"}] if p["handle"] == "product-1" else []}} for p in items]
            first = int(v.get("first") or 50)
            start = int(v.get("after") or 0)
            page = items[start:start + first]
            nxt = start + first < len(items)
            d["products"] = {"nodes": page, "pageInfo": {"hasNextPage": nxt, "endCursor": str(start + first) if nxt else None}}
        if "collectionByIdentifier" in q:
            h = v.get("handle"); c = next((c for c in COLLECTIONS if c["handle"] == h), None)
            d["collectionByIdentifier"] = c
        elif re.search(r"\bcollections\s*\(", q):
            qf = v.get("q") or ""
            m = re.search(r"handle:(\S+)", qf)
            items = [c for c in COLLECTIONS if c["handle"] == m.group(1)] if m else COLLECTIONS
            items = [dict(c, products={"nodes": []}, metafields={"nodes": []}) for c in items]
            d["collections"] = {"nodes": items, "pageInfo": {"hasNextPage": False, "endCursor": None}}
        if "metafieldDefinitions(" in q and "productsCount" not in q:
            d["metafieldDefinitions"] = {"nodes": [{"namespace": "custom", "key": "material", "name": "Material", "type": {"name": "single_line_text_field"}}]}
            if "collection:" in q:
                d["product"] = d["metafieldDefinitions"]; d["collection"] = {"nodes": []}
        if "metaobjectDefinitions" in q and "productsCount" not in q:
            d["metaobjectDefinitions"] = {"nodes": [{"id": "md1", "type": "faq", "name": "FAQ", "metaobjectsCount": 1, "fieldDefinitions": [{"key": "question", "name": "Q", "required": True, "type": {"name": "single_line_text_field"}}]}]}
        if re.search(r"\bmetaobjects\s*\(", q):
            d["metaobjects"] = {"nodes": [{"id": "mo1", "handle": "faq-1", "displayName": "", "updatedAt": "2026-09-01T00:00:00Z", "fields": [{"key": "question", "value": "", "type": "single_line_text_field", "reference": None}]}], "pageInfo": {"hasNextPage": False, "endCursor": None}}
        if re.search(r"\blocations\s*\(", q) and "productsCount" not in q:
            d["locations"] = {"nodes": LOCATIONS}
        if "productVariants(" in q:
            nodes = []
            for p in PRODUCTS:
                for var in p["variants"]["nodes"]:
                    nodes.append({"id": var["id"], "sku": var["sku"], "title": var["title"], "inventoryPolicy": var["inventoryPolicy"], "product": {"handle": p["handle"], "status": p["status"]},
                                  "inventoryItem": {"id": var["inventoryItem"]["id"], "tracked": True, "inventoryLevels": {"nodes": [{"location": LOCATIONS[0], "quantities": [{"name": "available", "quantity": -2 if p["handle"] == "product-3" else 5}, {"name": "on_hand", "quantity": 5}, {"name": "committed", "quantity": 0}]}]}}})
            d["productVariants"] = {"nodes": nodes, "pageInfo": {"hasNextPage": False, "endCursor": None}}
        if "urlRedirects(" in q:
            d["urlRedirects"] = {"nodes": REDIRECTS, "pageInfo": {"hasNextPage": False, "endCursor": None}}
        if "bulkOperations(" in q:
            # phase 0: an old completed op; after a run mutation: RUNNING once, then COMPLETED
            status = "RUNNING" if STATE["bulk_phase"] == 1 else "COMPLETED"
            if STATE["bulk_phase"] == 1:
                STATE["bulk_phase"] = 2
            d["bulkOperations"] = {"nodes": [{"id": gid("BulkOperation", 1), "type": "MUTATION" if "mutation" in (v.get("q") or "") else "QUERY", "status": status, "errorCode": None, "createdAt": "2026-09-13T00:00:00Z", "completedAt": None,
                                              "objectCount": "16", "fileSize": "1000", "url": base + "/bulk.jsonl" if status == "COMPLETED" else None, "partialDataUrl": None}]}
        # ---- mutations: record and echo ----
        m = re.search(r"mutation[^{]*\{\s*(\w+)\s*\(", q)
        if m:
            name = m.group(1); STATE["mutations"].append((name, v))
            if name == "productUpdate":
                inp = v["input"]; p = next(p for p in PRODUCTS if p["id"] == inp["id"])
                p = dict(p); p.update({k: val for k, val in inp.items() if k != "seo"})
                if "seo" in inp:
                    p["seo"] = dict(p["seo"], **inp["seo"])
                d["productUpdate"] = {"product": p, "userErrors": []}
                if inp.get("vendor") == "BOOM":
                    d["productUpdate"] = {"product": None, "userErrors": [{"field": ["vendor"], "message": "Vendor is invalid"}]}
            elif name == "productCreate":
                d["productCreate"] = {"product": {"id": gid("Product", 99), "handle": v["product"].get("handle") or "new", "title": v["product"]["title"], "status": v["product"].get("status", "DRAFT"), "vendor": v["product"].get("vendor"), "productType": None, "tags": v["product"].get("tags", []), "seo": v["product"].get("seo", {}), "variants": {"nodes": [{"id": gid("ProductVariant", 9900), "price": "0.00", "sku": None}]}}, "userErrors": []}
            elif name == "productVariantsBulkUpdate":
                d["productVariantsBulkUpdate"] = {"productVariants": [dict(x, compareAtPrice=x.get("compareAtPrice"), sku=(x.get("inventoryItem") or {}).get("sku")) for x in v["vars"]], "userErrors": []}
            elif name == "metafieldsSet":
                d["metafieldsSet"] = {"metafields": [{"id": "m", "namespace": x["namespace"], "key": x["key"], "value": x["value"]} for x in v["m"]], "userErrors": []}
            elif name == "urlRedirectCreate":
                d["urlRedirectCreate"] = {"urlRedirect": dict(v["r"], id=gid("UrlRedirect", 9)), "userErrors": []}
            elif name == "fileUpdate":
                d["fileUpdate"] = {"files": [{"id": f["id"], "alt": f["alt"]} for f in v["files"]], "userErrors": []}
            elif name in ("collectionUpdate", "collectionCreate"):
                cin = v.get("c") or v.get("input") or {}
                c = dict(COLLECTIONS[1]); c.update({k: val for k, val in cin.items() if k in ("title", "sortOrder", "descriptionHtml")}); c["seo"] = dict(c["seo"], **(cin.get("seo") or {}))
                d[name] = {"collection": c, "userErrors": []}
            elif name == "bulkOperationRunQuery":
                STATE["bulk_phase"] = 1
                d[name] = {"bulkOperation": {"id": gid("BulkOperation", 1), "status": "CREATED"}, "userErrors": []}
            elif name == "stagedUploadsCreate":
                d[name] = {"stagedTargets": [{"url": base + "/upload", "resourceUrl": base + "/upload/x", "parameters": [{"name": "key", "value": "tmp/vars.jsonl"}]}], "userErrors": []}
            elif name == "bulkOperationRunMutation":
                STATE["bulk_phase"] = 1
                d[name] = {"bulkOperation": {"id": gid("BulkOperation", 1), "status": "CREATED"}, "userErrors": []}
        return d


def run(script, *args, env_extra=None, cwd=None, timeout=120):
    env = dict(os.environ, SHOPIFY_STORE_DOMAIN=DOMAIN, SHOPIFY_ADMIN_ACCESS_TOKEN=TOKEN, SHOPIFY_API_VERSION="2026-07",
               SHOPIFY_API_URL=BASE_URL + "/graphql", PYTHONDONTWRITEBYTECODE="1")
    env.update(env_extra or {})
    p = subprocess.run([sys.executable, os.path.join(SCRIPTS, script)] + list(args), capture_output=True, text=True, timeout=timeout, env=env, cwd=cwd)
    assert TOKEN not in p.stdout + p.stderr, "token leaked by %s" % script
    return p.returncode, p.stdout, p.stderr


failures = 0


def check(name, ok, detail=""):
    global failures
    failures += 0 if ok else 1
    print("  %s  %s%s" % ("PASS" if ok else "FAIL", name, ("  -> " + detail.strip().replace("\n", " | ")[:300]) if detail and not ok else ""))


def main():
    global BASE_URL
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Mock)
    BASE_URL = "http://127.0.0.1:%d" % srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    tmp = tempfile.mkdtemp()
    try:
        # client: retries through a 429 and a THROTTLED response (calls 1 and 2)
        rc, out, err = run("connection_check.py", "--json", os.path.join(tmp, "c.json"))
        check("connection_check: retries 429 then THROTTLED and passes", rc == 0 and "PASS  authenticated" in out, out + err)
        check("connection_check: reports scopes", "read_products" in out)
        rc, out, err = run("connection_check.py", env_extra={"SHOPIFY_ADMIN_ACCESS_TOKEN": ""})
        check("missing token exits 3 with guidance", rc == 3 and "configuration" in err, err)
        rc, out, err = run("connection_check.py", env_extra={"SHOPIFY_ADMIN_ACCESS_TOKEN": "shpat_" + "0" * 32})
        check("wrong token: 401 explained, exit 3", rc == 3 and "401" in err, err)
        rc, out, err = run("connection_check.py", env_extra={"SHOPIFY_STORE_DOMAIN": "fixture.example"})
        check("custom domain instead of myshopify domain is rejected", rc == 3 and "myshopify" in err, err)
        rc, out, err = run("connection_check.py", env_extra={"SHOPIFY_API_VERSION": "latest"})
        check("malformed API version is rejected", rc == 3, err)
        # .env loading from cwd
        with open(os.path.join(tmp, ".env"), "w") as fh:
            fh.write("SHOPIFY_STORE_DOMAIN=%s\nSHOPIFY_ADMIN_ACCESS_TOKEN=%s\nSHOPIFY_API_VERSION=2026-07\nSHOPIFY_API_URL=%s/graphql\n" % (DOMAIN, TOKEN, BASE_URL))
        p = subprocess.run([sys.executable, os.path.join(SCRIPTS, "shopify_client.py"), "shop"], capture_output=True, text=True, cwd=tmp,
                           env={k: v for k, v in os.environ.items() if not k.startswith("SHOPIFY")})
        check("client CLI reads .env from the working directory", p.returncode == 0 and "Fixture Store" in p.stdout, p.stdout + p.stderr)
        os.remove(os.path.join(tmp, ".env"))

        rc, out, err = run("store_discovery.py", "--json", os.path.join(tmp, "d.json"))
        check("store_discovery: summarises counts", rc == 0 and "products:      8" in out, out + err)

        pj = os.path.join(tmp, "products.json")
        rc, out, err = run("product_export.py", "--out", pj)
        check("product_export: JSON export paginates the fixture (8 products)", rc == 0 and json.load(open(pj))["count"] == 8, out + err)
        rc, out, err = run("product_export.py", "--out", os.path.join(tmp, "v.csv"), "--format", "variants")
        check("product_export: variant CSV", rc == 0 and os.path.getsize(os.path.join(tmp, "v.csv")) > 100)

        rc, out, err = run("product_audit.py", "--input", pj, "--json", os.path.join(tmp, "pa.json"))
        j = json.load(open(os.path.join(tmp, "pa.json"))); checks = {f["check"] for f in j["findings"]}
        check("product_audit: exits 2 on HIGH findings", rc == 2, out + err)
        for c in ("missing description", "no media", "active but unpublished", "duplicate title", "inconsistent vendor", "handle quality", "in no collection", "draft"):
            check("product_audit: finds '%s'" % c, c in checks, str(checks))
        rc, out, err = run("seo_audit.py", "--input", pj, "--json", os.path.join(tmp, "sa.json"))
        checks = {f["check"] for f in json.load(open(os.path.join(tmp, "sa.json")))["findings"]}
        for c in ("missing SEO title", "duplicate SEO title", "SEO description under 70 characters", "active but not on the online store", "image alt text missing"):
            check("seo_audit: finds '%s'" % c, c in checks, str(checks))
        rc, out, err = run("media_audit.py", "--input", pj, "--csv", os.path.join(tmp, "alt.csv"), "--json", os.path.join(tmp, "ma.json"))
        checks = {f["check"] for f in json.load(open(os.path.join(tmp, "ma.json")))["findings"]}
        check("media_audit: finds no media, missing alt, small image", {"no media", "missing alt text", "small image"} <= checks, str(checks))
        check("media_audit: writes the alt-text worksheet with one row", open(os.path.join(tmp, "alt.csv")).read().count("\n") == 2)
        rc, out, err = run("variant_audit.py", "--input", pj, "--json", os.path.join(tmp, "va.json"))
        checks = {f["check"] for f in json.load(open(os.path.join(tmp, "va.json")))["findings"]}
        check("variant_audit: duplicate SKU is HIGH (exit 2) and missing SKU found", rc == 2 and {"duplicate SKU", "missing SKU"} <= checks, str(checks))
        rc, out, err = run("pricing_audit.py", "--input", pj, "--json", os.path.join(tmp, "pr.json"))
        checks = {f["check"] for f in json.load(open(os.path.join(tmp, "pr.json")))["findings"]}
        check("pricing_audit: zero price is CRITICAL, compare-at below price found", rc == 2 and {"zero price", "compare-at not above price"} <= checks, str(checks))
        rc, out, err = run("collection_audit.py", "--members", "--json", os.path.join(tmp, "ca.json"))
        checks = {f["check"] for f in json.load(open(os.path.join(tmp, "ca.json")))["findings"]}
        check("collection_audit: empty, unpublished, empty source, orphan products", {"empty collection", "not published to any channel", "collection source with no conditions and no products", "active product in no collection"} <= checks, str(checks))
        rc, out, err = run("metafield_export.py", "--owner", "product", "--audit", "--out", os.path.join(tmp, "mf.csv"))
        check("metafield_export: exports and reports missing defined metafields", "missing defined metafield custom.material" in out and os.path.exists(os.path.join(tmp, "mf.csv")), out + err)
        rc, out, err = run("metaobject_audit.py", "--json", os.path.join(tmp, "mo.json"))
        check("metaobject_audit: required field empty is HIGH", rc == 2 and "required field empty" in out, out + err)
        rc, out, err = run("inventory_audit.py", "--json", os.path.join(tmp, "inv.json"))
        check("inventory_audit: negative tracked quantity is HIGH", rc == 2 and "negative available quantity" in out, out + err)
        rc, out, err = run("redirect_audit.py", "--json", os.path.join(tmp, "ra.json"))
        checks = {f["check"] for f in json.load(open(os.path.join(tmp, "ra.json")))["findings"]}
        check("redirect_audit: loop is CRITICAL; deep path to homepage found", rc == 2 and "redirect loop" in checks and "deep path redirected to the homepage" in checks, str(checks))
        rc, out, err = run("store_audit.py", "--input", pj, "--out", os.path.join(tmp, "audit.md"), "--json", os.path.join(tmp, "audit.json"), cwd=tmp)
        aj = json.load(open(os.path.join(tmp, "audit.json"))); md = open(os.path.join(tmp, "audit.md")).read()
        check("store_audit: scores every area and writes md + json", rc == 2 and set(aj["areas"]) == {"products", "seo", "collections", "media", "variants", "pricing", "metafields", "inventory", "redirects"}, out + err)
        check("store_audit: report has the required sections", all(s in md for s in ("SHOPIFY STORE AUDIT", "SHOPIFY CATALOG HEALTH", "CRITICAL ISSUES", "TOP RECOMMENDED ACTIONS", "API Version:")))

        # ---- writes: dry run by default, preview, confirm, read back ----
        before = len(STATE["mutations"])
        csvp = os.path.join(tmp, "upd.csv")
        open(csvp, "w").write("handle,vendor,tags_add,seo_title,status\nproduct-1,Northwind Supply,new,Product 1 | New,ACTIVE\nproduct-2,,,,\nnope,X,,,\n")
        rc, out, err = run("product_update.py", "--input", csvp, cwd=tmp)
        check("product_update: dry run previews and writes nothing", "MODE: DRY RUN" in out and "PLANNED CHANGES" in out and len(STATE["mutations"]) == before, out + err)
        check("product_update: status column refused without --allow-status", "allow-status" in out, out)
        check("product_update: unknown handle skipped, exit 1", rc == 1 and "not found" in out, out)
        open(csvp, "w").write("handle,vendor,tags_add,seo_title\nproduct-1,Northwind Supply,new,Product 1 | New\nproduct-2,,,\n")
        rc, out, err = run("product_update.py", "--input", csvp, "--confirm", "--json", os.path.join(tmp, "u.json"), cwd=tmp)
        check("product_update: --confirm writes one productUpdate, verifies read-back, exit 0", rc == 0 and "verified 1" in out and any(m[0] == "productUpdate" for m in STATE["mutations"][before:]), out + err)
        check("product_update: a row with no changes is not written", sum(1 for m in STATE["mutations"][before:] if m[0] == "productUpdate") == 1)
        check("product_update: backup written before the write", any(f.startswith("product_update-") for f in os.listdir(os.path.join(tmp, "backups"))))
        rc, out, err = run("product_update.py", "--handle", "product-1", "--set", "vendor=BOOM", "--confirm", cwd=tmp)
        check("product_update: userErrors reported, exit 2", rc == 2 and "FAIL product-1" in out and "Vendor is invalid" in out, out + err)
        rc, out, err = run("product_update.py", "--input", csvp, "--confirm", "--limit", "0", cwd=tmp)
        check("product_update: --limit caps writes", "exceed --limit" in out or "applied 0" in out, out)

        yp = os.path.join(tmp, "p.yaml")
        open(yp, "w").write("title: New Thing\nhandle: new-thing\nstatus: DRAFT\ntags: [x, y]\nseo:\n  title: New Thing | Store\n  description: Long enough description for the new thing that we are creating today.\nprice: 12.5\nsku: NT-1\n")
        rc, out, err = run("product_create.py", "--input", yp, cwd=tmp)
        check("product_create: YAML parsed, dry run, nothing sent", rc == 0 and '"status": "DRAFT"' in out and "12.50" in out and not any(m[0] == "productCreate" for m in STATE["mutations"]), out + err)
        rc, out, err = run("product_create.py", "--input", yp, "--confirm", cwd=tmp)
        check("product_create: --confirm creates and sets the variant price", rc == 0 and "created new-thing" in out and any(m[0] == "productVariantsBulkUpdate" for m in STATE["mutations"]), out + err)
        open(yp, "w").write("title: \nstatus: LIVE\n")
        rc, out, err = run("product_create.py", "--input", yp, cwd=tmp)
        check("product_create: validation failures exit 1", rc == 1 and "title is required" in out and "status must be" in out, out)

        sp = os.path.join(tmp, "seo.csv")
        open(sp, "w").write('kind,handle,title,current_seo_title,proposed_seo_title,current_seo_description,proposed_seo_description,notes\n'
                            'product,product-1,Product 1,Product 1 | Northwind,Product 1 | Waxed Cotton Jacket,,,\n'
                            'product,product-2,Product 2,,TODO fill in,,,\n'
                            'product,product-7,Product 7,STALE,New title,,,\n'
                            'collection,jackets,Jackets,Jackets | Northwind,Jackets | Northwind Supply,,,\n')
        rc, out, err = run("seo_import.py", "--input", sp, cwd=tmp)
        check("seo_import: placeholder rejected, stale row skipped, dry run", rc == 1 and "placeholder" in out and "stale" in out and "WRITE OPERATION:      NO" in out, out + err)
        before = len(STATE["mutations"])
        rc, out, err = run("seo_import.py", "--input", sp, "--confirm", cwd=tmp)
        names = [m[0] for m in STATE["mutations"][before:]]
        check("seo_import: --confirm updates the product and the collection with collection:", "productUpdate" in names and "collectionUpdate" in names and "c" in STATE["mutations"][-1][1] or "input" in STATE["mutations"][-1][1], str(names))

        import csv as _csv
        ap = os.path.join(tmp, "alt.csv")
        alt_rows = list(_csv.DictReader(open(ap, newline="")))

        def write_alt(text):
            for r in alt_rows:
                r["alt"] = text
            with open(ap, "w", newline="") as fh:
                w = _csv.DictWriter(fh, fieldnames=list(alt_rows[0].keys())); w.writeheader(); w.writerows(alt_rows)
        write_alt("Olive jacket on a hanger, front view")
        rc, out, err = run("alt_text_update.py", "--input", ap, "--confirm", cwd=tmp)
        check("alt_text_update: applies via fileUpdate and verifies", rc == 0 and "applied 1 image" in out and STATE["mutations"][-1][0] == "fileUpdate", out + err)
        write_alt("x" * 130)
        rc, out, err = run("alt_text_update.py", "--input", ap, "--confirm", cwd=tmp)
        check("alt_text_update: over-long alt rejected", rc == 1 and "125" in out, out)

        mp = os.path.join(tmp, "mf.csv")
        open(mp, "w").write('owner,handle,namespace,key,type,value\nproduct,product-1,custom,material,single_line_text_field,Waxed cotton\nproduct,product-1,custom,weight,number_integer,abc\nproduct,product-2,custom,spec,json,{"a":1}\n')
        rc, out, err = run("metafield_update.py", "--input", mp, "--confirm", cwd=tmp)
        check("metafield_update: unchanged skipped, bad number rejected, JSON set", rc == 1 and "not a number" in out and "applied 1" in out, out + err)

        rp = os.path.join(tmp, "r.csv")
        open(rp, "w").write("path,target\n/new-1,/collections/jackets\n/old-a,/x\n/new-2,/old-c\nbad,/x\n/new-1,/dup\n")
        rc, out, err = run("redirect_import.py", "--input", rp, cwd=tmp)
        check("redirect_import: existing source skipped, chain warned, bad path skipped, dup skipped", "already redirects" in out and "chain" in out and "leading" not in out and "duplicate row" in out and "start with /" in out, out)
        before = len(STATE["mutations"])
        rc, out, err = run("redirect_import.py", "--input", rp, "--confirm", "--limit", "1", cwd=tmp)
        check("redirect_import: --confirm --limit 1 creates exactly one", sum(1 for m in STATE["mutations"][before:] if m[0] == "urlRedirectCreate") == 1, out + err)

        cp = os.path.join(tmp, "col.yaml")
        open(cp, "w").write("handle: empty-test\ntitle: Renamed\nsort_order: MANUAL\nproducts:\n  - product-2\n  - missing-handle\n")
        rc, out, err = run("collection_write.py", "--input", cp, "--confirm", cwd=tmp)
        m = STATE["mutations"][-1]
        check("collection_write: updates via collection: with sourcesToUpdate selections", rc == 0 and m[0] == "collectionUpdate" and "sourcesToUpdate" in m[1]["c"] and m[1]["c"]["sourcesToUpdate"][0]["condition"]["inclusion"]["selectionsToAdd"] == [{"productId": gid("Product", 2)}], out + err + json.dumps(m[1]))
        check("collection_write: missing product handle warned, never removes", "not found" in out and "products removed: 0" in out, out)

        # ---- bulk ----
        rc, out, err = run("bulk_query.py", "--inline", "{ products { edges { node { id } } } }", "--out", os.path.join(tmp, "b.jsonl"), "--poll", "0", cwd=tmp)
        check("bulk_query: starts, polls RUNNING then COMPLETED, downloads JSONL", rc == 0 and os.path.exists(os.path.join(tmp, "b.jsonl")) and "saved" in out, out + err)
        rc, out, err = run("jsonl_summary.py", os.path.join(tmp, "b.jsonl"))
        check("jsonl_summary: types and parent links", "ProductVariant" in out and "-> Product" in out, out)
        rc, out, err = run("jsonl_to_csv.py", os.path.join(tmp, "b.jsonl"), "--type", "ProductVariant", "--out", os.path.join(tmp, "b.csv"))
        check("jsonl_to_csv: extracts one type", rc == 0 and "8 ProductVariant row" in out, out + err)
        open(os.path.join(tmp, "vend.csv"), "w").write("id,vendor\n1,Acme\n2,\n")
        rc, out, err = run("csv_to_jsonl.py", os.path.join(tmp, "vend.csv"), "--out", os.path.join(tmp, "vars.jsonl"), "--shape", "input.id=id,input.vendor=vendor")
        lines = open(os.path.join(tmp, "vars.jsonl")).read().strip().split("\n")
        check("csv_to_jsonl: expands ids, drops rows with only an id", len(lines) == 1 and json.loads(lines[0]) == {"input": {"id": gid("Product", 1), "vendor": "Acme"}}, out + str(lines))
        rc, out, err = run("jsonl_validate.py", os.path.join(tmp, "vars.jsonl"), "--require", "input.id", "--gid", "Product")
        check("jsonl_validate: valid file exits 0", rc == 0, out)
        mut = os.path.join(tmp, "m.graphql"); open(mut, "w").write("mutation($input: ProductUpdateInput!) { productUpdate(product: $input) { product { id } userErrors { field message } } }")
        rc, out, err = run("bulk_mutation.py", "--mutation", mut, "--input", os.path.join(tmp, "vars.jsonl"), cwd=tmp)
        check("bulk_mutation: dry run validates and sends nothing", rc == 0 and "WRITE OPERATION: NO" in out, out + err)
        rc, out, err = run("bulk_mutation.py", "--mutation", mut, "--input", os.path.join(tmp, "vars.jsonl"), "--confirm", "--out", os.path.join(tmp, "res.jsonl"), cwd=tmp)
        check("bulk_mutation: --confirm uploads, runs, downloads the result", rc == 0 and any(m[0] == "bulkOperationRunMutation" for m in STATE["mutations"]), out + err)
        rc, out, err = run("bulk_status.py", cwd=tmp)
        check("bulk_status: reports the operation", rc in (0, 1) and "status:" in out, out + err)
        rc, out, err = run("bulk_cancel.py", cwd=tmp)
        check("bulk_cancel: without --confirm cancels nothing", rc == 0 and not any(m[0] == "bulkOperationCancel" for m in STATE["mutations"]), out)

        # every script answers --help
        for f in sorted(os.listdir(SCRIPTS)):
            if f.endswith(".py") and not f.startswith("_"):
                rc, out, err = run(f, "--help")
                check("--help: %s" % f, rc == 0 and "usage" in (out + err).lower(), err)
    finally:
        srv.shutdown()
    print("\n%d failure(s)" % failures)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
