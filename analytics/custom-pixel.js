/* Site Builder Stack — custom pixel
 *
 * Paste into Shopify admin: Settings -> Customer events -> Add custom pixel.
 * Permission: "Analytics". It reads no customer data and sets no cookie.
 *
 * WHY THIS EXISTS
 * The storefront publishes about thirty custom events through
 * `Shopify.analytics.publish` — tool completions, lesson completions, learning
 * path steps, product placements. Shopify does NOT surface custom events in the
 * standard Analytics reports; it delivers them to Web Pixels and nowhere else.
 * Without a pixel subscribing to them, every one of those events fires into
 * nothing. That was the state of this store until this file existed.
 *
 * WHAT IT SENDS
 * Event name, the short label the storefront already attaches, the path, and a
 * coarse timestamp. That is all. Specifically NOT sent:
 *   - anything typed into a tool (the storefront never puts it in the payload)
 *   - any identifier, cookie, or fingerprint
 *   - the referrer, the user agent, or the IP beyond what the transport reveals
 *   - saved learning progress, which never leaves the browser at all
 *
 * DESTINATION
 * Set ENDPOINT below. `analytics/collector-worker.js` in the repository is a
 * first-party collector that runs on Cloudflare Workers and stores counts only.
 * Leaving ENDPOINT empty is a supported state: the pixel then does nothing at
 * all rather than half-working, which is the honest default for a file whose
 * destination has not been decided.
 */
const ENDPOINT = '';           // e.g. 'https://collect.example.com/e'
const SAMPLE = 1;              // 1 = send everything. Lower only if volume demands it.

/* Every event the storefront publishes, from docs/analytics/EVENTS.md.
   Listed explicitly rather than subscribed with a wildcard: a wildcard would
   also forward Shopify's own standard events, which are already recorded, and
   double-counting them would make both numbers wrong. */
const EVENTS = [
  // discovery and navigation
  'pillar_view', 'pillar_article_click', 'pillar_up_click', 'pillar_cross_link',
  'related_guide_clicked', 'next_step_clicked', 'learning_path_next_clicked',
  'resource_cta_clicked',
  // learning paths
  'learning_path_started', 'learning_path_step', 'learning_path_next',
  'learning_path_prev',
  // learning progress
  'lesson_completed', 'lesson_saved', 'learning_reset',
  'readiness_product_clicked',
  // lead capture
  'lead_segment_build', 'lead_segment_rank', 'lead_segment_convert',
  // guide library
  'guide_filter_used', 'guide_search_used',
  // free tools
  'tool_started', 'tool_completed', 'tool_result_copied', 'tool_reset',
  'tool_cta_clicked',
  // roadmap
  'route_started', 'route_goal_selected', 'route_level_selected',
  'route_stage_selected', 'route_generated', 'route_step_clicked',
  'route_step_completed', 'route_step_uncompleted', 'route_completed',
  'route_reset',
  // copyable resources
  'prompt_copied', 'command_copied', 'claudemd_example_copied', 'code_copied',
  // checklists and resources
  'checklist_item_toggled', 'checklist_reset', 'checklist_printed',
  'lead_magnet_clicked',
  // commerce placements
  'product_cta_clicked', 'product_nav_clicked', 'product_ecosystem_clicked',
  'product_sample_viewed', 'bundle_cta_clicked',
];

function send(name, data) {
  if (!ENDPOINT) return;
  if (SAMPLE < 1 && Math.random() > SAMPLE) return;

  const body = JSON.stringify({
    e: name,
    /* The storefront's own label, truncated again here as a belt-and-braces
       measure. The storefront already caps it at 80, but this file must not
       depend on that staying true. */
    l: typeof data?.label === 'string' ? data.label.slice(0, 80) : undefined,
    p: typeof data?.path === 'string' ? data.path.slice(0, 200) : undefined,
    /* Hour resolution. Minute or second resolution starts to be a weak
       identifier when volume is low, and nothing here needs it. */
    t: new Date().toISOString().slice(0, 13),
  });

  try {
    /* keepalive so an event fired on the click that navigates away is not
       cancelled by the unload. Failures are swallowed: analytics must never
       be able to break a page, and there is nothing useful to do with the
       error inside a sandbox. */
    fetch(ENDPOINT, {
      method: 'POST',
      keepalive: true,
      headers: { 'Content-Type': 'text/plain;charset=UTF-8' },
      body,
    }).catch(() => {});
  } catch (e) { /* ignore */ }
}

EVENTS.forEach((name) => {
  analytics.subscribe(name, (event) => {
    send(name, event?.customData || {});
  });
});
