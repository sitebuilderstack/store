# BUILD sequence

For subscribers tagged `goal-build`: they need to build or launch a website.

---

## Email 1 — day 0

**Subject:** Your CLAUDE.md Starter Kit
**Preheader:** Four templates, and the one rule that decides whether they work.

Here it is: **[Download the CLAUDE.md Starter Kit](https://sitebuilderstack.com/pages/production-claude-md-starter)**

Four `CLAUDE.md` files — static site, web application, Shopify theme, monorepo package —
plus a review checklist. Free for client work.

**Do this first.** Open the one closest to your project, copy it to your repository root,
replace everything in angle brackets, then delete about a third of it.

That last step is not a joke. Length is how these files fail. Every line competes with
every other line for attention, so a 400-line `CLAUDE.md` is followed *less* reliably than
a 120-line one. If you are not sure what to cut, cut the rules you have never actually
seen broken.

**The 60-second check.** Start a session and ask it to summarise your project's rules
back to you. If it gets your build command wrong, the file is too long or the command is
buried. Fix that before you write another line of it.

---

## Email 2 — day 2

**Subject:** Why "build me a website" isn't enough
**Preheader:** The failure isn't the model. It's the missing discovery step.

The most expensive failure in agent-assisted work is not bad code. It is forty files
changed on assumptions nobody checked, in a session you cannot now unpick.

It happens because the request skipped a step. "Build me a marketing site in Astro" gives
the model no way to distinguish what you decided from what it guessed, so it guesses
everything and presents all of it with the same confidence.

The fix is one paragraph at the top of the prompt:

> Read the repository and report its structure, stack and versions — taking versions from
> the manifest and lockfile rather than inferring them from directory names. List every
> command that already exists for dev, build, test and lint, run each, and show the
> output. State what you cannot determine and ask me rather than assuming. Then stop and
> wait for my approval before writing any code.

Nothing in that is clever. It just makes the difference between knowing and guessing
visible before the guessing gets committed.

[How to build a website with Claude Code](https://sitebuilderstack.com/blogs/guides/how-to-build-a-website-with-claude-code)
is the long version.

No product in this email. There is one in a few days.

---

## Email 3 — day 4

**Subject:** The build loop that survives a real project
**Preheader:** Small increments, and a check that has been seen to fail.

The loop, in the order that matters:

1. **Decide the rendering strategy first.** Static, server-rendered, client-rendered, or a
   deliberate mix. It determines performance, SEO risk, hosting cost and complexity more
   than any framework choice, and it is the most expensive thing to change later.
2. **Establish `CLAUDE.md` before the first feature**, not after the third.
3. **Build in increments you can verify**, and verify each one against the built output
   rather than the source.
4. **Write the check, then break the thing.** A test you have only ever seen pass is not
   evidence. Break it deliberately, watch it go red, restore it, watch it go quiet.
5. **Never let discovery and implementation share a session.**

Step 4 is the one people skip, and it is the one that makes the rest worth anything.

One question worth asking before any of it: *who updates this in six months, and what tool
do they open?* If the honest answer is "a non-technical person opens a Markdown file in a
Git repository", the architecture is wrong and the site is stale within a quarter.

---

## Email 4 — day 6

**Subject:** Five things every check called healthy
**Preheader:** From building this site, including what the first pass missed.

This site was built with the system I sell. That is either the best argument for it or the
worst, depending on whether I tell you what went wrong. So:

- A **contents grid rendered seventeen empty labels** on a live product page for weeks.
  The template wrote one field name, the section read another. Every automated check
  passed, because nothing checked that a rendered element had text in it.
- **`og:title` was double-escaped.** Link previews showed a literal `&amp;`. The `<title>`
  tag was correct, which is exactly why nobody noticed.
- A **comparison table scrolled the whole page sideways at 375px.** The rule existed, but
  only under a class the product description did not use.
- The **header CTA advertised the wrong price** on two product pages.
- **Two products are still not proven deliverable**, because the delivery app stores files
  privately and the API cannot see whether a file is attached. Only a real paid order
  proves it, and that is recorded as an open item rather than closed quietly.

None of those were found by a tool that reported "no issues". They were found by checks
written to fail on purpose first.

[The full case study](https://sitebuilderstack.com/pages/case-study).

---

## Email 5 — day 8

**Subject:** What's actually in the Website Launch System
**Preheader:** 113 files. Nothing to install.

You have the free `CLAUDE.md` kit. The [Website Launch
System](https://sitebuilderstack.com/products/claude-code-website-launch-system) is the
rest of the method: a production `CLAUDE.md`, a staged master build prompt that refuses to
write code during discovery, platform build systems for Shopify, WordPress, Astro, SaaS
and landing pages, security and accessibility audits, 100 reusable prompts, and the launch
checklists.

113 files of plain Markdown. One payment, no subscription, no account, nothing to install.
Licensed to one person for unlimited projects, including client work.

**Who it is not for:** anyone wanting a website built for them, and anyone who will not run
the checks. It is a system you operate, not a service.

---

## Email 6 — day 11

**Subject:** Build is one of three problems
**Preheader:** The other two arrive later, in a predictable order.

Sites tend to fail at one of three points, in order: they never launch properly, they
launch and are never found, or they get traffic that does not turn into anything.

Building well only solves the first. The other two need different work, and most projects
meet all three eventually.

The [Complete Site Builder Stack](https://sitebuilderstack.com/products/complete-site-builder-stack)
is all three systems: the Launch System, the SEO & Website Audit Toolkit, and the
Conversion & Revenue Optimization Toolkit. $39.99 together; $59.97 bought separately. Both are
prices this store charges — the difference is not a discount off anything, because the
three have never been sold together at their separate total.

If you only have the build problem, buy the one product. There is no advantage to owning a
system you are not going to open, and I would rather say so than sell you three.
