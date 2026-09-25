/* src/analytics.js — the measurement interface, and the attribution links.
 *
 * WHAT THIS DOES NOT DO: it does not transmit anything. The claude.ai
 * artifact sandbox serves the page under a Content Security Policy that
 * allows fetch, XHR and WebSocket only to the page's own origin and the
 * Google Fonts hosts. No permitted destination for these events has been
 * verified, so REMOTE is false and the only provider is a local debug
 * journal that never leaves the visitor's browser. Turning it on is one
 * object with a send(name, props) method — and a verified destination.
 *
 * The journal is DEBUG INSTRUMENTATION. It counts what one browser did.
 * It is not analytics, it is not a visitor count, and the page says so.
 *
 * The only thing that actually reaches SiteBuilderStack is the campaign
 * parameters on an outbound link the visitor chooses to follow, and those
 * carry a fixed placement name — never an answer.
 */
window.SBSPlannerAnalytics = (function () {
  'use strict';

  var VERSION = '1.0.0';
  var NAME = 'sitebuilderstack-website-action-planner';

  /* The ten canonical events. Nothing else is ever recorded. */
  var EVENTS = [
    'artifact_opened',
    'planner_started',
    'planner_completed',
    'recommendation_viewed',
    'starter_prompt_copied',
    'plan_export_requested',
    'plan_export_completed',
    'product_cta_clicked',
    'free_resource_clicked',
    'planner_share_clicked',
  ];
  /* Fired at most once per page view. */
  var ONCE = ['artifact_opened', 'planner_started', 'planner_completed'];

  /* The only properties that may travel with an event. Questionnaire
     answers, ownership selections, free text, email addresses and website
     URLs are not on this list and are dropped by reduce(). */
  var ALLOWED = ['artifact_name', 'artifact_version', 'product_id', 'cta_placement', 'environment', 'timestamp'];

  /* Fixed, documented utm_content values. An outbound link may use one of
     these and nothing else — see measurement.md. */
  var PLACEMENTS = [
    'primary_recommendation',
    'recommendation_repeat',
    'complementary_recommendation',
    'bundle_comparison',
    'product_comparison',
    'free_next_step',
    'example_result',
    'header_brand',
    'footer_brand',
  ];
  /* Note: there is no 'share_planner' placement. The share control copies the
     artifact's own claude.ai URL, which is not a sitebuilderstack.com link and
     carries no campaign parameters at all. */

  var CAMPAIGN = {
    utm_source: 'claude_artifact',
    utm_medium: 'interactive_tool',
    utm_campaign: 'website_action_planner',
  };

  /* Remote transmission is off until a permitted destination and the full
     delivery path have been verified. Neither has been. */
  var REMOTE = false;
  var REMOTE_REASON = 'No permitted destination has been verified for this runtime. The artifact sandbox blocks outbound requests, so nothing is sent.';

  var environment = (typeof window !== 'undefined' && window.Shopify && window.Shopify.analytics && typeof window.Shopify.analytics.publish === 'function')
    ? 'sitebuilderstack' : 'claude_artifact';

  var journal = [];
  var MAX = 200;
  var fired = {};

  function reduce(props) {
    var out = {};
    ALLOWED.forEach(function (k) {
      var v = props[k];
      if (v === undefined || v === null || v === '') return;
      out[k] = typeof v === 'string' ? v.slice(0, 80) : (typeof v === 'number' || typeof v === 'boolean') ? v : String(v).slice(0, 80);
    });
    return out;
  }

  function track(name, props) {
    try {
      if (EVENTS.indexOf(name) === -1) return false;
      if (ONCE.indexOf(name) !== -1) { if (fired[name]) return false; fired[name] = true; }
      var payload = reduce(Object.assign({
        artifact_name: NAME,
        artifact_version: VERSION,
        environment: environment,
        timestamp: new Date().toISOString(),
      }, props || {}));
      journal.push({ event: name, props: payload });
      if (journal.length > MAX) journal = journal.slice(-MAX);
      persist();
      /* if (REMOTE) providers.forEach(function (p) { p.send(name, payload); }); */
      return true;
    } catch (e) { return false; }
  }

  function persist() {
    try { window.sessionStorage.setItem('sbs-planner-journal', JSON.stringify(journal)); } catch (e) { /* private window, blocked storage — the journal stays in memory */ }
  }
  function restore() {
    try {
      var v = window.sessionStorage.getItem('sbs-planner-journal');
      if (v) { var j = JSON.parse(v); if (Array.isArray(j)) journal = j.slice(-MAX); }
    } catch (e) { /* ignored on purpose */ }
  }
  restore();

  /* Outbound links. Existing query parameters on the target are preserved;
     the campaign parameters are set, not appended blindly. */
  function tag(url, placement) {
    try {
      var u = new URL(url, 'https://sitebuilderstack.com');
      if (u.protocol !== 'https:' || u.hostname !== 'sitebuilderstack.com') return url;
      Object.keys(CAMPAIGN).forEach(function (k) { u.searchParams.set(k, CAMPAIGN[k]); });
      u.searchParams.set('utm_content', PLACEMENTS.indexOf(placement) !== -1 ? placement : 'unknown_placement');
      return u.toString();
    } catch (e) { return url; }
  }

  return {
    VERSION: VERSION, NAME: NAME,
    EVENTS: EVENTS, ALLOWED: ALLOWED, PLACEMENTS: PLACEMENTS, CAMPAIGN: CAMPAIGN,
    remoteEnabled: REMOTE, remoteReason: REMOTE_REASON,
    environment: environment,
    track: track, tag: tag,
    journal: function () { return journal.slice(); },
    clear: function () { journal = []; fired = {}; persist(); },
  };
})();
