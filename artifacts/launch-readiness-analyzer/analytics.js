/* analytics.js — one function: LRA_ANALYTICS.track(name, props).
 * Canonical event names, an allowlist of properties, one-shot dedupe for
 * open/start/complete, and providers: Shopify + Plausible when the page is
 * hosted on sitebuilderstack.com; otherwise a local journal (the claude.ai
 * artifact sandbox blocks every outbound request, so events cannot leave the
 * page — they are kept in the visitor's browser, never sent, and the
 * abstraction is where a provider is added later). Never throws. */
window.LRA_ANALYTICS = (function () {
  'use strict';
  var CFG = window.LRA_CONFIG;
  var EVENTS = ['artifact_opened', 'assessment_started', 'assessment_step_completed', 'assessment_completed', 'report_generated', 'launch_plan_copied', 'claude_prompt_copied', 'report_downloaded', 'product_recommendation_viewed', 'product_cta_clicked', 'product_page_visited', 'returning_artifact_session'];
  var ONCE = ['artifact_opened', 'assessment_started', 'assessment_completed', 'report_generated', 'product_recommendation_viewed', 'returning_artifact_session'];
  var ALLOWED = ['artifact_name', 'artifact_version', 'assessment_version', 'anonymous_visitor_id', 'session_id', 'timestamp', 'project_type', 'claude_usage', 'readiness_score_band', 'lowest_category', 'step', 'step_index', 'cta_location', 'product_url', 'report_format', 'prompt_category', 'visit_count', 'is_returning', 'environment', 'utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'referrer_host'];
  var mem = {};
  function lsGet(k, d) { try { var v = window.localStorage.getItem(k); return v == null ? d : JSON.parse(v); } catch (e) { return mem[k] === undefined ? d : mem[k]; } }
  function lsSet(k, v) { try { window.localStorage.setItem(k, JSON.stringify(v)); } catch (e) { mem[k] = v; } }
  function ssGet(k, d) { try { var v = window.sessionStorage.getItem(k); return v == null ? d : JSON.parse(v); } catch (e) { return mem['s:' + k] === undefined ? d : mem['s:' + k]; } }
  function ssSet(k, v) { try { window.sessionStorage.setItem(k, JSON.stringify(v)); } catch (e) { mem['s:' + k] = v; } }
  function rid(p) { var a = new Uint8Array(10); try { window.crypto.getRandomValues(a); } catch (e) { for (var i = 0; i < 10; i++) a[i] = Math.random() * 256 | 0; } return p + Array.prototype.map.call(a, function (b) { return ('0' + b.toString(16)).slice(-2); }).join(''); }

  // visitor + session (anonymous; a refresh or a second tab within 30 minutes is the same session)
  var now = Date.now(), IDLE = 30 * 60 * 1000;
  var v = lsGet('lra-visitor', null); var isNew = !v;
  if (!v) v = { id: rid('v_'), first_seen: now, last_seen: now, visit_count: 0, session: null };
  var s = ssGet('lra-session', null);
  if (!s && v.session && now - v.session.last_activity <= IDLE) s = v.session;
  var newSession = false;
  if (!s || now - s.last_activity > IDLE) { newSession = true; s = { id: rid('s_'), started: now, last_activity: now }; v.visit_count++; }
  var returning = newSession && !isNew && v.visit_count > 1;
  s.last_activity = now; v.last_seen = now; v.session = s; lsSet('lra-visitor', v); ssSet('lra-session', s);

  var inbound = (function () { var o = {}; try { new URLSearchParams(window.location.search).forEach(function (val, k) { if (/^utm_/.test(k)) o[k] = String(val).slice(0, 80); }); } catch (e) {} try { o.referrer_host = document.referrer ? new URL(document.referrer).hostname : ''; } catch (e) {} return o; })();
  var environment = (window.Shopify && window.Shopify.analytics && typeof window.Shopify.analytics.publish === 'function') ? 'sitebuilderstack' : 'claude_artifact';
  var providers = [];
  if (environment === 'sitebuilderstack') providers.push({ name: 'shopify', send: function (n, p) { try { window.Shopify.analytics.publish(n, p); } catch (e) {} try { if (typeof window.plausible === 'function') window.plausible(n, { props: p }); } catch (e) {} } });
  providers.push({ name: 'local', send: function (n, p) { var j = lsGet('lra-journal', []); j.push({ e: n, p: p }); if (j.length > 300) j = j.slice(-300); lsSet('lra-journal', j); } });

  function reduce(props) { var o = {}; ALLOWED.forEach(function (k) { var x = props[k]; if (x === undefined || x === null || x === '') return; o[k] = typeof x === 'string' ? x.slice(0, 120) : (typeof x === 'number' || typeof x === 'boolean') ? x : String(x).slice(0, 120); }); return o; }
  function track(name, props) {
    try {
      if (EVENTS.indexOf(name) === -1) return false;
      if (ONCE.indexOf(name) !== -1) { var k = 'lra-once:' + s.id + ':' + name; if (ssGet(k, false)) return false; ssSet(k, true); }
      var payload = reduce(Object.assign({ artifact_name: CFG.artifact.name, artifact_version: CFG.artifact.version, assessment_version: CFG.artifact.assessmentVersion, anonymous_visitor_id: v.id, session_id: s.id, timestamp: new Date().toISOString(), environment: environment, visit_count: v.visit_count }, inbound, props || {}));
      providers.forEach(function (p) { try { p.send(name, payload); } catch (e) {} });
      s.last_activity = Date.now(); ssSet('lra-session', s); v.session = s; lsSet('lra-visitor', v);
      return true;
    } catch (e) { return false; }
  }
  function productUrl(content) {
    var u = new URL(CFG.product.productUrl);
    Object.keys(CFG.product.utm).forEach(function (k) { u.searchParams.set(k, CFG.product.utm[k]); });
    u.searchParams.set('utm_content', String(content || 'unknown').replace(/[^a-z0-9_-]/gi, '').slice(0, 40) || 'unknown');
    u.searchParams.set('artifact_ref', v.id);
    return u.toString();
  }
  return { track: track, productUrl: productUrl, visitor: function () { return v; }, isReturning: returning, journal: function () { return lsGet('lra-journal', []); }, environment: environment, providers: providers.map(function (p) { return p.name; }) };
})();
