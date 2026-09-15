#!/usr/bin/env python3
"""Validate the skills shipped in the GitHub starter kit.

A skill that Claude Code silently ignores is worse than no skill, and the two
ways to get that are both mechanical: the file must be named SKILL.md inside a
directory named for the skill, and the opening `---` must be the file's first
line or the frontmatter is treated as content.

Checks the frontmatter fields against the documented set so a typo in a field
name is caught here rather than by a user wondering why nothing happens.

Usage: validate-skills.py
"""
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS = os.path.join(ROOT, "github", "claude-code-website-starter-kit", "skills")

# From code.claude.com/docs/en/skills — frontmatter reference.
KNOWN = {
    "name", "description", "when_to_use", "argument-hint", "arguments",
    "disable-model-invocation", "user-invocable", "allowed-tools",
    "disallowed-tools", "model", "effort", "context", "agent", "background",
    "hooks", "paths", "shell", "metadata", "license", "compatibility",
}
CAP = 1536          # description + when_to_use are truncated at this in the listing

fail = []


def main():
    if not os.path.isdir(SKILLS):
        raise SystemExit("no skills directory at %s" % SKILLS)
    names = sorted(d for d in os.listdir(SKILLS)
                   if os.path.isdir(os.path.join(SKILLS, d)))
    if not names:
        raise SystemExit("no skills found")

    for name in names:
        d = os.path.join(SKILLS, name)
        p = os.path.join(d, "SKILL.md")

        # The file must be SKILL.md, exactly, inside a directory named for the skill.
        entries = os.listdir(d)
        if "SKILL.md" not in entries:
            fail.append("%s: no SKILL.md (found %s)" % (name, entries))
            continue
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", name):
            fail.append("%s: directory name is not a usable slash-command name" % name)

        src = io.open(p, encoding="utf-8").read()

        # The opening --- must be the very first line or the whole block is content.
        if not src.startswith("---\n"):
            fail.append("%s: frontmatter does not start on line 1" % name)
            continue
        end = src.find("\n---\n", 3)
        if end == -1:
            fail.append("%s: frontmatter is not closed" % name)
            continue
        fm = src[4:end]

        keys, desc, when = [], "", ""
        for line in fm.split("\n"):
            m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
            if not m:
                continue
            k, v = m.group(1), m.group(2)
            keys.append(k)
            if k == "description":
                desc = v
            if k == "when_to_use":
                when = v

        for k in keys:
            if k not in KNOWN:
                fail.append("%s: unknown frontmatter field %r" % (name, k))
        if not desc:
            fail.append("%s: no description — Claude cannot tell when to use it" % name)
        if len(desc) + len(when) > CAP:
            fail.append("%s: description + when_to_use is %d chars, truncated at %d"
                        % (name, len(desc) + len(when), CAP))

        body = src[end + 5:]
        if len(body.split()) < 80:
            fail.append("%s: body is %d words — too thin to be worth loading"
                        % (name, len(body.split())))

        print("  %-20s desc=%-4d body=%-4d fields=%s"
              % (name, len(desc), len(body.split()), ",".join(keys)))

    print()
    print("%d skill(s), %d failure(s)" % (len(names), len(fail)))
    for f in fail:
        print("  FAIL", f)
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
