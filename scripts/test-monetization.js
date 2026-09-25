/* Offline checks for the four monetization paths.
 *
 * The browser behaviour is covered by the render suite; this proves the
 * claims that must not drift in source: that no page asserts an affiliate
 * relationship the register does not record, that the inquiry pages carry no
 * purchasable-offer schema, that no price is published where the owner has
 * not approved one, and that the analytics allowlist admits exactly the four
 * documented events.
 */
const fs = require('fs'), path = require('path'), vm = require('vm');
const R = path.join(__dirname, '..');
const read = (p) => fs.readFileSync(path.join(R, p), 'utf8');
let failures = 0;
const check = (n, ok, d) => { if (!ok) failures++; console.log(`  ${ok ? 'PASS' : 'FAIL'}  ${n}${d && !ok ? '  -> ' + String(d).slice(0, 300) : ''}`); };

const register = read('docs/monetization/PARTNER-REGISTER.md');
const recsTpl = read('theme/dev/templates/page.recommended-tools.json');
const recs = JSON.parse(recsTpl);
const blocks = Object.values(recs.sections.main.blocks);

// ---- affiliate honesty -----------------------------------------------------
const approved = (register.match(/\*\*Relationship status\*\* \| \*\*approved\*\*/g) || []).length;
check('register records no approved affiliate relationship today', approved === 0);
check('no recommendation is flagged as compensated while none is approved',
  blocks.every((b) => b.settings.affiliate === false), JSON.stringify(blocks.map((b) => [b.settings.partner, b.settings.affiliate])));
check('the page-level disclosure states plainly that no link earns a commission',
  /no link on this page earns a commission/i.test(recs.sections.main.settings.disclosure));
check('every recommended tool is in the register',
  blocks.every((b) => register.includes(b.settings.url.replace(/\/$/, '')) || register.includes(b.settings.name)),
  blocks.map((b) => b.settings.name).join());
check('every recommendation states the basis for its description',
  blocks.every((b) => /read|used by this site|documentation/i.test(b.settings.basis)), blocks.map((b) => b.settings.basis && b.settings.basis.slice(0, 40)).join(' | '));
check('every recommendation names a limitation and a cheaper-or-free alternative',
  blocks.every((b) => b.settings.limits && b.settings.limits.length > 40 && b.settings.alternative && b.settings.alternative.length > 30));
check('"used by this site" appears only where the site actually uses the tool (Plausible)',
  blocks.filter((b) => /(^|[^t] )used by this site/i.test(String(b.settings.basis).replace(/<[^>]+>/g, ''))).map((b) => b.settings.partner).join() === 'plausible',
  blocks.map((b) => [b.settings.partner, String(b.settings.basis).replace(/<[^>]+>/g, '').slice(0, 50)]).join(' | '));
const snippet = read('theme/dev/snippets/sbs-recommend.liquid');
check('the snippet marks a compensated link sponsored+nofollow and a plain link noopener only',
  /sponsored nofollow noopener/.test(snippet) && /\{% else %\}noopener\{% endif %\}/.test(snippet));
check('the commission disclosure renders above the link, not only in a footer',
  snippet.indexOf('sbs-rec__disclosure') < snippet.indexOf('sbs-rec__link'));
check('the disclosure is rendered only when the link is compensated',
  /\{%- if is_aff -%\}\s*<p class="sbs-rec__disclosure"/.test(snippet));

// ---- no unapproved prices or purchasable schema ----------------------------
const pages = { 'team-licenses': read('content/pages/team-licenses.md'), membership: read('content/pages/membership.md'), 'website-review': read('content/pages/website-review.md') };
const templates = { 'team-licenses': JSON.parse(read('theme/dev/templates/page.team-licenses.json')), membership: JSON.parse(read('theme/dev/templates/page.membership.json')), 'website-review': JSON.parse(read('theme/dev/templates/page.website-review.json')) };
for (const [name, body] of Object.entries(pages)) {
  const prices = (body.match(/\$\d[\d,]*(\.\d\d)?/g) || []);
  check(`${name}: publishes no price (the owner has approved none)`, prices.length === 0, prices.join());
  check(`${name}: states that no payment is taken`, /no payment|takes no money|nothing is for sale/i.test(body + JSON.stringify(templates[name])));
}
check('membership does not promise a launch date or reserve a price',
  !/launch(ing)? (in|on|by)\b/i.test(pages.membership) && /does not reserve a price|no price has been set/i.test(pages.membership));
check('website-review does not advertise a turnaround time',
  !/within \d+ (business )?(days|hours)\b/i.test(pages['website-review']));
check('website-review states a request is not a booking',
  /takes requests, not bookings/i.test(JSON.stringify(templates['website-review'])));
