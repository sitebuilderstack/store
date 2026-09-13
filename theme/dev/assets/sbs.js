/* Site Builder Stack — landing enhancements.
   Progressive: every feature here works without JS, this only improves it.
   No dependencies. */
(function () {
  'use strict';

  /* ---- FAQ accordion -------------------------------------------------
     Markup ships expanded and functional without JS. This collapses the
     panels and wires up the buttons only once JS is available, so a
     no-JS visitor still reads every answer. */
  function initFaq() {
    var groups = document.querySelectorAll('[data-sbs-faq]');
    Array.prototype.forEach.call(groups, function (group) {
      var buttons = group.querySelectorAll('.sbs-faq__q');
      Array.prototype.forEach.call(buttons, function (btn, i) {
        var panel = document.getElementById(btn.getAttribute('aria-controls'));
        if (!panel) return;
        var open = i === 0;                      // first one stays open
        btn.setAttribute('aria-expanded', String(open));
        panel.hidden = !open;

        btn.addEventListener('click', function () {
          var isOpen = btn.getAttribute('aria-expanded') === 'true';
          btn.setAttribute('aria-expanded', String(!isOpen));
          panel.hidden = isOpen;
        });
      });
    });
  }

  /* ---- Sticky mobile buy bar -----------------------------------------
     Appears once the hero CTA has scrolled out of view, hides again over
     the buy section so it never covers the real form. */
  function initSticky() {
    var bar = document.querySelector('[data-sbs-sticky]');
    if (!bar) return;

    var heroCta = document.querySelector('[data-sbs-hero-cta]');
    var buySection = document.querySelector('[data-sbs-buy]');
    if (!heroCta) return;

    if (!('IntersectionObserver' in window)) return;  // bar stays hidden

    var pastHero = false;
    var atBuy = false;

    function update() {
      bar.setAttribute('data-visible', String(pastHero && !atBuy));
    }

    /* Show the bar only once the hero CTA has scrolled UP and out of view.
       Checking isIntersecting alone is not enough: at page load the CTA is
       below a shrunken root and reports as not intersecting, which showed the
       bar immediately. boundingClientRect.top < 0 distinguishes
       "scrolled past above" from "not reached yet". */
    new IntersectionObserver(function (entries) {
      var e = entries[0];
      pastHero = !e.isIntersecting && e.boundingClientRect.top < 0;
      update();
    }).observe(heroCta);

    if (buySection) {
      new IntersectionObserver(function (entries) {
        atBuy = entries[0].isIntersecting;
        update();
      }, { rootMargin: '0px 0px -20% 0px' }).observe(buySection);
    }
  }

  /* ---- Add-to-cart feedback ------------------------------------------
     The form posts normally without JS. With JS we give an immediate
     busy state so nobody double-submits. */
  function initForms() {
    var forms = document.querySelectorAll('[data-sbs-buy-form]');
    Array.prototype.forEach.call(forms, function (form) {
      form.addEventListener('submit', function () {
        var btn = form.querySelector('button[type="submit"]');
        if (!btn || btn.disabled) return;
        btn.disabled = true;
        btn.setAttribute('aria-busy', 'true');
        var original = btn.textContent;
        btn.textContent = btn.getAttribute('data-busy-label') || 'Adding…';
        // Re-enable if the browser restores the page from bfcache.
        window.addEventListener('pageshow', function () {
          btn.disabled = false;
          btn.removeAttribute('aria-busy');
          btn.textContent = original;
        }, { once: true });
      });
    });
  }

  /* ---- Smooth in-page links, respecting reduced motion --------------- */
  function initAnchors() {
    var reduce = window.matchMedia('(prefers-reduced-motion: reduce)');
    document.addEventListener('click', function (e) {
      var link = e.target.closest && e.target.closest('a[href^="#"]');
      if (!link) return;
      var id = link.getAttribute('href').slice(1);
      if (!id) return;
      var target = document.getElementById(id);
      if (!target) return;

      e.preventDefault();
      target.scrollIntoView({ behavior: reduce.matches ? 'auto' : 'smooth', block: 'start' });

      /* Move focus too — scrolling alone leaves keyboard and screen reader
         users where they were, which is the usual skip-link bug. */
      var hadTabindex = target.hasAttribute('tabindex');
      if (!hadTabindex) target.setAttribute('tabindex', '-1');
      target.focus({ preventScroll: true });
      if (!hadTabindex) {
        target.addEventListener('blur', function () {
          target.removeAttribute('tabindex');
        }, { once: true });
      }
      if (history.replaceState) history.replaceState(null, '', '#' + id);
    });
  }

  /* ---- Copy buttons on code blocks ------------------------------------
     Added by JS only: with no JS there is simply no button, and the code is
     still selectable. */
  /* ---- analytics ------------------------------------------------------
     Shopify's own analytics is the only analytics on this site, so events go
     through Shopify.analytics.publish rather than a second vendor script.
     Everything is guarded: if the object is absent the call is a no-op and
     nothing throws. No personal data is ever sent — only the event name and
     a short label describing what was interacted with. */
  function track(name, payload) {
    try {
      if (window.Shopify && window.Shopify.analytics &&
          typeof window.Shopify.analytics.publish === 'function') {
        window.Shopify.analytics.publish(name, payload || {});
      }
    } catch (e) { /* analytics must never break the page */ }
  }

  /* A single polite live region, shared by every component that needs to
     announce something. Created once, on demand. */
  var liveRegion = null;
  function announce(message) {
    if (!liveRegion) {
      liveRegion = document.createElement('div');
      liveRegion.className = 'sbs-visually-hidden';
      liveRegion.setAttribute('role', 'status');
      liveRegion.setAttribute('aria-live', 'polite');
      document.body.appendChild(liveRegion);
    }
    liveRegion.textContent = '';
    // Re-setting identical text does not re-announce, so defer a tick.
    window.setTimeout(function () { liveRegion.textContent = message; }, 30);
  }

  /* Links and buttons opt into an event by carrying data-sbs-track. Delegated
     from the document so markup rendered later still reports. */
  function initTracking() {
    document.addEventListener('click', function (ev) {
      var el = ev.target.closest ? ev.target.closest('[data-sbs-track]') : null;
      if (!el) return;
      track(el.getAttribute('data-sbs-track'), {
        label: (el.textContent || '').trim().slice(0, 80),
        href: el.getAttribute('href') || ''
      });
    }, { passive: true });
  }

  /* ---- copy buttons ---------------------------------------------------
     A <pre> can declare what it holds with data-sbs-copy="prompt|command|
     claudemd", which changes the button label and the event name. Anything
     else gets a plain Copy button, as before.

     The block's text is captured BEFORE the button is inserted. Reading
     pre.textContent at click time includes the button's own label, which
     silently appended "Copy" to the end of everything anyone copied. */
  var COPY_KINDS = {
    prompt:   { label: 'Copy prompt',  done: 'Prompt copied',  event: 'prompt_copied' },
    command:  { label: 'Copy command', done: 'Command copied', event: 'command_copied' },
    claudemd: { label: 'Add to CLAUDE.md', done: 'Copied — paste into CLAUDE.md', event: 'claudemd_example_copied' }
  };

  /* A single short line beginning with a shell command is a command, not a
     code sample. Deliberately narrow: a false "Copy command" on a config file
     is a worse outcome than a plain "Copy" on a real command, so multi-line
     blocks and anything unrecognised keep the generic label. */
  var COMMAND_START = /^(\$ |# |claude|npm|npx|pnpm|yarn|git|cd |curl|python3?|node|shopify|bash|sh |mkdir|cp |mv |chmod|export )/;
  function isCommand(text) {
    var lines = text.trim().split('\n');
    return lines.length === 1 && lines[0].length < 200 && COMMAND_START.test(lines[0]);
  }

  function initCopy() {
    if (!navigator.clipboard) return;
    var blocks = document.querySelectorAll('.sbs-article__body pre, .sbs-rte pre, [data-sbs-copyable] pre');
    Array.prototype.forEach.call(blocks, function (pre) {
      if (pre.querySelector('.sbs-copy')) return;
      var text = pre.textContent;
      var declared = pre.getAttribute('data-sbs-copy');
      if (!declared && pre.classList.contains('sbs-prompt')) declared = 'prompt';
      if (!declared && isCommand(text)) declared = 'command';
      var kind = COPY_KINDS[declared] ||
                 { label: 'Copy', done: 'Copied', event: 'code_copied' };

      var btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'sbs-copy';
      btn.textContent = kind.label;
      btn.setAttribute('aria-label', kind.label + ' to clipboard');
      btn.addEventListener('click', function () {
        navigator.clipboard.writeText(text).then(function () {
          btn.textContent = kind.done;
          announce(kind.done);
          track(kind.event, { label: kind.label });
          window.setTimeout(function () { btn.textContent = kind.label; }, 1800);
        }).catch(function () {
          btn.textContent = 'Press Ctrl+C';
          announce('Copying failed. Select the text and press Control C.');
          window.setTimeout(function () { btn.textContent = kind.label; }, 2600);
        });
      });
      pre.appendChild(btn);
    });
  }

  /* ---- guide library filter -------------------------------------------
     Filters by hiding rendered cards. No fetching, no templating, no
     dependency. With JS off the controls stay hidden and every guide is
     visible, which is also what a crawler sees. */
  function initLibrary() {
    var form = document.querySelector('[data-sbs-library-controls]');
    var list = document.querySelector('[data-sbs-library-list]');
    if (!form || !list) return;

    var status = document.querySelector('[data-sbs-library-status]');
    var empty = document.querySelector('[data-sbs-library-empty]');
    var items = Array.prototype.slice.call(list.querySelectorAll('[data-sbs-item]'));
    var q = form.querySelector('#sbs-lib-q');
    var selects = ['topic', 'level', 'goal', 'type'].map(function (k) {
      return { key: k, el: form.querySelector('#sbs-lib-' + k) };
    }).filter(function (s) { return s.el; });

    form.hidden = false;

    // Selecting a filter that matches nothing would be a dead end, so a value
    // in the URL is only applied if the control actually offers it.
    function applyFromUrl() {
      var params = new URLSearchParams(window.location.search);
      if (q && params.get('q')) q.value = params.get('q');
      selects.forEach(function (s) {
        var v = params.get(s.key);
        if (!v) return;
        var ok = Array.prototype.some.call(s.el.options, function (o) { return o.value === v; });
        if (ok) s.el.value = v;
      });
    }

    function writeUrl() {
      var params = new URLSearchParams();
      if (q && q.value.trim()) params.set('q', q.value.trim());
      selects.forEach(function (s) { if (s.el.value) params.set(s.key, s.el.value); });
      var qs = params.toString();
      var url = window.location.pathname + (qs ? '?' + qs : '');
      try { window.history.replaceState(null, '', url); } catch (e) { /* ignore */ }
    }

    var announceTimer = null;
    function apply(fromUser) {
      var term = q ? q.value.trim().toLowerCase() : '';
      var shown = 0;
      items.forEach(function (li) {
        var ok = true;
        selects.forEach(function (s) {
          if (s.el.value && li.getAttribute('data-' + s.key) !== s.el.value) ok = false;
        });
        if (ok && term && (li.getAttribute('data-text') || '').indexOf(term) === -1) ok = false;
        li.hidden = !ok;
        if (ok) shown++;
      });

      if (status) status.textContent = shown === 1 ? '1 guide' : shown + ' guides';
      if (empty) empty.hidden = shown !== 0;

      if (fromUser) {
        writeUrl();
        // Debounced so typing does not fire an event per keystroke.
        window.clearTimeout(announceTimer);
        announceTimer = window.setTimeout(function () {
          track(term ? 'guide_search_used' : 'guide_filter_used', { label: String(shown) });
        }, 500);
      }
    }

    function reset() {
      if (q) q.value = '';
      selects.forEach(function (s) { s.el.value = ''; });
      apply(true);
      announce('Filters cleared.');
      if (q) q.focus();
    }

    form.addEventListener('input', function () { apply(true); });
    form.addEventListener('change', function () { apply(true); });
    form.addEventListener('submit', function (ev) { ev.preventDefault(); });
    Array.prototype.forEach.call(document.querySelectorAll('[data-sbs-library-reset]'),
      function (b) { b.addEventListener('click', reset); });

    applyFromUrl();
    apply(false);
  }

  /* ---- learning-path engine -------------------------------------------
     Three questions reveal one of the server-rendered roadmaps. Nothing is
     built in JavaScript, so there is no shift and no flash of empty space —
     every panel is already in the document, just hidden.

     Progress is kept in localStorage under one key, with completed steps keyed
     by "<goal>:<index>". That means several roadmaps can hold progress at once
     and changing goal does not discard what was already ticked. Every storage
     call is guarded: private windows and blocked site data throw on access, and
     a roadmap that cannot remember is still a usable roadmap.

     Without this script the questions stay hidden and the hub list stays
     visible, which is why the fallback is rendered unconditionally. */
  /* ---- learning progress ------------------------------------------------
     One key for the whole site, deliberately separate from `sbs-route`: the
     roadmap on the homepage answers "where do I start" and is keyed by goal,
     while this records "what have I read" and is keyed by guide. Merging them
     would mean changing goal discarded reading history.

     Shape: { done: { "<handle>": <ts> }, saved: { "<handle>": {t,u,ts} } }

     Completion is keyed by guide rather than by track:guide on purpose. A guide
     that appears in two paths has been read once, and ticking it in one place
     while it stays unticked in another is the kind of detail that makes people
     stop trusting the feature.

     Every access is wrapped: private windows and blocked site data throw on
     read as well as write, and a page that cannot remember must still work. */
  /* ---- product picker ---------------------------------------------------
     Five questions, one recommendation, no framework.

     Each option carries its own score string in its value, so the weighting
     lives beside the question in the template rather than in a lookup table
     here that would have to be kept in step with it.

     The tie-break is the part worth stating. When the bundle ties with a single
     product, the SINGLE product wins. A quiz sold by the shop that breaks ties
     towards the most expensive answer is not a recommendation, and the cheapest
     way to make this untrustworthy would be to do the opposite quietly.

     `all` therefore has to win outright, which it does when the answers really
     do span the lifecycle.

     scripts/test-picker.js asserts the whole table, including the case that
     matters commercially: "traffic is not converting" must never return the
     Launch System. */
  var PICK_KEYS = ['build', 'rank', 'convert', 'operate', 'all'];
  var PICK_WHY = {
    build: 'Your answers point at getting the site built and shipped correctly, which is the problem before search and before conversion.',
    rank: 'The site exists; being found is the bottleneck. That is a diagnosis problem, and it comes before conversion work — conversion changes cannot be measured on traffic this thin.',
    convert: 'People are arriving and stopping. The job is finding where, with evidence, before changing anything.',
    operate: 'The site is live and the job is keeping it that way: monitoring, security, backups, updates and deploys, on a schedule, without a change ever reaching production unauthorised.',
    all: 'Your answers span all three stages, which is a lifecycle rather than a stage. A repeatable system across the three costs less than the three bought separately.'
  };

  function pickScore(form) {
    var totals = { build: 0, rank: 0, convert: 0, operate: 0, all: 0 };
    Array.prototype.forEach.call(form.querySelectorAll('input[type=radio]:checked'),
      function (input) {
        (input.value || '').split(',').forEach(function (pair) {
          var bits = pair.split(':');
          var key = (bits[0] || '').trim();
          var n = parseInt(bits[1], 10);
          if (PICK_KEYS.indexOf(key) > -1 && !isNaN(n)) totals[key] += n;
        });
      });
    return totals;
  }

  function pickWinner(totals) {
    var best = null, bestN = -1;
    /* Iterated in PICK_KEYS order with a strict >, so on a tie the earlier key
       wins — and `all` is last, which is what makes the bundle lose ties. */
    PICK_KEYS.forEach(function (k) {
      if (totals[k] > bestN) { bestN = totals[k]; best = k; }
    });
    /* The runner-up, offered only when it is genuinely close and is not the
       same recommendation dressed differently. */
    var second = null, secondN = -1;
    PICK_KEYS.forEach(function (k) {
      if (k !== best && totals[k] > secondN) { secondN = totals[k]; second = k; }
    });
    return { key: best, score: bestN,
             alt: (secondN > 0 && bestN - secondN <= 2) ? second : null };
  }

  function initPicker() {
    var root = document.querySelector('[data-sbs-picker]');
    if (!root) return;
    var form = root.querySelector('[data-sbs-picker-form]');
    var result = root.querySelector('[data-sbs-picker-result]');
    var fallback = document.querySelector('[data-sbs-picker-fallback]');
    var altEl = root.querySelector('[data-sbs-picker-alt]');
    if (!form || !result) return;

    root.hidden = false;
    if (fallback) fallback.hidden = true;

    var started = false;
    form.addEventListener('change', function () {
      if (started) return;
      started = true;
      track('product_selector_started', { label: 'picker' });
    });

    form.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var totals = pickScore(form);
      var win = pickWinner(totals);

      Array.prototype.forEach.call(result.querySelectorAll('[data-pick]'),
        function (c) { c.hidden = true; });
      var card = result.querySelector('[data-pick="' + win.key + '"]');
      if (!card) return;
      var why = card.querySelector('[data-sbs-pick-why]');
      if (why) why.textContent = PICK_WHY[win.key] || '';
      card.hidden = false;
      result.hidden = false;

      if (altEl) {
        var altCard = win.alt && result.querySelector('[data-pick="' + win.alt + '"] h4 a');
        if (altCard) {
          altEl.innerHTML = '';
          altEl.appendChild(document.createTextNode('Close second, and worth reading: '));
          var a = document.createElement('a');
          a.href = altCard.getAttribute('href');
          a.textContent = altCard.textContent;
          a.setAttribute('data-sbs-track', 'product_selector_alt_clicked');
          altEl.appendChild(a);
          altEl.appendChild(document.createTextNode('.'));
          altEl.hidden = false;
        } else { altEl.hidden = true; }
      }

      track('product_selector_completed', { label: 'picker' });
      track('product_recommended', { label: win.key });
      announce('Recommendation ready.');
      result.focus();
      result.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    });

    form.addEventListener('reset', function () {
      window.setTimeout(function () {
        result.hidden = true;
        if (altEl) altEl.hidden = true;
        announce('Answers cleared.');
      }, 0);
    });
  }

  /* ---- reading progress ------------------------------------------------
     How far through the article body you are, plus the heading you are under.

     Two things this deliberately does not do. It does not measure the whole
     document: the footer, the related-guides grid and the product CTA are not
     reading, and counting them makes the bar reach 70% at the end of the prose.
     And it does not announce anything to assistive technology — a screen reader
     navigates by heading and would hear the section name re-read on every
     scroll tick.

     The header is measured rather than assumed. It wraps to two rows below
     940px and carries an announcement bar above it, so a hard-coded offset
     would float the strip over the nav at exactly the widths where the page is
     hardest to read. */
  function initReadingProgress() {
    var root = document.querySelector('[data-sbs-reading]');
    var body = document.querySelector('.sbs-article__body');
    if (!root || !body) return;

    var fill = root.querySelector('[data-sbs-reading-fill]');
    var where = root.querySelector('[data-sbs-reading-section]');
    var heads = Array.prototype.slice.call(body.querySelectorAll('h2[id]'));

    function headerHeight() {
      var h = 0;
      ['.sbs-announcement', '.sbs-header'].forEach(function (sel) {
        var el = document.querySelector(sel);
        if (!el) return;
        var r = el.getBoundingClientRect();
        /* Only count what is actually pinned above the viewport top. The
           announcement bar scrolls away; the header does not. */
        if (r.bottom > 0 && r.top < 40) h = Math.max(h, r.bottom);
      });
      return h;
    }

    var ticking = false;
    function paint() {
      ticking = false;
      var top = body.getBoundingClientRect().top + window.scrollY;
      var height = body.offsetHeight;
      var seen = window.scrollY + window.innerHeight - top;
      var pct = Math.max(0, Math.min(100, (seen / height) * 100));
      if (fill) fill.style.width = pct.toFixed(1) + '%';

      root.style.top = headerHeight() + 'px';

      if (where && heads.length) {
        var mark = window.scrollY + headerHeight() + 24;
        var current = null;
        for (var i = 0; i < heads.length; i++) {
          if (heads[i].getBoundingClientRect().top + window.scrollY <= mark) current = heads[i];
          else break;
        }
        var label = current ? (current.textContent || '').trim() : '';
        if (where.textContent !== label) where.textContent = label;
      }
    }
    function onScroll() {
      if (ticking) return;
      ticking = true;
      window.requestAnimationFrame(paint);
    }

    root.hidden = false;
    paint();
    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', onScroll, { passive: true });
  }

  var LEARN_KEY = 'sbs-learning';

  function learnRead() {
    try {
      var raw = window.localStorage.getItem(LEARN_KEY);
      var v = raw ? JSON.parse(raw) : {};
      if (!v || typeof v !== 'object') v = {};
      if (!v.done || typeof v.done !== 'object') v.done = {};
      if (!v.saved || typeof v.saved !== 'object') v.saved = {};
      return v;
    } catch (e) { return { done: {}, saved: {} }; }
  }
  function learnWrite(v) {
    try {
      window.localStorage.setItem(LEARN_KEY, JSON.stringify(v));
      return true;
    } catch (e) { return false; }
  }
  function learnAvailable() {
    try {
      window.localStorage.setItem(LEARN_KEY + '-t', '1');
      window.localStorage.removeItem(LEARN_KEY + '-t');
      return true;
    } catch (e) { return false; }
  }

  /* Hub: fill in the progress bar over a path's own steps. */
  function initPathProgress() {
    var list = document.querySelector('[data-sbs-path]');
    if (!list || !learnAvailable()) return;
    var items = Array.prototype.slice.call(list.querySelectorAll('[data-sbs-lesson]'));
    if (!items.length) return;
    var wrap = document.querySelector('[data-sbs-path-progress]');
    var countEl = document.querySelector('[data-sbs-path-count]');
    var fillEl = document.querySelector('[data-sbs-path-fill]');

    function paint() {
      var state = learnRead();
      var done = 0;
      items.forEach(function (li) {
        var hit = !!state.done[li.getAttribute('data-sbs-lesson')];
        li.classList.toggle('is-done', hit);
        if (hit) done++;
      });
      var pct = Math.round((done / items.length) * 100);
      if (countEl) {
        countEl.textContent = done + ' of ' + items.length + ' complete — ' + pct + '%';
      }
      if (fillEl) fillEl.style.width = pct + '%';
      if (wrap) wrap.hidden = false;
    }
    paint();
  }

  /* Article: mark complete and save for later. */
  function initLessonControls() {
    var root = document.querySelector('[data-sbs-lesson-controls]');
    if (!root || !learnAvailable()) return;
    var id = root.getAttribute('data-lesson');
    if (!id) return;
    root.hidden = false;

    var doneBtn = root.querySelector('[data-sbs-lesson-done]');
    var saveBtn = root.querySelector('[data-sbs-lesson-save]');
    var doneLbl = root.querySelector('[data-sbs-lesson-done-label]');
    var saveLbl = root.querySelector('[data-sbs-lesson-save-label]');

    function paint() {
      var state = learnRead();
      var isDone = !!state.done[id];
      var isSaved = !!state.saved[id];
      if (doneBtn) {
        doneBtn.setAttribute('aria-pressed', isDone ? 'true' : 'false');
        doneBtn.classList.toggle('is-on', isDone);
      }
      if (saveBtn) {
        saveBtn.setAttribute('aria-pressed', isSaved ? 'true' : 'false');
        saveBtn.classList.toggle('is-on', isSaved);
      }
      /* The label states the CURRENT state, not the action, because the
         pressed state is what a screen reader announces from aria-pressed. */
      if (doneLbl) doneLbl.textContent = isDone ? 'Completed' : 'Mark complete';
      if (saveLbl) saveLbl.textContent = isSaved ? 'Saved' : 'Save for later';
    }

    if (doneBtn) {
      doneBtn.addEventListener('click', function () {
        var state = learnRead();
        if (state.done[id]) { delete state.done[id]; }
        else { state.done[id] = Date.now(); track('lesson_completed', { label: id }); }
        learnWrite(state);
        paint();
        announce(state.done[id] ? 'Marked complete.' : 'Marked not complete.');
      });
    }
    if (saveBtn) {
      saveBtn.addEventListener('click', function () {
        var state = learnRead();
        if (state.saved[id]) { delete state.saved[id]; }
        else {
          state.saved[id] = { t: root.getAttribute('data-title') || id,
                              u: root.getAttribute('data-url') || '',
                              ts: Date.now() };
          track('lesson_saved', { label: id });
        }
        learnWrite(state);
        paint();
        announce(state.saved[id] ? 'Saved for later.' : 'Removed from saved.');
      });
    }
    paint();
  }

  /* My learning: progress across every track, plus saved guides.

     Reads the tracks out of the rendered markup rather than from a copy of the
     site graph, so this cannot disagree with what the hubs show. */
  function initLearningHub() {
    var root = document.querySelector('[data-sbs-learning]');
    if (!root) return;
    if (!learnAvailable()) return;

    var tracks = Array.prototype.slice.call(root.querySelectorAll('[data-sbs-learn-track]'));
    var summary = root.querySelector('[data-sbs-learn-summary]');
    var doneEl = root.querySelector('[data-sbs-learn-done]');
    var subEl = root.querySelector('[data-sbs-learn-sub]');
    var savedBlock = root.querySelector('[data-sbs-learn-saved-block]');
    var savedList = root.querySelector('[data-sbs-learn-saved]');
    var resetBlock = root.querySelector('[data-sbs-learn-reset-block]');
    var resetBtn = root.querySelector('[data-sbs-learn-reset]');

    function paint() {
      var state = learnRead();
      var totalDone = 0, totalLessons = 0, tracksStarted = 0;

      tracks.forEach(function (t) {
        var lessons = Array.prototype.slice.call(t.querySelectorAll('[data-sbs-lesson]'));
        if (!lessons.length) return;
        var done = 0, next = null;
        lessons.forEach(function (li) {
          var hit = !!state.done[li.getAttribute('data-sbs-lesson')];
          li.classList.toggle('is-done', hit);
          var tick = li.querySelector('[data-sbs-learn-tick]');
          if (tick) tick.textContent = hit ? '\u2713' : '';
          if (hit) done++;
          else if (!next) next = li.querySelector('a');
        });
        totalDone += done;
        totalLessons += lessons.length;
        if (done > 0) tracksStarted++;

        var pct = Math.round((done / lessons.length) * 100);
        var countEl = t.querySelector('[data-sbs-learn-count]');
        var bar = t.querySelector('[data-sbs-learn-bar]');
        var fill = t.querySelector('[data-sbs-learn-fill]');
        var nextEl = t.querySelector('[data-sbs-learn-next]');
        if (countEl) {
          countEl.textContent = done + ' of ' + lessons.length + ' complete — ' + pct + '%';
          countEl.hidden = false;
        }
        if (bar) bar.hidden = false;
        if (fill) fill.style.width = pct + '%';
        if (nextEl) {
          if (next && done > 0) {
            nextEl.innerHTML = '';
            nextEl.appendChild(document.createTextNode('Next: '));
            var a = document.createElement('a');
            a.href = next.getAttribute('href');
            a.textContent = next.textContent;
            a.setAttribute('data-sbs-track', 'learning_path_next_clicked');
            nextEl.appendChild(a);
            nextEl.hidden = false;
          } else {
            nextEl.hidden = true;
          }
        }
        t.classList.toggle('is-complete', done === lessons.length);
      });

      if (doneEl) doneEl.textContent = String(totalDone);
      if (subEl) {
        subEl.textContent = totalLessons
          ? ('out of ' + totalLessons + ' across ' + tracks.length + ' tracks. ' +
             (tracksStarted ? tracksStarted + ' started.' : 'None started yet.'))
          : '';
      }
      if (summary) summary.hidden = false;

      /* Saved guides. Built from storage rather than from the page, because a
         saved guide need not be a lesson in any track. */
      var keys = Object.keys(state.saved);
      if (savedList) {
        savedList.innerHTML = '';
        keys.sort(function (a, b) {
          return (state.saved[b].ts || 0) - (state.saved[a].ts || 0);
        }).forEach(function (k) {
          var rec = state.saved[k] || {};
          var li = document.createElement('li');
          var a = document.createElement('a');
          a.href = rec.u || '#';
          a.textContent = rec.t || k;          /* textContent, never innerHTML */
          a.setAttribute('data-sbs-track', 'related_guide_clicked');
          li.appendChild(a);
          var rm = document.createElement('button');
          rm.type = 'button';
          rm.className = 'sbs-learn__remove';
          rm.textContent = 'Remove';
          rm.setAttribute('aria-label', 'Remove ' + (rec.t || k) + ' from saved');
          rm.addEventListener('click', function () {
            var st = learnRead();
            delete st.saved[k];
            learnWrite(st);
            paint();
            announce('Removed from saved.');
          });
          li.appendChild(rm);
          savedList.appendChild(li);
        });
      }
      if (savedBlock) savedBlock.hidden = keys.length === 0;
      if (resetBlock) {
        resetBlock.hidden = (totalDone === 0 && keys.length === 0);
      }
    }

    if (resetBtn) {
      resetBtn.addEventListener('click', function () {
        if (!window.confirm('Clear all saved progress in this browser? This cannot be undone.')) return;
        learnWrite({ done: {}, saved: {} });
        paint();
        announce('Progress reset.');
        track('learning_reset', { label: 'my-learning' });
      });
    }
    paint();
  }

  var ROUTE_KEY = 'sbs-route';
  var ROUTE_TOTAL = 7;

  function routeRead() {
    try {
      var raw = window.localStorage.getItem(ROUTE_KEY);
      var v = raw ? JSON.parse(raw) : {};
      if (!v || typeof v !== 'object') return { done: {} };
      if (!v.done || typeof v.done !== 'object') v.done = {};
      return v;
    } catch (e) { return { done: {} }; }
  }
  function routeWrite(v) {
    try { window.localStorage.setItem(ROUTE_KEY, JSON.stringify(v)); } catch (e) { /* ignore */ }
  }

  function initRoute() {
    var root = document.querySelector('[data-sbs-route]');
    if (!root) return;
    var fallback = document.querySelector('[data-sbs-selector-fallback]');
    var result = root.querySelector('[data-sbs-route-result]');
    var prompt = root.querySelector('[data-sbs-route-prompt]');
    var bar = root.querySelector('[data-sbs-route-bar]');
    var countEl = root.querySelector('[data-sbs-route-count]');
    var trackEl = root.querySelector('[data-sbs-route-track]');
    var fillEl = root.querySelector('[data-sbs-route-fill]');
    var panels = Array.prototype.slice.call(root.querySelectorAll('[data-sbs-route-panel]'));
    if (!result || !panels.length) return;

    root.hidden = false;
    if (fallback) fallback.hidden = true;

    var state = routeRead();
    var started = false;

    function picked(name) {
      var el = root.querySelector('input[name="' + name + '"]:checked');
      return el ? el.value : '';
    }
    function entryStep() {
      var el = root.querySelector('input[name="sbs-stage"]:checked');
      var n = el ? parseInt(el.getAttribute('data-entry'), 10) : 1;
      return isNaN(n) ? 1 : n;
    }

    function writeUrl(g, st, lv) {
      var params = new URLSearchParams(window.location.search);
      g ? params.set('build', g) : params.delete('build');
      st ? params.set('stage', st) : params.delete('stage');
      lv ? params.set('level', lv) : params.delete('level');
      var qs = params.toString();
      try {
        window.history.replaceState(null, '', window.location.pathname + (qs ? '?' + qs : '') + '#start');
      } catch (e) { /* ignore */ }
    }

    function paintProgress(goal) {
      var steps = root.querySelectorAll('[data-sbs-route-panel="' + goal + '"] [data-sbs-step]');
      var done = 0;
      Array.prototype.forEach.call(steps, function (li) {
        if (li.hidden) return;
        var id = li.getAttribute('data-step-id');
        var box = li.querySelector('[data-sbs-step-done]');
        var isDone = Boolean(state.done[id]);
        if (box) box.checked = isDone;
        li.classList.toggle('is-done', isDone);
        if (isDone) done++;
      });
      var pct = Math.round((done / ROUTE_TOTAL) * 100);
      if (countEl) countEl.textContent = done + ' of ' + ROUTE_TOTAL + ' steps completed';
      if (fillEl) fillEl.style.width = pct + '%';
      if (trackEl) trackEl.setAttribute('aria-valuenow', String(pct));
      var panel = root.querySelector('[data-sbs-route-panel="' + goal + '"]');
      var doneMsg = panel && panel.querySelector('[data-sbs-route-complete]');
      if (doneMsg) doneMsg.hidden = done < ROUTE_TOTAL;
      return done;
    }

    function render(fromUser) {
      var g = picked('sbs-goal'), st = picked('sbs-stage'), lv = picked('sbs-level');
      var complete = Boolean(g && st && lv);
      var entry = entryStep();

      panels.forEach(function (p) {
        var on = complete && p.getAttribute('data-sbs-route-panel') === g;
        p.hidden = !on;
        Array.prototype.forEach.call(p.querySelectorAll('[data-step-level]'), function (li) {
          li.hidden = !(on && li.getAttribute('data-step-level') === lv);
        });
        if (!on) return;
        // Mark where this visitor joins the roadmap. Earlier steps are shown
        // but de-emphasised rather than auto-ticked — ticking them would be
        // claiming progress the visitor never told us about.
        Array.prototype.forEach.call(p.querySelectorAll('[data-sbs-step]'), function (li) {
          var n = parseInt(li.getAttribute('data-sbs-step'), 10);
          li.classList.toggle('is-entry', n === entry);
          li.classList.toggle('is-before-entry', n < entry);
        });
      });

      result.hidden = false;
      if (bar) bar.hidden = !complete;
      if (prompt) {
        prompt.hidden = complete;
        if (!complete) {
          prompt.textContent = !g ? 'Pick what you are trying to accomplish.'
            : !st ? 'Now tell us where you are right now.'
            : 'Last one — how much Claude Code have you used?';
        }
      }

      if (complete) {
        state.goal = g; state.stage = st; state.level = lv;
        routeWrite(state);
        paintProgress(g);
      }
      if (fromUser) {
        writeUrl(g, st, lv);
        if (complete) {
          announce('Roadmap ready. Seven steps.');
          track('route_generated', { label: g + '/' + st + '/' + lv });
        }
      }
    }

    root.addEventListener('change', function (ev) {
      var t = ev.target;
      if (t.hasAttribute && t.hasAttribute('data-sbs-step-done')) {
        var id = t.getAttribute('data-sbs-step-done');
        if (t.checked) { state.done[id] = 1; } else { delete state.done[id]; }
        routeWrite(state);
        var n = paintProgress(picked('sbs-goal'));
        track(t.checked ? 'route_step_completed' : 'route_step_uncompleted', { label: id });
        if (n >= ROUTE_TOTAL) {
          announce('Roadmap complete.');
          track('route_completed', { label: picked('sbs-goal') });
        }
        return;
      }
      if (!started) { started = true; track('route_started', {}); }
      if (t.name === 'sbs-goal') track('route_goal_selected', { label: t.value });
      if (t.name === 'sbs-stage') track('route_stage_selected', { label: t.value });
      if (t.name === 'sbs-level') track('route_level_selected', { label: t.value });
      render(true);
    });

    var changeBtn = root.querySelector('[data-sbs-route-change]');
    if (changeBtn) {
      changeBtn.addEventListener('click', function () {
        var g = root.querySelector('input[name="sbs-goal"]:checked');
        if (g) g.checked = false;
        delete state.goal;
        routeWrite(state);
        render(true);
        announce('Pick a new goal.');
        var first = root.querySelector('input[name="sbs-goal"]');
        if (first) first.focus();
      });
    }

    var resetBtn = root.querySelector('[data-sbs-route-reset]');
    if (resetBtn) {
      resetBtn.addEventListener('click', function () {
        var g = picked('sbs-goal');
        // Only this roadmap's progress, so switching goals is not destructive.
        Object.keys(state.done).forEach(function (k) {
          if (k.indexOf(g + ':') === 0) delete state.done[k];
        });
        routeWrite(state);
        paintProgress(g);
        announce('Progress reset for this roadmap.');
        track('route_reset', { label: g });
      });
    }

    /* A shared link wins over saved state, so a link someone sent you opens
       the roadmap they meant rather than the one you last looked at. */
    var params = new URLSearchParams(window.location.search);
    [['build', 'sbs-goal'], ['stage', 'sbs-stage'], ['level', 'sbs-level']].forEach(function (pair) {
      var v = params.get(pair[0]) || state[{ build: 'goal', stage: 'stage', level: 'level' }[pair[0]]];
      if (!v) return;
      var input = root.querySelector('input[name="' + pair[1] + '"][value="' + CSS.escape(v) + '"]');
      if (input) input.checked = true;
    });
    render(false);
  }

  /* ---- interactive checklists -----------------------------------------
     Progress, persistence and printing on top of markup that already works:
     the checkboxes are real, and the reset is a native <button type="reset">
     inside a form, so both function with this script absent.

     State is keyed by the page path plus each item's own content hash, so
     inserting an item into a checklist does not shift anyone's saved progress
     onto different items. Every storage call is guarded — private windows and
     blocked site data throw on access, and a checklist that cannot remember is
     still a usable checklist. */
  function initChecklist() {
    var form = document.querySelector('[data-sbs-checklist-form]');
    if (!form) return;
    var boxes = Array.prototype.slice.call(form.querySelectorAll('[data-sbs-check]'));
    if (!boxes.length) return;

    var countEl = form.querySelector('[data-sbs-cl-count]');
    var barEl = form.querySelector('[data-sbs-cl-bar]');
    var fillEl = form.querySelector('[data-sbs-cl-fill]');
    var printBtn = form.querySelector('[data-sbs-cl-print]');
    var KEY = 'sbs-check:' + window.location.pathname;

    function read() {
      try {
        var raw = window.localStorage.getItem(KEY);
        return raw ? JSON.parse(raw) : {};
      } catch (e) { return {}; }
    }
    function write(state) {
      try { window.localStorage.setItem(KEY, JSON.stringify(state)); } catch (e) { /* ignore */ }
    }
    function clear() {
      try { window.localStorage.removeItem(KEY); } catch (e) { /* ignore */ }
    }

    function paint() {
      var done = boxes.filter(function (b) { return b.checked; }).length;
      var pct = Math.round((done / boxes.length) * 100);
      if (countEl) countEl.textContent = done + ' of ' + boxes.length + ' complete';
      if (fillEl) fillEl.style.width = pct + '%';
      if (barEl) barEl.setAttribute('aria-valuenow', String(pct));
    }

    var state = read();
    boxes.forEach(function (b) { if (state[b.id]) b.checked = true; });
    paint();

    form.addEventListener('change', function (ev) {
      if (!ev.target.hasAttribute('data-sbs-check')) return;
      var s = read();
      if (ev.target.checked) { s[ev.target.id] = 1; } else { delete s[ev.target.id]; }
      write(s);
      paint();
      track('checklist_item_toggled', { label: ev.target.checked ? 'checked' : 'unchecked' });
    });

    // reset fires before the inputs clear, so repaint on the next tick.
    form.addEventListener('reset', function () {
      clear();
      window.setTimeout(function () {
        paint();
        announce('Checklist cleared.');
        track('checklist_reset', {});
      }, 0);
    });

    if (printBtn) {
      printBtn.hidden = false;
      printBtn.addEventListener('click', function () {
        track('checklist_printed', {});
        window.print();
      });
    }
  }

  /* ---- free tools ------------------------------------------------------
     Four generators sharing one scaffold. Everything runs here in the browser:
     nothing typed into a form is transmitted to this site or to anyone else,
     and the analytics events carry the tool's name and nothing else. That is
     deliberate — a CLAUDE.md or a project description is exactly the kind of
     thing that must not end up in an analytics payload.

     Empty fields are omitted rather than filled with a guess. A generated file
     containing "npm test" for a project that has no tests is worse than one
     that stays quiet about testing. */

  function val(form, id) {
    var el = form.querySelector('#' + id);
    return el ? el.value.trim() : '';
  }
  function lines(form, id) {
    return val(form, id).split('\n').map(function (l) { return l.trim(); })
      .filter(function (l) { return l.length > 0; });
  }
  function bullets(list, prefix) {
    return list.map(function (l) { return (prefix || '- ') + l; }).join('\n');
  }

  function genClaudeMd(form) {
    var name = val(form, 'p-name') || 'This project';
    var type = val(form, 'p-type');
    var stack = val(form, 'p-stack');
    var pm = val(form, 'p-pm');
    var deploy = val(form, 'p-deploy');
    var out = ['# CLAUDE.md', ''];

    out.push('## Project');
    out.push(name + ' — ' + type.toLowerCase() + (stack ? ', built with ' + stack : '') + '.');
    out.push('');

    var cmds = [
      ['Dev', val(form, 'p-dev')],
      ['Build', val(form, 'p-build')],
      ['Test', val(form, 'p-test')],
      ['Lint / typecheck', val(form, 'p-lint')],
    ].filter(function (c) { return c[1]; });
    if (cmds.length) {
      out.push('## Commands');
      cmds.forEach(function (c) { out.push('- ' + c[0] + ': `' + c[1] + '`'); });
      if (pm && pm !== 'none') out.push('- Install with `' + pm + '`, from the lockfile. Never update it as a side effect.');
      out.push('');
    }

    var conv = lines(form, 'p-conv');
    if (conv.length) {
      out.push('## Conventions');
      out.push(bullets(conv));
      out.push('');
    }

    if (deploy && deploy !== 'Not decided yet') {
      out.push('## Deployment');
      out.push('- Production is ' + deploy + '. Nothing deploys any other way.');
      out.push('- Never deploy from a local machine. Deploys go through the pipeline.');
      out.push('');
    }

    var never = lines(form, 'p-never');
    out.push('## Prohibited');
    if (never.length) out.push(bullets(never));
    out.push('- Never commit a credential. If one is printed or committed, say so immediately — it has to be rotated.');
    out.push('- No new dependency without saying what it replaces and what it costs.');
    out.push('');

    out.push('## Definition of done');
    if (cmds.length) {
      out.push('- ' + cmds.map(function (c) { return '`' + c[1] + '`'; }).join(' and ') + ' pass.');
    }
    out.push('- The change was verified by looking at the result, not by assuming it worked.');
    out.push('- Any check added was watched failing first. A check that has never failed is not evidence.');
    out.push('');
    out.push('<!-- Generated as a starting point by sitebuilderstack.com/pages/claude-md-generator');
    out.push('     Review every line. Delete anything you cannot state honestly. Aim for');
    out.push('     roughly 150 lines — every rule competes with every other rule for');
    out.push('     attention, and rules that are mechanical belong in a hook instead. -->');
    return out.join('\n');
  }

  function genSeoPrompt(form) {
    var platform = val(form, 's-platform');
    var type = val(form, 's-type');
    var goal = val(form, 's-goal');
    var focus = val(form, 's-focus');
    var gsc = val(form, 's-gsc');
    var schema = val(form, 's-schema');
    var url = val(form, 's-url');

    var plat = {
      'Shopify': ['Shopify generates sitemap.xml and it cannot be hand-edited — the lever is publication state, not the file.',
                  'Titles and descriptions live in the global.title_tag and global.description_tag metafields.',
                  'Tag archives inherit the blog title and description by default, which duplicates it across every tag URL.',
                  'Response headers are not yours. Permissions-Policy cannot be set from a theme at all.'],
      'WordPress': ['If an SEO plugin is active it owns titles, descriptions, canonicals and the sitemap. Do not emit competing tags from the theme.',
                    'Check whether output is coming from a template, a hook, or a page builder storing layout in post meta.',
                    'Do not write to the database. Propose the change and stop.'],
      'Astro': ['Confirm `site` is set in astro.config — without it canonicals silently become relative and the sitemap integration produces nothing useful.',
                'Check every structural claim against the built output in dist/, not against source.',
                'Confirm an unknown path returns a real 404 rather than the index page with a 200.'],
      'Static site': ['Check every structural claim against the built output, not the source.',
                      'Confirm an unknown path returns 404 and not a 200 fallback to the index page.'],
      'Custom application': ['Establish which routes are server-rendered and which are client-rendered before auditing anything.',
                             'Confirm what a crawler receives, not what the browser assembles after hydration.']
    }[platform] || [];

    var out = [];
    out.push('You are a technical SEO specialist auditing a ' + type.toLowerCase() +
             ' on ' + platform + '.' + (url ? ' The site is ' + url + '.' : ''));
    out.push('');
    out.push('## Objective');
    out.push({
      'Pages are not being indexed': 'Establish why pages are not being indexed, and separate what is technically preventing indexing from what is simply not yet worth indexing to a search engine.',
      'Rankings have stalled': 'Establish whether the constraint is on-page, technical, or authority — and say plainly which, rather than producing a list of everything.',
      'Getting ready to launch': 'Establish whether this site is technically ready to be crawled and indexed on launch day.',
      'Recovering from a migration': 'Establish what the migration broke: redirects, canonicals, indexable URL set, or structured data.',
      'Improving click-through rate': 'Find pages that already rank but are not clicked, and establish whether the cause is the title, the description, or a mismatch with the query.'
    }[goal] || 'Audit this site for technical SEO defects.');
    out.push('');
    out.push('## Rules');
    out.push('- Report findings with evidence. Show the URL, the response, and the exact markup — not a summary.');
    out.push('- If you cannot verify something, say so. Do not infer it from the source and present it as observed.');
    out.push('- Do not fix anything in this run. An audit whose findings disappear into a commit is not an audit.');
    out.push('- Prove any check you write can fail before you trust it passing.');
    out.push('');
    out.push('## Work through these in order. Later checks are meaningless if an earlier one fails.');
    out.push('');
    out.push('1. **Crawlability** — robots.txt, response codes, redirect chains, and whether content is in the initial HTML or arrives via JavaScript.');
    out.push('2. **Canonicalisation** — self-referencing canonicals, absolute URLs, parameter handling, trailing slashes, apex versus www.');
    out.push('3. **Indexability decisions** — which listing, tag, filter and paginated URLs should be indexed. State the decision for each family, not just the current state.');
    out.push('4. **Metadata** — one h1 per page, unique titles and descriptions, and their rendered lengths.');
    out.push('5. **Heading structure** — order that does not skip levels, headings that describe the section rather than decorate it.');
    out.push('6. **Images** — alt text presence and usefulness, explicit dimensions, format and size.');
    if (schema !== 'None') {
      out.push('7. **Structured data** — parse every JSON-LD block. Report anything describing content not visible on the page, and any fabricated field. `aggregateRating` without real reviews is a guidelines violation, not an optimisation.');
    } else {
      out.push('7. **Structured data** — none is present. Recommend only types that describe what is genuinely on each page, and nothing that would need invented values.');
    }
    out.push('8. **Internal links** — orphan pages, crawl distance from the homepage, anchor text that describes the destination.');
    out.push('9. **Sitemap** — every URL returns 200, is canonical, and is indexable. Flag any that are not.');
    out.push('10. **Core Web Vitals** — LCP, INP and CLS at the 75th percentile, segmented across mobile and desktop. Lab tools cannot measure INP; say so rather than reporting a lab number as if it were field data.');
    out.push('11. **Accessibility overlap** — the parts that are also SEO: heading order, alt text, link text, language attribute.');
    if (focus !== 'Technical only') {
      out.push('12. **Content** — pages competing for the same intent, thin pages, pages whose title promises something the body does not deliver.');
    }
    out.push('');
    if (plat.length) {
      out.push('## ' + platform + ' specifics');
      out.push(bullets(plat));
      out.push('');
    }
    out.push('## Search Console');
    out.push({
      'Verified and I can export data': '- I can supply Search Console exports. Ask me for the query and page reports before drawing conclusions about rankings.\n- Note that the Search Analytics API returns top rows rather than all rows, so totals will not reconcile with the interface. Treat query data as a ranked sample.',
      'Verified but no API access': '- Search Console is verified but you have no API access. Ask me for a CSV export rather than guessing at ranking data.',
      'Not set up': '- Search Console is not set up. Do not claim anything about rankings, impressions or click-through rate. Recommend verifying the property as a finding in its own right.'
    }[gsc]);
    out.push('');
    out.push('## Deliverable');
    out.push('A findings report. For each finding: severity, the URL or file, the evidence, the fix, and how to prove the fix worked. Order by severity, and put anything you could not verify in a separate "unmeasured" section rather than omitting it.');
    return out.join('\n');
  }

  function genPromptBuilder(form) {
    var what = val(form, 'b-what') || 'a website';
    var platform = val(form, 'b-platform');
    var type = val(form, 'b-type');
    var deploy = val(form, 'b-deploy');
    var a11y = val(form, 'b-a11y');
    var features = lines(form, 'b-features');
    var seo = lines(form, 'b-seo');
    var cons = lines(form, 'b-constraints');
    var task = val(form, 'b-task') || 'Build it';
    var stage = val(form, 'b-stage') || 'Planning';

    /* Task decides the shape of the prompt, not a line inside it. An audit that
       is permitted to edit files produces a diff and no report, and you cannot
       afterwards tell which finding was real — so the read-only tasks say so in
       the role, before anything else. */
    var READ_ONLY = { 'Audit it': 1, 'Review security': 1, 'Improve accessibility': 1,
                      'Improve performance': 1, 'Improve conversion': 1, 'Improve SEO': 1 };
    var readOnly = !!READ_ONLY[task];

    var ROLE = {
      'Build it': 'a senior web engineer',
      'Fix a specific problem': 'a senior engineer debugging an existing system',
      'Audit it': 'an auditor',
      'Improve SEO': 'a technical SEO auditor',
      'Review security': 'a security reviewer',
      'Improve accessibility': 'an accessibility auditor',
      'Improve performance': 'a performance engineer',
      'Improve conversion': 'a conversion analyst',
      'Deploy it': 'a release engineer',
      'Refactor it': 'a senior engineer refactoring working code'
    };

    /* Stage changes what carries risk. In production the cost of a mistake is
       paid by real users, so the prompt has to say that before it says
       anything else. */
    var STAGE_RULE = {
      'Planning': 'Nothing is built yet. Do not write implementation code in this session; the output is decisions and their costs.',
      'Initial build': 'The codebase is new. Prefer establishing conventions and checks over volume of features.',
      'Testing': 'The build exists and is being verified. Changes must come with the check that would have caught the problem.',
      'Pre-production': 'This ships soon. Prefer the smallest change that is defensible, and say what you are choosing not to do.',
      'In production': 'This is LIVE and real users depend on it. Every change must state its blast radius and how to reverse it. Nothing goes out without a way back.',
      'Optimising': 'This works and is being improved. A change that cannot be measured is not an improvement — say how each one will be judged.'
    };

    var out = [];
    out.push('# ' + task + ': ' + type + (platform ? ' on ' + platform : ''));
    out.push('');
    out.push('## Role');
    out.push('You are ' + (ROLE[task] || 'a senior web engineer') +
             '. You are working on this with me, not for me: you propose, I approve, and you show evidence rather than conclusions.');
    if (readOnly) {
      out.push('');
      out.push('**This task changes nothing.** Do not edit, create or delete any file in this session. Produce findings. If you believe something must be fixed immediately, say so and stop — an audit whose fixes land in the same run leaves a diff and no report, and afterwards nobody can tell which finding was real.');
    }
    out.push('');
    out.push('## Objective');
    out.push(what);
    out.push('');
    out.push('## Project stage');
    out.push(stage + '. ' + (STAGE_RULE[stage] || ''));
    out.push('');
    out.push('## Discovery — do this first, and change nothing');
    out.push('1. Read the repository and report its structure, stack and versions, taking versions from the manifest and lockfile rather than inferring them from directory names.');
    out.push('2. List every command that already exists for dev, build, test and lint. Run each and show the output.');
    out.push('3. State what you cannot determine from the repository, and ask me rather than assuming.');
    out.push('4. Stop and wait for my approval before writing any code.');
    out.push('');
    out.push('## Requirements');
    if (features.length) {
      out.push(bullets(features));
    } else {
      out.push('- To be specified. Ask me for the functional requirements before building.');
    }
    out.push('');
    out.push('## Technical constraints');
    if (platform) out.push('- Built with ' + platform + '.');
    if (deploy && deploy !== 'Not decided') out.push('- Deploys to ' + deploy + ', through a pipeline. Never from a local machine.');
    if (cons.length) out.push(bullets(cons));
    out.push('- No new dependency without saying what it replaces and what it costs in shipped bytes.');
    out.push('- No credentials in the repository, in logs, in generated documents, or in the built output.');
    out.push('');
    out.push('## SEO requirements');
    if (seo.length) out.push(bullets(seo));
    out.push('- Every page: one h1, a unique title, a unique meta description, an absolute self-referencing canonical.');
    out.push('- A decision, stated per URL family, about what should be indexed. Not a default.');
    out.push('- Structured data only where it describes content visibly on the page. Never a field with an invented value.');
    out.push('');
    out.push('## Accessibility requirements');
    if (a11y !== 'No stated target') out.push('- Target: ' + a11y + '.');
    out.push('- Every interactive control reachable and operable by keyboard, with a visible focus state.');
    out.push('- Native elements before ARIA. If you add an ARIA attribute, say why the native element was not enough.');
    out.push('- Report machine-answerable findings separately from the ones that need a person to judge.');
    out.push('');
    if (readOnly) {
      out.push('## Reporting');
      out.push('- Every finding: what you looked at, the evidence you found, why it matters, and how confident you are.');
      out.push('- Separate what you proved from what you suspect. Label anything you could not verify as exactly that.');
      out.push('- Rank by impact and confidence over effort, and say what you would do first.');
      out.push('- Do not pad the list. A short report of real findings is worth more than a long one padded to look thorough.');
    } else {
      out.push('## Implementation');
      out.push('- One concern per change. If the work grows beyond what was asked, stop and tell me.');
      out.push('- Show me the diff before moving to the next piece.');
      out.push('- Never commit directly to the default branch.');
      if (stage === 'In production') {
        out.push('- State the blast radius and the rollback for every change before making it.');
      }
    }
    out.push('');
    out.push('## Validation');
    out.push('- Every check you write must be shown failing before I will trust it passing. Break the thing, watch it go red, restore it, watch it go quiet.');
    out.push('- Structural checks run against the built output, not the source.');
    out.push('- Verify against the deployed URL after deploying, not only locally. Canonicals, redirects and robots directives are exactly where the two differ.');
    out.push('');
    out.push('## Deliverables');
    if (readOnly) {
      out.push('1. The findings, each with its evidence and a confidence you are willing to defend.');
      out.push('2. The order you would work through them, and why that order.');
      out.push('3. A list of what you could not check, and what access would be needed to check it.');
      out.push('4. No code changes. None.');
    } else {
      out.push('1. The working site.');
      out.push('2. A CLAUDE.md recording the commands, the conventions and the prohibitions.');
      out.push('3. The checks, in the pipeline, each one having been seen to fail.');
      out.push('4. A short note of anything you could not verify.');
    }
    return out.join('\n');
  }

  /* Order must match `cats` in sections/sbs-tool.liquid. The form supplies a
     category index per answer, so a mismatch here silently files every answer
     under the wrong heading rather than erroring. */
  var READINESS_CATS = ['SEO', 'Performance', 'Accessibility', 'Security',
                        'Analytics and legal', 'Conversion',
                        'Deployment and operations'];

  /* Which product the answers point at, if any.

     Derived only from the category percentages — nothing here is a default or
     a house preference. "Weak" is under 60, which is the point at which more
     than a third of a category was answered below "Yes".

     Order matters: the broadest problem is checked first, so someone weak in
     three areas is not sent a single-product recommendation for the first one
     that happened to match. Returning null is a real outcome and shows
     nothing rather than inventing a reason to sell. */
  var READINESS_WEAK = 60;

  function readinessRecommendation(cats) {
    function pct(name) {
      var c = cats.filter(function (x) { return x.name === name; })[0];
      return (c && c.max) ? Math.round((c.got / c.max) * 100) : 100;
    }
    var weak = cats.filter(function (c) {
      return c.max && Math.round((c.got / c.max) * 100) < READINESS_WEAK;
    }).length;

    if (weak >= 3) return 'stack';
    if (pct('Conversion') < READINESS_WEAK) return 'cro';
    if (pct('SEO') < READINESS_WEAK) return 'seo';
    if (pct('Security') < READINESS_WEAK ||
        pct('Deployment and operations') < READINESS_WEAK ||
        pct('Performance') < READINESS_WEAK ||
        pct('Accessibility') < READINESS_WEAK) return 'launch';
    return null;
  }

  function genReadiness(form) {
    var cats = READINESS_CATS.map(function (name) {
      return { name: name, got: 0, max: 0, gaps: [] };
    });
    var groups = form.querySelectorAll('.sbs-tool__q');
    Array.prototype.forEach.call(groups, function (g) {
      var chosen = g.querySelector('input:checked');
      if (!chosen) return;
      var ci = parseInt(chosen.getAttribute('data-cat'), 10);
      var score = parseInt(chosen.value, 10);
      var label = g.querySelector('.sbs-tool__qtext').textContent.trim();
      var answer = g.querySelector('label[for="' + chosen.id + '"]').textContent.trim();
      cats[ci].max += 2;
      cats[ci].got += score;
      if (score < 2) cats[ci].gaps.push({ text: label, answer: answer, score: score });
    });

    var got = cats.reduce(function (a, c) { return a + c.got; }, 0);
    var max = cats.reduce(function (a, c) { return a + c.max; }, 0);
    var overall = max ? Math.round((got / max) * 100) : 0;

    // Recommendations: outright No first, then Partly, keeping category order
    // so the list reads as a plan rather than a ranking of anxieties.
    var recs = [];
    [0, 1].forEach(function (s) {
      cats.forEach(function (c) {
        c.gaps.filter(function (g) { return g.score === s; })
          .forEach(function (g) { recs.push('[' + c.name + '] ' + g.text + '  (' + g.answer + ')'); });
      });
    });

    var out = ['Website launch readiness: ' + overall + '/100', ''];
    cats.forEach(function (c) {
      var pct = c.max ? Math.round((c.got / c.max) * 100) : 0;
      out.push(c.name + ': ' + pct);
    });
    out.push('');
    if (recs.length) {
      out.push('Work on these, in this order:');
      out.push('');
      recs.forEach(function (r, i) { out.push((i + 1) + '. ' + r); });
    } else {
      out.push('Nothing was answered below "Yes". Verify a sample of them against the live site rather than against memory — a checklist you agreed with is not a check.');
    }
    out.push('');
    out.push('This is a self-assessment, not a technical audit. It reports what you');
    out.push('told it. Every "Yes" above is worth confirming against the real site.');
    out.push('Generated at sitebuilderstack.com/pages/launch-readiness-score');
    return { text: out.join('\n'), overall: overall, cats: cats };
  }

  function initTools() {
    var root = document.querySelector('[data-sbs-tool]');
    if (!root) return;
    var tool = root.getAttribute('data-sbs-tool');
    var form = root.querySelector('[data-sbs-tool-form]');
    var result = root.querySelector('[data-sbs-tool-result]');
    var output = root.querySelector('[data-sbs-tool-output]');
    var scoreEl = root.querySelector('[data-sbs-tool-score]');
    var copyBtn = root.querySelector('[data-sbs-tool-copy]');
    if (!form || !result || !output) return;

    root.hidden = false;
    var started = false;
    var text = '';

    form.addEventListener('input', function () {
      if (started) return;
      started = true;
      track('tool_started', { label: tool });
    }, { once: false });

    form.addEventListener('submit', function (ev) {
      ev.preventDefault();
      if (tool === 'readiness') {
        var r = genReadiness(form);
        text = r.text;
        scoreEl.hidden = false;
        scoreEl.innerHTML = '';
        var big = document.createElement('p');
        big.className = 'sbs-score';
        big.innerHTML = '<strong>' + r.overall + '</strong><span>/100</span>';
        scoreEl.appendChild(big);
        var list = document.createElement('ul');
        list.className = 'sbs-score__cats';
        r.cats.forEach(function (c) {
          var pct = c.max ? Math.round((c.got / c.max) * 100) : 0;
          var li = document.createElement('li');
          li.innerHTML = '<span>' + c.name + '</span>' +
            '<span class="sbs-cl__bar"><span class="sbs-cl__fill" style="width:' + pct + '%"></span></span>' +
            '<b>' + pct + '</b>';
          list.appendChild(li);
        });
        scoreEl.appendChild(list);

        /* Reveal at most one recommendation card. Every card is already in the
           document with a live price; this only unhides one. */
        var recEl = root.querySelector('[data-sbs-tool-rec]');
        if (recEl) {
          Array.prototype.forEach.call(recEl.querySelectorAll('[data-rec]'),
            function (el) { el.hidden = true; });
          var pick = readinessRecommendation(r.cats);
          var card = pick && recEl.querySelector('[data-rec="' + pick + '"]');
          if (card) { card.hidden = false; recEl.hidden = false; }
          else { recEl.hidden = true; }
        }
      } else {
        text = tool === 'claudemd' ? genClaudeMd(form)
             : tool === 'seo-prompt' ? genSeoPrompt(form)
             : genPromptBuilder(form);
      }
      output.textContent = text;
      result.hidden = false;
      announce('Result ready.');
      // The tool's name only. Never the generated text or anything typed.
      track('tool_completed', { label: tool });
      result.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });

    form.addEventListener('reset', function () {
      window.setTimeout(function () {
        result.hidden = true;
        output.textContent = '';
        if (scoreEl) { scoreEl.hidden = true; scoreEl.innerHTML = ''; }
        var rec = root.querySelector('[data-sbs-tool-rec]');
        if (rec) { rec.hidden = true; }
        text = '';
        announce('Form cleared.');
        track('tool_reset', { label: tool });
      }, 0);
    });

    if (copyBtn) {
      copyBtn.addEventListener('click', function () {
        if (!text || !navigator.clipboard) return;
        navigator.clipboard.writeText(text).then(function () {
          copyBtn.textContent = 'Copied';
          announce('Copied to the clipboard.');
          track('tool_result_copied', { label: tool });
          window.setTimeout(function () { copyBtn.textContent = 'Copy'; }, 1800);
        }).catch(function () {
          copyBtn.textContent = 'Press Ctrl+C';
          announce('Copying failed. Select the text and press Control C.');
          window.setTimeout(function () { copyBtn.textContent = 'Copy'; }, 2600);
        });
      });
    }
  }

  /* ---- header navigation ------------------------------------------------
     Two behaviours over one set of markup, chosen by viewport:

       desktop (>= 56em) — the nav is an inline row and "Products" is a
         disclosure opened by its button.
       mobile  (<  56em) — the nav is a panel opened by the burger, and the
         products list is always expanded inside it, labelled by a heading
         rather than by a button that would do nothing there.

     Both start from the same server-rendered markup: burger hidden, nav
     visible, product list visible. Every hiding step happens here, so a
     failure to run leaves a plain stacked list of every link rather than
     content locked behind a control. */
  var DESKTOP = '(min-width: 56em)';

  function initHeaderNav() {
    var header = document.querySelector('.sbs-header');
    var nav = document.getElementById('sbs-primary-nav');
    var burger = document.getElementById('sbs-burger');
    if (!header || !nav) return;

    var mq = window.matchMedia(DESKTOP);
    var groups = Array.prototype.slice.call(nav.querySelectorAll('[data-sbs-menu]'));

    header.classList.add('is-enhanced');

    /* ---- the Products disclosure, desktop only ---- */
    function setGroup(group, enhanced) {
      var btn = group.querySelector('.sbs-nav__toggle');
      var panel = group.querySelector('.sbs-nav__sub');
      if (!btn || !panel) return;
      group.classList.toggle('is-enhanced', enhanced);
      btn.hidden = !enhanced;
      // On mobile the list is part of the panel and always shown.
      panel.hidden = enhanced;
      if (!enhanced) btn.setAttribute('aria-expanded', 'false');
    }
    function groupOpen(group) {
      var btn = group.querySelector('.sbs-nav__toggle');
      return btn && btn.getAttribute('aria-expanded') === 'true';
    }
    function closeGroup(group, focusBtn) {
      var btn = group.querySelector('.sbs-nav__toggle');
      var panel = group.querySelector('.sbs-nav__sub');
      if (!btn || !panel) return;
      btn.setAttribute('aria-expanded', 'false');
      panel.hidden = true;
      if (focusBtn) btn.focus();
    }

    groups.forEach(function (group) {
      var btn = group.querySelector('.sbs-nav__toggle');
      var panel = group.querySelector('.sbs-nav__sub');
      if (!btn || !panel) return;

      btn.addEventListener('click', function () {
        if (groupOpen(group)) { closeGroup(group, false); return; }
        btn.setAttribute('aria-expanded', 'true');
        panel.hidden = false;
      });
      group.addEventListener('keydown', function (ev) {
        if (ev.key === 'Escape' && groupOpen(group)) {
          ev.stopPropagation();
          closeGroup(group, true);
        }
      });
      group.addEventListener('focusout', function () {
        window.setTimeout(function () {
          if (groupOpen(group) && !group.contains(document.activeElement)) closeGroup(group, false);
        }, 0);
      });
      document.addEventListener('click', function (ev) {
        if (groupOpen(group) && !group.contains(ev.target)) closeGroup(group, false);
      });
    });

    /* ---- the mobile panel ---- */
    function panelOpen() {
      return burger && burger.getAttribute('aria-expanded') === 'true';
    }
    function openPanel() {
      if (!burger) return;
      burger.setAttribute('aria-expanded', 'true');
      nav.hidden = false;
      document.documentElement.classList.add('sbs-menu-open');
      // Focus the first link rather than leaving focus on a button that sits
      // after the panel in the DOM — Tab would otherwise move backwards.
      var first = nav.querySelector('a');
      if (first) first.focus();
      track('nav_menu_opened', {});
    }
    function closePanel(focusBurger) {
      if (!burger) return;
      burger.setAttribute('aria-expanded', 'false');
      nav.hidden = true;
      document.documentElement.classList.remove('sbs-menu-open');
      if (focusBurger) burger.focus();
    }

    if (burger) {
      burger.hidden = false;
      burger.addEventListener('click', function () {
        panelOpen() ? closePanel(false) : openPanel();
      });
      header.addEventListener('keydown', function (ev) {
        if (ev.key === 'Escape' && panelOpen()) closePanel(true);
      });
      header.addEventListener('focusout', function () {
        window.setTimeout(function () {
          if (panelOpen() && !header.contains(document.activeElement)) closePanel(false);
        }, 0);
      });
      document.addEventListener('click', function (ev) {
        if (panelOpen() && !header.contains(ev.target)) closePanel(false);
      });
      // Following a link should not leave the panel open behind the new page
      // in browsers that restore from the back-forward cache.
      nav.addEventListener('click', function (ev) {
        if (panelOpen() && ev.target.closest('a')) closePanel(false);
      });
    }

    /* ---- react to the breakpoint ---- */
    function apply() {
      var desktop = mq.matches;
      groups.forEach(function (g) { setGroup(g, desktop); });
      if (!burger) return;
      burger.hidden = desktop;
      if (desktop) {
        // The nav is the inline row again; it must never stay hidden.
        nav.hidden = false;
        burger.setAttribute('aria-expanded', 'false');
        document.documentElement.classList.remove('sbs-menu-open');
      } else if (!panelOpen()) {
        nav.hidden = true;
      }
    }
    apply();
    if (mq.addEventListener) {
      mq.addEventListener('change', apply);
    } else if (mq.addListener) {
      mq.addListener(apply);
    }
  }

  function init() {
    initCopy();
    initTracking();
    initLibrary();
    initRoute();
    initPicker();
    initReadingProgress();
    initPathProgress();
    initLessonControls();
    initLearningHub();
    initChecklist();
    initTools();
    initHeaderNav();
    initFaq();
    initSticky();
    initForms();
    initAnchors();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
