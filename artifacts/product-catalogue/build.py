#!/usr/bin/env python3
"""Build index.html for the product catalogue artifact.

Every fact here is read from the live store or the product listings on
18 September 2026: titles, prices, SKUs, file/module counts. The images are
the products' own featured images, inlined because the artifact sandbox
blocks image loads from any host. Re-run after a price or product change.
"""
import json, os, html
HERE = os.path.dirname(os.path.abspath(__file__))
IMG = json.load(open(os.path.join(HERE, 'images.json')))
SITE = 'https://sitebuilderstack.com'
UTM = 'utm_source=claude_artifact&utm_medium=interactive_tool&utm_campaign=product_catalogue&utm_content='

P = [
 dict(key='launch-system', stage='Build', handle='claude-code-website-launch-system', sku='SBS-CCWLS-V1', price=19.99,
      name='The Claude Code Website Launch System', tag='Build and launch a production website',
      what='The end-to-end system for building a website with Claude Code: project definition, CLAUDE.md, the build workflow, SEO and security passes, and the launch checklist that decides go or no-go.',
      specs=[('Files','113'),('Modules','17'),('Prompts','100'),('Checklists','SEO · security · launch')],
      fit='You are building or rebuilding a site and want the whole path from empty folder to live, with the checks that stop a bad launch.'),
 dict(key='seo-toolkit', stage='Rank', handle='claude-code-seo-website-audit-toolkit', sku='SBS-CCSAT-V1', price=19.99,
      name='Claude Code SEO & Website Audit Toolkit', tag='Audit, optimise and validate for search',
      what='Fourteen audit modules — technical SEO through reporting — as Claude Code workflows that read the rendered site, capture evidence for every finding and change nothing until you decide.',
      specs=[('Files','55'),('Modules','14'),('Prompts','20'),('Platform workflows','Shopify · WordPress · Astro · Next.js · static')],
      fit='A site exists and is not found, or you want the audit method that produces findings you can re-check next month.'),
 dict(key='cro-toolkit', stage='Convert', handle='claude-code-conversion-revenue-optimization-toolkit', sku='SBS-CCCRO-V1', price=19.99,
      name='Claude Code Conversion & Revenue Optimization Toolkit', tag='Find where the site loses conversions, prove the fix',
      what='Measure, diagnose, prioritise, change and validate: funnels, analytics verification, landing pages, forms, copy and experiments, each workflow in a mode that observes before it touches anything.',
      specs=[('Files','99'),('Modules','13'),('Workflows','70'),('Commands','68')],
      fit='Traffic arrives and does not turn into leads or sales, and you want evidence rather than a redesign.'),
 dict(key='complete-stack', stage='Bundle', handle='complete-site-builder-stack', sku='SBS-CCSTACK-V1', price=39.99, bundle=True,
      name='Complete Site Builder Stack', tag='Launch System + SEO Toolkit + Conversion Toolkit',
      what='The three Build → Rank → Convert systems in one purchase, three downloads. Bought separately they are $19.99 each — $59.97; together, $39.99.',
      specs=[('Files','267'),('Systems','3'),('Separately','$59.97'),('Together','$39.99')],
      fit='You want the whole lifecycle for one site and would otherwise buy at least two of the three.'),
 dict(key='ops-system', stage='Operate', handle='claude-code-website-operations-maintenance-system', sku='SBS-CCWOMS-V1', price=39.99,
      name='Claude Code Website Operations & Maintenance System', tag='Keep a live website healthy',
      what='Monitoring, maintenance, security, troubleshooting and optimisation as scheduled workflows: the weekly inspection that changes nothing, the incident runbook, and the report and baseline templates that make next month a comparison.',
      specs=[('Files','106'),('Modules','17'),('Commands','19'),('Scripts','11'),('Checklists','9')],
      fit='The site is live and someone has to keep it that way — forms delivering, certificates renewing, backups actually restoring.'),
 dict(key='shopify-toolkit', stage='Shopify', handle='claude-code-shopify-automation-admin-api-toolkit', sku='SBS-CCSHOP-V1', price=39.99,
      name='Claude Code Shopify Automation & Admin API Toolkit', tag='Automate a Shopify store through the Admin API',
      what='Products, SEO metadata, collections, metafields, inventory, redirects and bulk operations through Shopify’s Admin GraphQL API — with dry runs, userErrors read on every call, and the rollback export taken first.',
      specs=[('Files','167'),('Modules','19'),('Commands','34'),('Scripts','32')],
      fit='You run a Shopify store and the work is repetitive, large, or both, and it must not break checkout.'),
 dict(key='migration-system', stage='Migrate', handle='claude-code-website-migration-replatforming-system', sku='SBS-CCWMRS-V1', price=29.99,
      name='Claude Code Website Migration & Replatforming System', tag='Move a website without losing what matters',
      what='Inventory, URL mapping with a scorecard, redirect generation for each platform, staging validation, the go/no-go audit and post-launch monitoring — so URLs, redirects, metadata, content, analytics and the forms survive the move.',
      specs=[('Files','190'),('Modules','20'),('Commands','37'),('Scripts','28'),('Checklists','13')],
      fit='A redesign, URL change, platform change or domain change is coming and the search traffic has to come with it.'),
 dict(key='agency-system', stage='Deliver', handle='claude-code-agency-client-delivery-system', sku='SBS-CCACDS-V1', price=39.99,
      name='Claude Code Agency & Client Delivery System', tag='Run client website projects end to end',
      what='Discovery, audits, proposals, scoping, onboarding, QA, launch, handoff, reporting and retainers as commands and templates, with a client-project skeleton and a worked example project.',
      specs=[('Files','201'),('Modules','21'),('Commands','37'),('Templates','29'),('Checklists','17')],
      fit='You deliver websites for other people and want the same process on every engagement.'),
]

