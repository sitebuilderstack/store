# Bundle architecture — what shipped, and what is still open

**Status: the Complete Site Builder Stack shipped in September 2026** at
`/products/complete-site-builder-stack`, $39.99 (was $149 at launch), SKU `SBS-CCSTACK-V1`.

This document was written before it existed, to record what launching one would
need. It has been updated rather than replaced, because the reasoning that led to
the chosen shape is worth keeping — particularly the parts arguing against the
options not taken.

## What was actually built

**One SKU, three attachments.** The second option in the table below. The bundle
delivers the three existing archives as three downloads on one order; there is no
fourth combined archive.

That avoided the maintenance cost the last section of this document warns about:
a combined ZIP would need rebuilding and its checksum republishing every time any
of the three changed, and its version would be a fourth number able to disagree
with the other three.

**Pricing is computed, never typed.** `sections/sbs-bundle-value.liquid` resolves
each component through `all_products[handle]`, sums the live prices and subtracts
the bundle's own. If any component is unavailable the whole comparison is
suppressed rather than shown with a smaller total.

**The publisher enforces the rule below.** `scripts/publish-bundle-product.py`
refuses to publish a description containing any money at all, a "was" price, a
percentage off, an urgency or scarcity claim, or a bundle price at or above the
separate total. All six guards were control-tested by breaking the description
and watching each fire.

**Still open:** no files are attached to the bundle in the digital-delivery app.
It is purchasable and undeliverable, exactly as the other two paid products are.
Only a fulfilled paid order proves delivery; the Admin API cannot see an
attachment.

## The rule that constrains all of this

A bundle price must be a real price. Not a struck-through "was" figure that was
never charged, not a permanent "40% off", not a countdown to a deadline nobody
will enforce. The store's own products prohibit exactly those patterns —
`01-core/ETHICAL-BOUNDARIES.md` in the conversion toolkit lists them by name —
and a storefront contradicting its own product would be the most expensive kind
of inconsistency available.

That is what shipped: three products at $19.99 each; together $39.99. Both
numbers are stated, $39.99 is charged, and nothing is decorated. The separate total is never
presented as a former price, because the store has never charged it in one
transaction.

## What was already ready, and was used

**The header menu** (`sections/sbs-header.liquid`) supports four product slots
and resolves each through `all_products[handle]`. A fourth entry is a setting,
not a code change. A product that is drafted or deleted drops out of the menu
rather than rendering a dead link at a stale price.

**The three-product row** (`sections/sbs-ecosystem.liquid`) takes up to four
blocks and does the same live resolution, with the same drop-out behaviour. A
bundle card would slot in as a fourth block on the homepage and on each product
page.

**The claims auditor** (`scripts/audit-storefront-claims.py`) and the agents
auditor (`scripts/audit-agents-claims.py`) are already multi-product: the latter
fails if any active product is missing from `templates/agents.md.liquid`, so a
bundle that shipped without being described to agents would be caught.

**Digital delivery verification** (`scripts/verify-digital-delivery.py`)
shape-checks every active product independently.

**The upload blocklist** (`scripts/upload-files.py`) refuses every paid product
slug unconditionally. `complete-site-builder-stack` was added to that tuple and
control-tested: the upload was refused with no override available.

## What needed building, and what was decided

**A decision about what a bundle is.** Shopify offers several mechanisms and
they behave differently:

| Mechanism | What the customer gets | Delivery |
| --- | --- | --- |
| A fourth product containing all three archives | One SKU, one download | One combined ZIP attached in the digital-delivery app |
| A fourth product with three files attached | One SKU, three downloads | Three attachments on one product |
| Shopify's native bundles (combined listing / product bundles) | Three line items, one price | Each product delivers its own file |
| An automatic discount on a qualifying cart | Three products, discounted at checkout | Unchanged |

**The second was chosen.** The last row is the least work, but it gives the
bundle no page of its own and therefore nothing to link to, explain on, or rank.
The first was rejected for the maintenance reason below. Three attachments on one
SKU keeps each archive as its own source of truth with its own checksum, and
still gives the bundle a real product page.

