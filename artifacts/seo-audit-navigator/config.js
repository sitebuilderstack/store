/* SiteBuilder SEO Audit Navigator — configuration.
 *
 * One place for everything commercial and environmental. The product block
 * is the ONLY source of the product name, price and URL used by every CTA
 * and every event; change it here and nothing else.
 *
 * On 18 September 2026 the store sells no $9.99 "SiteBuilder SEO Auditor".
 * The product this navigator demonstrates — the fourteen audit modules — is
 * the Claude Code SEO & Website Audit Toolkit at $19.99, so the CTA points
 * at that real page and shows that real price. If a $9.99 SKU is created,
 * update the four fields below and republish; nothing else references them. */
window.SBSNAV_CONFIG = {
  artifact: { name: 'sitebuilder-seo-audit-navigator', version: '1.0.0' },
  product: {
    identifier: 'claude-code-seo-website-audit-toolkit',
    name: 'Claude Code SEO & Website Audit Toolkit',
    shortName: 'SEO Auditor',
    price: 19.99,
    currency: 'USD',
    url: 'https://sitebuilderstack.com/products/claude-code-seo-website-audit-toolkit',
  },
  attribution: {
    utm_source: 'claude_artifact',
    utm_medium: 'interactive_tool',
    utm_campaign: 'sitebuilder_seo_audit_navigator',
  },
  session: { idleMinutes: 30 },
  site: 'https://sitebuilderstack.com',
};
