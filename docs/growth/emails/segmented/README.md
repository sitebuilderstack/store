# Segmented email sequences

Three sequences, chosen by the goal the subscriber picked on the signup form.

**None of this is configured or sending.** The blockers are at the bottom, and one of
them still is that no signup has ever completed successfully. Writing the sequences
does not change that, and nothing here should be reported as a working funnel.

## How someone lands in a sequence

The opt-in form (`sections/sbs-optin.liquid`) asks one question and writes the answer to
the customer record as a Shopify tag, alongside the tag identifying which resource they
downloaded:

| They picked | Tag applied | Sequence |
| --- | --- | --- |
| I need to build or launch a website | `goal-build` | [BUILD](./build.md) |
| I have a website and need more organic traffic | `goal-rank` | [RANK](./rank.md) |
| I have traffic and need more leads or sales | `goal-convert` | [CONVERT](./convert.md) |

The first option is pre-selected, so a subscriber who ignores the question still lands in
BUILD rather than in nothing. That is a deliberate choice: BUILD is the safest default
because its early emails are useful to all three groups, and because someone who did not
engage with the question is more likely to be early-stage than late.

Radios named `contact[tags]` submit through Shopify's own customer form. There is no
second platform, no JavaScript, and no identifier beyond the email address they typed.

## The shape, in all three

```
Deliver → Teach → Workflow → Worked example → The matching product → The bundle
```

Four of the six are worth reading by someone who never buys anything. That is not
generosity; it is the only reason the fifth and sixth get opened.

| # | Day | Job |
| --- | --- | --- |
| 1 | 0 | Deliver what was promised, plus one thing they can do in five minutes |
| 2 | 2 | The idea underneath their problem, with no product mention |
| 3 | 4 | A workflow they can run today |
| 4 | 6 | A worked example, including what the first pass got wrong |
| 5 | 8 | The product that matches their goal |
| 6 | 11 | The bundle, for the ones with more than one of the three problems |

## Rules these were written under

- No fake scarcity, no countdown, no "price goes up at midnight". Nothing expires unless
  it genuinely does, and nothing currently does.
- No fabricated results, customer counts, or revenue figures. The case study cites what
  was measured on this site and says when something was not measured.
- Email 6 states the bundle price and the separate total. Both are real prices. It never
  calls the difference a discount off a former price, because there was no former price.
- Every email is shorter than the reader expects.
- No `Hey {{first_name}}!`. The list does not collect a first name and inventing a
  merge field that resolves to nothing is worse than not greeting anyone.

## What has to happen before any of this runs

1. **A signup has to work end to end.** The form has never produced a subscriber.
   Until one does, sequence configuration is premature.
2. **An email platform has to be chosen and connected.** Shopify Email can read customer
   tags; anything else needs the tags synced. This is not set up.
3. **The unsubscribe and privacy wording has to match the privacy policy**, which
   currently describes the list but not a multi-sequence automation.

Nothing above is scheduled, queued, or connected to a sending domain.
