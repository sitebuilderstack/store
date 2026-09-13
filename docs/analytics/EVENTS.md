# Engagement events

## What this uses, and what it does not

Shopify's own analytics, through `Shopify.analytics.publish`. No second vendor,
no additional script, no extra network request beyond the ones the storefront
already makes.

That was a deliberate constraint. The site had no analytics of its own before
this work, and adding Google Analytics or Plausible alongside Shopify's would
have meant two systems disagreeing about the same sessions, plus a consent
question the store does not currently have to answer.

**Nothing personal is sent.** Every payload is an event name, a short `label`
(a link's visible text truncated to 80 characters, or a filter value), and for
links an `href`. No identifiers, no input contents, no email addresses. The
checklist's saved progress never leaves the browser at all — it is
`localStorage`, keyed per page, and is not sent anywhere.

## How it is wired

One delegated listener on `document` handles anything carrying
`data-sbs-track="<event name>"`, so markup added later reports without new
JavaScript. Components that need more than a click — the selector, the library
filter, the checklists — call the same `track()` helper directly.

`track()` is guarded in both directions: if `Shopify.analytics.publish` is
missing it is a no-op, and if it throws the exception is swallowed. Analytics is
never allowed to break a page. That guard is asserted by
`scripts/test-analytics-events.js`, which stubs `publish` to throw and confirms
the workflow selector still works.

## The events

Every one below is verified firing against the live site by
`scripts/test-analytics-events.js` — it stubs `Shopify.analytics.publish`,
performs the real interaction, and asserts the event was published. An event
listed here that stopped firing would fail that test.

### Discovery and navigation

| Event | Fires when | Label |
| --- | --- | --- |
| `pillar_view` | A topic hub link is clicked from the library or the selector | Hub title |
| `pillar_article_click` | A guide is opened from a hub's guide list | Guide title |
| `pillar_up_click` | The hub link in an article's header or footer is clicked | Hub title |
| `pillar_cross_link` | Another hub is opened from a hub page | Hub title |
| `related_guide_clicked` | A related guide is opened, from the in-article card or the footer block | Guide title |
| `next_step_clicked` | The in-article "Next in this path" card is clicked | Guide title |
| `learning_path_next_clicked` | A link in the end-of-guide continue block is clicked | Guide title |
| `resource_cta_clicked` | A resource is opened from a tool page | Resource title |

### Learning paths

| Event | Fires when | Label |
| --- | --- | --- |
| `learning_path_started` | The "Start with…" button on a hub is clicked | First guide title |
| `learning_path_step` | A specific step is opened from a hub's path list | Guide title |
| `learning_path_next` | The Next link at the foot of a guide is clicked | Guide title |
| `learning_path_prev` | The Previous link at the foot of a guide is clicked | Guide title |

There is no `learning_path_completed`. Completion cannot be observed without
tracking a visitor across sessions, which would mean an identifier this site
does not set. Reaching the last step is measurable as a `learning_path_next`
whose label is the final guide.

### Guide library

| Event | Fires when | Label |
| --- | --- | --- |
| `guide_filter_used` | A topic, level, goal or type filter changes | Number of results |
| `guide_search_used` | The search box is used | Number of results |

Both are debounced by 500 ms, so typing produces one event rather than one per
keystroke.

### Learning-path engine

| Event | Fires when | Label |
| --- | --- | --- |
| `route_started` | The first answer is given | — |
| `route_goal_selected` | A goal is chosen | Goal slug |
| `route_stage_selected` | A stage is chosen | Stage slug |
| `route_level_selected` | An experience level is chosen | Level slug |
| `route_generated` | All three answers are in and a roadmap is shown | `goal/stage/level` |
| `route_step_clicked` | A step in the roadmap is opened | Step title |
| `route_step_completed` | A step is ticked | Step id |
| `route_step_uncompleted` | A step is unticked | Step id |
| `route_completed` | All seven steps are ticked | Goal slug |
| `route_reset` | Progress is reset for that roadmap | Goal slug |

Progress itself never leaves the browser. The step id in the label is
`<goal>:<index>` — a position in a published roadmap, not anything about the
visitor.

### Free tools

| Event | Fires when | Label |
| --- | --- | --- |
| `tool_started` | The first field is touched | Tool name |
| `tool_completed` | A result is generated | Tool name |
| `tool_result_copied` | The result is copied | Tool name |
| `tool_reset` | The form is cleared | Tool name |

**The label is the tool's name and nothing else.** Generated CLAUDE.md files,
project descriptions, site URLs and questionnaire answers are never sent. The
test types a sentinel string into every field and then searches every published
payload for it, so this is asserted rather than promised.

### Learning progress

| Event | Fires when | Label |
| --- | --- | --- |
| `lesson_completed` | A guide is marked complete | Guide handle |
| `lesson_saved` | A guide is saved for later | Guide handle |
| `learning_reset` | Progress is cleared on `/pages/my-learning` | `my-learning` |
| `readiness_product_clicked` | The readiness score's recommendation is opened | Product title |
| `tool_cta_clicked` | The matched free tool is opened from the foot of a guide | Button label |

Only the handle is sent, and only on the transition into the state — unmarking a
guide publishes nothing. **The stored progress itself never leaves the browser.**
It is `localStorage` under one key, and there is no identifier tying it to a
visitor, so the site can see that *a* guide was completed and never which browser
completed it. `scripts/test-learning.js` asserts the storage behaviour, including
that a reset actually empties it rather than only clearing the view.

### Lead capture

| Event | Fires when | Label |
| --- | --- | --- |
| `lead_segment_build` | The signup form's "build" option is chosen | — |
| `lead_segment_rank` | The signup form's "rank" option is chosen | — |
| `lead_segment_convert` | The signup form's "convert" option is chosen | — |

The choice is also written to the customer record as a Shopify tag
(`goal-build`, `goal-rank`, `goal-convert`) through the native customer form, so
the segmentation lives where the email platform can already read it rather than
in a second system. No email address is ever published to analytics.

### Copyable resources

| Event | Fires when | Label |
| --- | --- | --- |
| `prompt_copied` | A `.sbs-prompt` block is copied | Button label |
| `command_copied` | A single-line shell command is copied | Button label |
| `claudemd_example_copied` | A CLAUDE.md example is copied | Button label |
| `code_copied` | Any other code block is copied | Button label |

### Checklists and resources

| Event | Fires when | Label |
| --- | --- | --- |
| `checklist_item_toggled` | An item is ticked or unticked | `checked` / `unchecked` |
| `checklist_reset` | Clear all is used | — |
| `checklist_printed` | Print is used | — |
| `lead_magnet_clicked` | A free resource is opened from an article, hub or selector | Resource title |

### Commerce

| Event | Fires when | Label |
| --- | --- | --- |
| `product_cta_clicked` | Any product call to action is clicked | Button text |
| `product_nav_clicked` | A product is opened from the header menu | Product title |
| `product_ecosystem_clicked` | A product is opened from the product row (four on the homepage, the other three on a product page) | Product title |
| `product_sample_viewed` | The free sample workflow is opened from a product page | Link text |
| `bundle_cta_clicked` | The bundle line under a guide's product CTA is clicked | Bundle title |

Four separate names for four placements on purpose. Merging them into one
`product_click` would make all four unreadable — the question worth answering is
*which placement* sells, and a combined number cannot answer it.

Checkout starts and purchases are already recorded by Shopify's own analytics
and are not duplicated here.

## Reading the results

Shopify surfaces custom events to Web Pixels rather than in the standard
Analytics reports. To use them, add a custom pixel in
**Settings → Customer events** that subscribes to the event names above and
forwards them wherever you want them. Until such a pixel exists the events are
published and simply have no subscriber — which is why this document does not
claim the data is already being collected somewhere.

## What is deliberately not tracked

- Scroll depth. It correlates poorly with reading and costs a listener on every page.
- Time on page. Shopify already reports session duration; a second measurement would disagree with it.
- Anything typed into the search box. Only the result count is sent.
- Checklist contents. Which items a person ticked stays in their browser.

## Baselines

None are recorded here, because none have been measured since these events
started firing. The `Before` column of any future comparison has to come from
Search Console and Shopify analytics for the period before 6 September 2026 —
see `docs/analytics/BASELINE-2026-09-06.md` for what was actually measured on
the day this shipped.
