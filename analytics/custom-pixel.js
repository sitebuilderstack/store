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
  // engagement layer (Try-this modules, labs, My Projects, Weekly Fix);
  // payloads are ids only, enforced in the storefront's track()
  'engagement_module_started', 'artifact_generated', 'artifact_copied',
  'artifact_exported', 'artifact_saved', 'lab_started', 'lab_completed',
  'challenge_started', 'challenge_completed', 'project_created',
  'project_resumed', 'related_product_clicked',
  // SEO Audit Navigator funnel (docs/analytics/ARTIFACT-FUNNEL.md): the
  // storefront publishes the arrival; the purchase is derived below from
  // Shopify's own checkout_completed, never from a click.
  'sitebuilderstack_product_page_visited',
  // monetization paths (docs/monetization/): offers viewed, CTAs clicked,
  // leads CONFIRMED (never on submit), affiliate links clicked
  'monetization_offer_view', 'monetization_cta_click', 'monetization_lead_submitted',
  'affiliate_link_clicked',
  // 'product_purchased' is not subscribed (it is not a storefront event); it is
  // sent from the checkout_completed handler below and listed in the
  // collector's KNOWN set.

  // product picker, lifecycle page and header menu
  // (added 25 September 2026: published by the theme since the picker shipped,
  //  but absent from this list, EVENTS.md and the collector — all three agreed
  //  with each other and none was checked against the theme)
  'product_selector_started', 'product_selector_completed', 'product_selector_cta_clicked', 'product_selector_alt_clicked', 'product_recommended', 'lifecycle_guide_clicked', 'lifecycle_product_clicked', 'nav_menu_opened',
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
    /* Engagement events carry a public identifier instead of a label: the
       module, lab, challenge or product handle, or a coarse kind. One field,
       first one present, already restricted to [a-z0-9-] upstream. */
    m: ['module', 'lab', 'challenge', 'product', 'product_identifier', 'offer_id', 'partner', 'kind'].map((k) => data?.[k]).find((v) => typeof v === 'string')?.slice(0, 80),
    /* Anonymous artifact attribution id (v_ + hex), from the event or the
       first-party cookie the storefront set on arrival. An id, not a person. */
    r: [data?.artifact_ref, readCookie('sbs_aref')].find((v) => typeof v === 'string' && /^v_[a-f0-9]{8,32}$/.test(v)),
    /* Order id for purchase deduplication (see product_purchased below). */
    o: typeof data?.order_id === 'string' ? data.order_id.slice(0, 64) : undefined,
    v: typeof data?.value === 'number' ? data.value : undefined,
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

function readCookie(name) {
  try {
    const raw = browser?.cookie?.get ? browser.cookie.get(name) : null;
    // browser.cookie.get returns a promise in the pixel sandbox; the value is
    // resolved by the caller below where it matters (checkout_completed).
    return typeof raw === 'string' ? raw : undefined;
  } catch (e) { return undefined; }
}

EVENTS.forEach((name) => {
  analytics.subscribe(name, (event) => {
    send(name, event?.customData || {});
  });
});

/* product_purchased — the authoritative purchase event. Fired only from
   Shopify's standard checkout_completed (the order exists), one line per
   product in the order, carrying the order id so the collector can drop a
   repeat (a refreshed thank-you page re-emits checkout_completed). The
   pixel also refuses to send the same order twice from this browser. The
   artifact attribution id comes from the cookie the storefront set when the
   visitor arrived from the navigator; absent that cookie the purchase is
   still counted, just unattributed. No customer, payment or address field
   is read. */
analytics.subscribe('checkout_completed', async (event) => {
  try {
    const checkout = event?.data?.checkout;
    const orderId = String(checkout?.order?.id || checkout?.token || '');
    if (!orderId) return;
    const seenKey = 'sbs_purchase_sent_' + orderId;
    try { if (await browser.sessionStorage.getItem(seenKey)) return; await browser.sessionStorage.setItem(seenKey, '1'); } catch (e) { /* no storage: the collector still dedupes */ }
    let ref;
    try { ref = await browser.cookie.get('sbs_aref'); } catch (e) { ref = undefined; }
    let camp;
    try { camp = await browser.cookie.get('sbs_acamp'); } catch (e) { camp = undefined; }
    (checkout?.lineItems || []).forEach((li) => {
      const handle = li?.variant?.product?.url ? String(li.variant.product.url).split('/products/')[1]?.split('?')[0] : undefined;
      send('product_purchased', {
        product_identifier: handle || String(li?.variant?.product?.id || ''),
        label: String(li?.title || '').slice(0, 80),
        path: '/checkout/thank-you',
        artifact_ref: ref,
        order_id: orderId,
        value: typeof li?.finalLinePrice?.amount === 'number' ? li.finalLinePrice.amount : undefined,
        campaign: camp,
      });
    });
  } catch (e) { /* analytics never breaks checkout */ }
});
