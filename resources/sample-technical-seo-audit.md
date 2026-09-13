This is one complete workflow from the [Claude Code SEO & Website Audit
Toolkit](/products/claude-code-seo-website-audit-toolkit), reproduced in full and free to
use. The toolkit contains twenty of them.

It is the first one for a reason. Crawlability comes before everything else in the audit
order, because a page a search engine cannot fetch — or can fetch but not read — makes
every other finding about that page irrelevant. Optimising a title on a URL that is being
served as a soft 404 is wasted work.

Run this one on your own site before you read any further into SEO advice. It takes about
ten minutes and it reorders the rest of your list.

---

Can a search engine fetch this page, and does it get the content when it does?

## What to check

**Response codes**
Every URL that should be indexable returns 200. Report anything else with its
actual status, not a summary.

The dangerous one is the **soft 404**: a page that says "not found" and returns
200. Search engines have to guess, and they often guess wrong in both
directions. Test an obviously invalid path:

```
curl -s -o /dev/null -w '%{http_code}\n' https://example.com/definitely-not-a-page
```

A `200` there is a finding. On a static host it usually means a single-page-app
fallback is serving the index page for every unknown path, which turns every
typo and every rotted inbound link into an indexable duplicate of your homepage.

**Redirect chains**
Every redirect costs a hop. Report any chain longer than one, and any loop.

```
curl -sIL https://example.com/old-page | grep -E '^HTTP|^location'
```

Internal links pointing at redirects are the common cause and the easy fix:
point them at the destination.

**Rendering**
Is the content in the initial HTML? Fetch with JavaScript disabled and compare.

```
curl -s https://example.com/some-page | wc -c
```

If that returns a near-empty shell while the browser shows a full page, the
content arrives via JavaScript. That is not automatically fatal — search engines
render — but it is slower, less reliable, and worth knowing about deliberately
rather than discovering later.

**Blocked resources**
A `robots.txt` rule blocking CSS or JavaScript the page needs to render means
the crawler evaluates a broken version of the page. Check that nothing under a
`Disallow` is required for rendering.

## What breaks crawlability without any error

- A staging `Disallow: /` carried into production.
- An `X-Robots-Tag` header, invisible in the page source.
- A `robots.txt` returning 500. Some crawlers treat that as "disallow
  everything", and nothing on the page tells you.
- Password protection or an IP allowlist left in place after launch.
- A firewall or bot-protection rule that serves crawlers a challenge page.

That last one is worth testing explicitly by requesting with a crawler user
agent and comparing the response to a browser's.

## Validation

Whatever you check, break it first. Add a `Disallow: /` to a local copy, run
your checker, confirm it goes red. Then remove it and confirm it goes quiet. A
crawlability checker you have never seen fail is a report, not a check.


---

## What the full toolkit adds

This workflow is deliberately complete: nothing has been cut from it to make the paid
version look better. What the [full
toolkit](/products/claude-code-seo-website-audit-toolkit) adds is the other nineteen, in
dependency order — indexability, canonicals, robots and sitemaps, on-page, structured
data, internal linking, Core Web Vitals, accessibility, content auditing, Search Console,
Bing and IndexNow — plus platform workflows and the report templates.

The order is the product as much as the prompts are. Each audit invalidates work done out
of sequence, which is why a flat checklist of the same items is so much less useful than
it looks.
