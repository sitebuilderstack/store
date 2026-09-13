# CLAUDE.md

> Starter version. Replace every line in angle brackets, delete what does not apply,
> and keep this file under roughly 150 lines. A file nobody trims stops being read.

## Project

<One sentence: what this is and who uses it.>

- **Stack:** <framework, language, runtime version>
- **Package manager:** <npm | pnpm | yarn | uv | poetry> — use this one, not another
- **Hosting:** <where production runs>
- **Repository layout:** <one line per top-level directory that is not obvious>

## Commands

Always use these. Do not invent equivalents.

```
<install>     # e.g. pnpm install --frozen-lockfile
<dev>         # e.g. pnpm dev
<build>       # e.g. pnpm build
<test>        # e.g. pnpm test
<lint>        # e.g. pnpm lint
<typecheck>   # e.g. pnpm typecheck
```

## Architecture rules

- <Where new code of each kind belongs, e.g. "UI components in `src/components`, one per file.">
- <The boundary that must not be crossed, e.g. "Nothing in `src/ui` imports from `src/server`.">
- <How state/data flows, in one sentence.>
- Prefer editing an existing module over adding a new one. Ask before introducing a dependency.
- Match the surrounding file's conventions over any general style preference.

## Coding standards

- <Formatter and linter; they are the authority, not this file.>
- Naming: <the convention actually used in this repo>.
- Comments explain *why*, never *what*. No commented-out code in a commit.
- No `any`, no unchecked casts, no swallowing errors with an empty catch.
- Public functions get types on their inputs and outputs.

## Testing

- Test framework: <name>. Tests live in <path> and are named <pattern>.
- A change to behaviour needs a test that fails without it.
- Do not delete or `skip` a failing test to make the suite green. Fix it or say it is broken.
- Run `<test>` before reporting work complete. Report real results, including failures.

## Security

- **Never** read, print, log, or commit secrets. Credentials live in the environment or a
  secret manager, never in source, never in a template, never in client-side JavaScript.
- `.env` and `.env.*` are git-ignored and stay that way. Use `.env.example` for names only.
- Validate and escape every value that came from a user before it reaches HTML, SQL,
  a shell, or a file path.
- Authorisation is checked on the server for every request, not in the UI.
- Do not add a dependency to solve a problem the standard library already solves.
- Do not disable a security header, CSP rule, or certificate check to make something work.

## Accessibility

- Semantic HTML first. A `div` with a click handler is not a button.
- Every interactive control is reachable and operable by keyboard, with a visible focus style.
- Every informative image has meaningful `alt`; decorative images have `alt=""`.
- Text contrast at least 4.5:1, non-text UI at least 3:1.
- Form inputs have an associated `<label>`. Errors are announced, not only coloured.
- Headings descend without skipping levels. One `<h1>` per page.

## SEO

- One unique `<title>` and one unique meta description per route.
- One self-referencing canonical per page.
- Structured data only where it describes what is actually on the page.
- Never add review, rating, or aggregate markup without real reviews behind it.
- Internal links use descriptive anchor text, not "click here".
- Images ship at the size they render, with width and height set.

## Performance

- Set `width` and `height` on images and video to prevent layout shift.
- Lazy-load below the fold; never lazy-load the largest element above it.
- No render-blocking third-party script without a reason written down.
- Measure before optimising. Report the number, not the impression.

## Deployment

- <Branch that deploys, and where it deploys to.>
- <The exact command or pipeline that ships.>
- Never push directly to <production branch>. Open a pull request.
- Migrations run <how>; they are forward-compatible with the running version.
- A deploy is not finished until <the check that proves it worked> passes.

## Do not

- Do not commit, push, or open a pull request unless asked.
- Do not run destructive commands (`rm -rf`, `DROP`, `--force`, history rewrites) without asking.
- Do not edit generated files, lockfiles, or anything under <build output dir> by hand.
- Do not reformat files you were not asked to change; it hides the real diff.
- Do not claim something is tested, deployed, or working without having verified it.

## Before you say it is done

1. `<lint>` and `<typecheck>` pass.
2. `<test>` passes, and any new behaviour has a test.
3. `<build>` succeeds.
4. The change was exercised for real — a page loaded, an endpoint called, a command run.
5. Anything skipped or still broken is stated plainly.
