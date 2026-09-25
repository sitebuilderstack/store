---
title: "Handing a WordPress site to Claude Code without it breaking anything"
subtitle: "Three sources of truth, one of which is invisible to a tool that reads files — and the rules that keep an agent out of the one that can't be rolled back"
canonical: https://sitebuilderstack.com/blogs/guides/claude-code-wordpress
tags: wordpress, claude, ai-tools, php, web-development
---

Claude Code is very good at working inside a repository. WordPress is not, primarily, a repository. It is a PHP application whose behaviour is decided by three things at once: the files on disk, the rows in a database, and whichever of the forty plugins you installed happens to hook the filter you are looking at. Two of those three are invisible to a tool that reads files. That is the whole difficulty, and everything below follows from it.

This is a condensed version of the [full WordPress guide on Site Builder Stack](https://sitebuilderstack.com/blogs/guides/claude-code-wordpress), which has the prompts, the `CLAUDE.md` and the command lists in full.

## On a static site the code tells you what happens; on WordPress it tells you what could

Reading an Astro project tells you what the site renders. Reading a WordPress theme tells you what *might* render, and the database tells you what actually does. The practical consequence: the first session on a WordPress project should change nothing. Its job is reconnaissance — establishing which of the three sources of truth is in charge of what — and the tool for that is WP-CLI, because it can see the database. Give the agent permission to run read-only WP-CLI commands and ask for a report, not a fix.

Two answers change everything that follows. **Is it a block theme or a classic theme?** A block theme keeps templates as HTML files and its styling in `theme.json`; a classic theme uses PHP templates and `functions.php`. Advice for one is often actively wrong for the other. **Is a page builder installed?** If Elementor, Divi or Beaver Builder owns the page layouts, the template files are not where the page comes from.

## A local environment worth breaking

Do not let an agent work against production. The consequences are worse on WordPress than elsewhere, because a bad migration or a plugin activation can take a site down in a way a file revert will not fix. Any local stack will do — `wp-env`, LocalWP, DDEV, Lando, Docker Compose — provided three things are true: the database can be reset in one command (so breaking it deliberately, to test a check, is cheap); it runs the same PHP major version as production; and debug output is on and logged to a file.

## Four things the agent has to be told

None of these is discoverable by reading a single file.

- **The template hierarchy.** For a single post WordPress looks for `single-post.php`, then `single.php`, then `singular.php`, then `index.php`, taking the first that exists. An agent editing `index.php` to change a post page is editing a file that is never reached. State the resolved template in the prompt.
- **Child themes.** Everything you write goes in the child theme; overriding a parent template means copying it across — and the copy is now yours to maintain against upstream. Say that trade-off out loud, because the default behaviour is to copy the whole file.
- **Plugins for behaviour, themes for presentation.** Site-specific behaviour belongs in a small single-purpose plugin — a self-contained file tree with a clear boundary, which is exactly the shape of task an agent completes well.
- **Escaping at the point of output, every time**, with the function that matches the context: `esc_html()` for text, `esc_attr()` for attributes, `esc_url()` for hrefs, `wp_kses_post()` for editor content. The linter catches formatting; it does not catch this.

## The rule that matters most: the agent stays out of the database

File changes are reversible with `git checkout`. Database changes are not. A search-and-replace across `wp_posts` that gets the pattern slightly wrong damages every post on the site, and the only recovery is a backup you hopefully took. An agent has no way to evaluate that asymmetry, and it will run the command if it can.

So: reading is fine; writing is *proposed* and never executed. The agent produces the `wp search-replace` command; you run it, after taking a backup, with `--dry-run` first — which should be a rule in your project context, not a suggestion.

## A CLAUDE.md that does most of the work in two lines

The reconnaissance turns into a `CLAUDE.md` the agent reads on every session. Keep it around 150 lines; past that, instructions compete for attention. Two lines carry most of the value:

- "**Never edit the parent theme.**" It prevents an entire class of change that works, survives testing, and silently vanishes at the next vendor update.
- "**Do not write to the database.**" It turns the most dangerous available action into a proposal you approve.

Add the mechanical, unconditional rules beside them: always escape on output; always clear the cache before verifying; if an SEO plugin is active it owns titles, descriptions, canonicals and the sitemap, and the theme must not write competing tags (duplicate canonicals are worse than none).

## Deployment, and the row people get wrong

| Layer | In git? | Moves to production how |
|---|---|---|
| Child theme, custom plugins | yes | with the repository |
| Third-party plugins | ideally via Composer | installed at build from a lockfile |
| WordPress core | no | host or Composer |
| Uploads | no | never — they are user data |
| Database | no | **never automatically, in either direction** |

Pushing a database from staging to production destroys everything that happened on production since the copy — orders, comments, form submissions, new posts.

## Verify against the live URL

Local and production differ in exactly the places that are hardest to notice: canonical URLs, redirect behaviour, robots directives, anything that depends on a response header. Verify after deploy, with the cache cleared, by fetching the live page — not by reading the template. Rollback for files is a git revert and a redeploy; rollback for the database is the export you took before you started, which is why taking it is a step rather than a suggestion.

## The mistakes that cost the most

Editing the parent theme. Trusting a change a cache is hiding (clear it first, every time). Letting the agent write to the database. Assuming the file is the template. Adding a plugin to solve a fifteen-line problem — every plugin is an update, an attack surface and a script on every page.

## The workflow, end to end

1. Reconnaissance session — no changes; theme type, active plugins, template resolution, where each behaviour lives — written into `CLAUDE.md`.
2. Local environment — matching PHP, debug logging on, one-command database reset.
3. Project context — the mechanical, unconditional rules.
4. One change at a time — a hook if a hook exists, a template override if it does not, a plugin for behaviour.
5. Lint and log — `phpcs` clean and no new notices in `debug.log`.
6. Verify on the live URL, cache cleared. Roll back with git for files and with the export for data.

The [full guide](https://sitebuilderstack.com/blogs/guides/claude-code-wordpress) has the prompts for each step and the complete `CLAUDE.md`. If the site is a client's, the [Agency & Client Delivery System](https://sitebuilderstack.com/products/claude-code-agency-client-delivery-system) runs the engagement around this work; if the site is *leaving* WordPress, the [Website Migration & Replatforming System](https://sitebuilderstack.com/products/claude-code-website-migration-replatforming-system) covers the move.

---

*Adapted from [Claude Code for WordPress](https://sitebuilderstack.com/blogs/guides/claude-code-wordpress) on Site Builder Stack. Independent; not affiliated with Anthropic or Automattic.*
