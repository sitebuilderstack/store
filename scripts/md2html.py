#!/usr/bin/env python3
"""Markdown -> HTML for the resource pages.

Deliberately supports only the subset used by content in `resources/`, so the
output markup matches the conventions the rest of the site already uses
(`.sbs-table` wrappers, `.sbs-checklist`, `<pre><code>`). A general-purpose
converter would emit markup the stylesheet does not know about.

The leading `# Title` is dropped: the section template renders the page title
as the h1, and two h1 elements on one page is an SEO and accessibility fault.
"""
import hashlib
import html
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "resources")


def inline(s):
    """Escape, then re-introduce the small set of inline constructs."""
    out = []
    # Protect code spans first: their contents must not be link- or bold-parsed.
    parts = re.split(r"(`[^`]+`)", s)
    for part in parts:
        if part.startswith("`") and part.endswith("`") and len(part) > 1:
            out.append("<code>%s</code>" % html.escape(part[1:-1], quote=False))
            continue
        t = html.escape(part, quote=False)
        # Images before links: ![alt](src) would otherwise match the link rule
        # and render as a literal "!" followed by an anchor.
        t = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", _image, t)
        t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", _link, t)
        t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
        t = t.replace("--", "&mdash;") if False else t
        out.append(t)
    return "".join(out)


def _image(m):
    """Images become a figure. Dimensions are required so the layout cannot
    shift while they load, so the source must carry them in the query string
    as ?w=NNN&h=NNN — an image without them is a build error rather than a
    silent CLS regression."""
    alt, src = m.group(1), m.group(2)
    if not src.startswith("https://cdn.shopify.com/"):
        raise SystemExit("image not on the Shopify CDN: %s" % src)
    if len(alt) < 40:
        raise SystemExit("image alt too short to be informative: %r" % alt)
    dims = re.search(r"[?&]w=(\d+)&(?:amp;)?h=(\d+)", src)
    if not dims:
        raise SystemExit("image src needs ?w=NNN&h=NNN for dimensions: %s" % src)
    clean = re.sub(r"[?&]w=\d+&(?:amp;)?h=\d+", "", src).rstrip("?&")
    return ('<figure><img src="%s" alt="%s" width="%s" height="%s" '
            'loading="lazy" decoding="async"></figure>'
            % (html.escape(clean, quote=True), html.escape(alt, quote=True),
               dims.group(1), dims.group(2)))


def _link(m):
    text, url = m.group(1), m.group(2)
    if url.startswith("http"):
        if not url.startswith("https://"):
            raise SystemExit("non-https external link: %s" % url)
        return '<a href="%s" rel="noopener">%s</a>' % (html.escape(url, quote=True), text)
    return '<a href="%s">%s</a>' % (html.escape(url, quote=True), text)


def slug(text):
    s = re.sub(r"<[^>]+>", "", text).lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return re.sub(r"^\d+-", "", s) or "section"


def expand_includes(lines):
    out = []
    for ln in lines:
        m = re.match(r"^\{\{INCLUDE:(.+?)\}\}\s*$", ln)
        if not m:
            out.append(ln)
            continue
        path = os.path.join(RES, m.group(1))
        body = io.open(path, encoding="utf-8").read().rstrip("\n")
        out.append("```")
        out.extend(body.split("\n"))
        out.append("```")
    return out


