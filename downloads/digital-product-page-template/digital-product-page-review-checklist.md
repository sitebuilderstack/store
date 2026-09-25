# Digital product page — review checklist

Run this against a page before you call it finished, and again after any theme
change. Each line is checkable by looking, not by opinion.

Free to use and adapt. From [SiteBuilderStack](https://sitebuilderstack.com).

---

## 1. The purchase path

The checks that cost money when they fail.

- [ ] The opening purchase control is **this** product, at the live price.
- [ ] Every purchase control on the page resolves to the **same variant id**.
      View source and count the distinct `name="id"` values — there should be one.
- [ ] The closing section sells this product. Not the flagship, not the bundle.
- [ ] Any cross-sell is visually secondary and explicitly labelled as a
      different product.
- [ ] Button labels match behaviour: *Add to cart* adds, *Buy now* goes to
      checkout, *View sample* opens a sample.
- [ ] A double click does not add twice.
- [ ] An unavailable product shows an unavailable state, not a dead button.
- [ ] Price is rendered from the product. Search the page source for a
      hard-coded price string — there should be none.

## 2. The offer

- [ ] The headline names an outcome, not a quantity.
- [ ] A reader can say who it is for within one screen.
- [ ] Three benefits, each specific enough to be falsifiable.
- [ ] No superlative you cannot check ("ultimate", "best", "complete").
- [ ] Nothing implies a hosted service, an app, or an agent that works
      unattended, if the product is a download.

## 3. Proof

- [ ] At least one real artefact is visible without paying.
- [ ] The artefact is **output**, not packaging — a finished report or filled
      template, not a folder tree.
- [ ] Every example is labelled: real output / worked example / fictional
      demonstration.
- [ ] No fabricated screenshot, dashboard or customer evidence.
- [ ] No testimonial you cannot attribute to a real person who agreed to it.
- [ ] No countdown, stock-scarcity claim or "N people viewing".

## 4. Requirements and honesty

- [ ] Prerequisites are stated before the second purchase action.
- [ ] They are **not** inside a collapsed accordion.
- [ ] Any runtime is named with a version.
- [ ] Any access the buyer must grant is named.
- [ ] "No dependencies" does not appear unless it is literally true, including
      the software needed to use the files.
- [ ] At least one limitation is stated plainly.
- [ ] No promise of rankings, revenue, traffic, uptime, security or time saved.

## 5. Delivery, licence, refunds

- [ ] Delivery is described concretely: what arrives, where, when.
- [ ] The licence says whether client work is permitted.
- [ ] Redistribution terms are stated.
- [ ] The refund line **matches the store policy**. Open both and compare the
      words. This is the most common contradiction on a digital product page.
- [ ] The policy is linked, not summarised into something different.

## 6. Structure and rendering

- [ ] One `<h1>`. If the theme renders the product title as `<h1>`, the
      description must not contain another.
- [ ] Heading order does not skip levels.
- [ ] Every in-page anchor resolves to an id that exists **on this page**.
      A link to `/#faq` from a product page goes to the homepage.
- [ ] Exactly one `Product` structured-data block, with a price matching the
      visible price.
- [ ] No `aggregateRating` or `review` markup unless real reviews exist.
- [ ] The canonical URL is the product URL.

## 7. Mobile and access

- [ ] No horizontal page scroll at 390px. Tables and code blocks scroll inside
      their own container, not the document.
- [ ] Tap targets on purchase controls are at least 44px tall.
- [ ] The primary image is not lazy-loaded.
- [ ] Every image has alt text describing what it shows.
- [ ] The page is usable by keyboard: every control reachable, focus visible.
- [ ] Content is readable at 200% zoom.
- [ ] The core offer is readable with JavaScript disabled.
- [ ] No new console errors.

## 8. After a change

- [ ] Re-read the rendered page, not the template.
- [ ] Check the variant id again — a template edit is the usual way it drifts.
- [ ] Check the refund and requirement lines again if any policy moved.

---

## How to check the ones that are not obvious

**Distinct variant ids**

```
curl -s https://yourstore.com/products/your-handle \
  | grep -o 'name="id" value="[0-9]*"' | sort -u
```

More than one line means two purchase controls disagree about what they sell.

**Hard-coded prices**

```
curl -s https://yourstore.com/products/your-handle \
  | grep -oE '\$[0-9]+\.[0-9]{2}' | sort | uniq -c
```

Every occurrence should be the product's real price. A stale number here is a
price that was typed into the description.

**Anchors that leave the page**

```
curl -s https://yourstore.com/products/your-handle \
  | grep -oE 'href="/#[a-z-]+"'
```

Anything returned is a link to the **homepage's** section, from a product page.
