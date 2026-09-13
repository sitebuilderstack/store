# Product demonstration — script, shot list, and how to install the recording

**Status: no video exists.** The homepage `sbs-demo` section renders a written
walkthrough instead, and will keep doing so until `video_url` is set. Nothing on the
site implies a video is available.

This document is what someone needs to record it.

---

## Constraints

- **Target length: 3 minutes.** Under 2:30 is better than over 3:30.
- **Everything on screen must be real.** Real folder, real files, real terminal. No
  mocked file trees, no invented output, no simulated Claude responses.
- **No voice-over required.** On-screen captions carry it. This is a developer
  audience watching with sound off on a laptop.
- **Numbers on screen must match the shipped product.** Verify before recording with
  `scripts/validate-product.py`.

Verified at time of writing: **113 files, 17 modules, 100 prompts, 114,556 words.**
The site says "more than 110,000 words", which stays true as the product grows.

---

## Shot list

### Scene 1 — What the buyer gets (0:00–0:25)

Terminal, in the unzipped directory:

```bash
tree -L 1 Claude-Code-Website-Launch-System/
```

Let the real listing render. Do not trim it to look tidier.

**Caption:** One ZIP. 17 modules. Nothing to install.

---

### Scene 2 — START-HERE (0:25–0:55)

Open `START-HERE.md`. Scroll to **section 6, "Pick your workflow"**, and hold on the
table long enough to read two rows.

**Caption:** Find your situation. Open the file next to it.

---

### Scene 3 — Choose a workflow (0:55–1:15)

Open `04-Shopify/SHOPIFY-MASTER-BUILD-PROMPT.md` (or the master builder prompt if a
generic build reads better). Scroll enough to show it is a staged prompt, not a
paragraph.

**Caption:** Not one wish. Staged work with a checkpoint at each stage.

---

### Scene 4 — Claude Code (1:15–2:05)

The only scene that needs care. Start a real session:

```bash
claude
```

Paste the real instruction:

```
Read 01-Master-System/MASTER-WEBSITE-BUILDER-PROMPT.md and work
through it stage by stage. Stop at the end of each stage and show
me what you have.
```

Let it actually run for one stage. **Cut on a real stage boundary, not mid-thought.**
If the run produces something unimpressive, record it again — do not edit the output.

**Caption:** Research → Plan → Architect → Design → Build → Write → Optimize → Secure
→ Test → Deploy → Index → Monitor → Improve

---

### Scene 5 — The specialist modules (2:05–2:40)

Quick cuts, roughly 5 seconds each, showing the real files:

| File | Caption |
| --- | --- |
| `03-SEO-System/TECHNICAL-SEO-AUDIT-PROMPT.md` | Audits that produce evidence |
| `11-Security/…` | Security review |
| `02-Claude-Code-Configuration/PRODUCTION-CLAUDE.md` | The project context |
| `14-Checklists/PRE-LAUNCH-CHECKLIST.md` | What to check before launch |
| `15-Claude-Code-Prompt-Library/SEO-PROMPTS.md` | 100 prompts for everything between |

---

### Scene 6 — Close (2:40–3:00)

Static card:

```
113 files
17 modules
100 reusable prompts
One repeatable website production system.
```

Then the URL. No price on screen — the page it sits on already carries it.

---

## Extended cut — scenes 7 to 10 (3:00–6:30)

The six scenes above are a three-minute overview, which is the right length for
a product page. A longer cut of five to eight minutes belongs on the free
resources hub and on YouTube, where the audience is learning rather than
deciding. It reuses scenes 1 to 6 unchanged and adds four.

### Scene 7 — The SEO system (3:00–4:00)

**Screen.** `03-SEO-System/`, then a real audit running in a terminal.

**Narration.** "The SEO module is not a list of tips. It is a set of checks with
a rule attached: every one has to be able to fail. Watch — I break the canonical
tag on purpose, run the audit, and it goes red. Then I fix it and it goes quiet.
That is the only way a passing audit means anything."

**Why this scene.** It is the argument the whole product rests on, and it is far
more convincing shown than claimed.

### Scene 8 — Security and accessibility (4:00–5:00)

**Screen.** `11-Security/` and `12-Accessibility/` side by side, then the
accessibility audit separating what a machine answered from what needs a person.

**Narration.** "Two modules people expect to be checklists. The accessibility
one splits its findings in two: what a tool can answer — contrast, labels,
heading order — and what only a person can, like whether the alt text is
actually useful. A report that blends those is telling you it found forty-seven
issues and nothing else."

### Scene 9 — The prompt library as skills (5:00–5:50)

**Screen.** `15-Claude-Code-Prompt-Library/`, then copying one into
`.claude/skills/` and invoking it as a slash command.

