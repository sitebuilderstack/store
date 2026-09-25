Twenty ways a website built with an AI coding assistant breaks quietly. Not crashes —
those announce themselves. These are the failures where the build succeeds, the page
renders, the check reports success, and something is still wrong.

Each entry states the problem, why it happens, how to detect it, how to fix it, and how
to prove the fix actually worked. That last step is the one worth insisting on.

**Every entry is labelled.** Sixteen of these were observed on this site during its
build and are marked **Observed here**, with what actually happened. The rest are marked
**General**: real failure classes documented in vendor guidance or standards, included
because they are common, but not things that happened here. Nothing below is invented,
and nothing general is dressed up as a case study.

## How to use this

Work the detection column first. Most of these are invisible to review and obvious to a
five-line script — which is the whole point. Then prove the check works by breaking the
thing it checks and confirming it goes red. A check that has never failed is not
evidence.

## 1. A template setting the platform silently discards

**Observed here.**

- **Problem.** A JSON template referencing a section setting the section's own schema does not yet define. The upload succeeds. The setting is gone. The page renders with defaults and no error anywhere.
- **Why it happens.** Shopify validates template JSON against the schema it currently holds. Unknown keys are dropped rather than rejected. Push order decides whether the schema is current.
- **How to detect it.** Read the setting back after pushing, or render the page and look for the value. Nothing in the push output will tell you.
- **How to fix it.** Push the section `.liquid` first, then the template that uses it. Same rule for raising `max_blocks` before a section group exceeds the old limit.
- **How to validate the fix.** Fetch the rendered page and assert the new setting's value appears. On this site the dropped settings were a FAQ section's `more_url` and `more_label`; they were only found by looking at the live HTML.

## 2. An identifier that is not the identifier you stored

**Observed here.**

- **Problem.** Every hub page on this site rendered with an empty guide list. No error, no warning, correct heading, no content.
- **Why it happens.** `article.handle` in Shopify Liquid is the *qualified* handle — `guides/claude-code-seo`, not `claude-code-seo`. Filtering an article list by the bare handle matches nothing, and a filter that matches nothing renders nothing.
- **How to detect it.** Print the value rather than assuming it. One debug line showing `first_handle=guides/claude-code-accessibility-audit` ended an hour of theorising about metafield visibility.
- **How to fix it.** Compose the qualified form, and keep the bare form as a fallback so a future platform change degrades instead of emptying every page.
- **How to validate the fix.** Assert a non-zero count of resolved items on a page that must have them. "Renders without error" and "renders the content" are different tests.

## 3. `display` beating the `hidden` attribute

**Observed here.**

- **Problem.** Elements toggled with `el.hidden` stayed fully visible and their links stayed in the tab order. On this site, all three experience-level branches of the homepage selector painted at once, and the guide library's filter form appeared for visitors with JavaScript disabled, where it does nothing.
- **Why it happens.** `[hidden] { display: none }` lives in the user-agent stylesheet. *Any* author rule setting `display` on that element wins, regardless of specificity, because author styles beat UA styles. Components laid out with `display: grid` are the usual casualties.
- **How to detect it.** Assert what is painted, not what the attribute says. `el.hidden === true` was true the whole time. `getBoundingClientRect().height > 0` is what caught it.
- **How to fix it.** One rule: `[hidden] { display: none !important; }`, scoped to your root.
- **How to validate the fix.** Re-run the paint assertion, and check that no link inside a hidden container can take focus.

## 4. A copy button that copies itself

**Observed here.**

- **Problem.** Every code block anyone copied from this site had the word `Copy` appended to the end of it.
- **Why it happens.** The button was appended inside the `<pre>`, and the click handler read `pre.textContent` at click time — which by then included the button's own label. There was a guard stripping a *leading* "Copy", which never matched, because `appendChild` puts it last.
- **How to detect it.** Actually paste the result. Nobody does, because the button visibly works.
- **How to fix it.** Capture the text before inserting the button, or read from the `<code>` child, or exclude the button node.
- **How to validate the fix.** Assert the clipboard contents equal the code block's original text exactly, including the last character.

