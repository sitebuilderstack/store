# Theme Workflow

How to change the storefront safely.

---

## The rule

**Never edit the published theme.** All work happens on
**Site Builder Stack — Development** (`191811453220`).

The live theme is now **Site Builder Stack — Live** (`191797854500`) — our own
work, published on 26 August 2026. The original purchased theme,
`one-speaker` (`191794807076`), is retained unpublished as the rollback target.

`scripts/theme_push.py` enforces this — it refuses to push to a theme whose role
is `MAIN` unless `SBS_ALLOW_LIVE=1` is set. Do not set it.

## Local source of truth

```text
theme/dev/        the files we author — this is the source of truth
theme/dev-full/   a full pulled snapshot, for running theme check
theme/one-live/   a reference copy of the original ONE theme
```

Edit `theme/dev/`. Never edit `theme/dev-full/` — it is a working copy.

## Making a change

```bash
# 1. edit files under theme/dev/

# 2. render and audit locally (see below)
python3 scripts/render-preview.py theme/dev theme/dev/templates/index.json /tmp/pv.html
node scripts/audit-rendered-a11y.js /tmp/pv.html 390

# 3. push
python3 scripts/theme_push.py 191811453220 theme/dev <relative/path> [...]
```

### Push order matters

Shopify validates references at upload time. Push in this order or the section
groups will fail with *"Section type 'x' does not refer to an existing section
file"*:

1. `assets/`, `layout/`, `snippets/`, `sections/*.liquid`
2. `sections/*-group.json`
3. `templates/*.json`
4. `config/settings_data.json`

Pushing everything at once sorts alphabetically and puts the group JSON before
the Liquid it references.

### Setting types

`config/settings_data.json` is validated by Shopify against
`settings_schema.json`. Clearing a setting requires the right empty value for
its declared type — `[]` for `product_list`, `""` for text and image pickers.
Shopify rejects the push with a clear message if you get it wrong.

## Local preview

The storefront is password-protected, and the Shopify CLI cannot render a
password-protected storefront with an Admin API token — it says so explicitly.
So there is a local renderer:

```bash
python3 scripts/render-preview.py theme/dev theme/dev/templates/index.json /tmp/pv.html
```

**It is not a Liquid engine.** It handles only the constructs used in our own
`sbs-*` sections: settings, block loops, nested conditionals, `{% assign %}`,
filters, and whitespace-control markers. It exists so CSS and layout can be
checked in a real browser.

**What it proves:** layout, contrast, overflow, tap targets, heading structure,
JavaScript behaviour.
**What it does not prove:** that the Liquid renders identically on Shopify.
`shopify theme check` covers that.

## Audits

```bash
# Liquid correctness (whole theme)
cd theme/dev-full && shopify theme check

# rendered accessibility, contrast, overflow, console
node scripts/audit-rendered-a11y.js /tmp/pv.html 320

# every link and anchor resolves to a real resource
python3 scripts/audit-theme-links.py
```

Run all three before pushing anything structural.

### Theme check baseline

The ONE theme carries **3,327 pre-existing offences** — 2,517 of them locale
translation mismatches, the rest deprecated filters and tags in `nov-*` files.
**Our 27 authored files have zero.** That was verified with a control: a
deliberate error was injected into `sbs-hero.liquid`, theme check reported it,
and the file was restored.

When reading theme-check output, filter to `sbs`/`landing` paths — otherwise the
inherited noise buries anything real.

## CSS specificity — read this before touching `sbs.css`

Two shipped bugs came from one mistake, and the same mistake is easy to repeat.

`.sbs a { color: … }` has specificity (0,1,1). `.sbs-btn--primary { color: … }`
has (0,1,0). **The element selector wins**, so the primary button rendered
accent-on-accent — invisible — and the logo and skip link were wrong too.

The fix, now in place, is to give base element rules **zero** specificity:

```css
:where(.sbs) :where(a) { color: var(--accent); }
:where(.sbs) :where(button, input, select, textarea) { color: inherit; }
```

Any class-based component rule now wins regardless of source order.

**If you add a base element rule, wrap it in `:where()`.** Then re-run the
rendered audit, which computes real contrast against the real backdrop and would
have caught this immediately.

## Rollback

**Our theme is now live.** To roll back, republish `one-speaker`
(`191794807076`) from Online Store → Themes — it is retained unpublished for
exactly this. Under a minute.

Rolling back returns the storefront to the purchased ONE theme with its speaker
demo content, which is worse than the current state but functional. Prefer
fixing forward unless the site is actually broken.

Keep a pulled snapshot of the last-known-good dev theme before any large change:

```bash
python3 scripts/theme_pull.py 191797854500 theme/backup-$(date -u +%Y%m%d)   # pull from LIVE
```
