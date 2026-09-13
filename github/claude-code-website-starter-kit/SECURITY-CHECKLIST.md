# Claude Code Security Checklist

A practical website security checklist for developers working with Claude Code. It covers
the mistakes that actually get made on small and mid-sized sites, in roughly the order they
cause damage.

**This list does not make a site secure.** No checklist does. It catches common, avoidable
problems. Anything handling payments, health data, or personal data at scale needs a real
security review by someone who does that for a living. Treat this as a floor, not a ceiling.

There is one addition worth making for AI-assisted development specifically: an assistant
that can read your repository can also read anything you leave in it. Most of the credential
exposure below is not exotic — it is a `.env` file that was never git-ignored.

## 1. Secrets and credentials

- [ ] No API keys, tokens, passwords or private keys anywhere in the repository
- [ ] Git **history** checked too — deleting a secret in a later commit does not remove it
- [ ] Any secret that was ever committed is treated as compromised and rotated
- [ ] `.env`, `.env.*`, `*.pem`, `*.key`, credential JSON files are all git-ignored
- [ ] `.env.example` contains variable names and no values
- [ ] Secrets live in the environment or a secret manager, injected at runtime
- [ ] Credential files on disk are readable only by their owner (`chmod 600`)
- [ ] No secret is ever printed to stdout, written to a log, or included in an error message
- [ ] No secret reaches client-side JavaScript, a template, or a build artefact
- [ ] Public and secret keys are not confused — publishable keys are safe, secret keys are not
- [ ] Diagnostic and debug output is redacted before it can be shared or pasted
- [ ] Screenshots and screen recordings checked before sharing
- [ ] A secret-scanning check runs in CI and blocks the merge

## 2. Environment separation

- [ ] Development, staging and production use different credentials
- [ ] Production credentials are not present on a developer machine
- [ ] Staging is not reachable by the public and is not indexable
- [ ] Test and seed data never contain real customer records
- [ ] Deleting or resetting a database requires an explicit, deliberate action

## 3. Transport and headers

- [ ] HTTPS enforced everywhere; HTTP redirects to it
- [ ] HSTS enabled, with a max-age you are prepared to honour
- [ ] No mixed content — no `http://` subresources on an HTTPS page
- [ ] TLS certificate valid, covering every hostname served, auto-renewing
- [ ] `Content-Security-Policy` set, as tight as the site allows
- [ ] CSP does not use `unsafe-inline`/`unsafe-eval` unless the reason is written down
- [ ] `X-Content-Type-Options: nosniff`
- [ ] `Referrer-Policy` set (`strict-origin-when-cross-origin` is a sane default)
- [ ] `X-Frame-Options` or CSP `frame-ancestors` set, unless embedding is intended
- [ ] `Permissions-Policy` disables device APIs the site does not use
- [ ] Server, framework and version headers removed or made uninformative

## 4. Input handling

- [ ] Every input validated on the **server**; client validation is a convenience only
- [ ] Allow-list validation where the set of valid values is known
- [ ] Output escaped for its destination: HTML, attribute, URL, JavaScript, SQL, shell
- [ ] Database access uses parameterised queries or an ORM — never string concatenation
- [ ] No user input reaches a shell command, `eval`, or a deserialiser
- [ ] File paths built from user input are normalised and confined to a known root
- [ ] Uploaded files: type and size limited, renamed, stored outside the web root, never executed
- [ ] Rich text or Markdown from users is sanitised with a maintained library, not a regex
- [ ] Redirect targets from query parameters are validated against an allow-list
- [ ] Request body size is capped

## 5. Authentication

- [ ] Passwords hashed with a modern algorithm (argon2, bcrypt, scrypt) — never MD5 or SHA-1
- [ ] No password length ceiling below ~64 characters, and no character-class rules that block passphrases
- [ ] Rate limiting and lockout on login, registration, and password reset
- [ ] Login and reset responses do not reveal whether an account exists
- [ ] Password reset tokens are random, single-use, short-lived, and invalidate on use
- [ ] Multi-factor authentication available for privileged accounts, and enabled on yours
- [ ] Default and shared accounts removed
- [ ] Admin surfaces are not on a guessable path *and* are properly authenticated — obscurity alone is not a control

## 6. Sessions

- [ ] Session cookies set `HttpOnly`, `Secure`, and `SameSite` (`Lax` or `Strict`)
- [ ] Session identifier regenerated on login and on privilege change
- [ ] Sessions expire, both idle and absolute
- [ ] Logout invalidates the session server-side, not only in the browser
- [ ] No session identifiers in URLs
- [ ] CSRF protection on every state-changing request that uses cookie auth
- [ ] Tokens stored somewhere XSS cannot read them, where the architecture allows it

## 7. Authorisation

