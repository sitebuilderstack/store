# Security headers — what is set, and what cannot be

Measured on the live storefront:

```
$ curl -sI https://sitebuilderstack.com/
```

| Header | State | Set by |
| --- | --- | --- |
| `Strict-Transport-Security` | `max-age=7889238` | Shopify |
| `Content-Security-Policy` | `block-all-mixed-content; frame-ancestors 'none'; upgrade-insecure-requests` | Shopify |
| `X-Content-Type-Options` | `nosniff` | Shopify |
| `X-Frame-Options` | `DENY` | Shopify |
| `Referrer-Policy` | **not sent as a header** — set as `<meta name="referrer" content="strict-origin-when-cross-origin">` in both layouts | Theme |
| `Permissions-Policy` | **not set, and not settable** | — |

## Why two of them are handled differently

Shopify's storefront does not expose response headers to the theme. There is no
`headers.liquid`, no equivalent of `robots.txt.liquid` for headers, and no Admin API
surface for them. Whatever Shopify sends is what the browser receives.

**Referrer-Policy** has a documented meta equivalent —
[MDN](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Referrer-Policy) gives
`<meta name="referrer" content="...">` — so it is set that way in `layout/landing.liquid`
and `layout/theme.liquid`.

Worth being precise about the benefit: `strict-origin-when-cross-origin` **is already the
browser default** when no policy is sent, per the November 2020 Fetch spec revision. So
this change does not alter what browsers do today. What it does is make the policy
explicit and auditable, and protect against a client that defaults differently.

**Permissions-Policy** is a response header only. MDN documents no meta form, and there is
no `<meta http-equiv>` support for it in any browser. On Shopify it therefore cannot be
set at all.

## What that means for the security checklist

`/pages/claude-code-security-checklist` lists `Permissions-Policy` under headers, and that
item is correct for a site where you control the server. It is not achievable on a hosted
Shopify storefront, and the checklist has a note saying so rather than quietly listing an
item this site cannot satisfy.

The honest position for a Shopify store is: four of the six headers are set by the
platform, the fifth is set as a meta element, and the sixth would require control of the
response that the platform does not give you. If `Permissions-Policy` genuinely matters
for a project, that is an argument about hosting, not about the theme.

## Re-checking

```bash
curl -sI https://sitebuilderstack.com/ | grep -iE \
  'strict-transport|content-security|x-content-type|referrer-policy|permissions-policy|x-frame'

curl -s https://sitebuilderstack.com/ | grep -o '<meta name="referrer"[^>]*>'
```
