# CONVERT sequence

For subscribers tagged `goal-convert`: they have traffic and need more leads or sales.

---

## Email 1 — day 0

**Subject:** Your website audit checklist
**Preheader:** Before you change anything, check the number you are optimising.

Here it is: **[The website audit checklist](https://sitebuilderstack.com/pages/claude-code-website-audit-checklist)**

**Do this first.** Open your analytics and find your conversion rate. Then answer two
questions about it: what counts as a conversion, and what is the denominator — sessions,
users, or something else?

If you cannot answer both from memory, that is the first job. Not because the number is
wrong, but because you are about to spend weeks trying to move it, and half the changes
people make to conversion rate are actually changes to how it is counted.

Verify the event fires once. A purchase event that fires twice makes every number in your
funnel wrong in the same direction, which is exactly the kind of wrong that never looks
unusual.

---

## Email 2 — day 2

**Subject:** Why traffic doesn't equal revenue
**Preheader:** And why the obvious fixes are usually the wrong ones.

Ask a capable model to "increase conversions" and a fair share of what comes back is a
countdown timer, a fake stock warning, and a confident prediction that the change will lift
revenue by some percentage.

None of that is knowledge. Two thirds of it is a compliance risk in several jurisdictions,
and the prediction is not something anyone can know in advance.

The quieter failure is more expensive. An audit that finds problems and fixes them in the
same session leaves a diff across thirty files, no report, and no way to tell which finding
was real. Six weeks later the number has moved and nobody can say which of the thirty
changes did it — so you cannot repeat it, and you cannot undo the one that hurt.

Conversion work has an evidence problem before it has an ideas problem. Almost everyone has
more ideas than they can test. Very few can say which of last quarter's changes worked.

No product in this email.

---

## Email 3 — day 4

**Subject:** A conversion audit that changes nothing
**Preheader:** Findings first. Fixes are a separate session.

The audit runs in a mode that is not allowed to edit anything. That constraint is the
whole method.

For each finding, record: what you looked at, the evidence, why it matters, and — the field
most people skip — **how confident you are, in a form you would defend.** Four labels are
enough:

- **Proven bug.** You reproduced it. A form that drops submissions above a length, a button
  that does nothing on iOS.
- **Strong heuristic.** Well-evidenced practice, not verified here.
- **Experiment opportunity.** Plausible, genuinely unknown, worth testing if you have the
  traffic.
- **Insufficient data.** You do not know, and saying so is the finding.

Then rank by **impact × confidence ÷ effort**. Not by how annoying each one is.

The fourth label is the one that earns its place. Most conversion reports have no way to
say "I don't know", so everything gets written up as if it were known, and the reader
cannot tell the reproduced bug from the hunch.

---

## Email 4 — day 6

**Subject:** When not to run the test
**Preheader:** The most useful output is sometimes "you can't measure this".

An A/B test needs enough traffic to detect the size of effect you care about. If it does
not have that, it does not return "no result" — it returns a *number*, and the number is
noise wearing a decimal point.

Work it out before you build the variant, not after. If your baseline conversion rate is 2%
and you want to detect a relative improvement of 10%, you need roughly 30,000 visitors per
arm for a conventionally powered test. At 500 visitors a week that is well over a year, by
which point seasonality has eaten the result.

So the honest output is often: **do not test this.** Ship the change on the strength of the
reasoning, write down what you expected, and check the trend later. Or fix the proven bugs
first, which need no test at all — a form that silently drops submissions is not a
hypothesis.

I ran this on my own store recently. The correct answer was "you have had one order ever;
do not test anything." That is not a satisfying finding. It is the right one, and a system
that could not produce it would be worse.

---

## Email 5 — day 8

**Subject:** The Conversion & Revenue Optimization Toolkit
**Preheader:** 70 workflows. None of them predicts a lift.

The [Conversion & Revenue Optimization
Toolkit](https://sitebuilderstack.com/products/claude-code-conversion-revenue-optimization-toolkit)
is the method from the last three emails: thirteen modules, 70 workflows, 68 commands, six
report templates and four worked examples.

The master CRO audit, page-by-page audits, funnel analysis, analytics verification, the
experimentation system, and a 30/60/90 roadmap generator.

Two things it will not do, enforced at build time rather than promised:

**It will not predict a percentage lift.** The build refuses to package if one appears in
any file.

**It will not recommend manipulative tactics.** Fake countdowns, fake scarcity, fabricated
customer numbers, confirmshaming, forced continuity — prohibited by name, and the same
check runs against the sales copy on its own product page.

99 files, plain Markdown, one payment. If your traffic is too low to test, it says so.

---

## Email 6 — day 11

**Subject:** Where your traffic comes from matters too
**Preheader:** Two of three, or all three.

Conversion is the last of three problems, and it depends on the two before it.

Traffic that converts badly is sometimes a page problem. Often it is a *traffic* problem —
the wrong visitors arriving on the right page, which no amount of button-colour work
fixes. And sometimes it is a build problem: a form that drops submissions, a page that
takes eight seconds on a real phone.

The [Complete Site Builder Stack](https://sitebuilderstack.com/products/complete-site-builder-stack)
is all three systems: build, rank, convert. $39.99 together; $59.97 bought separately. Both are
prices this store charges. The difference is not a discount off a former price — the three
have never been sold together at their separate total, and presenting it that way would
break the same rules the conversion toolkit prohibits by name.

If conversion really is your only problem, the single toolkit is the right purchase, and
I would rather you bought that one.
