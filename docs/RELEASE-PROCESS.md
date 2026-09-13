# Release Process

How to ship a new version of the product.

```text
Edit product source
      ↓
Run validation
      ↓
Update VERSION.md
      ↓
Build (generates manifest, ZIP, checksum)
      ↓
Verify the archive
      ↓
Upload to the delivery app
      ↓
Test a real purchase
      ↓
Publish release notes
```

---

## 1. Edit

Everything ships from `product/Claude-Code-Website-Launch-System/`. Edit the
Markdown directly.

**When adding a file:** put it in the right numbered module. Do not renumber
directories — customers' notes and slash commands reference those paths, so
renumbering is a **major** version change.

**When making a version-sensitive claim** about Claude Code, Shopify, WordPress,
Astro, GitHub, or Cloudflare: verify it against primary documentation and cite
the URL in the file. That standard is what the product asks of its readers; it
has to hold for the product itself.

## 2. Validate

```bash
python3 scripts/validate-product.py
```

Checks: empty files, placeholder text, credentials of any known shape,
machine-local paths, broken internal links and cross-references, unintended
TODO markers, byte-identical duplicates, near-duplicate content, unbalanced code
fences, malformed tables, naming consistency, and required files.

**Errors fail the build. Warnings do not** — three warnings are expected and
benign: they are passages that mention "lorem ipsum", "placeholder text", and
"coming soon" while instructing readers to remove them.

## 3. Update `VERSION.md`

Bump the version and add a changelog entry. Scheme:

| Change | Bump |
| --- | --- |
| Typos, clarifications, link fixes | patch — 1.0 → 1.0.1 |
| New prompts, templates, expanded sections | minor — 1.0 → 1.1 |
| Renumbered directories, renamed files, restructure | major — 1.x → 2.0 |

## 4. Build

```bash
./scripts/build-product.sh 1.1
```

The script:

1. Checks 29 required files exist
2. Runs the validation suite
3. Confirms the prompt library still has ≥75 prompts
4. Generates `PRODUCT-MANIFEST.md` — every count derived from actual files,
   plus a self-consistent content digest
5. Builds the ZIP deterministically (sorted entries, single top-level directory)
6. Verifies the archive: CRCs, entry count, no empty entries, **no
   credential-shaped strings**, required files present
7. Writes `dist/<name>.zip.sha256`

It refuses to continue on any validation error.

### On the two checksums

A file cannot contain its own hash, so:

- **The archive SHA-256** goes in `dist/*.sha256` and in the release notes. It
  verifies the download arrived intact.
- **The content digest** goes inside `PRODUCT-MANIFEST.md`. It is a SHA-256 over
  the name and hash of every bundled file except the manifest, so a customer can
  verify the extracted contents. The command to reproduce it is printed in the
  manifest and has been tested.

## 5. Verify the archive independently

```bash
mkdir -p /tmp/verify && cd /tmp/verify
python3 -c "import zipfile;zipfile.ZipFile('<path>/dist/claude-code-website-launch-system-v1.1.zip').extractall('.')"
cd Claude-Code-Website-Launch-System

# contents match the manifest
find . -type f ! -name PRODUCT-MANIFEST.md | LC_ALL=C sort | while read -r f; do
  printf '%s  %s\n' "${f#./}" "$(sha256sum "$f" | cut -d" " -f1)"
done | sha256sum

# nothing sensitive slipped in
grep -rIlE 'AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{36}|shp(at|ss)_[0-9a-fA-F]{32}' . || echo clean
```

## 6. Ship it

1. Upload the new ZIP in the digital delivery app, replacing the old file
2. Update the product description if the counts changed —
   **every number on the sales page must match the manifest**
3. Update the hero and buy-section copy in the theme editor if counts changed
4. **Buy it yourself.** Confirm the link works and the checksum matches.
5. Publish release notes; tell existing customers if the change is substantial

## 7. Rollback

Keep the previous archive. To roll back, re-upload it in the delivery app and
revert the product copy. Nothing else needs changing.

---

## Numbers that appear on the storefront

These are asserted in the product description, the hero, the module cards, and
the buy list. **Re-check every one after a build**, because the manifest is
generated and the copy is not:

| Claim | Source of truth |
| --- | --- |
| 113 files | `find … -type f \| wc -l` |
| 17 modules | directory count |
| 100 prompts | `grep -cE '^## (DIS\|PLN\|…)-[0-9]+'` |
| 11 checklists | filename count |
| 10 templates | filename count |
| 67 prompt documents | filename count |
| over 110,000 words | manifest word count |
| per-module file counts | manifest module table |

`scripts/audit-storefront-claims.py` checks these automatically against the
built bundle.