def e(s): return html.escape(str(s), quote=True)
def url(p, loc): return f"{SITE}/products/{p['handle']}?{UTM}{loc}"

stages = [('Build','launch-system'),('Rank','seo-toolkit'),('Convert','cro-toolkit'),('Operate','ops-system'),('Shopify','shopify-toolkit'),('Migrate','migration-system'),('Deliver','agency-system'),('Bundle','complete-stack')]

cards = []
for i, p in enumerate(P):
    specs = ''.join(f'<div class="spec"><dt>{e(k)}</dt><dd>{e(v)}</dd></div>' for k, v in p['specs'])
    cards.append(f'''
<article class="sheet{' sheet-bundle' if p.get('bundle') else ''}" id="{p['key']}" aria-labelledby="h-{p['key']}">
  <div class="sheet-media"><img src="{IMG[p['key']]}" alt="Product image for {e(p['name'])}" width="720" height="540" loading="lazy" decoding="async"></div>
  <div class="sheet-body">
    <p class="stage"><span class="stage-tag">{e(p['stage'])}</span><span class="sku">{e(p['sku'])}</span></p>
    <h2 id="h-{p['key']}">{e(p['name'])}</h2>
    <p class="tagline">{e(p['tag'])}</p>
    <p class="what">{e(p['what'])}</p>
    <dl class="specs">{specs}</dl>
    <p class="fit"><span>For you if</span> {e(p['fit'])}</p>
    <div class="buy"><span class="price"><span class="amount">${p['price']:.2f}</span><span class="terms">one-time · instant download</span></span><a class="btn" href="{e(url(p, 'card_' + p['key']))}" target="_blank" rel="noopener">View {e(p['stage'] if not p.get('bundle') else 'the bundle')} on sitebuilderstack.com</a></div>
  </div>
</article>''')

chooser = [
 ('I am building a new website', 'launch-system'), ('My site is not getting found', 'seo-toolkit'), ('Traffic arrives but does not convert', 'cro-toolkit'),
 ('I want build, rank and convert together', 'complete-stack'), ('My site is live and needs looking after', 'ops-system'), ('I run a Shopify store', 'shopify-toolkit'),
 ('I am moving or replatforming a site', 'migration-system'), ('I deliver websites for clients', 'agency-system'),
]
chooser_html = ''.join(f'<button type="button" class="pick" data-pick="{k}">{e(q)}</button>' for q, k in chooser)
byname = {p['key']: p for p in P}
chooser_data = json.dumps({k: {'name': p['name'], 'price': f"${p['price']:.2f}", 'tag': p['tag'], 'url': url(p, 'chooser'), 'stage': p['stage']} for k, p in byname.items()})

