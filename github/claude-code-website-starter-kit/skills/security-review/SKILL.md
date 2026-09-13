---
name: security-review
description: Run a defensive security review of code and configuration you own. Covers secrets and git history, dependencies, authentication, authorisation, input handling, sessions, headers, browser exposure, webhooks, CI/CD and logging.
when_to_use: Use when asked to review security, check for secrets or vulnerabilities, audit authentication or authorisation, or before shipping something that handles user data.
disable-model-invocation: true
argument-hint: [path]
allowed-tools: Read Grep Glob Bash
---

# Defensive security review

Review **$1**. Read code and configuration, and make ordinary requests to systems you
own.

## Hard limits

**Do not attempt exploitation of any kind** — no credential stuffing, no brute force,
no host scanning, no request designed to trigger a vulnerability. That is penetration
testing. It needs written authorisation and someone who does it for a living.

**Never print a secret value.** Print enough to locate it and no more. A report
containing the actual keys is itself a disclosure, and it will end up in an issue
tracker.

Report findings. Do not fix anything in this run.

## Scope first

Half an hour establishing what the system is makes everything after it specific.
Inventory: language and framework versions, how authentication works, where data lives
and how it is queried, every route and which require auth, third-party services and
what credentials each holds, file upload destinations, webhook receivers, admin
surfaces, deployment and pipeline, anything touching payment. Give file paths. **If you
cannot determine something, say so** — a guess propagates into everything downstream.

## Order

Secrets come third because a leaked credential makes every other finding academic.

1. **Scope and inventory** (above).
2. **Secrets** — keys, tokens, private keys, database URLs with passwords, hard-coded
   or test credentials, in source, config, build output and the client bundle. Then
   **git history**: deleting a secret in a later commit does not remove it.
   ```
   git log -p -S'API_KEY' --oneline | head -50
   ```
   A dedicated scanner beats grep here. **Any secret ever committed is compromised and
   must be rotated** — rewriting history does not un-clone the repository.
3. **Dependencies** — `npm audit` / `pip-audit` / `bundle audit`. Then the part a
   scanner cannot do: for each high-severity advisory, say whether the vulnerable code
   path is actually reachable from this codebase.
4. **Authentication** — password hashing (argon2, bcrypt, scrypt — never MD5 or SHA);
   reset tokens random, single-use and short-lived; rate limiting on login, registration
   and reset; no account enumeration through body, status **or timing**; MFA available
   for privileged accounts; no password length ceiling that blocks passphrases.
5. **Authorisation** — the one that matters most. For every route returning or
   modifying a record, find the line verifying the current user may access **that
   specific record**, not merely that they are logged in. List any route where you
   cannot find one.
6. **Input handling** — parameterised queries, never string concatenation; output
   escaped for its destination; no user input reaching a shell, `eval` or a
   deserialiser; file paths normalised and confined; uploads type- and size-limited,
   renamed, stored outside the web root, never executed; server-side URL fetches
   blocked from internal addresses.
7. **Sessions** — cookies `HttpOnly`, `Secure`, `SameSite`; identifier regenerated on
   login and privilege change; expiry both idle and absolute; logout invalidates
   server-side; CSRF protection on cookie-authenticated state changes.
8. **Headers** — check the live response, not the config; a proxy can add or strip
   them.
   ```
   curl -sI https://example.com | grep -iE 'content-security-policy|strict-transport|x-content-type|referrer-policy|permissions-policy|x-frame'
   ```
   The right values depend on the application. Do not propose a generic set that breaks
   an embed the site needs.
9. **Browser exposure** — secrets in the bundle, source maps served in production,
   unsafe DOM writes, every third-party script named and justified, tokens in
   `localStorage`.
10. **APIs and webhooks** — rate limiting; CORS not `*` on anything authenticated;
    responses returning only needed fields; errors generic to the caller. For each
    webhook: signature verification, constant-time comparison, and what happens on a
    replayed or duplicate delivery.
11. **CI/CD** — secrets in the platform store not the config file, masked in logs, not
    exposed to forked pull requests; deploy credentials scoped; branch protection.
12. **Logging** — what accidentally lands in them: tokens, passwords, card numbers,
    personal data, stack traces returned to users.

## Output

```
Finding:
Severity:       critical | high | medium | low
Location:       file:line, or the URL
Evidence:       what you observed
Risk:           what an attacker gains
Fix:            the smallest change that resolves it
Validation:     how I confirm the fix worked
```

Rank by real impact on **this** system, not by generic severity. Do not report a
missing nice-to-have as critical. End with what you could not check.

## What this does not replace

Penetration testing, threat modelling, compliance auditing, runtime and behavioural
analysis, and a specialist's judgement on anything holding payment, health or
large-scale personal data. This removes the large avoidable class of problems so a
specialist's time goes on what only they can find.

See `SECURITY-CHECKLIST.md` in this repository.
