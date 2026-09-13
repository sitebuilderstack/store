# Search engine submission

Submitted 27 August 2026. One command covers all three:

```
scripts/submit-search-engines.py --status     # report, submit nothing
scripts/submit-search-engines.py --sitemaps   # (re)submit the sitemap
scripts/submit-search-engines.py --urls <url> [...]   # ping changed pages
```

## Credentials

Every credential is read at runtime from a path **outside this repository**.
No secret is in source, in a commit, in a Liquid template, in a theme asset,
or in any generated report. Each client redacts its own before printing.

| What | Path | Used by |
|------|------|---------|
| Google service account key | `/opt/site-builder-stack-726cbbfd0bed.json` | `google_search_console.py` |
| Bing API key | `/opt/bing-webmaster-tools-api-key.txt` | `bing_webmaster.py` |
| Bing OAuth2 client id | `/opt/bing-webmaster-tools-client-id.txt` | unused — see below |
| Bing OAuth2 client secret | `/opt/bing-webmaster-tools-client-secret.txt` | unused — see below |
| IndexNow key | `/opt/indexnow-key.txt` | `indexnow-submit.py` |

All five are mode `0600`. They arrived world-readable (`664`/`775`) and were
tightened. Google access tokens cache at `~/.cache/sitebuilderstack/gsc-token.json`,
mode `0600`, outside the repo.

The Bing OAuth2 client id and secret were **not needed**. The API key
authenticates every Bing Webmaster call used here. OAuth2 is only required to
act on behalf of a user who has not issued an API key. The files are recorded
above so nobody goes looking for a use that does not exist.

## Google Search Console

Property: `sc-domain:sitebuilderstack.com` (domain property).
The service account already held `siteOwner`, so no manual grant was needed.

Submission is a `PUT` to
`/webmasters/v3/sites/{site}/sitemaps/{feedpath}`, which returns `204`.
Auth is a self-signed RS256 JWT exchanged for a bearer token — scope
`https://www.googleapis.com/auth/webmasters`.

Result: registered, 0 errors, 0 warnings, `isPending: true` awaiting Google's
first fetch. Google does not participate in IndexNow; the sitemap is the whole
discovery mechanism here.

## Bing Webmaster Tools

Site: `https://sitebuilderstack.com/`, already verified.

The API key can see **eight** properties on this account, most unrelated to
this project. Only `sitebuilderstack.com` was ever acted on. `redact()` also
strips the `AuthenticationCode` and `DnsVerificationCode` the API returns for
every property, so other domains' verification material stays out of our logs.

Two things were submitted:

- `SubmitFeed` — the sitemap. Bing crawled it within a minute:
  `Status: Success`, `UrlCount: 5` (the five child sitemaps of the index).
- `SubmitUrlbatch` — seven changed URLs, authenticated by API key with no
  dependence on the IndexNow key file. Verified by quota: daily went
  100 → 93 and monthly 500 → 493, exactly seven consumed.

## IndexNow

Participants: Bing, Yandex, Seznam, Naver. **Not Google.**

IndexNow proves ownership by fetching a key file from the host root. Shopify
cannot serve an arbitrary file at the site root — a bare `.txt` there returns
a `text/plain` 404 from the router, not the theme.

The working arrangement:

1. The key file is uploaded to Shopify Files, which serves it from
   `cdn.shopify.com` as `text/plain`.
2. A store URL redirect maps `/<key>.txt` onto that CDN URL.
3. `https://sitebuilderstack.com/<key>.txt` resolves `301 → 200` with the key
   as the body.

This was not assumed to work — it was measured. The first submission returned
`202 Accepted` (key validation pending); polling until validation completed
returned `200 OK — key accepted`. A cross-host redirect is accepted.

Two consequences worth knowing:

- **The redirect is load-bearing.** Delete it and IndexNow submissions start
  failing `403`. It looks like a stray redirect in the admin; it is not.
- **Rotating the key** means uploading a new key file, repointing the
  redirect, and updating `/opt/indexnow-key.txt`. The old redirect can then go.

## After publishing new content

```
scripts/submit-search-engines.py --urls \
  https://sitebuilderstack.com/blogs/guides/<new-handle> \
  https://sitebuilderstack.com/blogs/guides
```

The sitemap does not need resubmitting — Shopify regenerates it and both
engines refetch it on their own schedule. Resubmit only if the sitemap URL
itself changes.
