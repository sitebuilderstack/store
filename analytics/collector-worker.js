/* First-party event collector — Cloudflare Worker.
 *
 * Receives the events the custom pixel forwards and stores COUNTS. It is
 * deliberately not an analytics product: there are no sessions, no visitor
 * records, no funnels and no way to reconstruct one person's path. It answers
 * one question — which events happen, on which pages, in which hour — because
 * that is the question the store actually has, and anything more would be
 * collecting data nobody has a use for.
 *
 * Why first-party rather than a vendor: the store's analytics decision is
 * recorded in docs/analytics/EVENTS.md — Shopify's own analytics, no second
 * vendor, no consent banner to add. A worker on your own domain keeps that
 * true. It sets no cookie, stores no identifier, and never sees a payload
 * containing one, because the pixel does not send one.
 *
 * DEPLOY
 *   npx wrangler kv namespace create SBS_EVENTS
 *   # put the returned id in wrangler.toml, then:
 *   npx wrangler deploy
 * Then set ENDPOINT in analytics/custom-pixel.js to the deployed URL + '/e'
 * and paste that file into Settings -> Customer events.
 *
 * READ
 *   GET /report?key=<READ_KEY>          counts for the last 7 days
 *   GET /report?key=<READ_KEY>&days=30
 */

const ALLOWED_ORIGIN = 'https://sitebuilderstack.com';
const MAX_BODY = 1024;

/* The pixel's own list. Anything not here is dropped rather than stored, so a
   misconfigured or hostile caller cannot fill the namespace with junk keys. */
const KNOWN = new Set([
  'pillar_view','pillar_article_click','pillar_up_click','pillar_cross_link',
  'related_guide_clicked','next_step_clicked','learning_path_next_clicked',
  'resource_cta_clicked','learning_path_started','learning_path_step',
  'learning_path_next','learning_path_prev','lesson_completed','lesson_saved',
  'learning_reset','readiness_product_clicked','lead_segment_build',
  'lead_segment_rank','lead_segment_convert','guide_filter_used',
  'guide_search_used','tool_started','tool_completed','tool_result_copied',
  'tool_reset','tool_cta_clicked','route_started','route_goal_selected',
  'route_level_selected','route_stage_selected','route_generated',
  'route_step_clicked','route_step_completed','route_step_uncompleted',
  'route_completed','route_reset','prompt_copied','command_copied',
  'claudemd_example_copied','code_copied','checklist_item_toggled',
  'checklist_reset','checklist_printed','lead_magnet_clicked',
  'product_cta_clicked','product_nav_clicked','product_ecosystem_clicked',
  'product_sample_viewed','bundle_cta_clicked',
]);

const cors = {
  'Access-Control-Allow-Origin': ALLOWED_ORIGIN,
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
  'Access-Control-Max-Age': '86400',
};

function day(t) {
  /* The pixel sends hour resolution; the key keeps the day and the hour so a
     report can group either way. */
  return typeof t === 'string' ? t.slice(0, 13) : new Date().toISOString().slice(0, 13);
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (request.method === 'OPTIONS') return new Response(null, { status: 204, headers: cors });

    if (url.pathname === '/e' && request.method === 'POST') {
      /* Reject anything not from the storefront. This is not security — an
         Origin header is trivially forged — it is hygiene, so ordinary
         crawlers and misrouted traffic do not become data. */
      if (request.headers.get('Origin') !== ALLOWED_ORIGIN) {
        return new Response(null, { status: 204, headers: cors });
      }
      let body;
      try {
        const text = await request.text();
        if (text.length > MAX_BODY) return new Response(null, { status: 204, headers: cors });
        body = JSON.parse(text);
      } catch { return new Response(null, { status: 204, headers: cors }); }

      const name = body?.e;
      if (!KNOWN.has(name)) return new Response(null, { status: 204, headers: cors });

      /* One counter per event / path / hour. Labels are counted separately and
         capped, so a label with unbounded cardinality cannot grow the store
         without limit. */
      const hour = day(body.t);
      const path = typeof body.p === 'string' ? body.p.slice(0, 120) : '-';
      const keys = [`c|${hour}|${name}|${path}`];
      if (typeof body.l === 'string' && body.l.length <= 80) {
        keys.push(`l|${hour.slice(0, 10)}|${name}|${body.l}`);
      }
      await Promise.all(keys.map(async (k) => {
        const n = parseInt((await env.SBS_EVENTS.get(k)) || '0', 10) + 1;
        /* 400 days, so a year-on-year comparison is possible and nothing is
           kept indefinitely for no reason. */
        await env.SBS_EVENTS.put(k, String(n), { expirationTtl: 400 * 86400 });
      }));
      return new Response(null, { status: 204, headers: cors });
    }

    if (url.pathname === '/report' && request.method === 'GET') {
      if (!env.READ_KEY || url.searchParams.get('key') !== env.READ_KEY) {
        return new Response('unauthorised', { status: 401 });
      }
      const days = Math.min(parseInt(url.searchParams.get('days') || '7', 10), 90);
      const since = new Date(Date.now() - days * 86400000).toISOString().slice(0, 13);
      const out = {};
      let cursor;
      do {
        const page = await env.SBS_EVENTS.list({ prefix: 'c|', cursor, limit: 1000 });
        for (const k of page.keys) {
          const [, hour, name, path] = k.name.split('|');
          if (hour < since) continue;
          const v = parseInt((await env.SBS_EVENTS.get(k.name)) || '0', 10);
          out[name] = out[name] || { total: 0, paths: {} };
          out[name].total += v;
          out[name].paths[path] = (out[name].paths[path] || 0) + v;
        }
        cursor = page.list_complete ? null : page.cursor;
      } while (cursor);
      return new Response(JSON.stringify({ days, events: out }, null, 1),
        { headers: { 'Content-Type': 'application/json' } });
    }

    return new Response('not found', { status: 404 });
  },
};