**Narration.** "A hundred prompts, written to be installed rather than pasted.
Drop one into your skills directory and it becomes a command you can run by
name. The file has to be called SKILL.md and live in a folder named for the
skill — get that wrong and Claude Code ignores it silently, which is the most
common reason a copied skill never shows up."

### Scene 10 — Close on the free half (5:50–6:30)

**Screen.** sitebuilderstack.com/blogs/guides, then a topic hub.

**Narration.** "Everything I have shown you is documented for free on the site.
Twenty-three guides, four topic hubs, four checklists you can tick off in your
browser. Read those first and decide for yourself whether the packaged version
is worth ninety-nine dollars. If it is not, you still have the method."

**Why end here.** It is true, it is checkable in one click, and it is the
strongest thing the product has to say about itself.

---

## Thumbnail

Three that would work, in order of preference. All should be produced at
1280×720 and legible as a 210px-wide card.

1. **Terminal, mid-audit, with one red FAIL line.** The single most
   representative frame in the whole recording. No face, no arrow, no shocked
   expression. Overlay four words at most — `Prove the check fails` — in the
   site's own mono face, bottom-left, on a dark plate.
2. **The module tree.** `START-HERE.md` plus the seventeen numbered
   directories, slightly angled, with `17 modules` set large. Concrete, shows
   scale, no claim that needs verifying.
3. **Split frame.** Vague prompt and its plausible-but-wrong output on the left;
   scoped prompt and a verified diff on the right. Hardest of the three to make
   legible at card size, so only attempt it if 1 and 2 have been tried.

Avoid, because they misrepresent: a play button composited onto a still, any
number that is not measured, a face reacting, and red arrows.

The poster image is a separate asset from the thumbnail. The poster should be a
real first frame of the video so nothing changes when playback starts; the
thumbnail is for YouTube and social cards and may be composed.

---

## Transcript outline

Publish the transcript as a page under the video, not as a download. It is the
accessible alternative, it is indexable, and it costs one page.

| Section | Covers | Approx. words |
| --- | --- | --- |
| What you get | The ZIP, seventeen modules, no account, no subscription | 120 |
| START-HERE | The situation-to-file table, six minutes to read | 130 |
| Choosing a workflow | New site, Shopify, existing site | 110 |
| Setting project context | `02-Claude-Code-Configuration`, why length matters | 180 |
| Running a build | The staged master prompt, one stage at a time | 200 |
| SEO | Checks that can fail, shown failing and then passing | 190 |
| Security and accessibility | Machine-answerable versus person-answerable | 170 |
| Prompts as skills | Installing one, the SKILL.md naming rule | 150 |
| Close | The free guides, and deciding for yourself | 110 |

Rules for the transcript: it is the same words as the captions, not a tidied
paraphrase; timestamps at each section heading; and no claim in it that is not
also in the recording.

---

## Deliverables to produce

| File | Format | Notes |
| --- | --- | --- |
| `launch-system-demo.mp4` | H.264 MP4, 1280×720, target under 20 MB | Keep it small; it loads on a product page |
| `launch-system-demo.vtt` | WebVTT captions | **Required.** Not optional, not "later" |
| `launch-system-demo-poster.png` | 1280×720 PNG | First meaningful frame, not a black frame |
| Transcript | A page under the video | Same words as the captions; outline above |
| `launch-system-demo-thumb.png` | 1280×720 PNG | For YouTube and social cards only — the poster is a separate, uncomposed frame |
| `launch-system-demo-long.mp4` | H.264 MP4, 1280×720 | The 6:30 extended cut, for the resources hub and YouTube. Not the product page |

---

## Installing it

1. Upload the MP4, the VTT and the poster:
   ```bash
   python3 scripts/upload-files.py \
     dist/launch-system-demo.mp4 \
     dist/launch-system-demo.vtt \
     dist/launch-system-demo-poster.png
   ```
2. In the theme editor, open the **SBS — Demo** section and set **Video file URL**,
   **Captions file** and **Poster image** to the returned CDN URLs.
3. The written walkthrough disappears automatically and the player takes its place.
   That switch is a single condition in `sections/sbs-demo.liquid` and has been
   tested in both directions.
4. Re-measure the page afterwards:
   ```bash
   node scripts/audit-performance.js https://sitebuilderstack.com/ 412
   ```
   The player uses `preload="metadata"`, so LCP should not move. If it does, the
   poster is too large.

---

## Why the section does not fake it

A play button over a still image, or a "coming soon" overlay on a dead player, is the
kind of thing that costs more trust than the video would have earned. The written
walkthrough contains the same information, works today, is crawlable, and adds no
bytes. When there is a real recording it replaces it.