for (const [name, t] of Object.entries(templates)) {
  const mode = t.sections.main.settings.mode;
  check(`${name}: mode is inquiry or waitlist, never purchase`, mode === 'inquiry' || mode === 'waitlist', mode);
  const consent = Object.values(t.sections.main.blocks).filter((b) => b.type === 'consent');
  check(`${name}: the marketing opt-in, where present, is its own optional block`,
    consent.every((c) => !c.settings.required), JSON.stringify(consent));
}
const offer = read('theme/dev/sections/sbs-offer.liquid');
check('the offer section emits no Offer/Product structured data', !/schema\.org|itemtype|"@type"/.test(offer));
check('the offer section uses the platform contact form, not a third-party endpoint',
  /\{%- form 'contact'/.test(offer) && !/fetch\(|action="http/.test(offer));
check('the success state is rendered only by Shopify posted_successfully',
  /form\.posted_successfully\?[\s\S]{0,400}data-sbs-offer-success/.test(offer));

// ---- analytics -------------------------------------------------------------
const js = read('theme/dev/assets/sbs.js');
const listed = (/var ENGAGE_EVENTS = \{([\s\S]*?)\};/.exec(js)[1].match(/[a-z_]+(?=:)/g) || []);
const want = ['monetization_offer_view', 'monetization_cta_click', 'monetization_lead_submitted', 'affiliate_link_clicked'];
check('the four monetization events are in the allowlist', want.every((w) => listed.includes(w)));
check('offer_view, lead and cta dedupe correctly (view/lead once, cta repeatable)',
  /monetization_offer_view: 1/.test(js) && /monetization_lead_submitted: 1/.test(js) && /monetization_cta_click: 0/.test(js));
check('the lead event is fired from the success element, never from a submit handler',
  /querySelector\('\[data-sbs-offer-success\]'\)[\s\S]{0,400}monetization_lead_submitted/.test(js)
  && !/addEventListener\('submit'[\s\S]{0,600}monetization_lead_submitted/.test(js));
check('source_path is stripped of any query string', /offerPath[\s\S]{0,200}location\.pathname/.test(js) && !/location\.search[\s\S]{0,80}source_path/.test(js));
// payload reduction, executed
{
  const sent = [];
  const sb = { window: { Shopify: { analytics: { publish: (n, p) => sent.push([n, p]) } }, setTimeout, matchMedia: () => ({ matches: false, addEventListener() {} }), location: { pathname: '/pages/team-licenses', search: '?utm_source=x' }, sessionStorage: { getItem: () => null, setItem() {} }, localStorage: { getItem: () => null, setItem() {} } },
    document: { readyState: 'loading', addEventListener() {}, createElement: () => ({ setAttribute() {}, style: {} }), body: { appendChild() {} }, querySelector: () => null, querySelectorAll: () => [], getElementById: () => null, cookie: '' },
    navigator: {}, console, Date, Array, String, RegExp, Math, JSON, Object, Promise, setTimeout, clearTimeout, URL, URLSearchParams };
  sb.window.document = sb.document;
  vm.createContext(sb); vm.runInContext(js, sb);
  const T = sb.window.SBS.track;
  T('monetization_lead_submitted', { offer_id: 'team-licenses', mode: 'inquiry', source_path: '/pages/team-licenses', email: 'a@b.c', organisation: 'Acme Ltd', seats: '3 seats please', website: 'https://client.example' });
  check('lead payload keeps ids and the path, drops email, organisation and free text',
    JSON.stringify(sent[0][1]) === '{"offer_id":"team-licenses","source_path":"/pages/team-licenses","mode":"inquiry"}', JSON.stringify(sent[0]));
  T('affiliate_link_clicked', { partner: 'uptimerobot', placement: 'guide-maintenance', mode: 'editorial', source_path: '/blogs/guides/claude-code-website-maintenance', href: 'https://uptimerobot.com/pricing/' });
  check('affiliate payload carries no destination URL', !JSON.stringify(sent[1][1]).includes('http'), JSON.stringify(sent[1]));
  T('monetization_offer_view', { offer_id: 'a', mode: 'inquiry', source_path: '/pages/x?utm_source=y' });
  check('a path carrying a query string is dropped rather than sent', !JSON.stringify(sent[2][1]).includes('utm_source'), JSON.stringify(sent[2]));
}

// ---- documents exist and say what the pages claim ---------------------------
check('the team addendum is marked draft and changes no existing licence',
  /Status: DRAFT/.test(read('docs/monetization/TEAM-LICENCE-ADDENDUM.md')) && /reduces, restricts, or alters any licence any\nindividual already holds/.test(read('docs/monetization/TEAM-LICENCE-ADDENDUM.md')));
const scope = read('docs/monetization/review-service/SCOPE-AND-FULFILMENT.md');
check('the service price is recorded as an unapproved assumption', /ASSUMPTIONS, owner approval required/.test(scope) && /Internal hypothesis. Not published, not charged/.test(scope));
const sample = read('docs/monetization/review-service/SAMPLE-REPORT.md').replace(/^>\s?/gm, '').replace(/\s+/g, ' ');
check('the sample report is labelled a self-review, not a customer engagement',
  /reviewing Site Builder Stack's own website/i.test(sample) && /not a customer engagement/i.test(sample));
check('the sample report claims no visitor behaviour it could not observe',
  !/bounce rate|conversion rate of|% of visitors|most visitors/i.test(sample) && /No analytics was accessed/i.test(sample));
const pilot = read('content/membership/pilot-01/README.md').replace(/\s+/g, ' ');
check('the pilot states its tested environment and does not claim untested coverage',
  /Tested environment:/.test(pilot) && /Not tested against authenticated pages/.test(pilot));
check('the pilot is labelled as not yet delivered', /Not yet delivered to anyone/i.test(pilot));

console.log(`\n${failures} failure(s)`);
process.exit(failures ? 1 : 0);
