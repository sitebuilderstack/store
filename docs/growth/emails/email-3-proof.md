# Email 3 — day 4

**Subject:** Five production problems this workflow caught
**Preheader:** All five were invisible. All five were reported as fine.

---

This store was built with the system it sells. It did not go smoothly, and the failures
are more useful than the successes.

Five real ones. None of them were visible to somebody looking at the site.

**1. The primary call-to-action was invisible.** Text and background computed to the same
colour, because a generic link rule outranked the button rule by one point of CSS
specificity. Found by computing contrast in a rendered DOM. Reading the stylesheet would
never have caught it.

**2. The homepage title was the raw `.myshopify.com` domain.** Shopify falls back to it
when a preference field is empty. It looked completely normal in a browser tab. Found by
fetching the page and reading the title out of the response.

**3. Every call-to-action on every non-home page was dead.** They pointed at `#buy`, a
fragment that only exists on the homepage. No error, no navigation, just a click that did
nothing.

**4. The store could not accept payments.** Checkout said so — but the notice is injected
by JavaScript, so it was absent from the initial HTML and every fetch-based check reported
a healthy checkout for as long as it lasted.

**5. An order was fulfilled and delivered nothing.** It was placed with a phone number and
no email address, and the delivery app sends by email only. Every status the platform
reported said success.

## The thing they have in common

Every one was reported as fine by something. That turned out to be the real lesson, and it
kept happening to the checks themselves — a link crawler reported "0 broken links" across a
run where nine of twenty-eight pages had never been fetched.

So there is now one rule, and it applies to every check in the repository:

> **After a check passes, break the thing it checks and confirm it goes red.**

It costs about a minute. It has caught more real problems than anything else in the build.

The full write-up, with the mechanism behind each failure and a screenshot of the checkout
one, is here: **[How SiteBuilderStack.com was built](https://sitebuilderstack.com/pages/case-study)**

Next: how to pick which workflow you actually need.

— James