page = f'''<title>Site Builder Stack Catalogue</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700;12..96,800&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
  :root {{
    --bg: #F4F5F9; --paper: #FFFFFF; --ink: #12151F; --muted: #4B5468; --dim: #6F788C; --rule: #D8DCE6; --rule-strong: #8A93A8;
    --accent: #3554D1; --accent-ink: #FFFFFF; --accent-soft: rgba(53,84,209,.09); --teal: #0B8F7E; --teal-soft: rgba(11,143,126,.10);
    --display: "Bricolage Grotesque", "Avenir Next", "Segoe UI", system-ui, sans-serif; --body: "IBM Plex Sans", "Helvetica Neue", Arial, system-ui, sans-serif; --mono: "IBM Plex Mono", ui-monospace, Menlo, Consolas, monospace;
  }}
  @media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ --bg: #0B0D12; --paper: #12151D; --ink: #E9ECF3; --muted: #A7B0C0; --dim: #7D8798; --rule: #232A38; --rule-strong: #7D8798; --accent: #8AA6FF; --accent-ink: #0B0D12; --accent-soft: rgba(138,166,255,.12); --teal: #5EEAD4; --teal-soft: rgba(94,234,212,.12); }} }}
  :root[data-theme="dark"] {{ --bg: #0B0D12; --paper: #12151D; --ink: #E9ECF3; --muted: #A7B0C0; --dim: #7D8798; --rule: #232A38; --rule-strong: #7D8798; --accent: #8AA6FF; --accent-ink: #0B0D12; --accent-soft: rgba(138,166,255,.12); --teal: #5EEAD4; --teal-soft: rgba(94,234,212,.12); }}
  * {{ box-sizing: border-box; }}
  html {{ color-scheme: light dark; }}
  body {{ margin: 0; background: var(--bg); color: var(--ink); font: 16px/1.55 var(--body); -webkit-font-smoothing: antialiased; }}
  .wrap {{ max-width: 72rem; margin: 0 auto; padding: 0 clamp(1rem, 4vw, 3rem); }}
  h1, h2, h3 {{ font-family: var(--display); line-height: 1.08; text-wrap: balance; letter-spacing: -.015em; margin: 0 0 .5rem; }}
  h1 {{ font-size: clamp(2.2rem, 1.4rem + 3.6vw, 4.4rem); font-weight: 800; max-width: 18ch; }}
  h2 {{ font-size: clamp(1.4rem, 1.15rem + 1vw, 2rem); font-weight: 700; }}
  a {{ color: var(--accent); }}
  .mono {{ font-family: var(--mono); }}
  .eyebrow {{ font: 500 .72rem var(--mono); letter-spacing: .14em; text-transform: uppercase; color: var(--accent); margin: 0 0 .75rem; }}
  .lede {{ font-size: 1.15rem; color: var(--muted); max-width: 60ch; margin: 0 0 1.5rem; }}

  header.hero {{ padding-block: clamp(2.5rem, 6vw, 5rem) 2rem; border-bottom: 1px solid var(--rule); }}
  .brand {{ display: flex; align-items: center; gap: .6rem; margin-bottom: 2.5rem; color: var(--ink); text-decoration: none; }}
  .brand .mark {{ width: 2rem; height: 2rem; border-radius: 7px; background: var(--accent); color: var(--accent-ink); display: grid; place-items: center; font: 700 .78rem var(--mono); }}
  .brand strong {{ font-family: var(--display); }}
  .lifecycle {{ display: flex; flex-wrap: wrap; gap: .5rem; margin: 1.5rem 0 0; padding: 0; list-style: none; }}
  .lifecycle a {{ display: inline-flex; align-items: center; gap: .5rem; padding: .5rem .9rem; border: 1px solid var(--rule-strong); border-radius: 999px; color: var(--ink); text-decoration: none; font-weight: 500; }}
  .lifecycle a:hover {{ border-color: var(--accent); color: var(--accent); }}
  .lifecycle .n {{ font: 500 .7rem var(--mono); color: var(--dim); }}
  .lifecycle .bundle a {{ background: var(--teal-soft); border-color: var(--teal); }}
  .facts {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(10rem, 1fr)); gap: 1rem; margin: 2rem 0 0; padding: 1.25rem 0 0; border-top: 1px solid var(--rule); }}
  .facts div {{ font-size: .9rem; color: var(--muted); }}
  .facts strong {{ display: block; font: 700 1.5rem var(--display); color: var(--ink); font-variant-numeric: tabular-nums; }}

  section.chooser {{ padding-block: 2.5rem; border-bottom: 1px solid var(--rule); }}
  .picks {{ display: flex; flex-wrap: wrap; gap: .5rem; margin: 1rem 0; }}
  .pick {{ font: inherit; cursor: pointer; padding: .55rem .95rem; border-radius: 999px; border: 1px solid var(--rule-strong); background: var(--paper); color: var(--ink); }}
  .pick.is-on {{ background: var(--accent); color: var(--accent-ink); border-color: var(--accent); }}
  .answer {{ margin-top: 1rem; padding: 1.1rem 1.25rem; border: 1px solid var(--rule); border-left: 4px solid var(--teal); border-radius: 0 12px 12px 0; background: var(--paper); display: grid; gap: .3rem; justify-items: start; }}
  .answer[hidden] {{ display: none; }}
  .answer p {{ margin: 0; }}

  .catalogue {{ padding-block: 2rem 1rem; display: grid; gap: 2rem; }}
  .sheet {{ display: grid; grid-template-columns: minmax(0, 5fr) minmax(0, 7fr); gap: clamp(1rem, 3vw, 2.5rem); align-items: start; padding: clamp(1.25rem, 3vw, 2rem); background: var(--paper); border: 1px solid var(--rule); border-radius: 18px; }}
  .sheet:nth-child(even) .sheet-media {{ order: 2; }}
  .sheet-bundle {{ border-color: var(--teal); box-shadow: 0 0 0 4px var(--teal-soft); }}
  .sheet-media img {{ width: 100%; height: auto; border-radius: 12px; border: 1px solid var(--rule); display: block; }}
  .stage {{ display: flex; align-items: center; gap: .8rem; margin: 0 0 .6rem; }}
  .stage-tag {{ font: 500 .7rem var(--mono); letter-spacing: .14em; text-transform: uppercase; color: var(--accent); background: var(--accent-soft); padding: .25rem .6rem; border-radius: 4px; }}
  .sheet-bundle .stage-tag {{ color: var(--teal); background: var(--teal-soft); }}
  .sku {{ font: 400 .72rem var(--mono); color: var(--dim); }}
  .tagline {{ font-family: var(--display); font-weight: 500; font-size: 1.15rem; margin: 0 0 .75rem; color: var(--muted); }}
  .what {{ margin: 0 0 1rem; max-width: 60ch; }}
  .specs {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(8.5rem, 1fr)); gap: .5rem; margin: 0 0 1rem; padding: .9rem 0; border-top: 1px solid var(--rule); border-bottom: 1px solid var(--rule); }}
  .spec dt {{ font: 500 .66rem var(--mono); letter-spacing: .12em; text-transform: uppercase; color: var(--dim); }}
  .spec dd {{ margin: 0; font: 600 1.05rem var(--display); font-variant-numeric: tabular-nums; }}
  .fit {{ margin: 0 0 1.1rem; color: var(--muted); max-width: 60ch; }}
  .fit span {{ font: 500 .7rem var(--mono); letter-spacing: .12em; text-transform: uppercase; color: var(--dim); display: block; }}
  .buy {{ display: flex; flex-wrap: wrap; align-items: center; gap: 1rem 1.5rem; }}
  .price {{ display: flex; flex-direction: column; }}
  .amount {{ font: 800 2rem/1 var(--display); font-variant-numeric: tabular-nums; }}
  .terms {{ font-size: .78rem; color: var(--dim); }}
  .btn {{ display: inline-flex; align-items: center; justify-content: center; min-height: 2.9rem; padding: .6rem 1.2rem; border-radius: 10px; background: var(--accent); color: var(--accent-ink); font-weight: 600; text-decoration: none; }}
  .btn:hover {{ filter: brightness(1.08); }}
  .btn:focus-visible, .pick:focus-visible, a:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 2px; }}

  section.terms {{ padding-block: 2.5rem 3rem; }}
  .cols {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr)); gap: 1.5rem; }}
  .cols h3 {{ font-size: 1rem; margin-bottom: .4rem; }}
  .cols ul {{ margin: 0; padding-left: 1.1rem; color: var(--muted); font-size: .95rem; }}
  .cols li {{ margin-bottom: .3rem; }}
  footer {{ padding-block: 1.5rem 3rem; border-top: 1px solid var(--rule); color: var(--dim); font-size: .82rem; }}
  footer p {{ max-width: 70ch; margin: 0 0 .5rem; }}
  @media (max-width: 760px) {{
    .sheet {{ grid-template-columns: 1fr; }}
    .sheet:nth-child(even) .sheet-media {{ order: 0; }}
    h1 {{ max-width: none; }}
  }}
  @media (prefers-reduced-motion: no-preference) {{ .btn, .pick, .lifecycle a {{ transition: background-color .15s, border-color .15s, color .15s; }} }}
</style>

<header class="hero"><div class="wrap">
  <a class="brand" href="{SITE}?{UTM}brand" target="_blank" rel="noopener"><span class="mark">SBS</span><strong>Site Builder Stack</strong></a>
  <p class="eyebrow">Digital products · September 2026</p>
  <h1>Eight systems for directing Claude Code through website work.</h1>
  <p class="lede">Each one is a downloadable set of Claude Code workflows, commands, checklists and templates for one job — building a site, getting it found, converting the traffic, keeping it running, automating a Shopify store, moving a site, or delivering for clients. Bought once, used on every site you own or manage.</p>
  <ol class="lifecycle" aria-label="Products by stage">{''.join(f'<li{" class=\"bundle\"" if s=="Bundle" else ""}><a href="#{k}"><span class="n">{i+1:02d}</span>{s}</a></li>' for i,(s,k) in enumerate(stages))}</ol>
  <div class="facts"><div><strong>8</strong>products, $19.99–$39.99</div><div><strong>931</strong>files across the seven systems (the bundle repackages three of them)</div><div><strong>1</strong>purchase per product — no subscription</div><div><strong>0</strong>results promised: these direct the work; you still review it</div></div>
</div></header>

<section class="chooser"><div class="wrap">
  <p class="eyebrow">Which one?</p>
  <h2>Pick the sentence that fits</h2>
  <div class="picks" role="group" aria-label="Your situation">{chooser_html}</div>
  <div class="answer" id="answer" hidden aria-live="polite"><p class="eyebrow" id="a-stage"></p><h3 id="a-name"></h3><p id="a-tag"></p><p><strong id="a-price"></strong></p><a class="btn" id="a-link" href="#" target="_blank" rel="noopener">View it on sitebuilderstack.com</a></div>
</div></section>

<main class="wrap catalogue" id="catalogue" aria-label="Product catalogue">{''.join(cards)}</main>

<section class="terms"><div class="wrap">
  <p class="eyebrow">Before you buy</p>
  <h2>What every product includes, and what none of them does</h2>
  <div class="cols">
    <div><h3>How it arrives</h3><ul><li>Instant download after Shopify checkout — a zip of Markdown files, commands and scripts you open in your own Claude Code session</li><li>One-time purchase; no account subscription, no seat licences</li><li>Nothing runs on our servers; nothing phones home</li></ul></div>
    <div><h3>What you may do</h3><ul><li>Use it on an unlimited number of your own sites and commercial projects</li><li>Use it on paid client work and charge what you like</li><li>Modify, adapt and extend any file; keep everything you produce with it</li></ul></div>
    <div><h3>What you may not do</h3><ul><li>Share, resell, sublicense or upload the files anywhere</li><li>Republish them as your own toolkit or course</li><li>Share one licence across a team — it is single-user</li></ul></div>
    <div><h3>What it is not</h3><ul><li>Not a guarantee of rankings, conversions or uptime — these are professional systems for directing Claude Code; the work still has to be reviewed by you</li><li>Not an official Anthropic product. Site Builder Stack is independent and not affiliated with Anthropic</li><li>The full terms are in LICENSE.md inside each download and on the store&rsquo;s <a href="{SITE}/pages/licence" target="_blank" rel="noopener">licence page</a></li></ul></div>
  </div>
</div></section>

<footer><div class="wrap"><p>Prices in USD as listed on sitebuilderstack.com on 18 September 2026; the product page is authoritative if they differ. &ldquo;Claude&rdquo; and &ldquo;Claude Code&rdquo; are product names and trademarks of Anthropic, PBC, referenced here to describe compatibility.</p><p><a href="{SITE}/collections/all?{UTM}footer" target="_blank" rel="noopener">All products</a> · <a href="{SITE}/blogs/guides?{UTM}footer" target="_blank" rel="noopener">Free guides</a> · <a href="{SITE}/pages/resources?{UTM}footer" target="_blank" rel="noopener">Free resources</a> · <a href="{SITE}/pages/build-rank-convert?{UTM}footer" target="_blank" rel="noopener">How the systems fit together</a></p></div></footer>

<script>
(function () {{
  var DATA = {chooser_data};
  var picks = document.querySelectorAll('.pick'), box = document.getElementById('answer');
  Array.prototype.forEach.call(picks, function (b) {{
    b.addEventListener('click', function () {{
      Array.prototype.forEach.call(picks, function (x) {{ x.classList.toggle('is-on', x === b); }});
      var d = DATA[b.getAttribute('data-pick')]; if (!d) return;
      document.getElementById('a-stage').textContent = d.stage + ' · ' + d.price;
      document.getElementById('a-name').textContent = d.name;
      document.getElementById('a-tag').textContent = d.tag;
      document.getElementById('a-price').textContent = d.price + ' one-time';
      document.getElementById('a-link').setAttribute('href', d.url);
      box.hidden = false;
    }});
  }});
}})();
</script>
'''
open(os.path.join(HERE, 'index.html'), 'wb').write(page.encode('ascii', 'xmlcharrefreplace'))
print('wrote index.html', len(page), 'bytes; total files', sum(int(p['specs'][0][1]) for p in P if not p.get('bundle')) + 0)