**Licence wording.** Stated on the bundle page and in `agents.md`: still one
person, now with three products. The `LICENSE.md` inside each archive is
unchanged and still correct, since each archive is still one product licensed to
one person. **Open:** a v1.1 of each archive could say so explicitly.

**The build.** No fourth build script was needed, which was the point of
choosing three attachments. Each archive keeps its own manifest and checksum.

**A comparison table that includes it.** A fourth column was **not** added. The
three-column table already needed a horizontal-scroll container to survive
375px, and a fourth would have made that worse for the two products that carry
it. Each table gained a sentence beneath it pointing at the bundle instead —
which also avoids touching the READMEs inside the shipped archives, and so avoids
changing their checksums.

## The maintenance cost nobody counts

Every product multiplies the places a number can go stale. The store already
carries this: the file, module and prompt counts appear on the product page, in
the manifest, in `templates/agents.md.liquid`, in each bundle's README and on
the product image. That is why the publish scripts refuse to run when the
description disagrees with the bundle, and why the product images are generated
from the bundle rather than drawn.

A bundle adds a fourth set of numbers that must agree with three others. That
cost was paid mechanically rather than by discipline: the bundle publisher counts
the three product directories and refuses to publish a description that misstates
either total, the storefront auditor checks the bundle page against the sum of all
three, and the agents auditor verifies that the stated separate total still equals the live
component prices. All three were control-tested by breaking them.

## The fourth product, and why the bundle was left alone

The Website Operations & Maintenance System shipped on 13 September 2026 at
$39.99 — the same figure as the bundle. The bundle was **not** changed: not its
price, not its contents, not its copy beyond making "all three" read as "the
first three". The brief for the fourth product said so explicitly, and the
mechanics agree: the bundle's page computes its saving from the three live
component prices, the agents auditor asserts that the stated separate total is
the sum of exactly those three, and a fourth attachment would need a fourth
archive in the delivery app and a fourth set of counts on the bundle page.

**Recommendation, for the owner to decide.** Two coherent options, and one to
avoid:

1. *Leave it.* The bundle stays "build, rank, convert" at $39.99; the
   operations system is the fourth stage at $39.99 on its own. This is what is
   live. It is simple to explain, and the operations product's buyer is
   someone with a site already live, who is not the bundle's buyer.
2. *A second bundle — the four together — at a price above $39.99 and below
   $79.96.* Only worth doing once there is evidence (below) that people buy the
   operations system alongside another product. It would need its own product,
   four attachments, and the same computed-price plumbing the current bundle
   has; `BUNDLE_COMPONENTS` in `audit-agents-claims.py` and `STACK_TRUTH` in
   `audit-storefront-claims.py` would each need a second definition.
3. *Avoid:* adding the operations system to the existing bundle at the
   existing price. It would make a $79.96 set of products cost $39.99, which
   is a price cut on the three existing products dressed as a bundle change,
   and it would put a product that sells for $39.99 on its own into a $39.99
   bundle — a comparison nobody can explain at checkout.

The fact worth stating plainly: a customer today can buy the bundle ($39.99,
three products) or the operations system ($39.99, one product). The first
three products are $19.99 each, so the operations system is priced at twice
any one of them. That is defensible — it is the only product with working
code and the only one used weekly for the life of a site — but it is a
comparison a visitor will make, and the product page and FAQ say why rather
than hoping nobody notices.

## What would tell you it is worth doing

Not a hunch. The signals that would actually support it:

- Customers buying two products in separate orders, repeatedly
- Support or pre-sales questions asking whether there is a bundle
- Two products appearing together in the same cart and one being removed

None of these was measured before launching, and that is a fair criticism of the
decision. The store has had one paid order in its lifetime, so the signals above
could not have existed either way — there was no demand evidence to gather, and
the bundle was built because the brief asked for it, not because the data called
for it. Worth knowing when judging whether it works.
