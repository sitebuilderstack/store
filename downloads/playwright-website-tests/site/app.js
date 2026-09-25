// Fixture site behaviour: a booking form with client-side validation and a
// mobile navigation toggle. Deliberately small; the tests assert what a
// visitor sees, not how this file is written.
(function () {
  var form = document.getElementById('book-form');
  var msg = document.getElementById('form-msg');
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.getElementById('site-nav');

  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  if (!form) return;
  function say(text, kind) { msg.textContent = text; msg.className = kind; }

  form.addEventListener('submit', function (ev) {
    ev.preventDefault();
    var name = form.elements.name.value.trim();
    var email = form.elements.email.value.trim();
    if (!name) { say('Please enter your name.', 'error'); form.elements.name.focus(); return; }
    if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) { say('Please enter a valid email address so we can confirm your slot.', 'error'); form.elements.email.focus(); return; }
    say('Sending…', '');
    fetch(form.action, { method: 'POST', body: new FormData(form) })
      .then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
      .then(function () { say('Thanks! We will email you to confirm.', 'ok'); form.reset(); })
      .catch(function () { say('Sorry — that did not send. Please call the clinic.', 'error'); });
  });
})();
