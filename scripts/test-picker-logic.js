/* Unit test for the product picker's scoring.
 *
 * Extracted from sbs.js and run without a browser, because the important
 * assertions are about the recommendation table rather than the DOM, and a
 * table is cheap to test exhaustively.
 *
 * The assertion that matters commercially is the last group: a visitor whose
 * problem is conversion must never be sent the Website Launch System, and the
 * bundle must never win a tie. A quiz sold by the shop that breaks ties towards
 * the most expensive answer is not a recommendation.
 */
const fs = require('fs');
const src = fs.readFileSync(__dirname + '/../theme/dev/assets/sbs.js', 'utf8');

/* Pull the two pure functions and their key list out of the real file, so this
   tests the shipped code rather than a copy of it. */
function extract(name) {
  const i = src.indexOf('function ' + name + '(');
  if (i < 0) throw new Error('not found in sbs.js: ' + name);
  let depth = 0, started = false;
  for (let j = i; j < src.length; j++) {
    if (src[j] === '{') { depth++; started = true; }
    else if (src[j] === '}') { depth--; if (started && depth === 0) return src.slice(i, j + 1); }
  }
  throw new Error('unterminated: ' + name);
}
const keys = src.match(/var PICK_KEYS = (\[[^\]]*\]);/)[1];
const sandbox = new Function(
  'var PICK_KEYS = ' + keys + ';\n' +
  extract('pickScore') + '\n' + extract('pickWinner') + '\n' +
  'return { pickWinner: pickWinner, PICK_KEYS: PICK_KEYS };')();
const { pickWinner, PICK_KEYS } = sandbox;

let failures = 0;
const check = (n, ok, d) => { if (!ok) failures++; console.log(`  ${ok ? 'PASS' : 'FAIL'}  ${n}${d ? '  -> ' + d : ''}`); };
const t = (o) => Object.assign({ build: 0, rank: 0, convert: 0, operate: 0, all: 0 }, o);

check('the key list is the five products, bundle last', PICK_KEYS.join(',') === 'build,rank,convert,operate,all', PICK_KEYS.join(','));

// ---- the four clean paths -------------------------------------------------
check('all-build answers return the Launch System',
      pickWinner(t({ build: 11, rank: 0, convert: 0, all: 0 })).key === 'build');
check('all-rank answers return the SEO toolkit',
      pickWinner(t({ rank: 9, build: 0, convert: 1, all: 0 })).key === 'rank');
check('all-convert answers return the Conversion toolkit',
      pickWinner(t({ convert: 8, build: 0, rank: 1, all: 0 })).key === 'convert');
check('all-operate answers return the Operations system',
      pickWinner(t({ operate: 10, rank: 1, convert: 1, all: 0 })).key === 'operate');
check('lifecycle answers return the bundle',
      pickWinner(t({ all: 13, build: 0, rank: 0, convert: 1 })).key === 'all');

// ---- the commercial guardrails -------------------------------------------
/* The exact case the brief calls out. Q1 "it's live" gives rank+1 convert+1;
   Q2 "traffic isn't converting" gives convert+4; Q5 "converting" convert+3.
   Even with a developer role adding build+1, convert must win by a distance. */
const converting = t({ build: 1, rank: 1, convert: 8, all: 0 });
check('"traffic is not converting" never returns the Launch System',
      pickWinner(converting).key !== 'build', pickWinner(converting).key);
check('"traffic is not converting" returns the Conversion toolkit',
      pickWinner(converting).key === 'convert');

check('the bundle loses a tie with a single product',
      pickWinner(t({ build: 6, all: 6 })).key === 'build',
      pickWinner(t({ build: 6, all: 6 })).key);
check('the bundle loses a tie with every single product',
      ['build', 'rank', 'convert', 'operate'].every(k => pickWinner(t({ [k]: 7, all: 7 })).key === k));
/* The fourth product must not overwhelm the flagship or the conversion toolkit:
   "it's live" alone gives rank, convert and operate one point each, so a live
   site with a converting problem still goes to the Conversion toolkit. */
check('"live" plus a converting problem still returns the Conversion toolkit',
      pickWinner(t({ rank: 1, convert: 8, operate: 1 })).key === 'convert');
check('"live" plus a maintenance problem returns the Operations system, not the bundle',
      pickWinner(t({ rank: 1, convert: 1, operate: 8, all: 2 })).key === 'operate');
check('the bundle wins only outright',
      pickWinner(t({ build: 6, all: 7 })).key === 'all');

// ---- runner-up ------------------------------------------------------------
check('a close runner-up is offered',
      pickWinner(t({ convert: 8, rank: 7 })).alt === 'rank');
check('a distant runner-up is not offered',
      pickWinner(t({ convert: 11, rank: 2 })).alt === null,
      String(pickWinner(t({ convert: 11, rank: 2 })).alt));
check('a zero-scoring runner-up is not offered',
      pickWinner(t({ build: 2, rank: 0, convert: 0, all: 0 })).alt === null);
check('the runner-up is never the winner',
      pickWinner(t({ convert: 8, rank: 7 })).alt !== pickWinner(t({ convert: 8, rank: 7 })).key);

// ---- degenerate input -----------------------------------------------------
check('all-zero answers still return something deterministic',
      pickWinner(t({})).key === 'build', pickWinner(t({})).key);

console.log(`\n${failures} failure(s)`);
process.exit(failures ? 1 : 0);
