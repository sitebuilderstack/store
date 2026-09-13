---
name: a11y-audit
description: Audit a site or component library against WCAG 2.2 Level AA and report findings, separating what a tool can determine from what needs a person. Covers semantics, headings, keyboard, focus, forms, names, contrast, target size and ARIA.
when_to_use: Use when asked about accessibility, WCAG, screen readers, keyboard navigation, contrast, focus, ARIA or a11y.
disable-model-invocation: true
argument-hint: [url or path]
allowed-tools: Read Grep Glob Bash
---

# Accessibility audit — WCAG 2.2 Level AA

Audit **$1**. Do not fix anything in this run.

## What this can and cannot establish

You can read components and rendered HTML, so you can find structural problems a
scanner misses — a click handler on a `div` repeated across forty components, an ARIA
pattern applied inconsistently, a focus trap that exists in only one branch.

You cannot determine whether the experience makes sense. W3C is explicit that "tools
can't do it all. Some accessibility checks just cannot be automated and require manual
intervention."

**Never claim this audit establishes conformance.** It does not.

## Order

1. **Inventory** — every page template and interactive component. Note which involve
   focus management, keyboard interaction or dynamic updates.
2. **Semantics** — `div` with a click handler instead of `button`; anchors without
   `href`; buttons that navigate; layout tables; bold text used as a heading; missing
   `header`/`nav`/`main`/`footer` landmarks.
3. **Headings** — one `h1` per page; no skipped levels; headings chosen for structure
   rather than the size they render at.
4. **Keyboard** — everything interactive reachable in a sensible order; focus always
   visible; no traps; Escape closes what it opened. Flag any `outline: none` without a
   replacement.
5. **Focus management** — dialogs move focus in, trap it, and return it on close;
   route changes move focus; disclosure controls carry `aria-expanded`.
6. **Forms** — every input has an associated `<label for>`; a placeholder is not a
   label; errors are associated via `aria-describedby`, described in words rather than
   colour, and focus moves to the first one; `autocomplete` set where it applies.
7. **Accessible names** — no bare "click here"; icon-only buttons labelled; a control's
   name makes sense read out of context.
8. **Images** — informative images have meaningful `alt`; decorative have `alt=""`
   (empty, not missing); functional images describe the action.
9. **Contrast** — 4.5:1 text, 3:1 large text and UI components, computed against the
   actual composited backdrop rather than the declared colour. Check focus indicators
   separately; they fail often and only in one state.
10. **Target size** — SC 2.5.8 requires 24×24 CSS pixels, with five exceptions. The one
    that matters most is **Inline**: a target in a sentence is exempt. A naive check
    without that exception produces a wall of false positives.
11. **ARIA** — last, deliberately. Prefer the native element. Flag roles on elements
    that already have them, `aria-label` overriding good visible text, and anything
    focusable inside `aria-hidden`.

## Output

```
Issue:
Component:
Impact:                blocks | hinders | polish
Evidence:              file:line, or what was observed
Criterion:             the WCAG SC, or "uncertain" — do not guess
Fix:                   prefer changing the element over adding ARIA
Automated validation:  what a tool can confirm
Manual validation:     what a person still has to check
```

Then a separate list: **what needs a human.** Tab order in the rendered page, whether
alt text is meaningful, whether an announcement makes sense, and anything requiring a
screen reader.

## What not to claim

- A Lighthouse score of 100 is not WCAG conformance.
- Zero axe violations is not "accessible".
- None of this replaces testing with disabled users.

See `WEBSITE-AUDIT-CHECKLIST.md` in this repository for the wider inspection.