## 5. A class name that already means something else

**Observed here.**

- **Problem.** A new navigation component took the class `sbs-inline-cta`, which was already the "From the toolkit" product aside authored into all 23 guides. The cascade collided and a navigation link was styled as a third advert.
- **Why it happens.** Naming a component without checking whether the name is taken. In a project where content contains authored markup, the CSS namespace includes the content.
- **How to detect it.** Grep the content, not just the templates, before naming anything.
- **How to fix it.** Rename the new component. The existing one has more callers and is not yours to redefine.
- **How to validate the fix.** Grep for the old name in the new component's markup and assert zero, then look at a page carrying both.

## 6. A duplicated title tag across a whole URL family

**Observed here.**

- **Problem.** All eight `/blogs/guides/tagged/*` archives shipped the blog index's exact title and meta description. Eight indexable URLs, one title.
- **Why it happens.** Shopify falls back to the parent resource's SEO fields for tag archives. The default is a duplicate.
- **How to detect it.** Crawl your own site and group by title tag. Any group with more than one URL is a finding.
- **How to fix it.** Give them a distinct title, and decide honestly whether they should be indexed. These are now `noindex, follow` — they add no text the index does not already have, but they still pass link equity through.
- **How to validate the fix.** Re-crawl and assert every title is unique, and that the pages you meant to noindex carry the directive and the ones you did not, do not.

## 7. Paginated pages that duplicate page one

**Observed here.**

- **Problem.** `?page=2` shipped page one's title and description. Worse, a page number past the end of the list returned `200` with an empty result set — a thin page reachable by guessing.
- **Why it happens.** Nothing in a default template appends the page number, and most paginators do not bound-check.
- **How to detect it.** Your crawler has to follow query strings. This site's own SEO auditor stripped them, so it never fetched `?page=2` and reported the duplicate title as absent. Fixing the crawler took coverage from 48 URLs to 74.
- **How to fix it.** Append the page number to title and description. Keep the pages indexable and self-canonicalising — pointing them all at page one hides everything that only appears later. Noindex only the out-of-range ones.
- **How to validate the fix.** Assert that the page-size constant in the paginator equals the one the layout uses to decide what is out of range. This site has a test for exactly that, because the drift is silent and drops real pages from the index.

## 8. A page you have never looked at

**Observed here.**

- **Problem.** `/collections/frontpage` sat in the sitemap, rendering through the purchased parent theme with an `h1` of "Home page" and no title tag at all.
- **Why it happens.** Layering your own templates over a bought theme claims the routes you built. Everything else falls through to the original, including routes you did not know existed.
- **How to detect it.** Enumerate URLs from the sitemap, not from your templates directory. The sitemap knows about pages you have forgotten.
- **How to fix it.** Either claim the route with your own template or unpublish the resource. Unpublishing removes it from the storefront *and* the sitemap, which is cleaner than a noindex that still has to be fetched to be discovered.
- **How to validate the fix.** Re-fetch the sitemap and assert the URL is gone, rather than assuming the change propagated.

## 9. A Liquid error rendered into the page head

**Observed here.**

- **Problem.** An `og:image` tag emitted a Liquid error string into the document head. The page looked entirely normal.
- **Why it happens.** A theme setting held a value but the schema had no matching `image_picker`, so it stayed a plain string, and `image_url` on a string produces an error rather than a URL.
- **How to detect it.** Fetch the rendered HTML and grep the head. Browsers do not complain about a malformed meta tag, and neither will you if you only ever look at the page visually.
- **How to fix it.** Guard on the object, not on the setting's truthiness.
- **How to validate the fix.** Assert no page in the crawl contains the platform's error format anywhere in its source. Match the specific format — the words "Liquid error" appear in prose on this very site.

