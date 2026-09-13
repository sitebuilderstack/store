# Benchmark tasks

Written before any trial was run. Acceptance criteria are fixed: a task whose
criteria are adjusted after seeing results is disqualified, not rescored.

Each prompt is sent verbatim, with `<PLATFORM>` replaced by the platform name and
nothing else changed.

---

## T-01 — Ship a page that is actually indexable

**Prompt.** On <PLATFORM>, add a page at `/pricing` with three plan tiers, a
heading structure, and a call to action on each tier. It must be reachable from
the site's main navigation.

**Acceptance criteria**

- The URL returns 200.
- Exactly one `h1`.
- A unique `<title>` and a unique meta description.
- An absolute, self-referencing canonical.
- The content is present in the initial HTML response, not only after JavaScript.
- A link to it exists in the rendered navigation.

---

## T-02 — A form that cannot silently fail

**Prompt.** On <PLATFORM>, add a contact form with name, email and message. It
must validate on the server, not only in the browser, and must tell the user
clearly when a submission fails.

**Acceptance criteria**

- A submission with a malformed email is rejected when JavaScript is disabled.
- The rejection is visible on the page, not only in a console or a network tab.
- A successful submission produces a confirmation the user can see.
- The error message is associated with its field programmatically.

---

## T-03 — Make an existing page keyboard-operable

**Prompt.** On <PLATFORM>, the navigation has a dropdown that only opens on
hover. Make the whole navigation operable by keyboard without breaking mouse use.

**Acceptance criteria**

- Every menu item is reachable by Tab in a logical order.
- The dropdown opens and closes from the keyboard.
- Focus is visible at every step, against the real background.
- Escape closes an open dropdown and returns focus to its trigger.
- Mouse behaviour is unchanged.

---

## T-04 — Fix a layout shift

**Prompt.** On <PLATFORM>, the hero image causes visible layout shift on load.
Fix it without changing the design.

**Acceptance criteria**

- Lighthouse CLS for the page is 0.
- The rendered design is unchanged at 375px and 1280px.
- The fix does not rely on a fixed pixel height that breaks at another width.

---

## T-05 — Add structured data that is not a lie

**Prompt.** On <PLATFORM>, add structured data to the pricing page from T-01.

**Acceptance criteria**

- The JSON-LD parses.
- It validates against schema.org's expected types for what it claims to be.
- Every field it asserts corresponds to something visible on the page.
- No `Review` or `AggregateRating` is present, since there are no reviews.

The last criterion is the interesting one. It tests whether the tool invents
credible-looking fields when the page gives it nothing to put in them.

---

## T-06 — Deploy it

**Prompt.** On <PLATFORM>, get the site deployed to its usual production target,
through a pipeline rather than from this machine.

**Acceptance criteria**

- A pipeline configuration exists in the repository.
- The pipeline runs the project's own build and test commands.
- A deliberately broken commit fails the pipeline. This must be demonstrated,
  not assumed.
- The deployed URL serves the change.

The third criterion is the point of the task. A pipeline nobody has seen fail is
not a pipeline.
