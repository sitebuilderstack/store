/* analytics/storage.js — the only place that touches localStorage.
 *
 * Every read and write is wrapped: private windows and blocked site data
 * throw on access, and analytics must never break the page. When storage
 * is unavailable the page falls back to memory for the visit and says so
 * through `available()`. */
window.SBSAnalyticsStorage = (function () {
  'use strict';
  var memory = {};
  var ok = null;
  function available() {
    if (ok !== null) return ok;
    try { var k = '__sbsnav_probe'; window.localStorage.setItem(k, '1'); window.localStorage.removeItem(k); ok = true; }
    catch (e) { ok = false; }
    return ok;
  }
  function get(key, fallback) {
    try { var raw = available() ? window.localStorage.getItem(key) : memory[key]; return raw == null ? fallback : JSON.parse(raw); }
    catch (e) { return fallback; }
  }
  function set(key, value) {
    var raw = JSON.stringify(value);
    try { if (available()) window.localStorage.setItem(key, raw); else memory[key] = raw; return true; }
    catch (e) { memory[key] = raw; return false; }
  }
  function sessionGet(key, fallback) {
    try { var raw = window.sessionStorage.getItem(key); return raw == null ? fallback : JSON.parse(raw); } catch (e) { return memory['s:' + key] === undefined ? fallback : memory['s:' + key]; }
  }
  function sessionSet(key, value) {
    try { window.sessionStorage.setItem(key, JSON.stringify(value)); } catch (e) { memory['s:' + key] = value; }
  }
  return { available: available, get: get, set: set, sessionGet: sessionGet, sessionSet: sessionSet };
})();
