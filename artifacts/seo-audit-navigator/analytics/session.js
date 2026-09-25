/* analytics/session.js — anonymous visitor and session model.
 *
 * Visitor: a random id kept in localStorage with first_seen, last_seen,
 * visit_count and the previous session's timestamp. Session: a random id
 * kept in sessionStorage; a new one starts when the tab has none, or when
 * the visitor was last seen more than `idleMinutes` ago. A rerender, a
 * route change inside the app, or a plain refresh in the same tab keeps
 * the session, so none of them counts as a return. Nothing here is
 * personally identifying: no email, no name, no IP, no fingerprint. */
window.SBSAnalyticsSession = (function () {
  'use strict';
  var S = window.SBSAnalyticsStorage;
  var CFG = window.SBSNAV_CONFIG;
  var VKEY = 'sbsnav-visitor', SKEY = 'sbsnav-session';
  function rid(prefix) {
    var a = new Uint8Array(12);
    try { (window.crypto || window.msCrypto).getRandomValues(a); } catch (e) { for (var i = 0; i < 12; i++) a[i] = Math.floor(Math.random() * 256); }
    return prefix + Array.prototype.map.call(a, function (b) { return ('0' + b.toString(16)).slice(-2); }).join('');
  }
  var now = Date.now();
  var v = S.get(VKEY, null);
  var isNewVisitor = !v;
  if (!v) v = { anonymous_visitor_id: rid('v_'), first_seen: now, last_seen: now, visit_count: 0, previous_session: null };
  var current = S.sessionGet(SKEY, null);
  var idle = (CFG.session.idleMinutes || 30) * 60 * 1000;
  var startedNewSession = false;
  // A second tab has no sessionStorage of its own; if the visitor's last
  // session is still within the idle window it is the same visit, so adopt
  // it rather than counting a return.
  if (!current && v.current_session && (now - (v.current_session.last_activity || 0)) <= idle) {
    current = v.current_session; S.sessionSet(SKEY, current);
  }
  if (!current || (now - (current.last_activity || 0)) > idle) {
    startedNewSession = true;
    var prev = v.visit_count ? { session_id: current ? current.session_id : null, ended: v.last_seen } : null;
    current = { session_id: rid('s_'), started: now, last_activity: now, audit_id: null, audit_status: 'not-started', report_status: 'none', upgrade_status: 'none', platform: null, primary_problem: null };
    v.previous_session = prev || v.previous_session;
    v.visit_count = (v.visit_count || 0) + 1;
    S.sessionSet(SKEY, current);
  }
  v.last_seen = now;
  v.current_session = current;
  S.set(VKEY, v);
  var isReturning = startedNewSession && !isNewVisitor && v.visit_count > 1;
  function touch(patch) {
    if (patch) Object.keys(patch).forEach(function (k) { current[k] = patch[k]; });
    current.last_activity = Date.now();
    S.sessionSet(SKEY, current);
    v.last_seen = current.last_activity; v.current_session = current; S.set(VKEY, v);
  }
  function daysSincePrevious() {
    if (!v.previous_session || !v.previous_session.ended) return null;
    return Math.round((now - v.previous_session.ended) / 864e5 * 10) / 10;
  }
  return {
    visitor: function () { return v; },
    session: function () { return current; },
    touch: touch,
    newAuditId: function () { var id = rid('a_'); touch({ audit_id: id, audit_status: 'in-progress', report_status: 'none' }); return id; },
    isReturning: isReturning,
    isNewVisitor: isNewVisitor,
    startedNewSession: startedNewSession,
    daysSincePrevious: daysSincePrevious,
    ids: function () { return { anonymous_visitor_id: v.anonymous_visitor_id, session_id: current.session_id }; },
  };
})();
