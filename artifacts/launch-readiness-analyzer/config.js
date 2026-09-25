/* Product configuration — the ONLY place commercial facts live. Verified
 * against https://sitebuilderstack.com/products/claude-code-website-launch-system
 * on 18 September 2026 (price $19.99; 113 files across 17 modules; more than
 * 110,000 words; 100 reusable prompts). Update here, nowhere else. */
window.LRA_CONFIG = {
  artifact: { name: 'launch-readiness-analyzer', version: '1.0.0', assessmentVersion: '2026-09-18' },
  product: {
    productName: 'The Claude Code Website Launch System',
    productUrl: 'https://sitebuilderstack.com/products/claude-code-website-launch-system',
    price: 19.99,
    currency: 'USD',
    description: 'A repeatable system for taking Claude Code website projects from idea to production.',
    features: [
      ['17 modules', 'from research and planning to the first thirty days after launch'],
      ['113 files', 'plain Markdown you own; over 110,000 words'],
      ['100 reusable prompts', 'single-purpose, ready to save as slash commands'],
      ['Multiple platforms', 'Shopify, WordPress, Astro, SaaS applications, landing pages'],
      ['SEO + security + accessibility', 'audits with checklists, not just advice'],
      ['Deployment + CI/CD', 'GitHub workflows, four Actions files, Cloudflare guides'],
      ['Launch + post-launch', 'pre-launch, launch day, 24-hour, 7-day and 30-day reviews'],
      ['Unlimited projects', 'single-user licence, client work included'],
      ['One-time purchase', 'instant download, no subscription'],
    ],
    utm: { utm_source: 'claude_artifact', utm_medium: 'interactive_tool', utm_campaign: 'launch_readiness_analyzer' },
  },
  /* The module names below are the product's own (from its listing). */
  modules: {
    master: '01 — Master System (planning, discovery, roadmap, the staged build prompt)',
    claude: '02 — Claude Code Configuration (production CLAUDE.md template, memory guidance)',
    seo: '03 — SEO System (search architecture, technical audit, keyword research, clusters, internal linking, schema, sitemaps, robots.txt)',
    shopify: '04 — Shopify System (build prompt, audits, launch checklist)',
    wordpress: '05 — WordPress System (build prompt, audits, launch checklist)',
    astro: '06 — Astro System (build prompt, audits, launch checklist)',
    saas: '07 — SaaS Application System (build prompt, audits, launch checklist)',
    landing: '08 — Landing Page System (build prompt, audits, launch checklist)',
    deploy: '09–10 — Deployment (GitHub repository setup, CI/CD, four GitHub Actions files, Cloudflare DNS/Pages/caching/security)',
    security: '11 — Security (secret scanning, OWASP review, dependency auditing, HTTP security headers, production security checklist)',
    a11y: '12 — Accessibility (WCAG 2.2 AA audit, keyboard navigation, screen reader testing, checklist)',
    engines: '13 — Search Engines (Google Search Console, Bing Webmaster Tools, IndexNow)',
    checklists: '14 — Checklists (pre-launch, launch day, first 24 hours, 7-day and 30-day reviews)',
    prompts: '15 — Prompt Library (100 reusable single-purpose prompts)',
    bonus: '16–17 — Templates & Bonus (briefs, specs, QA and launch reports; rescue, existing-site audit, redesign, competitor analysis, code review)',
  },
  site: 'https://sitebuilderstack.com',
};
