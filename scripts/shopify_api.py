#!/usr/bin/env python3
"""
Site Builder Stack — Shopify Admin API client.

Security contract
-----------------
* Credentials are NEVER printed, logged, or written into any file that ships.
* The access token is cached with 0600 permissions outside the repository
  (see SBS_TOKEN_CACHE) and is redacted from every diagnostic path.
* `redact()` is applied to all network output before it can reach stdout.

Credential resolution order (first hit wins):
  1. env SHOPIFY_CLIENT_ID / SHOPIFY_CLIENT_SECRET
  2. env SHOPIFY_CLIENT_ID_FILE / SHOPIFY_CLIENT_SECRET_FILE (path to a file)
  3. built-in local defaults (this machine only)

Usage:
    python3 shopify_api.py shop                 # identity check
    python3 shopify_api.py gql <file.graphql>   # run a query from a file
    python3 shopify_api.py rest GET /themes.json
"""
import json, os, re, sys, time, urllib.request, urllib.error, urllib.parse

API_VERSION = os.environ.get("SHOPIFY_API_VERSION", "2025-07")
SHOP = os.environ.get("SHOPIFY_SHOP", "site-builder-stack.myshopify.com")
TOKEN_CACHE = os.environ.get(
    "SBS_TOKEN_CACHE",
    os.path.expanduser("~/.cache/sitebuilderstack/shopify-token.json"),
)
_DEFAULT_ID_FILE = "/opt/shopify-client-id.txt"
_DEFAULT_SECRET_FILE = "/opt/shopify-secret.txt"

_SECRETS: list = []


def _load(env_name: str, file_env: str, default_file: str) -> str:
    v = os.environ.get(env_name)
    if not v:
        path = os.environ.get(file_env, default_file)
        try:
            with open(path) as fh:
                v = fh.read().strip()
        except OSError as exc:
            raise SystemExit(
                f"Missing credential: set {env_name} or {file_env} "
                f"(tried {path}): {exc.strerror}"
            )
    if not v:
        raise SystemExit(f"Empty credential for {env_name}")
    _SECRETS.append(v)
    return v


CLIENT_ID = _load("SHOPIFY_CLIENT_ID", "SHOPIFY_CLIENT_ID_FILE", _DEFAULT_ID_FILE)
CLIENT_SECRET = _load("SHOPIFY_CLIENT_SECRET", "SHOPIFY_CLIENT_SECRET_FILE", _DEFAULT_SECRET_FILE)

_TOKEN_RE = re.compile(r"shp(at|ss|ca|pa|ut)_[0-9a-fA-F]{32}")


def redact(text: str) -> str:
    """Strip every known secret shape from a string before it is displayed."""
    if not isinstance(text, str):
        text = str(text)
    for s in _SECRETS:
        if s:
            text = text.replace(s, "[REDACTED]")
    return _TOKEN_RE.sub("[REDACTED_TOKEN]", text)


def _cached_token():
    try:
        with open(TOKEN_CACHE) as fh:
            blob = json.load(fh)
        if blob.get("expires_at", 0) > time.time() + 120 and blob.get("shop") == SHOP:
            _SECRETS.append(blob["access_token"])
            return blob["access_token"]
    except (OSError, ValueError, KeyError):
        pass
    return None


def get_token() -> str:
    """Mint (or reuse) an Admin API access token via the client_credentials grant."""
    tok = _cached_token()
    if tok:
        return tok
    data = urllib.parse.urlencode(
        {
            "grant_type": "client_credentials",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        }
    ).encode()
    req = urllib.request.Request(
        f"https://{SHOP}/admin/oauth/access_token", data=data, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            payload = json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        body = redact(exc.read().decode("utf8", "replace"))[:400]
        raise SystemExit(f"Token request failed: HTTP {exc.code}\n{body}")
    tok = payload["access_token"]
    _SECRETS.append(tok)
    os.makedirs(os.path.dirname(TOKEN_CACHE), exist_ok=True)
    fd = os.open(TOKEN_CACHE, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as fh:
        json.dump(
            {
                "access_token": tok,
                "shop": SHOP,
                "scope": payload.get("scope", ""),
                "expires_at": time.time() + int(payload.get("expires_in", 86399)),
            },
            fh,
        )
    return tok


def _request(url: str, method: str, body, extra_headers=None):
    headers = {
        "X-Shopify-Access-Token": get_token(),
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "SiteBuilderStack-Build/1.0",
    }
    headers.update(extra_headers or {})
    payload = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=payload, method=method, headers=headers)
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                raw = resp.read().decode("utf8", "replace")
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf8", "replace")
            if exc.code in (429, 502, 503, 504) and attempt < 4:
                time.sleep(2 ** attempt)
                continue
            raise SystemExit(f"HTTP {exc.code} {method} {url}\n{redact(raw)[:1200]}")
        except urllib.error.URLError as exc:
            if attempt < 4:
                time.sleep(2 ** attempt)
                continue
            raise SystemExit(f"Network error: {redact(repr(exc))}")


def gql(query: str, variables=None, tries: int = 4):
    """Run an Admin GraphQL operation. Retries on throttling. Raises on userErrors."""
    url = f"https://{SHOP}/admin/api/{API_VERSION}/graphql.json"
    for attempt in range(tries):
        out = _request(url, "POST", {"query": query, "variables": variables or {}})
        errs = out.get("errors")
        if errs:
            throttled = any(
                (e.get("extensions") or {}).get("code") == "THROTTLED" for e in errs
            )
            if throttled and attempt < tries - 1:
                time.sleep(3 * (attempt + 1))
                continue
            raise SystemExit("GraphQL errors:\n" + redact(json.dumps(errs, indent=2)))
        return out["data"]
    raise SystemExit("GraphQL: exhausted retries")


def rest(method: str, path: str, body=None):
    """Escape hatch for the few endpoints without GraphQL coverage (e.g. theme assets)."""
    url = f"https://{SHOP}/admin/api/{API_VERSION}{path}"
    return _request(url, method.upper(), body)


def check_user_errors(node: dict, label: str):
    for key in ("userErrors", "themeFilesUserErrors", "mediaUserErrors"):
        errs = (node or {}).get(key) or []
        if errs:
            raise SystemExit(f"{label} failed:\n" + redact(json.dumps(errs, indent=2)))
    return node


def main(argv):
    if not argv or argv[0] == "shop":
        data = gql(
            """{ shop { id name myshopifyDomain email currencyCode ianaTimezone
                 plan { displayName partnerDevelopment } primaryDomain { host url sslEnabled } } }"""
        )
        print(json.dumps(data, indent=2))
    elif argv[0] == "gql":
        with open(argv[1]) as fh:
            q = fh.read()
        variables = json.loads(argv[2]) if len(argv) > 2 else {}
        print(json.dumps(gql(q, variables), indent=2))
    elif argv[0] == "rest":
        print(json.dumps(rest(argv[1], argv[2], json.loads(argv[3]) if len(argv) > 3 else None), indent=2))
    elif argv[0] == "scopes":
        tok = get_token()
        with open(TOKEN_CACHE) as fh:
            print(json.load(fh)["scope"])
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
