/* analytics/attribution.js — where the visitor came from, and how the
 * store learns it was us.
 *
 * Inbound: utm_* and referrer are read once, at open, and kept for the
 * visitor so a later session still knows the campaign that brought them.
 * Outbound: every commercial link is built here and only here. It carries
 * the campaign parameters, the CTA location, the anonymous visitor id as
 * `artifact_ref`, and three coarse, non-identifying segments the store's
 * product-page event records: platform, primary problem, and whether a
 * report was downloaded. Never anything typed, never audit content. */
window.SBSAnalyticsAttribution = (function () {
  'use strict';
  var S = window.SBSAnalyticsStorage, CFG = window.SBSNAV_CONFIG;
  var KEY = 'sbsnav-attribution';
  var UTM = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term'];
  var SAFE = /^[A-Za-z0-9_.:\/-]{1,80}$/;
  function clean(v) { v = String(v || '').trim(); return SAFE.test(v) ? v : ''; }
  function readInbound() {
    var out = S.get(KEY, null);
    var params = {};
    try { new URLSearchParams(window.location.search).forEach(function (val, k) { params[k] = val; }); } catch (e) {}
    var fresh = {};
    UTM.forEach(function (k) { if (params[k]) fresh[k] = clean(params[k]); });
    if (Object.keys(fresh).length || !out) {
      out = out || {};
      UTM.forEach(function (k) { out[k] = fresh[k] || out[k] || ''; });
      try { var r = document.referrer ? new URL(document.referrer).hostname : ''; out.referrer = out.referrer || clean(r); } catch (e) { out.referrer = out.referrer || ''; }
      S.set(KEY, out);
    }
    return out;
  }
  var inbound = readInbound();
  function trafficSource() { return inbound.utm_source || inbound.referrer || 'direct'; }
  function productUrl(ctaLocation, segments) {
    var u = new URL(CFG.product.url);
    u.searchParams.set('utm_source', CFG.attribution.utm_source);
    u.searchParams.set('utm_medium', CFG.attribution.utm_medium);
    u.searchParams.set('utm_campaign', CFG.attribution.utm_campaign);
    u.searchParams.set('utm_content', clean(ctaLocation) || 'unknown');
    u.searchParams.set('artifact_ref', window.SBSAnalyticsSession.visitor().anonymous_visitor_id);
    segments = segments || {};
    if (segments.platform) u.searchParams.set('sbs_pf', clean(segments.platform));
    if (segments.primary_problem) u.searchParams.set('sbs_pp', clean(segments.primary_problem));
    u.searchParams.set('sbs_st', clean(segments.stage) || 'opened');
    return u.toString();
  }
  return { inbound: function () { return inbound; }, trafficSource: trafficSource, productUrl: productUrl };
})();
