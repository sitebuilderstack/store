# The public mirror

`github.com/sitebuilderstack/store` is a public, single-commit mirror of this
repository. It exists so the storefront source is inspectable — it is the
evidence behind the claims the site makes, and the thing an outreach email can
point at.

First published 5 September 2026. The mirror is always exactly one commit,
rebuilt on each publish, so its SHA changes every time and is not recorded
here — `scripts/publish-public-mirror.sh` prints the file count it pushed.

## What is excluded, and why

| Path | Reason |
| --- | --- |
| `product/` | The paid bundle. This is what customers buy. |
| `dist/` | Build output of `product/`, so the same content. |
| `freebie/` | The email-gated lead magnet. Publishing it removes the reason to opt in. |

`freebie/` was not named in the instruction to exclude `product` and `dist`; it
is excluded because publishing it defeats the opt-in funnel it exists to feed.
Include it by editing `EXCLUDE` in `scripts/publish-public-mirror.sh` and
re-running.

## Why there is no history

All 33 commits in this repository have `product/` in their tree. Pushing the
history would let anyone recover the bundle with `git log -p`, whatever the tip
commit contains. `git-filter-repo` is not available here, and a rewrite that
misses one path fails silently — the mirror looks clean while the product is
still reachable. So the mirror is rebuilt from the working tree as a single
commit every time, which cannot carry a path that is not in the payload.

The cost is that the mirror shows no development history. That is the intended
trade.

## Publishing an update

```
./scripts/publish-public-mirror.sh          # build and verify, no push
./scripts/publish-public-mirror.sh --push   # build, verify, force-push
```

The script refuses to push if an excluded directory survives into the payload,
or if any credential pattern appears in it. Both guards are control-tested:
they fire on a crafted failure and stay silent on a clean tree.

The push is always `--force`, because each run creates a new orphan history.

## The test suite on a clone

`tests/run-all.sh` skips the five checks that read `product/` rather than
failing them, so a clone reports **7 passed / 5 skipped** instead of five
failures. With the bundle present it still reports 12 passed. Adding a check
that reads the bundle means wrapping it in `run_if_bundle`.

## Outstanding

The repository has no description and no topics. Neither is settable over SSH,
and there is no GitHub API token here — both need a minute in the GitHub UI:

- Description: `Source for sitebuilderstack.com — a Shopify storefront built and audited with Claude Code.`
- Topics: `claude-code`, `shopify`, `liquid`, `seo`, `accessibility`, `web-performance`

### The starter kit repository

The kit is published separately at
`github.com/sitebuilderstack/sitebuilderstack_store`, 12 files at the repository
root, so an awesome-list can link a repo root rather than a subdirectory. It is
still mirrored inside this repository at `github/claude-code-website-starter-kit/`,
because that is where `scripts/build-github-kit.sh` regenerates it from
`resources/`. `scripts/publish-starter-kit.sh` pushes it, and refuses to if skill
validation fails, a credential pattern appears, or README/LICENSE are missing —
all three guards control-tested in each direction.

It also needs a description and topics set by hand:

- Description: `A CLAUDE.md starter, four production checklists and five installable Claude Code skills for building and auditing websites.`
- Topics: `claude-code`, `claude-md`, `claude-skills`, `seo`, `accessibility`, `checklist`

### Renaming it — decided, waiting on one click

`sitebuilderstack_store` reads as a store, not a kit, and the name is what a
maintainer sees in a pull request proposing it for a list. The decision is to
rename it to `claude-code-website-starter-kit`.

Renaming a repository is a REST API or web UI operation. Only an SSH key is
available here, and git cannot rename a repository, so this one step is manual:

> https://github.com/sitebuilderstack/sitebuilderstack_store/settings →
> Repository name → `claude-code-website-starter-kit` → Rename

Then `./scripts/rename-kit-repo.sh --apply` does the rest: rewrites the nine
files that quote the path, pushes the shared `agents.md` / `llms.txt` template
to both themes, republishes the skills guide and the resources hub, submits
both to IndexNow, and verifies on the live site that every surface carries the
new URL and none carries the old one.

The order is deliberate. GitHub redirects the old name to the new one, so links
written against the old name keep working after the rename — but a link written
against the new name 404s before it. The script therefore refuses to run until
`GET /repos/sitebuilderstack/claude-code-website-starter-kit` answers 200. It
also refuses to run outside this repository, because it rewrites every match
under its root.
