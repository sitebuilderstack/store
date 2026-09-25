/* analytics/analytics.js — the one function the app calls: track(name, props).
 *
 * Providers, chosen at load, in this order:
 *   shopify   — window.Shopify.analytics.publish exists (the navigator is
 *               hosted on sitebuilderstack.com as a page); events also go to
 *               Plausible as custom events when window.plausible exists.
 *   local     — the claude.ai artifact sandbox. Its Content Security Policy
 *               blocks every outbound request (fetch, beacons, image pixels,
 *               third-party scripts), so events cannot leave the page. They
 *               are journaled in localStorage (capped) and shown to the
 *               visitor under Help, and the visit's funnel state travels to
 *               the store in the upgrade link (attribution.js). This is a
 *               limitation of the sandbox, stated rather than papered over.
 * Adding a provider is one object with a send(name, props) method; nothing
 * in the app changes. Every event passes through the same gates: the name
 * must be canonical, the props are reduced to the allowlist, and the
 * one-shot events are sent once per session. */
window.SBSAnalytics = (function () {
  'use strict';
  var S = window.SBSAnalyticsStorage, CFG = window.SBSNAV_CONFIG;
  var EV = window.SBSAnalyticsEvents, ALLOWED = window.SBSAnalyticsAllowedProps;
  var SESSION = window.SBSAnalyticsSession, ATTR = window.SBSAnalyticsAttribution;
  var NAMES = Object.keys(EV).map(function (k) { return EV[k]; });
  var ONCE = [EV.ARTIFACT_OPENED, EV.RETURNING_USER_SESSION, EV.AUDIT_STARTED, EV.AUDIT_COMPLETED];
  var JOURNAL = 'sbsnav-journal', MAX_JOURNAL = 400;

  var providers = [];
  var shopifyProvider = {
    name: 'shopify',
    send: function (name, props) {
      try { window.Shopify.analytics.publish(name, props); } catch (e) {}
      try { if (typeof window.plausible === 'function') window.plausible(name, { props: props }); } catch (e) {}
    },
  };
  var localProvider = {
    name: 'local',
    send: function (name, props) {
      var j = S.get(JOURNAL, []);
      j.push({ e: name, p: props });
      if (j.length > MAX_JOURNAL) j = j.slice(j.length - MAX_JOURNAL);
      S.set(JOURNAL, j);
    },
  };
  var environment = (window.Shopify && window.Shopify.analytics && typeof window.Shopify.analytics.publish === 'function') ? 'sitebuilderstack' : 'claude_artifact';
  providers.push(environment === 'sitebuilderstack' ? shopifyProvider : localProvider);
  if (environment === 'sitebuilderstack') providers.push(localProvider); // the journal is also the visitor's own transparent log

  function reduce(props) {
    var out = {};
    ALLOWED.forEach(function (k) {
      var v = props[k];
      if (v === undefined || v === null || v === '') return;
      if (typeof v === 'number' || typeof v === 'boolean') { out[k] = v; return; }
      if (Array.isArray(v)) { out[k] = v.map(String).slice(0, 12).join(','); return; }
      if (typeof v === 'string') out[k] = v.slice(0, 120);
    });
    return out;
  }
  function base() {
    var ids = SESSION.ids(), inb = ATTR.inbound();
    return {
      artifact_name: CFG.artifact.name, artifact_version: CFG.artifact.version,
      anonymous_visitor_id: ids.anonymous_visitor_id, session_id: ids.session_id,
      timestamp: new Date().toISOString(), environment: environment,
      utm_source: inb.utm_source, utm_medium: inb.utm_medium, utm_campaign: inb.utm_campaign, utm_content: inb.utm_content, utm_term: inb.utm_term,
    };
  }
  function onceKey(name) { return 'sbsnav-once:' + SESSION.session().session_id + ':' + name; }
  function track(name, props) {
    if (NAMES.indexOf(name) === -1) { if (window.console) console.warn('[analytics] not a canonical event, dropped:', name); return false; }
    if (ONCE.indexOf(name) !== -1) {
      var k = onceKey(name) + (name === EV.AUDIT_STARTED || name === EV.AUDIT_COMPLETED ? ':' + (props && props.audit_id) : '');
      if (S.sessionGet(k, false)) return false;
      S.sessionSet(k, true);
    }
    var payload = reduce(Object.assign(base(), props || {}));
    providers.forEach(function (p) { try { p.send(name, payload); } catch (e) { /* analytics never breaks the page */ } });
    SESSION.touch();
    return true;
  }
  function journal() { return S.get(JOURNAL, []); }
  function clearJournal() { S.set(JOURNAL, []); }
  return { track: track, events: EV, journal: journal, clearJournal: clearJournal, environment: environment, providers: providers.map(function (p) { return p.name; }), storageAvailable: S.available };
})();
