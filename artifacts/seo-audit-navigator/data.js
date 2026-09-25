/* data.js — content for the navigator. Module descriptions are short
 * summaries of what each toolkit area covers; sample audits are fictional
 * and labelled as such everywhere they appear. Nothing here is the paid
 * product's text. */
window.SBSNAV_DATA = (function () {
  'use strict';

  var MODULES = [
    { id: '01', key: 'technical', name: 'Technical SEO', short: 'Crawlability, response codes, redirects, canonicals and the rendered head of every page.', problems: ['Redirect chains and loops', 'Wrong or missing canonicals', 'Non-200 responses on important URLs', 'Staging leaks into production'], example: 'A relaunch shipped with canonicals built from a "site origin" setting still set to staging. The rendered head said so; the template looked fine.' },
    { id: '02', key: 'onpage', name: 'On-Page SEO', short: 'Titles, descriptions, headings and body relevance, checked against what is rendered, not the template.', problems: ['Duplicate or truncated titles', 'Missing or repeated descriptions', 'Multiple H1s or none', 'Pages that rank for what they do not answer'], example: 'Forty product pages shared one description because a fallback fired whenever the SEO field was empty.' },
    { id: '03', key: 'indexation', name: 'Indexation', short: 'Submitted versus indexed, directives, sitemap coverage and the conflicts between them.', problems: ['URLs missing from Google', 'noindex on pages that should rank', 'Sitemap lists blocked or redirected URLs', 'Duplicate URL variants competing'], example: 'A store submitted 500 URLs and had 180 indexed; the sitemap included every noindexed variant and the canonical pointed elsewhere on half of them.' },
    { id: '04', key: 'schema', name: 'Structured Data', short: 'JSON-LD that parses, matches the visible page and claims nothing the page does not show.', problems: ['Invalid JSON-LD', 'Ratings or reviews that do not exist on the page', 'Product data out of step with the price shown', 'Breadcrumbs that do not match the path'], example: 'A theme emitted aggregateRating with no reviews on the page — a manual-action risk hiding behind a green validator.' },
    { id: '05', key: 'linking', name: 'Internal Linking', short: 'Orphans, depth, anchor text and whether the pages that matter receive links from the pages that have authority.', problems: ['Orphan pages', 'Money pages five clicks deep', 'Navigation links that resolve but go to the wrong place', 'Anchor text that says "click here"'], example: 'Twelve service pages were reachable only from a footer link removed in a redesign; they stayed indexed and lost every ranking within two months.' },
    { id: '06', key: 'cwv', name: 'Core Web Vitals', short: 'LCP, INP and CLS measured on the pages that earn, with the element responsible named.', problems: ['Slow LCP from an unsized hero image', 'Layout shift from late-loading banners', 'INP from third-party scripts', 'Passing lab scores, failing field data'], example: 'The homepage passed PageSpeed in the lab and failed in the field because a consent banner shifted the layout for real visitors only.' },
    { id: '07', key: 'a11y', name: 'Accessibility + SEO', short: 'The overlap: headings, link names, image text, focus and language — what helps assistive tech also helps a crawler.', problems: ['Images without alt', 'Links with no accessible name', 'Heading order that hides structure', 'Missing lang attribute'], example: 'A "Read more" link on every card gave the crawler 300 identical anchors and a screen reader 300 identical announcements.' },
    { id: '08', key: 'content', name: 'Content Auditing', short: 'Which pages earn, which decay, which duplicate each other, and which to merge, refresh or remove.', problems: ['Content decay', 'Thin or duplicated pages', 'Cannibalisation between similar articles', 'Pages with impressions and no clicks'], example: 'Three articles answered the same query; merging two into the strongest returned the ranking the three had split.' },
    { id: '09', key: 'gsc', name: 'Google Search Console', short: 'Reading the Pages, Performance and Sitemaps reports for evidence rather than reassurance, and what each cannot tell you.', problems: ['Coverage reasons misread', '"Crawled — currently not indexed" treated as a bug', 'URL Inspection quotas and stale results', 'Windows that hide the drop'], example: 'A traffic drop dated to a single week matched a redirect change — visible only with a page-level comparison window.' },
    { id: '10', key: 'bing', name: 'Bing + IndexNow', short: 'The second engine: Webmaster Tools, IndexNow submission and the checks that differ from Google.', problems: ['Bing ignores the sitemap', 'IndexNow keys misconfigured', 'Different canonical choices', 'AI search surfaces sourcing from Bing'], example: 'A site with healthy Google coverage had 40% of its URLs unknown to Bing because the sitemap index was never submitted there.' },
    { id: '11', key: 'platform', name: 'Platform Workflows', short: 'Shopify, WordPress, Astro, Next.js and static sites each break SEO in their own ways; the checks that are specific to each.', problems: ['Shopify collection/product URL variants', 'WordPress plugin conflicts over canonicals', 'Astro/Next builds that drop metadata', 'Static sites without redirects'], example: 'A Shopify store exposed the same product under five collection paths, each with its own canonical from an app.' },
    { id: '12', key: 'launch', name: 'Launch Validation', short: 'The go/no-go pass before a release: noindex removed, canonicals on the production host, redirects landing where the map says.', problems: ['Staging noindex shipped to production', 'Redirect chains after a migration', 'Sitemap pointing at the old host', 'Analytics not receiving'], example: 'A release summary with six green ticks; the homepage head said noindex,nofollow. Held at 16:40 for a 17:00 launch.' },
    { id: '13', key: 'competitor', name: 'Competitor Research', short: 'What the pages that outrank yours actually contain, structurally — not their traffic estimates.', problems: ['Guessing why a competitor ranks', 'Copying features that do not matter', 'Missing intent the query has moved to', 'No baseline to compare against'], example: 'The top three results for a service query all answered a pricing question the client page avoided.' },
    { id: '14', key: 'reporting', name: 'Reporting', short: 'Findings with evidence, priority and a next step — a report someone can act on and re-check next month.', problems: ['Reports that list checks, not findings', 'No evidence column', 'Priorities that are all HIGH', 'Nobody can tell what changed'], example: 'A report whose Evidence column was empty for "backups OK" — the log said 0 bytes.' },
  ];

  var PROBLEMS = [
    { id: 'not-indexed', label: "Pages aren't getting indexed", hint: 'Submitted but missing from Google' },
    { id: 'traffic-drop', label: 'Google traffic dropped', hint: 'Sessions down, rankings unclear' },
    { id: 'rankings-declined', label: 'Rankings declined', hint: 'Positions slid for known queries' },
    { id: 'migration', label: 'Website recently migrated', hint: 'New platform, URLs or domain' },
    { id: 'launch', label: 'Preparing for launch', hint: 'A release is coming' },
    { id: 'cwv', label: 'Core Web Vitals problems', hint: 'LCP, INP or CLS failing' },
    { id: 'linking', label: 'Internal linking problems', hint: 'Orphans, depth, wrong destinations' },
    { id: 'schema', label: 'Structured data problems', hint: 'Errors or warnings on rich results' },
    { id: 'content', label: 'Content performance problems', hint: 'Impressions without clicks, decay' },
    { id: 'full', label: 'Complete SEO audit', hint: 'Everything, in the right order' },
    { id: 'unsure', label: "I'm not sure what's wrong", hint: 'Something is off; start with the evidence' },
  ];
  var PLATFORMS = [
    { id: 'shopify', label: 'Shopify' }, { id: 'wordpress', label: 'WordPress' }, { id: 'astro', label: 'Astro' },
    { id: 'static', label: 'Static HTML' }, { id: 'nextjs', label: 'Next.js / React' }, { id: 'custom', label: 'Custom application' }, { id: 'other', label: 'Other / unknown' },
  ];
  var SYMPTOMS = [
    ['missing-urls', 'URLs missing from Google'], ['traffic-decline', 'Organic traffic decline'], ['ranking-decline', 'Ranking decline'],
    ['dup-content', 'Duplicate content'], ['dup-titles', 'Duplicate titles'], ['dup-descriptions', 'Duplicate meta descriptions'],
    ['canonical', 'Canonical problems'], ['crawl', 'Crawl problems'], ['broken-links', 'Broken links'], ['slow', 'Slow pages'],
    ['cwv', 'Core Web Vitals problems'], ['schema', 'Schema errors'], ['poor-linking', 'Poor internal linking'], ['orphans', 'Orphan pages'],
    ['decay', 'Content decay'], ['low-ctr', 'Low CTR'], ['migration', 'Recent migration'], ['sitemap', 'Sitemap problems'], ['robots', 'robots.txt concerns'], ['unknown', 'Unknown'],
  ].map(function (p) { return { id: p[0], label: p[1] }; });
  var DATA_SOURCES = [
    ['gsc', 'Google Search Console'], ['bing', 'Bing Webmaster Tools'], ['ga', 'Google Analytics'], ['psi', 'PageSpeed Insights'],
    ['source', 'Website source code'], ['sitemap', 'Sitemap'], ['robots', 'robots.txt'], ['crawl', 'Crawl export'], ['live', 'Live website only'], ['none', 'No data yet'],
  ].map(function (p) { return { id: p[0], label: p[1] }; });

  /* ---- recommendation rules -------------------------------------------
     Each rule adds an area with a base priority when its trigger matches.
     Later, priorities are raised by corroborating symptoms and the final
     list is ordered CRITICAL → LOW. The text is generated from the
     answers, so nothing claims more than what was reported. */
  var AREA_TEXT = {
    indexation: {
      problem: 'Pages that should be in the index are not, or the wrong versions are.',
      why: 'A page Google has not indexed cannot rank for anything. Most "missing" pages are excluded by something the site itself says: a noindex, a canonical to another URL, a sitemap that lists the wrong variant, or a robots rule.',
      investigate: ['Submitted vs indexed URLs (Pages report, by reason)', 'Sitemap coverage: every important URL present, no redirected or noindexed entries', 'noindex directives in the rendered head and X-Robots-Tag headers', 'Canonical conflicts: pages pointing at other pages, or at staging', 'robots.txt restrictions on paths that matter', 'Duplicate URL variants (parameters, trailing slashes, collection paths)'],
      evidence: ['sitemap.xml as served', 'Rendered robots meta and canonical per URL', 'Search Console Pages export, if available', 'robots.txt as served'],
      next: 'List the top 20 URLs that should be indexed and record, for each, its status, canonical, robots directive and sitemap presence — before changing anything.',
    },
    technical: {
      problem: 'Something in how pages are served — status codes, redirects, canonicals — is telling search engines the wrong thing.',
      why: 'Search engines act on the response, not the intention. A 302 where a 301 was meant, a redirect chain, or a canonical to the wrong host all cost visibility silently.',
      investigate: ['Status code and final URL after redirects for key pages', 'Redirect chains and loops', 'Canonical host and self-reference', 'Mixed http/https or www variants', 'Server headers that block crawling (X-Robots-Tag, cache rules)'],
      evidence: ['HTTP response traces (hop by hop)', 'Rendered head of each key page', 'Redirect rules as configured'],
      next: 'Fetch ten important URLs without following redirects and record each hop; compare the final page with what the map or navigation promised.',
    },
    onpage: {
      problem: 'Titles, descriptions and headings are duplicated, missing or do not match what the page answers.',
      why: 'Duplicate titles make pages compete with each other; a description that repeats site-wide gives searchers no reason to click; a page whose heading answers a different question loses the visit it won.',
      investigate: ['Duplicate titles and descriptions across the crawl', 'Pages with no H1 or several', 'Title length and truncation in results', 'Template fallbacks that fire when a field is empty'],
      evidence: ['Crawl export of title/description/H1 per URL', 'Rendered head of sample pages'],
      next: 'Group pages by identical title; the largest groups usually trace to one template fallback.',
    },
    schema: {
      problem: 'Structured data is invalid, or claims things the page does not show.',
      why: 'Invalid JSON-LD is ignored; JSON-LD that describes reviews, ratings or prices absent from the page is a policy risk that a validator will happily pass.',
      investigate: ['Every application/ld+json block parses', 'Types match the page (Product on products, Article on articles)', 'Values match visible content (price, availability, author, dates)', 'No aggregateRating/review without visible reviews'],
      evidence: ['JSON-LD blocks as rendered', 'Screenshots of the visible values they describe'],
      next: 'Validate the live URL, not the template, and compare each value against what a visitor sees.',
    },
    linking: {
      problem: 'Important pages are hard to reach, or links do not go where their labels promise.',
      why: 'Crawlers and visitors both follow links. A page with no inbound internal links is invisible to one and unreachable by the other; a link that resolves to the wrong page wastes the authority it carries.',
      investigate: ['Orphan pages (in the sitemap, linked from nowhere)', 'Click depth of the pages that earn', 'Navigation and footer destinations vs labels', 'Anchor text on the links that matter'],
      evidence: ['Crawl export with inlink counts and depth', 'Sitemap vs crawl reconciliation'],
      next: 'Reconcile the sitemap with the crawl: anything in the first and not the second is an orphan.',
    },
    cwv: {
      problem: 'Pages are slow or unstable for real visitors.',
      why: 'Core Web Vitals are a ranking signal and, more importantly, a conversion signal. Lab scores and field data disagree often enough that only the field number counts.',
      investigate: ['LCP element and its load path on the key pages', 'CLS sources (unsized media, late banners, fonts)', 'INP from third-party scripts', 'Field data vs lab data per template'],
      evidence: ['PageSpeed Insights field data per URL', 'Waterfall for the LCP resource'],
      next: 'Name the LCP element on the top three templates; most fixes follow from that one fact.',
    },
    content: {
      problem: 'Content is decaying, duplicated, or earning impressions without clicks.',
      why: 'Pages age. Queries move. Three pages answering one question split the ranking three ways. The audit finds which pages to refresh, merge or remove — with data, not taste.',
      investigate: ['Pages with declining clicks over 12 months', 'Queries where several pages rank', 'Impressions-without-clicks pages (title and snippet)', 'Thin pages and near-duplicates'],
      evidence: ['Search Console Performance export by page and query', 'Crawl export word counts and similarity'],
      next: 'Export 12 months of page-level performance and sort by change; the top decliners are the shortlist.',
    },
    gsc: {
      problem: 'The data that would explain the problem has not been read the right way, or is not connected.',
      why: 'Search Console is the only source that says what Google actually did. Without it, an audit guesses. With it misread, an audit guesses confidently.',
      investigate: ['Pages report by reason, not by total', 'Performance comparison windows around the change date', 'Sitemaps report: discovered vs submitted', 'Manual actions and security issues'],
      evidence: ['Exports with dates', 'Screenshots of the comparison window'],
      next: 'If Search Console is not connected, connect it first — nothing else in the plan is verifiable without it.',
    },
    launch: {
      problem: 'A release is about to ship, and the checks that stop a launch have not been run.',
      why: 'The three launch faults that cost the most — staging noindex on production, canonicals to the wrong host, redirects to the homepage — are each one request to find and one setting to fix.',
      investigate: ['noindex / X-Robots-Tag on the production host', 'Canonicals self-referencing on production', 'Redirect map tested on the live origin', 'Sitemap lists the new URLs', 'Forms and analytics verified from outside'],
      evidence: ['Response captures from the production host', 'Redirect check report', 'Sitemap as served'],
      next: 'Run the go/no-go pass against the production host, not the template, and hold if any of the three faults appears.',
    },
    platform: {
      problem: 'The platform has behaviours that decide URLs, canonicals and metadata for you.',
      why: 'Every platform has its own way of duplicating or hiding pages. Knowing which checks are platform-specific saves auditing what the platform already handles and catches what it silently does.',
      investigate: ['Platform-generated URL variants and their canonicals', 'Apps or plugins that write metadata or redirects', 'Generated sitemap contents', 'Theme or template metadata fallbacks'],
      evidence: ['Platform settings screenshots', 'Rendered head from platform-generated pages'],
      next: 'List every app or plugin that touches the head; each is a suspect.',
    },
    bing: {
      problem: 'Bing (and the AI answer engines that source from it) may not know the site the way Google does.',
      why: 'A site healthy in Google can be half-known to Bing. IndexNow makes submission cheap; the check is whether it was ever set up.',
      investigate: ['Bing Webmaster Tools coverage', 'IndexNow key and submissions', 'Differences in canonical selection'],
      evidence: ['Bing site scan export', 'IndexNow key file as served'],
      next: 'Verify the site in Bing Webmaster Tools and submit the sitemap index; it takes ten minutes.',
    },
    a11y: {
      problem: 'Structural accessibility faults are also crawl faults.',
      why: 'Missing alt text, unnamed links and broken heading order cost assistive-technology users first and crawlers second. Fixing one fixes both.',
      investigate: ['Images without alt on key pages', 'Links with no accessible name', 'Heading order', 'lang attribute'],
      evidence: ['Rendered audit per page', 'Screenshots of affected components'],
      next: 'Audit the three templates that carry the most traffic; faults repeat by template.',
    },
    competitor: {
      problem: 'The pages that outrank yours are structured differently, and the difference has not been named.',
      why: 'Rankings are relative. Knowing what a competing page actually contains — sections, questions answered, structured data — turns "improve the content" into a list.',
      investigate: ['Top three results for the target queries', 'Sections and questions each answers', 'Structured data types used', 'Internal links pointing at them'],
      evidence: ['Captured outlines of competing pages', 'Comparison table'],
      next: 'Outline the top three results for one query and mark what your page does not answer.',
    },
    reporting: {
      problem: 'Findings need to be written down with evidence, priority and a next step, or the audit changes nothing.',
      why: 'A report is how the work survives the week. Evidence per finding is what makes it re-checkable next month.',
      investigate: ['One line per finding: priority, URL, evidence, action', 'What was not checked, and why'],
      evidence: ['The report itself'],
      next: 'Use the report this navigator generates as the skeleton; add the evidence as you capture it.',
    },
  };
  var MODULE_BY_KEY = {}; MODULES.forEach(function (m) { MODULE_BY_KEY[m.key] = m; });
  var PRIO = { CRITICAL: 4, HIGH: 3, MEDIUM: 2, LOW: 1 };
  var PRIO_NAME = ['', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'];

  function recommend(answers) {
    var problem = answers.problem, platform = answers.platform, symptoms = answers.symptoms || [], data = answers.data || [];
    var score = {}; var reason = {};
    function add(key, level, why) { score[key] = Math.max(score[key] || 0, level); if (why && !reason[key]) reason[key] = why; }
    var byProblem = {
      'not-indexed': [['indexation', 4, 'You reported that pages are not getting indexed.'], ['technical', 3, 'Indexation faults usually trace to a response, canonical or directive.'], ['gsc', 3, 'Search Console is where "not indexed" is explained, by reason.'], ['linking', 2, 'Unlinked pages are discovered late or never.'], ['platform', 2, 'Platforms generate URL variants that compete for indexing.']],
      'traffic-drop': [['gsc', 4, 'A traffic drop is dated and located in Search Console before anything else.'], ['technical', 3, 'The most common cause of a sudden drop is a technical change.'], ['indexation', 3, 'Pages dropping out of the index look like a traffic drop.'], ['content', 2, 'A slow decline is often content decay.'], ['onpage', 2, 'Title changes move click-through.']],
      'rankings-declined': [['content', 3, 'Ranking declines on known queries usually mean the page answers less than the competition now does.'], ['competitor', 3, 'What outranks you has changed; find out how.'], ['onpage', 3, 'Titles and headings decide which query a page competes for.'], ['gsc', 3, 'Query-level movement is only visible in Search Console.'], ['technical', 2, 'Rule out a technical cause first.'], ['linking', 2, 'Pages that lost internal links lose rankings.']],
      'migration': [['launch', 4, 'A migration is a launch; the launch faults apply.'], ['technical', 4, 'Redirects, canonicals and hosts are where migrations go wrong.'], ['indexation', 3, 'The new URLs have to be indexed and the old ones released.'], ['gsc', 3, 'Both properties need watching for a month.'], ['linking', 2, 'Internal links still pointing at old URLs create chains.']],
      'launch': [['launch', 4, 'You are preparing a release.'], ['technical', 3, 'Redirects and canonicals are verified before go.'], ['indexation', 3, 'Staging directives must not ship.'], ['schema', 2, 'New templates often ship invalid structured data.'], ['cwv', 2, 'Measure before launch so after has a baseline.']],
      'cwv': [['cwv', 4, 'You reported Core Web Vitals problems.'], ['technical', 2, 'Redirect chains add to LCP.'], ['platform', 2, 'Platform apps and scripts are the usual INP cause.']],
      'linking': [['linking', 4, 'You reported internal linking problems.'], ['indexation', 3, 'Orphans drop out of the index.'], ['content', 2, 'Linking decisions follow which pages should earn.']],
      'schema': [['schema', 4, 'You reported structured data problems.'], ['onpage', 2, 'Schema values must match visible metadata.'], ['platform', 2, 'Apps and plugins write competing JSON-LD.']],
      'content': [['content', 4, 'You reported content performance problems.'], ['gsc', 3, 'Page and query performance is the evidence.'], ['onpage', 3, 'Snippets decide clicks on impressions.'], ['competitor', 2, 'What ranks instead is the benchmark.'], ['linking', 2, 'Decaying pages often lost links.']],
      'full': [['technical', 4, 'A complete audit starts with how pages are served.'], ['indexation', 4, 'Then whether they are indexed.'], ['onpage', 3, ''], ['schema', 3, ''], ['linking', 3, ''], ['cwv', 3, ''], ['content', 3, ''], ['gsc', 3, ''], ['platform', 2, ''], ['a11y', 2, ''], ['bing', 2, ''], ['competitor', 1, ''], ['reporting', 2, 'Every finding needs a line in the report.']],
      'unsure': [['gsc', 4, 'When the problem is unclear, the data says where to look first.'], ['technical', 3, 'A short technical pass rules out the loud faults.'], ['indexation', 3, 'Index status explains most invisible problems.'], ['onpage', 2, ''], ['reporting', 2, 'Write down what you find as you find it.']],
    };
    (byProblem[problem] || byProblem.unsure).forEach(function (r) { add(r[0], r[1], r[2]); });
    var bySymptom = { 'missing-urls': ['indexation', 4], 'traffic-decline': ['gsc', 3], 'ranking-decline': ['content', 3], 'dup-content': ['indexation', 3], 'dup-titles': ['onpage', 3], 'dup-descriptions': ['onpage', 3], 'canonical': ['technical', 4], 'crawl': ['technical', 3], 'broken-links': ['linking', 3], 'slow': ['cwv', 3], 'cwv': ['cwv', 4], 'schema': ['schema', 3], 'poor-linking': ['linking', 3], 'orphans': ['linking', 4], 'decay': ['content', 3], 'low-ctr': ['onpage', 3], 'migration': ['launch', 3], 'sitemap': ['indexation', 3], 'robots': ['indexation', 4] };
    symptoms.forEach(function (s) { var r = bySymptom[s]; if (r) add(r[0], r[1], 'You reported: ' + SYMPTOMS.filter(function (x) { return x.id === s; })[0].label.toLowerCase() + '.'); });
    if (platform && platform !== 'other') add('platform', Math.max(2, score.platform || 0), (PLATFORMS.filter(function (p) { return p.id === platform; })[0] || {}).label + ' has platform-specific checks.');
    if (data.indexOf('gsc') === -1) add('gsc', Math.max(3, score.gsc || 0), 'Search Console is not in your data yet; connecting it makes the rest verifiable.');
    if (data.indexOf('bing') !== -1) add('bing', 2, 'You have Bing Webmaster Tools; use it.');
    if (data.indexOf('psi') !== -1 && !score.cwv) add('cwv', 1, 'PageSpeed data is available.');
    add('reporting', Math.max(1, score.reporting || 0), 'Findings need evidence and a next step.');

    var list = Object.keys(score).map(function (key) {
      var m = MODULE_BY_KEY[key], t = AREA_TEXT[key];
      return { key: key, module: m, priority: PRIO_NAME[score[key]], level: score[key], reason: reason[key] || '', problem: t.problem, why: t.why, investigate: t.investigate, evidence: t.evidence, next: t.next };
    });
    list.sort(function (a, b) { return b.level - a.level || a.module.id.localeCompare(b.module.id); });
    return list;
  }

  /* ---- sample audits (fictional) --------------------------------------- */
  function f(priority, category, title, url, evidence, why, action, moduleKey) {
    return { priority: priority, category: category, title: title, url: url, evidence: evidence, why: why, action: action, module: moduleKey };
  }
  var CATS = [['technical', 'Technical SEO'], ['onpage', 'On-Page SEO'], ['indexation', 'Indexation'], ['linking', 'Internal Linking'], ['schema', 'Structured Data'], ['content', 'Content'], ['cwv', 'Core Web Vitals']];
  var SAMPLES = [
    {
      id: 'shopify-store', name: 'Shopify Ecommerce Store', host: 'harbourline-outdoors.example', platform: 'shopify', pages: 640,
      blurb: 'A 500-product outdoor gear store on Shopify, six months after a theme change.',
      scores: { technical: 84, onpage: 76, indexation: 68, linking: 62, schema: 91, content: 65, cwv: 73 },
      findings: [
        f('CRITICAL', 'indexation', 'Sitemap submits noindexed collection variants', '/collections/all/products/trail-jacket', 'Sitemap lists the URL; rendered head carries <meta name="robots" content="noindex">.', 'Search engines are being asked to index a page the page itself refuses. The conflict wastes crawl budget and hides the canonical product URL.', 'Determine which URL is meant to be canonical for the product before changing either the sitemap or the directive.', 'indexation'),
        f('CRITICAL', 'technical', 'Canonical points at a collection path, not the product', '/products/trail-jacket', 'rel="canonical" → /collections/jackets/products/trail-jacket (200). Product URL is the intended canonical per navigation.', 'The collection-path variant inherits the signals; the clean product URL loses them. Rankings split.', 'Confirm the theme setting or app that writes the canonical; record which variant Search Console reports as Google-selected.', 'technical'),
        f('HIGH', 'onpage', '38 products share one meta description', '/products/* (38 URLs)', 'Identical description text on 38 product pages; each has an empty SEO description field.', 'A site-wide fallback gives searchers nothing page-specific to click on.', 'Identify the fallback in the theme; write descriptions for the 10 products with the most impressions first.', 'onpage'),
        f('HIGH', 'linking', 'Collection "Sale" reachable only from a retired footer link', '/collections/sale', 'Zero internal inlinks in the crawl; present in sitemap; 24 products only reachable through it.', 'Twenty-four earning pages are one removed link from orphaned.', 'Decide where Sale belongs in the navigation; do not add a link just anywhere.', 'linking'),
        f('HIGH', 'cwv', 'LCP 3.9 s on product template (field)', '/products/trail-jacket', 'LCP element: hero image 2400×2400 served at 600 px display; no width/height; lazy-loaded.', 'The largest element on the page that earns loads last and shifts the layout when it arrives.', 'Confirm the theme image settings before editing; measure again after one change.', 'cwv'),
        f('MEDIUM', 'content', 'Buying guides decayed 41% year on year', '/blogs/guides/* (12 URLs)', 'Clicks down 41% over 12 months on 12 guides; impressions stable; positions slid 4→9.', 'The pages still show for the query and are being chosen less: the answer aged.', 'Compare the top three current results for each guide\'s main query with the guide\'s outline.', 'content'),
        f('MEDIUM', 'technical', 'www → non-www redirect is a 302', 'https://www.harbourline-outdoors.example/', '302 → https://harbourline-outdoors.example/ (one hop).', 'A temporary redirect on the host itself tells engines the move may reverse.', 'Change to 301 at the domain settings level, then re-check.', 'technical'),
        f('LOW', 'schema', 'BreadcrumbList names differ from visible breadcrumbs', '/collections/jackets', 'JSON-LD item name "Jackets & Shells"; visible breadcrumb "Jackets".', 'Minor mismatch; not a policy risk, but the markup should describe the page.', 'Align the theme snippet with the collection title.', 'schema'),
      ],
    },
    {
      id: 'wordpress-blog', name: 'WordPress Blog', host: 'kitchen-notes.example', platform: 'wordpress', pages: 1180,
      blurb: 'A recipe and technique blog with 1,100 posts, two SEO plugins and eight years of redirects.',
      scores: { technical: 71, onpage: 69, indexation: 74, linking: 58, schema: 66, content: 61, cwv: 55 },
      findings: [
        f('CRITICAL', 'schema', 'Recipe markup carries ratings with no visible reviews', '/recipes/sourdough-focaccia/', 'JSON-LD aggregateRating 4.8 (212); no rating or review element rendered on the page.', 'Markup that claims what the page does not show is a manual-action risk regardless of what a validator says.', 'Find which plugin emits the rating block; determine whether reviews exist anywhere before removing or restoring.', 'schema'),
        f('CRITICAL', 'cwv', 'CLS 0.42 on post template (field)', '/recipes/*', 'Layout shifts from an ad slot injected above the fold after fonts load; no reserved height.', 'Nearly every visitor sees the content jump; field data fails the threshold on the template that carries the traffic.', 'Reserve the slot height in the theme; re-measure field data after 28 days.', 'cwv'),
        f('HIGH', 'technical', 'Two plugins write competing canonicals', '/techniques/knife-skills/', 'Two rel="canonical" elements: self and a /?p=8812 variant.', 'Engines pick one; you do not get to choose which.', 'Disable canonical output in one plugin after confirming which is authoritative.', 'technical'),
        f('HIGH', 'linking', '212 posts with a single inlink (the archive page)', '/recipes/* (212 URLs)', 'Crawl inlink count = 1 for 212 posts; depth 4+.', 'Deep posts are crawled rarely and rank on nothing but their own merit.', 'Identify the 30 posts with the most impressions among them; link them from related posts first.', 'linking'),
        f('HIGH', 'content', 'Three posts rank for the same query and split it', '"how to sharpen a knife": /techniques/knife-skills/, /blog/sharpening/, /gear/whetstones/', 'Search Console shows all three for the query, positions 6, 9 and 14, alternating weekly.', 'Cannibalisation: none of the three earns what one would.', 'Decide which page should own the query; consolidate the others with a 301 or a clear scope.', 'content'),
        f('MEDIUM', 'onpage', 'Titles truncated on 140 posts', '/recipes/* (140 URLs)', 'Titles over 70 characters with the site name appended twice.', 'The searcher does not see the part that answers the query.', 'Check the plugin title template for a duplicated site-name variable.', 'onpage'),
        f('MEDIUM', 'indexation', 'Tag archives indexed (1,900 thin pages)', '/tag/* (1,900 URLs)', 'Indexed; average 40 words of unique content; no inbound links.', 'Thin archives dilute crawl and compete with posts.', 'Decide a policy for tag archives (noindex or curated) before bulk changes.', 'indexation'),
        f('LOW', 'technical', 'Redirect chain on legacy URLs', '/2018/03/focaccia/', '301 → /recipes/focaccia/ → 301 → /recipes/sourdough-focaccia/ (2 hops).', 'Two hops work but leak a little signal and slow the visit.', 'Point the first rule at the final URL.', 'technical'),
      ],
    },
    {
      id: 'saas', name: 'SaaS Website', host: 'ledgerline.example', platform: 'nextjs', pages: 210,
      blurb: 'A B2B SaaS marketing site on Next.js with docs, a blog and a pricing page that carries the revenue.',
      scores: { technical: 78, onpage: 81, indexation: 62, linking: 70, schema: 88, content: 72, cwv: 86 },
      findings: [
        f('CRITICAL', 'indexation', 'Docs section noindexed by a build-time flag', '/docs/* (96 URLs)', 'X-Robots-Tag: noindex on every /docs/ response; flag set for the preview environment and shipped.', 'Ninety-six pages of the most linkable content on the site are invisible.', 'Confirm the intended policy for docs; check the environment variable in the production build before flipping it.', 'indexation'),
        f('HIGH', 'technical', 'Pricing page canonical points at /pricing?plan=team', '/pricing', 'rel="canonical" → /pricing?plan=team; the parameterised URL 200s with identical content.', 'The page that earns points its signals at a variant.', 'Determine the canonical URL for pricing; check the router-generated head.', 'technical'),
        f('HIGH', 'content', 'Comparison pages earn impressions, no clicks', '/compare/* (8 URLs)', 'Impressions 12k/month, CTR 0.4%, position 8–12; titles are "Ledgerline vs X".', 'The query has moved to "X alternative"; the pages answer the old phrasing.', 'Read the top results for the target query; rewrite the title and opening to match intent before touching the body.', 'content'),
        f('HIGH', 'linking', 'Blog links to docs go through a redirect', '/blog/* → /documentation/* → /docs/*', '140 internal links point at the pre-rename path; each 301s.', 'Every link leaks a little and adds a hop.', 'Update links in the CMS; keep the redirect.', 'linking'),
        f('MEDIUM', 'onpage', 'Homepage H1 is the logo alt text', '/', 'H1 element wraps the logo image; visible headline is an H2.', 'The page\'s topic is stated in an image, not text.', 'Make the visible headline the H1; the logo needs no heading.', 'onpage'),
        f('MEDIUM', 'schema', 'SoftwareApplication schema lists a price not shown on the page', '/', 'offers.price "0" on the homepage; pricing page shows $29.', 'A free price the page does not show is inaccurate markup.', 'Remove the offer from the homepage markup or make it true.', 'schema'),
        f('LOW', 'cwv', 'INP 240 ms on pricing (field)', '/pricing', 'Long task from the chat widget on first interaction.', 'Just over the threshold; the widget is the cause.', 'Defer the widget until after first interaction.', 'cwv'),
      ],
    },
    {
      id: 'local-business', name: 'Local Business Website', host: 'harbourline-physio.example', platform: 'static', pages: 24,
      blurb: 'A three-location physiotherapy clinic on a static site: services, locations, a booking form.',
      scores: { technical: 88, onpage: 64, indexation: 90, linking: 75, schema: 52, content: 70, cwv: 92 },
      findings: [
        f('CRITICAL', 'schema', 'LocalBusiness markup on every page carries one address for three clinics', '/* (24 URLs)', 'Identical LocalBusiness block with the head-office address on all pages, including the two other locations\' pages.', 'The location pages tell engines they are somewhere else.', 'Decide one entity per location page; remove the site-wide block from pages it does not describe.', 'schema'),
        f('HIGH', 'onpage', 'All three location pages share a title', '/locations/*', '"Physiotherapy | Harbourline Physio" on all three; no town name.', 'The pages cannot rank for their own town.', 'Put the town in the title and H1 of each location page.', 'onpage'),
        f('HIGH', 'content', 'Service pages have no answer to price or duration', '/services/* (6 URLs)', 'Top three results for "physiotherapy [town]" all state first-session price and duration; these pages do not.', 'The competitor pages answer the question the searcher has.', 'Add the facts the query implies; measure position after four weeks.', 'competitor'),
        f('MEDIUM', 'technical', 'Booking form page returns 200 and a "coming soon" placeholder', '/book', 'Linked from every page; content is a placeholder; sitemap lists it.', 'A page every CTA points at that answers nothing.', 'Either finish the page or point the CTAs at the working form.', 'technical'),
        f('MEDIUM', 'linking', 'Location pages not linked from services', '/services/* → /locations/*', 'No links from service pages to the location that provides them.', 'The pages that should reinforce each other do not.', 'Add a "Available at" block to each service page.', 'linking'),
        f('LOW', 'indexation', 'Old PDF price list still indexed', '/downloads/prices-2023.pdf', 'Indexed; not linked; contains prices no longer charged.', 'Searchers can land on stale prices.', 'Decide whether to update, redirect or remove the file.', 'indexation'),
      ],
    },
  ];
  var CHECK_SEQUENCE = ['robots.txt', 'sitemap.xml', 'HTTP response codes', 'canonical URLs', 'titles', 'descriptions', 'headings', 'internal links', 'image ALT attributes', 'structured data', 'indexability', 'content', 'performance readiness'];

  return { MODULES: MODULES, MODULE_BY_KEY: MODULE_BY_KEY, PROBLEMS: PROBLEMS, PLATFORMS: PLATFORMS, SYMPTOMS: SYMPTOMS, DATA_SOURCES: DATA_SOURCES, recommend: recommend, SAMPLES: SAMPLES, CATS: CATS, CHECK_SEQUENCE: CHECK_SEQUENCE, PRIO: PRIO };
})();
