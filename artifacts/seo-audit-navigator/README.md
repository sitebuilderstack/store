# SEO Audit Navigator (claude.ai artifact)

Published: https://claude.ai/artifact/UCAPFvAEMcxF7zo857SdkF (private until shared).

An interactive SEO diagnostic and product-demo funnel: a four-step audit
wizard that builds an ordered, evidence-first audit plan; four fictional
sample audits with a dashboard and finding details; the "Don't trust a green
checkmark" and "break the test" demonstrations; an audit planner (rules, with
optional Claude refinement through the `sample` capability); a toolkit
explorer of the fourteen modules; a report generator (Markdown or HTML via the
`downloads` capability); and the upgrade page.

## Files

| File | Role |
| --- | --- |
| `index.html` | shell, styles (light + dark, three-state theme), script order |
| `config.js` | the ONLY place the product name/price/URL and campaign parameters live |
| `data.js` | modules, wizard options, recommendation rules, fictional samples |
| `app.js` | router (hash, no reload), state, views, report generator, capabilities |
| `analytics/storage.js` | guarded localStorage/sessionStorage |
| `analytics/events.js` | canonical event names + allowed property list |
| `analytics/session.js` | anonymous visitor / session / audit ids; returning detection |
| `analytics/attribution.js` | inbound utm/referrer; outbound product URL builder |
| `analytics/analytics.js` | `track(name, props)`: name check, prop allowlist, one-shot dedupe, providers |

Design and limits of the funnel: `docs/analytics/ARTIFACT-FUNNEL.md`.

## Product

The brief named a "$9.99 SiteBuilder SEO Auditor". No such product exists in
the store; the fourteen modules the navigator demonstrates are the Claude
Code SEO & Website Audit Toolkit ($19.99), so every CTA links to that real
page and shows that real price. To switch products, edit `config.js` only.

## Republishing

    # from the repository root, in the session that owns the artifact (or pass url)
    Artifact tool: file_path artifacts/seo-audit-navigator/index.html, root artifacts/seo-audit-navigator,
      files {config.js, data.js, app.js, analytics/*.js}, capabilities {downloads: true, sample: {}}

Tests: `node scripts/test-navigator-analytics.js` (part of `tests/run-all.sh`).