## 10. A homepage title that is your internal domain

**Observed here.**

- **Problem.** The homepage title fell back to the store's internal `myshopify.com` domain. Nothing was visibly wrong on the page.
- **Why it happens.** Shopify's `page_title` falls back to that domain when the Online Store preferences title is unset, and there is no API to set it.
- **How to detect it.** Read the `<title>` of your own homepage from the rendered HTML. It is the single most valuable thirty seconds in a technical audit.
- **How to fix it.** Supply the title from theme settings for that one template rather than depending on the platform's fallback.
- **How to validate the fix.** Assert the homepage title contains your brand and not `myshopify`.

## 11. An HTML entity escaped twice

**Observed here.**

- **Problem.** `&amp;mdash;` printed as visible text where an em dash was intended.
- **Why it happens.** An entity placed inside a Liquid `capture`, then passed through `escape`, has its ampersand escaped. The output is the entity's source code, not the character.
- **How to detect it.** Grep the rendered HTML for `&amp;` followed by a known entity name. It is a two-line check that catches an entire class.
- **How to fix it.** Use the literal character, not the entity, in anything that will be escaped later.
- **How to validate the fix.** Run the detector against both the broken and the fixed string. This site's had to be proven on both, because a detector that reports "clean" on input it cannot parse is worse than none.

## 12. An audit that cannot fail

**Observed here.**

- **Problem.** Checks reporting success without ever having run. This site's link crawler, tap-target checker and coverage reporter each produced confident, wrong output at some point.
- **Why it happens.** Nobody writes a passing test for their test. A green run feels like evidence.
- **How to detect it.** Break the thing deliberately and see whether the check notices. If it does not, it never did.
- **How to fix it.** Control-test in both directions: it must fire on a crafted failure *and* go quiet on a clean case. A check that fires on everything is ignored as fast as one that fires on nothing.
- **How to validate the fix.** Keep the broken case. Every validator on this site has a `--self-test` mode that mutates its own input and asserts each mutation is caught.

## 13. A standard implemented without its exceptions

**Observed here.**

- **Problem.** A tap-target checker flagged every link inside every paragraph, producing hundreds of failures on any article.
- **Why it happens.** WCAG 2.2 success criterion 2.5.8 has five exceptions, and one of them is **Inline** — targets in a sentence of text are exempt. A checker without that rule is technically measuring something true and practically useless.
- **How to detect it.** A wall of failures on content you believe is fine is a signal about the checker, not the content.
- **How to fix it.** Implement the exceptions, in the checker. Do not restructure correct markup to satisfy a broken tool, and do not train yourself to skim past its output.
- **How to validate the fix.** Assert it stays silent on an inline link and still fires on a genuinely small standalone button.

## 14. A generator that silently truncates

**Observed here.**

- **Problem.** Diagram subtitles were being clipped where they overflowed their box. Three diagrams had been shipping clipped since publication.
- **Why it happens.** Drawing code that overflows usually just draws outside the box or gets cut by a clip region. Neither raises.
- **How to detect it.** Measure the text and compare it to the space, then raise. The guard found all three immediately; review had not found them in weeks.
- **How to fix it.** Fail the build on overflow rather than rendering something wrong.
- **How to validate the fix.** Feed the guard a deliberately over-long string and confirm it raises.

## 15. An API that answers confidently with degraded data

**Observed here.**

- **Problem.** A coverage report claimed ten sitemap URLs were unknown to Google. They were not.
- **Why it happens.** Google's URL Inspection API, called rapidly in sequence, returns degraded records — "URL is unknown to Google" with `sitemap: false` for URLs in a sitemap Google had demonstrably downloaded. Re-inspected unhurriedly, the same URLs returned "Discovered".
- **How to detect it.** Cross-check one implausible result by hand before reporting a set of them.
- **How to fix it.** Retry, slow down, and label an unconfirmed result *unmeasured* rather than reporting absence as fact.
- **How to validate the fix.** Re-run and confirm the counts are stable across runs. An unstable count is the tell.

