/* src/config.js — the facts that are only known after publishing.
 *
 * SHARE_URL is the artifact's real, published URL. It is filled in after the
 * first publish and the page is republished; while it is empty the share
 * control is hidden rather than pointing at a URL that does not exist.
 * It is the planner's own address and carries no answers.
 *
 * COMPANION_PAGE is the proposed sitebuilderstack.com landing page. It is
 * empty because that page does not exist yet — see launch-copy.md.
 */
window.SBS_PLANNER_CONFIG = {
  SHARE_URL: 'https://claude.ai/artifact/8oUQrAFJyAZdKG86KeNZLX',
  COMPANION_PAGE: '',
};
