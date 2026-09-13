# Shopify Authentication

How this repository talks to the Shopify Admin API, and the rules around it.

---

## The credentials

Two values, held **outside this repository** on the build machine:

```text
/opt/shopify-client-id.txt      32-character app client ID
/opt/shopify-secret.txt         shpss_… app client secret
```

**They are never committed, printed, logged, or included in the product.**
`.gitignore` blocks the patterns, `scripts/validate-product.py` scans the bundle
for them, and `scripts/verify-archive.py` scans the built ZIP.

## How a token is obtained

This app supports the **client credentials grant**, so no browser OAuth round
trip is needed:

```text
POST https://{shop}/admin/oauth/access_token
  grant_type=client_credentials
  client_id=…
  client_secret=…
→ { access_token: "shpat_…", scope: "…", expires_in: 86399 }
```

The token is short-lived — **24 hours** — which is a meaningful safety property:
a leaked token expires on its own.

`scripts/shopify_api.py` handles this. It:

- Reads credentials from env vars first, then from files
- Caches the token at `~/.cache/sitebuilderstack/shopify-token.json` with mode
  `0600`, **outside the repository**
- Reuses a cached token until two minutes before expiry
- Registers every secret with a `redact()` function that is applied to **all**
  network output before it can reach stdout
- Retries on 429 and 5xx with backoff, and on GraphQL `THROTTLED`

## Granted scopes

Confirmed by querying `currentAppInstallation`:

```text
write_products      read_products
write_content       read_content
write_themes        read_themes
write_files         read_files
write_inventory     read_inventory
write_discounts     read_discounts
read_orders
```

## Scopes NOT granted — and what that blocked

This matters more than the list above, because it explains what is left manual:

| Missing scope | Blocked |
| --- | --- |
| `write_publications` | Publishing the product to the Online Store sales channel |
| `read_publications` | Reading which channels a product is on |
| `write_legal_policies` | Populating Settings → Policies |
| `read_legal_policies` | Reading existing policies |
| `write_online_store_navigation` | Creating or editing menus |
| `read_metaobject_definitions` | Metaobject work |
| (app install permissions) | Installing a digital delivery app |

Each was confirmed by making the call and reading the error, not assumed. See
`REMAINING-MANUAL-STEPS.md`.

**Because menus could not be created, the header and footer navigation is built
from section blocks rather than a Shopify menu resource.** That is arguably
better for a catalogue this small — the links live in the theme and are edited
in the theme editor — but it is a consequence of the scope limit, not purely a
design choice. It is also why the header's Products submenu resolves each entry
through `all_products[handle]`: a product that is drafted or renamed drops out
of the menu rather than leaving a dead link at a stale price.

## Using it

```bash
python3 scripts/shopify_api.py shop          # identity check
python3 scripts/shopify_api.py scopes        # granted scopes
python3 scripts/shopify_api.py gql query.graphql '{"var":1}'
```

Or from Python:

```python
import sys; sys.path.insert(0, "scripts")
from shopify_api import gql, check_user_errors, redact

data = gql("query($id:ID!){ product(id:$id){ title } }", {"id": PID})
```

**Always pass mutation payloads through `check_user_errors()`.** Shopify returns
`userErrors` with a 200 status, so a mutation can fail silently otherwise.

## Rules

1. **Never print a credential.** Use `redact()` on anything that could contain
   one, including error bodies.
2. **Never put a credential in a theme file.** Theme files are served publicly.
3. **Never commit the token cache.**
4. **Prefer GraphQL** over REST — Shopify has been moving Admin functionality to
   GraphQL and deprecating REST endpoints.
5. **Verify the shop before writing.** Every destructive script should confirm it
   is talking to Site Builder Stack:

```python
shop = gql("{ shop { name myshopifyDomain } }")["shop"]
assert shop["name"] == "Site Builder Stack", f"wrong store: {shop}"
```

## If a credential leaks

1. **Rotate first.** Shopify admin → the app → regenerate the client secret.
   Do this before anything else; the window between discovery and rotation is
   the window an attacker has.
2. Delete the cached token: `rm ~/.cache/sitebuilderstack/shopify-token.json`
3. Then work out how it leaked and fix that.
4. Review recent orders and theme changes for anything unexpected.

Removing a secret from a file does not un-expose it. Rotation is the remedy;
cleanup is housekeeping.