## 16. Replacing a file that does not get replaced

**Observed here.**

- **Problem.** Uploading a file under an existing name produced a second file with a UUID appended. Every page pointing at the old URL kept serving the old asset.
- **Why it happens.** Shopify's file API does not overwrite by filename.
- **How to detect it.** Compare the returned URL to the one you expected, and fetch the live asset rather than trusting the upload's success.
- **How to fix it.** Delete, then re-upload.
- **How to validate the fix.** Request the referenced URL and check the response body is the new content.

## 17. Secrets somewhere other than the repository

**General.**

- **Problem.** Credentials in a log line, a generated report, a screenshot, a template, or a downloadable artefact. Scanning only commits misses all five.
- **Why it happens.** "Do not commit secrets" is a rule about one destination. Diagnostic output has many.
- **How to detect it.** Pattern-scan the whole working tree, not just tracked files, and run every diagnostic through a redaction filter before it is printed.
- **How to fix it.** Read credentials from a path outside the repository and pass them by reference, never by value, into anything that prints.
- **How to validate the fix.** Plant a fake credential matching your own patterns and confirm the scanner aborts. If it does not fire on a planted key, it is decorative.

## 18. An API key in the client bundle

**General.**

- **Problem.** A key used from front-end JavaScript. It is public the moment it ships, whatever the file is named or how it is obfuscated.
- **Why it happens.** A build tool inlines an environment variable that was never meant to reach the client, often because the variable naming convention that marks a value public was not followed.
- **How to detect it.** Search the built bundle, not the source, for your key patterns.
- **How to fix it.** Move the call server-side. If a public key is genuinely required, scope and rate-limit it at the provider and treat it as disclosed.
- **How to validate the fix.** Rebuild, re-scan the output, and rotate the key that was exposed — a removed secret that was ever published is still published.

## 19. An accidental `noindex` that nobody notices

**General.**

- **Problem.** A staging directive, a blanket template rule, or a plugin default leaves `noindex` on pages that should rank. Traffic decays over weeks rather than dropping visibly.
- **Why it happens.** Robots directives are invisible in the rendered page. A blanket rule written for one case silently applies to resources created later.
- **How to detect it.** Crawl and assert directives per URL — both that the pages you meant to exclude are excluded, and that no others are. This site deliberately removed a blanket collection-level noindex for exactly that reason: it would have hidden any collection published afterwards.
- **How to fix it.** Make every exclusion a specific decision about a specific resource.
- **How to validate the fix.** Assert in both directions, and re-check after deploying — this is one of the things that genuinely differs between local and production.

## 20. Structured data describing a page that does not exist

**General.**

- **Problem.** Markup claiming ratings, reviews, prices, availability or FAQs that a visitor cannot see on the page. This is a guidelines violation and the most common reason for a manual action on structured data.
- **Why it happens.** A validator suggests an optional field, and it gets filled in with something plausible. `aggregateRating` on a site with no reviews is the classic.
- **How to detect it.** Parse every JSON-LD block and assert forbidden types are absent. This site's test suite fails the build if `aggregateRating`, `ratingValue` or `reviewCount` appear anywhere, because there are no reviews and there is no honest way to add them.
- **How to fix it.** Delete the field. An absent optional property costs nothing; a false one risks the whole property.
- **How to validate the fix.** Assert the JSON parses, that the types present are ones you intended, and that values like price come from the same source the visible page reads rather than a literal that can go stale.

## The pattern underneath

Almost every entry above is invisible until something asserts the opposite of what was
assumed. Very few were found by reading code; they were found by measuring output.

The habit worth taking away is smaller than a methodology: **when you write a check, break
the thing first and watch it fail.** Then fix it and watch it go quiet. Everything above
either was found that way, or would have been.
