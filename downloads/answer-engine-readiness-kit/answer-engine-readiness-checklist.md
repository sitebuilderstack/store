# Answer engine readiness checklist

Run this against one page. Every line is checkable by looking or by one
command — none of it requires a tool, an account or a subscription.

From [SiteBuilderStack](https://sitebuilderstack.com). Free to use and adapt.

**What this cannot tell you:** whether you will be cited. No answer engine
publishes its extraction rules. These are the things that are observable;
everything past them is inference.

---

## 1. Can it be fetched at all?

- [ ] A plain HTTP request returns the answer in the response body.

      curl -s -A "OAI-SearchBot" https://example.com/your-page | head -c 3000

- [ ] The answer is not dependent on JavaScript executing.
- [ ] No cookie wall, consent interstitial or paywall covers it.
- [ ] The page returns 200, not a redirect chain.
- [ ] `robots.txt` permits each agent you want to be cited by — checking the
      group that actually applies, remembering that no group means the `*`
      group applies.

If any of these fails, stop. Nothing below matters until they pass.

## 2. Is there a passage worth lifting?

- [ ] A complete answer appears in the first hundred words — not a preamble
      about why the topic matters.
- [ ] Read the opening cold, with no context. You can tell what question the
      page answers.
- [ ] Each opening sentence, taken alone, still means something.
- [ ] No opening sentence starts with a dependent word: *this, that, it, they,
      however, therefore, as mentioned, as described above*.
- [ ] The strongest self-contained passage is roughly 20–90 words. Shorter
      answers nothing; longer gets truncated mid-thought.

**The test that matters:** copy your first hundred words into a blank
document and read them. That is approximately what an answer engine sees.

## 3. Is it attributable?

- [ ] The publisher is named in the text, not only as "we" or "our team".
- [ ] A visible publication or updated date appears on the page.
- [ ] The author is stated and matches any structured data.
- [ ] Claims that came from somewhere else link to that source, next to the
      claim rather than in a list at the bottom.

## 4. Is it specific enough to be worth quoting?

- [ ] The opening contains at least three checkable details: counts, versions,
      dates, named products, measured values.
- [ ] No superlative you cannot verify: *best, leading, ultimate, most
      comprehensive*.
- [ ] Fewer than three hedges in the opening (*might, possibly, arguably, it
      depends*). Qualify where it is honest to; a passage that never commits
      gives a model nothing to quote.
- [ ] At least one sentence a competitor could not have written verbatim.

## 5. Structure

- [ ] At least one H2 is shaped as a question — one a reader would genuinely
      ask in those words.
- [ ] Three or more headings, so a specific answer has somewhere to anchor.
- [ ] One `h1`, matching what the page is about.
- [ ] Heading order does not skip levels.

## 6. Machine-readable extras

These are cheap. None of them causes a citation.

- [ ] `Article` or `BlogPosting` structured data, with dates matching the
      visible ones.
- [ ] No `FAQPage` markup on a page that is not questions and answers.
- [ ] No `aggregateRating` or `review` markup for reviews that do not exist.
- [ ] `llms.txt` or `agents.md` lists the page, with a sentence saying what it
      answers rather than just a URL.
- [ ] The page is self-canonical and is not a near-duplicate of another page
      on the site.

## 7. After any change

- [ ] Re-fetch as a crawler and confirm the answer is still in the body.
- [ ] Re-read the first hundred words cold.
- [ ] Check the date on the page is still true.

---

## The one-line version

Write so that any single paragraph can be removed from the page and still be
true, still make sense, and still say who is claiming it.
