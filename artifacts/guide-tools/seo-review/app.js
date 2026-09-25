/* Shopify SEO Review Worksheet — the review step from the guide, as a tool.
 *
 * No network of any kind: no store connection, no analytics, no fetch. Rows
 * live in memory for the life of the tab, which is stated on the page rather
 * than implied. The CSV it exports uses the worksheet's exact column order so
 * it drops into the same process.
 */
(function () {
  'use strict';

  var FIELDS = ['product_id', 'handle', 'product_url', 'current_seo_title',
    'current_seo_description', 'proposed_seo_title', 'proposed_seo_description',
    'approval_status', 'reviewer_notes'];

  var STATUSES = [
    ['needs review', 'Needs review', 'chip'],
    ['approved', 'Approved', 'chip chip--ok'],
    ['rejected', 'Rejected', 'chip chip--bad'],
    ['no change', 'No change', 'chip chip--same'],
    ['needs info', 'Needs info', 'chip chip--warn']
  ];

  /* Opens with the guide's worked example so the tool shows what it does
     rather than an empty shell. Fictional store, stated as such. */
  var SEED = [
    { product_id: 'gid://shopify/Product/2222222222222', handle: 'linen-tea-towel-set',
      product_url: 'https://example-store.myshopify.com/products/linen-tea-towel-set',
      current_seo_title: 'Linen Tea Towel Set',
      current_seo_description: 'Linen tea towel set. Buy now. Best prices. Free shipping on all orders.',
      proposed_seo_title: 'Linen Tea Towel Set of 3 | Example Store',
      proposed_seo_description: 'Three washed-linen tea towels, 50 x 70 cm, with hanging loops. Sold as a set.',
      approval_status: 'approved',
      reviewer_notes: 'Replaced unverifiable claims. Free shipping is a policy, not a product fact. Count and dimensions come from the body copy.' },
    { product_id: 'gid://shopify/Product/3333333333333', handle: 'enamel-mug-navy',
      product_url: 'https://example-store.myshopify.com/products/enamel-mug-navy',
      current_seo_title: 'Navy Enamel Mug 350ml | Example Store',
      current_seo_description: 'A 350 ml navy enamel camping mug with a rolled rim. Dishwasher safe.',
      proposed_seo_title: 'Navy Enamel Mug 350ml | Example Store',
      proposed_seo_description: 'A 350 ml navy enamel camping mug with a rolled rim. Dishwasher safe.',
      approval_status: 'no change',
      reviewer_notes: 'Already specific and accurate. Rewriting would churn the field for no reader benefit.' },
    { product_id: 'gid://shopify/Product/4444444444444', handle: 'cast-iron-skillet-26cm',
      product_url: 'https://example-store.myshopify.com/products/cast-iron-skillet-26cm',
      current_seo_title: 'Cast Iron Skillet 26cm | Example Store',
      current_seo_description: 'A 26 cm pre-seasoned cast iron skillet with a helper handle.',
      proposed_seo_title: 'Cast Iron Skillet 26cm - Lifetime Guarantee | Example Store',
      proposed_seo_description: 'Our lifetime-guaranteed 26 cm skillet is the last pan you will ever buy. Oven safe to 260 C.',
      approval_status: 'rejected',
      reviewer_notes: 'No lifetime guarantee exists. "The last pan you will ever buy" is unsupportable and the 260 C figure is nowhere in the product data. Three inventions in one row.' }
  ];

  var rows = JSON.parse(JSON.stringify(SEED));
  var downloads = null;

  function el(tag, attrs, kids) {
    var n = document.createElement(tag);
    if (attrs) Object.keys(attrs).forEach(function (k) {
      var v = attrs[k];
      if (v === null || v === undefined || v === false) return;
      if (k === 'class') n.className = v;
      else if (k === 'text') n.textContent = v;
      else if (k.slice(0, 2) === 'on') n.addEventListener(k.slice(2), v);
      else n.setAttribute(k, v === true ? '' : String(v));
    });
    (kids || []).forEach(function (k) { if (k) n.appendChild(typeof k === 'string' ? document.createTextNode(k) : k); });
    return n;
  }
  function clear(n) { while (n.firstChild) n.removeChild(n.firstChild); return n; }
  var $ = function (id) { return document.getElementById(id); };

  /* Guidance, not a rule. Google truncates on pixel width and may substitute
     its own text entirely, which the page says out loud. */
  var LIMITS = { proposed_seo_title: 60, proposed_seo_description: 155 };

  function counter(field, value) {
    var lim = LIMITS[field], n = (value || '').length;
    var c = el('span', { class: 'count' + (n > lim ? ' is-over' : ''),
      text: n + ' / ~' + lim });
    c.title = n > lim ? 'Longer than the guidance. Not an error — Google truncates by width, not characters.' : '';
    return c;
  }

  function textField(row, field, label, multiline) {
    var wrap = el('div', { class: 'field' });
    var head = el('div', { class: 'toolbar', style: 'justify-content:space-between;gap:var(--sp-2)' });
    head.appendChild(el('label', { class: 'lbl', for: field + '-' + row._id, text: label }));
    var cnt = LIMITS[field] ? counter(field, row[field]) : null;
    if (cnt) head.appendChild(cnt);
    wrap.appendChild(head);
    var input = el(multiline ? 'textarea' : 'input', {
      id: field + '-' + row._id,
      type: multiline ? null : 'text',
      rows: multiline ? 2 : null,
      oninput: function (e) {
        row[field] = e.target.value;
        if (cnt) { var nw = counter(field, row[field]); cnt.className = nw.className; cnt.textContent = nw.textContent; cnt.title = nw.title; }
        refreshOutputs();
      }
    });
    input.value = row[field] || '';
    wrap.appendChild(input);
    return wrap;
  }

  function statusPicker(row) {
    var wrap = el('div', { class: 'field' });
    wrap.appendChild(el('span', { class: 'lbl', text: 'Decision' }));
    var bar = el('div', { class: 'toolbar' });
    STATUSES.forEach(function (s) {
      var active = row.approval_status === s[0];
      var b = el('button', {
        type: 'button',
        class: 'btn btn--sm ' + (active ? '' : 'btn--ghost'),
        'aria-pressed': String(active),
        onclick: function () { row.approval_status = s[0]; render(); }
      }, [s[1]]);
      bar.appendChild(b);
    });
    wrap.appendChild(bar);
    return wrap;
  }

  function rowCard(row, i) {
    var st = STATUSES.filter(function (s) { return s[0] === row.approval_status; })[0] || STATUSES[0];
    var head = el('div', { class: 'toolbar', style: 'justify-content:space-between' }, [
      el('div', { class: 'toolbar' }, [
        el('span', { class: st[2], text: st[1] }),
        el('strong', { text: row.handle || 'untitled row' })
      ]),
      el('button', { class: 'btn btn--quiet btn--sm', type: 'button',
        onclick: function () { rows.splice(i, 1); render(); } }, ['Remove'])
    ]);

    var ident = el('div', { class: 'grid2' }, [
      textField(row, 'product_id', 'Product id'),
      textField(row, 'handle', 'Handle')
    ]);
    var cur = el('div', { class: 'grid2' }, [
      textField(row, 'current_seo_title', 'Current SEO title'),
      textField(row, 'current_seo_description', 'Current meta description', true)
    ]);
    var prop = el('div', { class: 'grid2' }, [
      textField(row, 'proposed_seo_title', 'Proposed SEO title'),
      textField(row, 'proposed_seo_description', 'Proposed meta description', true)
    ]);

    var same = row.proposed_seo_title === row.current_seo_title &&
               row.proposed_seo_description === row.current_seo_description;
    var hint = same && row.approval_status !== 'no change'
      ? el('p', { class: 'note', text: 'The proposed values are identical to the current ones. If nothing should change, mark it "No change" — that is a decision, and it belongs in the record.' })
      : null;

    return el('div', { class: 'card' }, [
      head, ident, cur, prop, hint,
      statusPicker(row),
      textField(row, 'reviewer_notes', 'Why (the column that makes the sheet worth keeping)', true)
    ]);
  }

  function blank() {
    var r = { _id: 'r' + Math.random().toString(36).slice(2, 8) };
    FIELDS.forEach(function (f) { r[f] = ''; });
    r.approval_status = 'needs review';
    return r;
  }

  function csv() {
    var q = function (v) { return '"' + String(v === undefined || v === null ? '' : v).replace(/"/g, '""') + '"'; };
    var lines = [FIELDS.map(q).join(',')];
    rows.forEach(function (r) {
      lines.push(FIELDS.map(function (f) {
        var v = String(r[f] || '');
        /* A non-empty value starting with = + - @ is executed as a formula by
           Excel and Sheets. Prefix it, exactly as the worksheet README says. */
        if (v && '=+-@'.indexOf(v[0]) !== -1) v = "'" + v;
        return q(v);
      }).join(','));
    });
    return lines.join('\n') + '\n';
  }

  function refreshOutputs() {
    var counts = {};
    rows.forEach(function (r) { counts[r.approval_status] = (counts[r.approval_status] || 0) + 1; });
    var parts = STATUSES.filter(function (s) { return counts[s[0]]; })
      .map(function (s) { return counts[s[0]] + ' ' + s[0]; });
    $('tally').textContent = rows.length + (rows.length === 1 ? ' row' : ' rows') +
      (parts.length ? ' — ' + parts.join(', ') : '');
    var pv = $('preview');
    if (!pv.hidden) pv.textContent = csv();
    $('copy').disabled = rows.length === 0;
    $('download').disabled = rows.length === 0;
  }

  function render() {
    var host = clear($('rows'));
    rows.forEach(function (r, i) {
      if (!r._id) r._id = 'r' + Math.random().toString(36).slice(2, 8);
      host.appendChild(rowCard(r, i));
    });
    if (!rows.length) {
      host.appendChild(el('div', { class: 'card' }, [
        el('p', { class: 'muted', text: 'No rows. Add a product to start a review.' })
      ]));
    }
    refreshOutputs();
  }

  /* ---- controls ---- */
  $('add').addEventListener('click', function () {
    rows.push(blank()); render();
    var cards = document.querySelectorAll('#rows .card');
    var last = cards[cards.length - 1];
    if (last) { var f = last.querySelector('input'); if (f) f.focus(); }
  });

  $('reset').addEventListener('click', function () {
    rows = JSON.parse(JSON.stringify(SEED));
    render();
    $('status').textContent = '';
    $('top').focus({ preventScroll: true });
    window.scrollTo(0, 0);
  });

  $('toggle-preview').addEventListener('click', function () {
    var pv = $('preview');
    pv.hidden = !pv.hidden;
    this.textContent = pv.hidden ? 'Show the CSV' : 'Hide the CSV';
    refreshOutputs();
  });

  function setStatus(msg, err) {
    var s = $('status');
    s.textContent = msg;
    s.className = 'status' + (err ? ' status--err' : '');
  }

  $('copy').addEventListener('click', function () {
    var text = csv();
    clear($('fallback'));
    var fail = function () {
      setStatus('Could not copy automatically.', true);
      var ta = el('textarea', { readonly: true, 'aria-label': 'CSV to copy', rows: 8, style: 'width:100%' });
      ta.value = text;
      $('fallback').appendChild(el('div', { class: 'field', style: 'margin-top:var(--sp-3)' }, [
        el('p', { class: 'small dim', text: 'Clipboard access was refused here. The text is selected below — press Ctrl+C or ⌘C.' }), ta
      ]));
      try { ta.focus(); ta.select(); } catch (e) {}
    };
    try {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(function () { setStatus('Copied.'); }, fail);
      } else { fail(); }
    } catch (e) { fail(); }
  });

  $('download').addEventListener('click', function () {
    if (!downloads) { setStatus('File download is not available in this view.', true); return; }
    setStatus('Waiting for you to confirm the download…');
    downloads.save({ filename: 'shopify-seo-review-worksheet.csv', data: csv() })
      .then(function (r) { setStatus(r && r.status === 'saved' ? 'Saved.' : 'Sent to your device.'); },
            function (err) {
              setStatus(err && err.code === 'declined' ? 'Download cancelled.'
                : 'The download could not be completed. Use “Copy CSV” instead.', true);
            });
  });

  if (window.claude && typeof window.claude.use === 'function') {
    try {
      window.claude.use('downloads').then(function (d) {
        downloads = d;
        $('download').hidden = !d;
        $('dl-note').hidden = !!d;
      }).catch(function () { $('dl-note').hidden = false; });
    } catch (e) { $('dl-note').hidden = false; }
  } else {
    $('dl-note').hidden = false;
  }

  render();
})();
