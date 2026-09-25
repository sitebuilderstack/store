/* analytics/events.js — the canonical funnel vocabulary.
 *
 * These names are the contract between the artifact, sitebuilderstack.com
 * and any future dashboard. The artifact fires the first five; the store
 * fires the next three (see docs/analytics/ARTIFACT-FUNNEL.md in the
 * SiteBuilderStack repository); the last is fired by whichever surface a
 * returning visitor opens. Nothing outside this list is sent to a provider.
 *
 * Provider naming: the artifact's own providers use the names verbatim.
 * On sitebuilderstack.com the same names are published through
 * Shopify.analytics.publish and Plausible custom events, also verbatim;
 * the store's custom pixel forwards them with the same `e` field. No
 * renaming happens anywhere, so no mapping table is needed. */
window.SBSAnalyticsEvents = Object.freeze({
  ARTIFACT_OPENED: 'artifact_opened',
  AUDIT_STARTED: 'audit_started',
  AUDIT_COMPLETED: 'audit_completed',
  REPORT_DOWNLOADED: 'report_downloaded',
  UPGRADE_BUTTON_CLICKED: 'upgrade_button_clicked',
  // Store-originated (never fired here; listed so the vocabulary is whole)
  PRODUCT_PAGE_VISITED: 'sitebuilderstack_product_page_visited',
  ACCOUNT_CREATED: 'account_created',
  PRODUCT_PURCHASED: 'product_purchased',
  // Either surface
  RETURNING_USER_SESSION: 'returning_user_session',
});
/* Properties every event may carry, and the only ones a provider will
   accept. Anything not listed is dropped before it leaves the abstraction —
   so a bug elsewhere cannot leak audit text into analytics. */
window.SBSAnalyticsAllowedProps = Object.freeze([
  'artifact_name', 'artifact_version', 'anonymous_visitor_id', 'session_id', 'audit_id',
  'timestamp', 'referrer', 'utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term',
  'is_returning_user', 'visit_count', 'days_since_previous_session', 'previous_session_timestamp',
  'primary_problem', 'platform', 'traffic_source', 'symptom_count', 'data_sources',
  'critical_recommendations', 'high_recommendations', 'medium_recommendations', 'low_recommendations',
  'audit_duration_seconds', 'report_format', 'cta_location', 'product_identifier', 'product_price', 'currency',
  'audit_status', 'report_status', 'environment', 'provider',
]);
