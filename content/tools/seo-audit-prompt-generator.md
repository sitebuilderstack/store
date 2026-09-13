This builds a technical SEO audit prompt scoped to your platform, your situation
and what you actually have access to — rather than a generic "audit my site"
request that produces a generic list back.

Everything runs in your browser. Nothing you enter, including a site URL, is
transmitted or fetched.

## Why a scoped prompt beats a general one

"Audit my site for SEO" is not a task with a finish line. What comes back is
plausible, comprehensive-looking, and impossible to act on, because nothing in
it is tied to evidence you can check.

The prompts this produces do three things differently:

- **They demand evidence.** Every finding has to come with the URL, the response and the exact markup, not a summary you have to trust.
- **They forbid fixing in the same run.** An audit whose findings disappear into a commit is not an audit — you get a diff and no report, and cannot tell which findings were real.
- **They work in dependency order.** Crawlability, then canonicals, then indexing decisions, then metadata, then speed. Optimising titles on URLs that are about to be canonicalised away is wasted work.

## Platform matters more than people expect

The generated prompt includes the specific behaviours of your platform, because
those are where audits go wrong. Shopify generates a sitemap you cannot edit,
so the lever is publication state. WordPress hands title and canonical ownership
to whichever SEO plugin is active, and a theme emitting competing tags produces
duplicates. Astro silently renders relative canonicals if `site` is missing from
the config.

None of those produce an error. All of them produce a confident wrong answer
from an audit that does not know to look.

## What it will not do

It will not claim anything about your rankings. If you tell it Search Console is
not set up, the generated prompt explicitly instructs the agent not to make
ranking claims — because there is no way to know, and an invented position is
worse than an absent one.

The full method behind these prompts is in the [technical SEO audit
workflow](/blogs/guides/claude-code-technical-seo-audit) and the [complete SEO
workflow](/blogs/guides/claude-code-seo-website-optimization).
