# Collecting the storefront's engagement events

**Status: the pixel is written and not installed.** Installing it is a manual
step in the Shopify admin, and it needs a destination you have chosen. Nothing
in this directory is running.

## The problem it solves

The storefront publishes 49 custom events through `Shopify.analytics.publish` —
tool completions, lesson completions, learning path steps, which product
placement was clicked. **Shopify does not surface custom events in the standard
Analytics reports.** It delivers them to Web Pixels and nowhere else.

Measured on 8 September 2026: `webPixel` returned *"No web pixel was found for
this app."* Every one of those events had been firing into nothing since the day
it shipped.

## Why this could not be automated

`webPixelCreate` fails with **"No extension found."** That mutation installs an
*app* pixel, which requires the app to ship a web pixel extension; this store's
app is an Admin API client and has none. A custom pixel can only be created in
**Settings → Customer events**, by a person, in the admin.

## The two files

| File | What it is |
| --- | --- |
| `custom-pixel.js` | Paste into Settings → Customer events. Subscribes to all 49 events and forwards four fields. |
| `collector-worker.js` | A first-party Cloudflare Worker that receives them and stores counts. |
| `wrangler.toml` | Its configuration. The KV id and the read key are yours to fill in. |

`scripts/validate-pixel.py` checks all three lists against each other and
against `docs/analytics/EVENTS.md`. An event documented but not subscribed is
uncollected; one forwarded but not in the collector's allowlist is dropped on
arrival. Both look correct in isolation, which is why they are checked together.

## Why a worker rather than an analytics vendor

The store's analytics decision is on the record: Shopify's own analytics, no
second vendor, no additional script, no consent banner to add. Pointing the
pixel at Plausible or GA4 would quietly reverse that decision and add a
processor to the privacy policy.

A worker on your own infrastructure keeps the decision intact. It sets no
cookie, stores no identifier, and never receives one — the pixel sends the event
name, the storefront's own short label, the path, and an hour-resolution
timestamp. That is the whole payload, and `validate-pixel.py` fails if a fifth
field appears.

It is also not an analytics product, deliberately. There are no sessions and no
visitor records, so it cannot answer "what did this person do" — only "how often
does this happen, on which page, in which hour". That is the question the store
actually has.

## Installing it

```bash
cd analytics
npx wrangler kv namespace create SBS_EVENTS    # put the id in wrangler.toml
npx wrangler secret put READ_KEY               # invent one; /report refuses without it
npx wrangler deploy
```

Then set `ENDPOINT` in `custom-pixel.js` to the deployed URL with `/e`, paste
the file into **Settings → Customer events → Add custom pixel**, give it the
**Analytics** permission, and save.

Leaving `ENDPOINT` empty is a supported state: the pixel does nothing at all
rather than half-working.

## Reading it

```
GET https://<your-worker>/report?key=<READ_KEY>&days=30
```

Returns a count per event, broken down by path. Nothing else.

## If you would rather not run a worker

Then do not install the pixel, and accept that in-page engagement is not
measured. Shopify's own analytics still reports sessions and landing pages,
which is most of what matters while the site has this little traffic. Half-
instrumenting is the worst of the three options: it costs a privacy disclosure
and returns data nobody reads.
