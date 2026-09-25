/* Render a real checkout and report whether the store can take money.
 *
 * Shopify's "This store can't accept payments right now" notice is rendered by
 * JavaScript -- it is NOT in the initial HTML, so fetching the page and
 * grepping it reports a healthy checkout on a store that cannot sell. This has
 * to run in a browser.
 *
 * Usage: node check-checkout-payments.js <checkoutUrl> [screenshot.png]
 */
// puppeteer-core is used with the Chrome for Testing binary already on this
// machine; fall back to the full puppeteer package if that is what is installed.
let puppeteer;
try { puppeteer = require('puppeteer-core'); }
catch (e) { puppeteer = require('puppeteer'); }

(async () => {
  const url = process.argv[2];
  const shot = process.argv[3];
  const b = await puppeteer.launch({
    executablePath: process.env.PUPPETEER_EXECUTABLE_PATH,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage'],
  });
  const p = await b.newPage();
  await p.setViewport({ width: 1100, height: 1400 });
  await p.goto(url, { waitUntil: 'networkidle2', timeout: 90000 });
  await new Promise(r => setTimeout(r, 4000));

  const r = await p.evaluate(() => {
    const t = document.body.innerText;
    const payBtn = [...document.querySelectorAll('button')]
      .find(b => /pay now|complete order/i.test(b.innerText));
    return {
      cannotAcceptPayments: /can.?t accept payments|cannot accept payments/i.test(t),
      asksShippingAddress:  /shipping address/i.test(t),
      hasBillingAddress:    /billing address/i.test(t),
      payButtonDisabled:    payBtn ? (payBtn.disabled || payBtn.getAttribute('aria-disabled') === 'true') : null,
      // A digital product is delivered by email. If checkout accepts a phone
      // number instead, a customer can pay and leave no address to deliver to.
      // The wording lives in the input's placeholder/label/aria-label, NOT in
      // body innerText -- reading innerText silently reports "safe" always.
      contactAcceptsPhone: (() => {
        const fields = [...document.querySelectorAll('input,label')];
        const txt = fields.map(el => [
          el.getAttribute('placeholder'), el.getAttribute('aria-label'),
          el.getAttribute('name'), el.innerText,
        ].filter(Boolean).join(' ')).join(' | ');
        return /email or mobile phone|phone number or email|email or phone/i.test(txt);
      })(),
      contactFieldLabel: (() => {
        const el = document.querySelector('input[name*="email" i], input[type="email"], #email');
        return el ? (el.getAttribute('placeholder') || el.getAttribute('aria-label') || '') : null;
      })(),
      total: (t.match(/Total[\s\S]{0,40}?([£$€]\s?[\d,]+\.\d{2})/) || [])[1] || null,
    };
  });
  if (shot) await p.screenshot({ path: shot });
  console.log(JSON.stringify(r, null, 1));
  await b.close();
  process.exit(r.cannotAcceptPayments ? 1 : 0);
})();