def convert(md):
    lines = expand_includes(md.replace("\r\n", "\n").split("\n"))
    out, i, n = [], 0, len(lines)
    headings = []          # (level, id, text) for the table of contents
    ids = set()
    dropped_h1 = False

    def push_id(text):
        base = slug(text)
        s, k = base, 2
        while s in ids:
            s, k = "%s-%d" % (base, k), k + 1
        ids.add(s)
        return s

    while i < n:
        ln = lines[i]

        if not ln.strip():
            i += 1
            continue

        # fenced code
        if ln.startswith("```"):
            i += 1
            buf = []
            while i < n and not lines[i].startswith("```"):
                buf.append(lines[i])
                i += 1
            i += 1
            out.append("<pre><code>%s</code></pre>" %
                       html.escape("\n".join(buf), quote=False))
            continue

        # headings
        m = re.match(r"^(#{1,4})\s+(.*)$", ln)
        if m:
            lvl, text = len(m.group(1)), m.group(2).strip()
            if lvl == 1:
                if dropped_h1:
                    raise SystemExit("second h1 in document: %r" % text)
                dropped_h1 = True
                i += 1
                continue
            hid = push_id(text)
            headings.append((lvl, hid, text))
            out.append('<h%d id="%s">%s</h%d>' % (lvl, hid, inline(text), lvl))
            i += 1
            continue

        # blockquote
        if ln.startswith("> "):
            buf = []
            while i < n and lines[i].startswith("> "):
                buf.append(lines[i][2:])
                i += 1
            out.append("<blockquote><p>%s</p></blockquote>" % inline(" ".join(buf)))
            continue

        # table
        if ln.lstrip().startswith("|") and i + 1 < n and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1]):
            def cells(row):
                return [c.strip() for c in row.strip().strip("|").split("|")]
            head = cells(ln)
            i += 2
            body = []
            while i < n and lines[i].lstrip().startswith("|"):
                body.append(cells(lines[i]))
                i += 1
            t = ['<div class="sbs-table">', "<table>", "<thead><tr>"]
            t += ["<th>%s</th>" % inline(c) for c in head]
            t += ["</tr></thead>", "<tbody>"]
            for r in body:
                t.append("<tr>" + "".join("<td>%s</td>" % inline(c) for c in r) + "</tr>")
            t += ["</tbody>", "</table>", "</div>"]
            out.append("\n".join(t))
            continue

        # checklist / unordered list
        if re.match(r"^-\s+", ln):
            checklist = bool(re.match(r"^-\s+\[[ xX]\]\s+", ln))
            items = []
            while i < n and re.match(r"^-\s+", lines[i]):
                item = re.sub(r"^-\s+", "", lines[i])
                is_check = bool(re.match(r"^\[[ xX]\]\s+", item))
                if is_check != checklist:
                    break
                item = re.sub(r"^\[[ xX]\]\s+", "", item)
                if checklist:
                    # A real checkbox and label, server-rendered. Ticking works
                    # with JavaScript disabled; the script only adds progress,
                    # persistence and reset on top.
                    #
                    # The id is a hash of the item's own text, so it is stable
                    # across rebuilds and across pages. That matters because it
                    # is the localStorage key: deriving ids from position would
                    # silently move everyone's saved progress onto different
                    # items the first time an item was inserted.
                    cid = "chk-" + hashlib.sha1(item.encode("utf-8")).hexdigest()[:12]
                    items.append(
                        '<li class="sbs-check">'
                        '<input type="checkbox" id="%s" data-sbs-check>'
                        '<label for="%s">%s</label></li>' % (cid, cid, inline(item)))
                else:
                    items.append("<li>%s</li>" % inline(item))
                i += 1
            cls = ' class="sbs-checklist" data-sbs-checklist' if checklist else ""
            out.append("<ul%s>\n%s\n</ul>" % (cls, "\n".join(items)))
            continue

        # ordered list
        if re.match(r"^\d+\.\s+", ln):
            items = []
            while i < n and re.match(r"^\d+\.\s+", lines[i]):
                items.append("<li>%s</li>" % inline(re.sub(r"^\d+\.\s+", "", lines[i])))
                i += 1
            out.append("<ol>\n%s\n</ol>" % "\n".join(items))
            continue

        # paragraph (soft-wrapped across lines until a blank or a block start)
        buf = []
        while i < n and lines[i].strip() and not re.match(
                r"^(#{1,4}\s|```|>\s|-\s|\d+\.\s|\|)", lines[i]):
            buf.append(lines[i].strip())
            i += 1
        out.append("<p>%s</p>" % inline(" ".join(buf)))

    return "\n\n".join(out), headings


def toc(headings):
    """Table of contents from the h2s, matching the guides' `.sbs-toc` markup."""
    h2 = [(hid, text) for lvl, hid, text in headings if lvl == 2]
    if len(h2) < 4:
        return ""
    li = "\n".join('    <li><a href="#%s">%s</a></li>' % (hid, inline(t)) for hid, t in h2)
    return ('<nav class="sbs-toc" aria-labelledby="toc-h">\n'
            '  <h2 id="toc-h">On this page</h2>\n  <ol>\n%s\n  </ol>\n</nav>' % li)


def render(path):
    md = io.open(path, encoding="utf-8").read()
    body, headings = convert(md)
    t = toc(headings)
    return (t + "\n\n" + body) if t else body


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("usage: md2html.py <file.md>")
    sys.stdout.write(render(sys.argv[1]))
