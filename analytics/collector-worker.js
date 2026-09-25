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
  'product_selector_started','product_selector_completed','product_selector_cta_clicked','product_selector_alt_clicked','product_recommended','lifecycle_guide_clicked','lifecycle_product_clicked','nav_menu_opened',
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
  'engagement_module_started','artifact_generated','artifact_copied','artifact_exported','artifact_saved',
  'lab_started','lab_completed','challenge_started','challenge_completed','project_created',
  'project_resumed','related_product_clicked',
  'sitebuilderstack_product_page_visited','product_purchased','account_created',
  'monetization_offer_view','monetization_cta_click','monetization_lead_submitted',
  'affiliate_link_clicked',
]);
/* Events that reach the collector from Shopify webhooks rather than the pixel. */
const WEBHOOK_EVENTS = new Set(['account_created']);

const cors = {
  'Access-Control-Allow-Origin': ALLOWED_ORIGIN,
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
  'Access-Control-Max-Age': '86400',
};

async function verifyHmac(secret, raw, given) {
  const key = await crypto.subtle.importKey('raw', new TextEncoder().encode(secret), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);
  const sig = await crypto.subtle.sign('HMAC', key, new TextEncoder().encode(raw));
  const b64 = btoa(String.fromCharCode(...new Uint8Array(sig)));
  if (b64.length !== given.length) return false;
  let diff = 0; for (let i = 0; i < b64.length; i++) diff |= b64.charCodeAt(i) ^ given.charCodeAt(i);
  return diff === 0;
}

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

      /* Purchase idempotency: one order id is counted once, ever. A refreshed
         thank-you page, a second tab, or a pixel retry hits the same key and
         is dropped before any counter moves. The key keeps the day it was
         first seen so revenue lands on the order's own date. */
      if (name === 'product_purchased') {
        const oid = typeof body.o === 'string' && /^[A-Za-z0-9:_\/.-]{1,64}$/.test(body.o) ? body.o : null;
        if (!oid) return new Response(null, { status: 204, headers: cors });
        const seenKey = `seen|${oid}|${typeof body.m === 'string' ? body.m.slice(0, 80) : '-'}`;
        if (await env.SBS_EVENTS.get(seenKey)) return new Response(null, { status: 204, headers: cors });
        await env.SBS_EVENTS.put(seenKey, day(body.t), { expirationTtl: 400 * 86400 });
        if (typeof body.v === 'number' && body.v >= 0 && body.v < 100000) {
          const rk = `rev|${day(body.t).slice(0, 10)}|${typeof body.m === 'string' ? body.m.slice(0, 80) : '-'}|${typeof body.r === 'string' ? 'artifact' : 'other'}`;
          const cur = parseFloat((await env.SBS_EVENTS.get(rk)) || '0');
          await env.SBS_EVENTS.put(rk, String(Math.round((cur + body.v) * 100) / 100), { expirationTtl: 400 * 86400 });
        }
      }

      /* One counter per event / path / hour. Labels are counted separately and
         capped, so a label with unbounded cardinality cannot grow the store
         without limit. */
      const hour = day(body.t);
      const path = typeof body.p === 'string' ? body.p.slice(0, 120) : '-';
      const keys = [`c|${hour}|${name}|${path}`];
      if (typeof body.l === 'string' && body.l.length <= 80) {
        keys.push(`l|${hour.slice(0, 10)}|${name}|${body.l}`);
      }
      /* Engagement events carry an identifier (module, lab, challenge,
         product handle or coarse kind) instead of a label; same daily
         counter shape, same cap, and only [a-z0-9-] is accepted. */
      if (typeof body.m === 'string' && /^[a-z0-9-]{1,80}$/.test(body.m)) {
        keys.push(`m|${hour.slice(0, 10)}|${name}|${body.m}`);
      }
      /* Artifact attribution: a daily count per event of visits that carry an
         artifact_ref, and the set of distinct refs per event per day (so the
         funnel can be built as unique visitors, not hits). The ref is an
         anonymous id minted in the navigator; it is never joined to a person. */
      if (typeof body.r === 'string' && /^v_[a-f0-9]{8,32}$/.test(body.r)) {
        keys.push(`a|${hour.slice(0, 10)}|${name}|artifact`);
        await env.SBS_EVENTS.put(`u|${hour.slice(0, 10)}|${name}|${body.r}`, '1', { expirationTtl: 400 * 86400 });
      }
      await Promise.all(keys.map(async (k) => {
        const n = parseInt((await env.SBS_EVENTS.get(k)) || '0', 10) + 1;
        /* 400 days, so a year-on-year comparison is possible and nothing is
           kept indefinitely for no reason. */
        await env.SBS_EVENTS.put(k, String(n), { expirationTtl: 400 * 86400 });
      }));
      return new Response(null, { status: 204, headers: cors });
    }

    /* account_created — from Shopify's customers/create webhook, verified
       with the app's webhook secret (HMAC-SHA256 over the raw body). Fires
       only when Shopify has actually created the customer record; the
       storefront cannot observe registration under new customer accounts.
       Only the customer's id and the note/tags that carry attribution are
       read; email, name and address are not stored. */
    if (url.pathname === '/webhooks/customers-create' && request.method === 'POST') {
      const raw = await request.text();
      const given = request.headers.get('X-Shopify-Hmac-Sha256') || '';
      if (!env.SHOPIFY_WEBHOOK_SECRET || !(await verifyHmac(env.SHOPIFY_WEBHOOK_SECRET, raw, given))) {
        return new Response('unauthorised', { status: 401 });
      }
      let c; try { c = JSON.parse(raw); } catch { return new Response(null, { status: 204 }); }
      const id = String(c?.id || '');
      if (!id) return new Response(null, { status: 204 });
      const seenKey = `seen|customer|${id}`;
      if (await env.SBS_EVENTS.get(seenKey)) return new Response(null, { status: 204 });
      await env.SBS_EVENTS.put(seenKey, '1', { expirationTtl: 400 * 86400 });
      const hour = new Date().toISOString().slice(0, 13);
      const ref = typeof c?.note === 'string' && /artifact_ref=(v_[a-f0-9]{8,32})/.exec(c.note)?.[1];
      const keys = [`c|${hour}|account_created|-`];
      if (ref) { keys.push(`a|${hour.slice(0, 10)}|account_created|artifact`); await env.SBS_EVENTS.put(`u|${hour.slice(0, 10)}|account_created|${ref}`, '1', { expirationTtl: 400 * 86400 }); }
      await Promise.all(keys.map(async (k) => { const n = parseInt((await env.SBS_EVENTS.get(k)) || '0', 10) + 1; await env.SBS_EVENTS.put(k, String(n), { expirationTtl: 400 * 86400 }); }));
      return new Response(null, { status: 204 });
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
