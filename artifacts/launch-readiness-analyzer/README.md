# Launch Readiness Analyzer (claude.ai artifact)

Published: https://claude.ai/artifact/7Q9Fwe467U4cUTstrrp3hk

| File | Role |
| --- | --- |
| `config.js` | product name/URL/price/features/UTM + module names (the only commercial constants) |
| `questions.js` | 71 questions in 8 categories with weights, project-type scopes and why/do/validate texts |
| `engine.js` | pure scoring, bands, gaps, risks, launch plan, prompts, product mapping |
| `analytics.js` | track(name, props): canonical events, allowlist, dedupe, providers |
| `app.js` | hero, 8-step assessment, report, copy/download, persistence |

Tests: `node scripts/test-launch-analyzer.js` (in `tests/run-all.sh`). The product page is authoritative for facts; verified 2026-09-18.