- [ ] Every request checks authorisation on the server, per resource
- [ ] Object-level checks: the user owns or may access *this* record, not just this route type
- [ ] IDs in URLs are not trusted — try changing one and confirm you get a 403, not the data
- [ ] Deny by default; new routes are unauthorised until explicitly opened
- [ ] Hiding a control in the UI is not an authorisation check
- [ ] Roles reviewed; nobody has more than they need
- [ ] Administrative actions are logged with who did what

## 8. APIs and webhooks

- [ ] Public endpoints rate-limited
- [ ] CORS restricted to known origins; not `*` on anything authenticated
- [ ] Responses return only the fields needed — no leaking whole records
- [ ] Errors are generic to the caller and detailed only in server logs
- [ ] Incoming webhooks verify a signature or shared secret before doing anything
- [ ] Signature comparison is constant-time
- [ ] Webhook handlers are idempotent and reject replayed or stale timestamps
- [ ] Outgoing requests to user-supplied URLs are blocked from internal addresses (SSRF)

## 9. Dependencies

- [ ] Lockfile committed; installs are reproducible
- [ ] Vulnerability audit runs in CI and fails on critical findings
- [ ] Automated dependency updates enabled, with tests gating them
- [ ] New dependencies vetted: maintained, used, and worth the surface area
- [ ] No dependency added to do something the standard library already does
- [ ] Package names checked for typosquats
- [ ] Third-party scripts loaded with Subresource Integrity where the provider supports it
- [ ] Every third-party tag on the site is one you can name and justify

## 10. CI/CD and infrastructure

- [ ] Pipeline secrets stored in the platform's secret store, never in the config file
- [ ] Secrets masked in build logs, and logs are not public
- [ ] Builds from forked pull requests do not receive secrets
- [ ] Deploy credentials are scoped to what they deploy
- [ ] Branch protection on the production branch; review required
- [ ] Infrastructure state files (e.g. Terraform state) are remote, encrypted, access-controlled
- [ ] Backups exist, are encrypted, and a restore has actually been tested
- [ ] Access to production is limited and revoked when people leave

## 11. Production hygiene

- [ ] Debug mode off; stack traces never shown to users
- [ ] Source maps not served publicly, or served deliberately with that understood
- [ ] Directory listing disabled
- [ ] `.git`, `.env`, `/vendor`, backup files and editor swap files not reachable over HTTP
- [ ] Default installation and example files removed
- [ ] Error pages are generic and return the correct status code
- [ ] Unused routes, endpoints and admin tools removed rather than left disabled

## 12. Logging and monitoring

- [ ] Authentication events, authorisation failures and admin actions are logged
- [ ] Logs never contain passwords, tokens, card numbers or full personal records
- [ ] Log retention has a policy, and logs are access-controlled
- [ ] Alerting exists for error spikes and authentication anomalies
- [ ] Someone receives the alerts and knows what to do with them
- [ ] Clocks synchronised so timestamps can be correlated

## 13. Privacy and data

- [ ] Only data you have a use for is collected
- [ ] Personal data is encrypted in transit and at rest
- [ ] A retention and deletion policy exists and is actually applied
- [ ] Privacy policy reflects what the site really does, including third parties
- [ ] Cookie and tracking consent implemented where required
- [ ] Data subject requests (access, deletion) can be fulfilled
- [ ] Analytics and marketing tags do not leak identifiers into URLs or referrers

## 14. Working with an AI assistant

- [ ] The assistant is not pointed at a directory containing production credentials
- [ ] Permissions are scoped; destructive commands require confirmation
- [ ] Generated code that touches auth, payments, or user data gets a human review
- [ ] Generated dependency additions are checked — a hallucinated package name is a supply-chain risk
- [ ] Output pasted into an issue, PR or chat is checked for secrets first
- [ ] Hooks or settings enforce the rules that matter, rather than relying on a prompt file

## 15. Before you call it done

- [ ] Try to reach an admin route while logged out
- [ ] Try to read another user's record by changing an ID
- [ ] Submit a form with a script tag and confirm it renders as text
- [ ] Request `/.env`, `/.git/config`, and a backup filename, and confirm 404
- [ ] Check response headers on the live site, not the dev server
- [ ] Confirm the security checks you wrote can actually fail

## Related

- [Claude Code website launch checklist](https://sitebuilderstack.com/pages/claude-code-launch-checklist)
- [Claude Code website audit checklist](https://sitebuilderstack.com/pages/claude-code-website-audit-checklist)
- [Claude Code for enterprise teams](https://sitebuilderstack.com/blogs/guides/claude-code-enterprise)
- [OWASP Top Ten](https://owasp.org/www-project-top-ten/) — the canonical reference
- [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/) — practical, per-topic detail

The [Claude Code Website Launch System](https://sitebuilderstack.com/products/claude-code-website-launch-system) includes
the security audit prompts that work through this list against a real codebase.

## Licence

Free to use in any project, including client work. Do not resell or republish it as your own.
