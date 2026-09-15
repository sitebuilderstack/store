#!/usr/bin/env python3
"""Run a ShopifyQL analytics query and print the result as a table.

Usage: shopifyql.py "FROM sessions SHOW sum(sessions) GROUP BY referrer_source SINCE -30d"
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shopify_api import gql  # noqa: E402

Q = """query($q:String!){ shopifyqlQuery(query:$q){
  tableData{ rows columns{ name dataType displayName } }
  parseErrors
} }"""


def run(ql):
    d = gql(Q, {"q": ql})["shopifyqlQuery"]
    errs = d.get("parseErrors") or []
    if isinstance(errs, str):
        errs = [errs]
    if errs:
        return None, [("PARSE", e if isinstance(e, str) else str(e)) for e in errs]
    td = d.get("tableData")
    if not td:
        return None, [("EMPTY", "no tableData returned")]
    cols = [c.get("displayName") or c["name"] for c in td["columns"]]
    return (cols, td["rows"]), []


def show(ql, title=None):
    print("=" * 74)
    print(title or ql)
    print("=" * 74)
    res, errs = run(ql)
    if errs:
        for c, m in errs:
            print("  ERROR %s: %s" % (c, m))
        return None
    cols, rows = res
    if not rows:
        print("  (no rows -- no data for this period)")
        return cols, rows
    # rows arrive as dicts keyed by the underlying column name
    keys = list(rows[0].keys()) if isinstance(rows[0], dict) else None
    def cell(r, i):
        return str(r[keys[i]]) if keys else str(r[i])
    hdr = cols if len(cols) == (len(keys) if keys else len(rows[0])) else (keys or cols)
    w = [max([len(str(hdr[i]))] + [len(cell(r, i)) for r in rows]) for i in range(len(hdr))]
    print("  " + "  ".join(str(hdr[i]).ljust(w[i]) for i in range(len(hdr))))
    print("  " + "  ".join("-" * w[i] for i in range(len(hdr))))
    for r in rows:
        print("  " + "  ".join(cell(r, i).ljust(w[i]) for i in range(len(hdr))))
    return cols, rows


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    show(sys.argv[1])
