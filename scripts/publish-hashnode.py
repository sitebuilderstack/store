#!/usr/bin/env python3
"""Publish (or preview) a syndicated article on Hashnode with its canonical URL set.

    publish-hashnode.py content/syndication/<file>.md [--dry-run] [--draft] [--host site-builder-stack.hashnode.dev | --publication-id ID]

--draft creates a Hashnode draft (createDraft) for review in the dashboard
instead of publishing; the canonical, tags and SEO fields are set on the
draft so publishing it later from the dashboard keeps them.

Reads the Personal Access Token from /opt/hashnode-token (never printed,
never logged, never in the repository). The Markdown file's front matter
supplies title, subtitle, canonical and tags; the body is the post. The
canonical becomes Hashnode's `originalArticleURL`, so the post points back
at sitebuilderstack.com for search engines.

Hashnode's GraphQL API (https://gql-beta.hashnode.com, per the official
Hashnode/gql-skill) requires a Pro plan on the target publication since May
2026; the old gql.hashnode.com host redirects to the announcement. Publication
is by host: --host site-builder-stack.hashnode.dev (default) resolves the id.
"""
import json
import re
import sys
import urllib.error
import urllib.request

ENDPOINT = "https://gql-beta.hashnode.com"  # the API host since the Pro-plan change; gql.hashnode.com now redirects to the announcement
TOKEN_FILE = "/opt/hashnode-token"


def gql(query, variables, token):
    req = urllib.request.Request(ENDPOINT, data=json.dumps({"query": query, "variables": variables}).encode(),
                                 headers={"Content-Type": "application/json", "Accept": "application/json", "Authorization": "Bearer " + token,
                                          "User-Agent": "sitebuilderstack-publisher/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read().decode()
    except urllib.error.HTTPError as e:
        loc = e.headers.get("Location", "")
        if e.code in (301, 302) and "announcements/graphql-api" in loc:
            raise SystemExit("Hashnode redirected the API call to %s — the GraphQL API requires a Pro plan on the publication "
                             "(Blog dashboard → Billing → Upgrade to Pro). Until then, paste the Markdown into the editor and set the canonical URL by hand." % loc)
        raise SystemExit("HTTP %d from Hashnode: %s" % (e.code, e.read().decode()[:200].replace(token, "[REDACTED]")))
    if body.lstrip().startswith("<"):
        raise SystemExit("Hashnode returned HTML instead of JSON — the API is not available to this publication (Pro plan required).")
    data = json.loads(body)
    if data.get("errors"):
        raise SystemExit("GraphQL errors: %s" % json.dumps(data["errors"])[:500].replace(token, "[REDACTED]"))
    return data["data"]


def parse(path):
    text = open(path, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, flags=re.S)
    if not m:
        raise SystemExit("no front matter in %s" % path)
    meta = {}
    for line in m.group(1).splitlines():
        k, _, v = line.partition(":")
        meta[k.strip()] = v.strip().strip('"')
    return meta, m.group(2).strip() + "\n"


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__); return 2
    dry = "--dry-run" in sys.argv; draft = "--draft" in sys.argv
    pub = sys.argv[sys.argv.index("--publication-id") + 1] if "--publication-id" in sys.argv else None
    host = sys.argv[sys.argv.index("--host") + 1] if "--host" in sys.argv else "site-builder-stack.hashnode.dev"
    meta, body = parse(args[0])
    for k in ("title", "canonical"):
        if not meta.get(k):
            raise SystemExit("front matter needs %s" % k)
    if not meta["canonical"].startswith("https://sitebuilderstack.com/"):
        raise SystemExit("canonical must point at sitebuilderstack.com")
    tags = [{"slug": t.strip(), "name": t.strip()} for t in meta.get("tags", "").split(",") if t.strip()]
    print("title:     %s\nsubtitle:  %s\ncanonical: %s\ntags:      %s\nwords:     %d" % (meta["title"], meta.get("subtitle", ""), meta["canonical"], ", ".join(t["slug"] for t in tags), len(body.split())))
    if dry:
        print("dry run — nothing published"); return 0
    token = open(TOKEN_FILE).read().strip()
    if not pub:
        p = gql("query($h:String!){ publication(host:$h){ id title url } }", {"h": host}, token)["publication"]
        if not p:
            raise SystemExit("no publication at %s" % host)
        pub = p["id"]; print("publication: %s (%s)" % (p["title"], p["url"]))
    if draft:
        r = gql("""mutation($input: CreateDraftInput!){ createDraft(input:$input){ draft{ id title } } }""",
                {"input": {"title": meta["title"], "subtitle": meta.get("subtitle") or None, "contentMarkdown": body, "publicationId": pub,
                           "originalArticleURL": meta["canonical"], "tags": tags,
                           "metaTags": {"title": meta["title"], "description": meta.get("subtitle", "")[:160]}}}, token)["createDraft"]["draft"]
        print("draft created: %s (id %s) — review at https://hashnode.com/drafts/%s" % (r["title"], r["id"], r["id"]))
        return 0
    # Hashnode has returned "Internal server error" on the post selection after a successful write;
    # the post exists regardless, so a failure here is followed by a lookup before it is reported.
    try:
        r = gql("""mutation($input: PublishPostInput!){ publishPost(input:$input){ post{ id url slug canonicalUrl } } }""",
            {"input": {"title": meta["title"], "subtitle": meta.get("subtitle") or None, "contentMarkdown": body, "publicationId": pub,
                       "originalArticleURL": meta["canonical"], "tags": tags,
                       "metaTitle": meta["title"], "metaDescription": meta.get("subtitle", "")[:160]}}, token)["publishPost"]["post"]
    except SystemExit as e:
        posts = gql("query($h:String!){ publication(host:$h){ posts(first:3){ edges{ node{ title url canonicalUrl } } } } }", {"h": host}, token)["publication"]["posts"]["edges"]
        match = [x["node"] for x in posts if x["node"]["title"] == meta["title"]]
        if not match:
            raise
        r = match[0]; print("note: Hashnode errored on the response but the post exists (%s)" % e)
    print("published: %s\ncanonical set to: %s" % (r["url"], r.get("canonicalUrl")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
