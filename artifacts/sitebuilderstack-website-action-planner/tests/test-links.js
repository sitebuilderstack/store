#!/usr/bin/env node
/* tests/test-links.js — every URL the artifact can send a visitor to must
 * resolve to 200 on the live storefront, with the campaign parameters
 * attached exactly as the artifact attaches them. Requires network access;
 * it is a separate file so tests/test-rules.js stays offline.
 *
 *   node tests/test-links.js
 */
'use strict';
const https = require('https');
const path = require('path');
const CAT = require(path.join(__dirname, '..', 'products.json'));

const UTM = { utm_source: 'claude_artifact', utm_medium: 'interactive_tool', utm_campaign: 'website_action_planner' };

function head(url) {
  return new Promise((resolve) => {
    const req = https.request(url, { method: 'GET', headers: { 'User-Agent': 'SiteBuilderStack-link-check/1.0' } }, (res) => {
      const chunks = [];
      res.on('data', (c) => { if (chunks.length < 40) chunks.push(c); });
      res.on('end', () => resolve({ status: res.statusCode, location: res.headers.location || '', body: Buffer.concat(chunks).toString('utf8') }));
    });
    req.on('error', (e) => resolve({ status: 0, error: e.message }));
    req.setTimeout(20000, () => { req.destroy(); resolve({ status: 0, error: 'timeout' }); });
    req.end();
  });
}

(async function () {
  let pass = 0, fail = 0;
  const targets = [];
  CAT.products.forEach((p) => targets.push({ what: 'product ' + p.id, url: p.url, tagged: true, expect: p.title }));
  CAT.freeResources.forEach((f) => targets.push({ what: 'free ' + f.id, url: f.url, tagged: true }));
  targets.push({ what: 'planner share target', url: 'https://sitebuilderstack.com/pages/resources', tagged: false });

  for (const t of targets) {
    const u = new URL(t.url);
    if (t.tagged) { Object.keys(UTM).forEach((k) => u.searchParams.set(k, UTM[k])); u.searchParams.set('utm_content', 'link_check'); }
    const r = await head(u.toString());
    const okStatus = r.status === 200;
    const okTitle = !t.expect || r.body.indexOf('<title') !== -1;
    if (okStatus && okTitle) { pass++; console.log('  ✓ ' + t.what + '  ' + r.status + '  ' + u.pathname); }
    else { fail++; console.log('  ✗ ' + t.what + '  ' + (r.status || r.error) + (r.location ? ' → ' + r.location : '') + '  ' + u.toString()); }
  }
  console.log('\n' + pass + ' reachable, ' + fail + ' broken\n');
  process.exit(fail ? 1 : 0);
})();
