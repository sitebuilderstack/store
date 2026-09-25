# Shopify SEO review worksheet

Two CSV files for reviewing product SEO titles and meta descriptions before
anything is written back to a store.

| File | What it is |
| --- | --- |
| `shopify-seo-review-worksheet.csv` | The blank template: a header row and one empty row. |
| `shopify-seo-review-worksheet-example.csv` | Five worked rows on a fictional store, showing an approved rewrite, a second approved rewrite, a product left alone, a rejected suggestion, and a product flagged for missing facts. |

Free to use and adapt. From [SiteBuilderStack](https://sitebuilderstack.com).

---

## This is not a Shopify import file

Read this before you try to upload it.

The worksheet is a **review document**. Shopify's product CSV import expects its
own column names, its own row structure (one row per variant, with the product
fields repeated or blank), and a specific handling of the SEO columns. This file
has neither that shape nor those headers, and importing it will not work.

The worksheet exists because the review is the part worth keeping. A Shopify
import file records what you decided; it does not record the current value you
replaced, who approved the change, or why one suggestion was thrown out. Those
are the columns that let you answer "why does this product say that?" in three
months.

**To move approved rows into Shopify**, do one of these:

- **Native bulk editor.** Filter to the approved products, add the *SEO title*
  and *SEO description* columns, and paste the approved values in. No
  transformation needed, and no API access needed either.
- **Product CSV.** Export the products from Shopify, copy the approved values
  into Shopify's own `SEO Title` and `SEO Description` columns in that export,
  and re-import. Keep Shopify's column names and row structure exactly as
  exported.
- **Admin API.** Read `approval_status`, keep only the `approved` rows, and
  write those two fields with a preview, a backup and a read-back. This is the
  route worth automating when the batch is large or recurring.

## The columns

| Column | What goes in it |
| --- | --- |
| `product_id` | The product's Admin GraphQL id (`gid://shopify/Product/…`). Stable across handle and title changes, which is why it, not the handle, is the key. |
| `handle` | The URL handle, for reading the sheet at a glance. **Changing this column changes nothing** — the worksheet never edits handles. |
| `product_url` | The live product URL, so a reviewer can open the page next to the row. |
| `current_seo_title` | The stored SEO title at export time. Empty means Shopify is falling back to the product title. |
| `current_seo_description` | The stored meta description at export time. Empty means Shopify (or the search engine) picks something. |
| `proposed_seo_title` | The draft. Leave it equal to the current value when nothing should change. |
| `proposed_seo_description` | The draft. Same rule. |
| `approval_status` | One of `approved`, `rejected`, `no change`, `needs info`. Anything else should stop a write script. |
| `reviewer_notes` | Why. This is the column that makes the sheet worth keeping. |

`current_seo_title` and `current_seo_description` are also the **staleness
check**: before writing, re-read the live values and compare them with these. If
they differ, someone edited the product after your export, and that row should
be skipped rather than overwritten.

## Two things the worksheet deliberately does not have

- **No product title, body description or handle columns.** Those are different
  fields from the SEO ones, and a sheet that carries all of them is a sheet that
  will eventually write one into another. If you need them for context, open the
  product URL.
- **No credentials, store domain or access token.** Nothing here should ever
  hold a secret. If your export tooling adds one, remove it before the file
  reaches a shared drive.

## Spreadsheet safety

Every field is quoted, the encoding is UTF-8, and no value begins with `=`, `+`,
`-` or `@`. A cell starting with one of those is treated as a formula by Excel
and Google Sheets, which is how a pasted product title can turn into `#NAME?` —
or worse, into something that runs. If you add rows by hand and a value has to
start with one of those characters, prefix it with an apostrophe.

## Length

Google truncates what it displays, and the cut-off depends on pixel width and
device, not character count. Treat roughly 60 characters for a title and roughly
155 for a description as editorial guidance for writing something that reads
well, not as a rule that changes rankings. Google also rewrites titles and
descriptions when it judges another version to be a better match for the query,
so a field being correct does not mean it will be the text a searcher sees.
