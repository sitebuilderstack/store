#!/usr/bin/env python3
"""Validate the Conversion & Revenue Optimization Toolkit before packaging.

Checks the things that would embarrass this product specifically. Two of them
are unique to it and matter more than the structural checks:

  * A predicted percentage lift. The toolkit's central promise is that it will
    never claim a change will raise conversions by N%. If one slipped into a
    workflow, the product would be contradicting itself on its own core claim.
  * A manipulative tactic recommended rather than prohibited. The prohibition
    list appears throughout; a file that recommends a countdown timer would be
    doing the thing the product exists to refuse.

Both are checked by pattern, which means they are approximate. The patterns are
tuned to fire on the phrasing a model actually produces, and each is
control-tested in --self-test.

Run with --self-test to prove every check fires.
"""
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUNDLE = os.path.join(ROOT, "product",
                      "Claude-Code-Conversion-Revenue-Optimization-Toolkit")

# Every workflow promises these. START-HERE and the README both describe the
# shape, so a workflow missing one is a promise the product does not keep.
REQUIRED = ["## Goal", "## Common mistakes"]

# A workflow is a Markdown file in one of the numbered modules 01- to 12-.
# 13-templates holds fill-in documents, not workflows. This is the definition
# the build script and the product page both use; the two must not drift.
WORKFLOW_DIR = re.compile(r"^(0[1-9]|1[0-2])-[a-z-]+/[^/]+\.md$")

# Files whose shape is deliberately different — references, indexes and
# frameworks rather than run-this-prompt workflows. The section and mode checks
# do not apply to them. They are still counted as workflows above where they
# sit inside a module, because that is what a buyer is getting.
NOT_WORKFLOWS = {
    "START-HERE.md", "README.md", "LICENSE.md", "VERSION.md", "CHANGELOG.md",
    "PRODUCT-MANIFEST.md",
    "01-core/OPERATING-MODES.md", "01-core/FINDING-FORMAT.md",
    "01-core/PRIORITIZATION.md", "01-core/EVIDENCE-STANDARDS.md",
    "01-core/ETHICAL-BOUNDARIES.md", "01-core/GLOSSARY.md",
    "09-user-behaviour/QUALITATIVE-METHODS.md",
    "11-platforms/PLATFORM-SELECTION-NOTES.md",
    "08-experimentation/EXPERIMENT-FRAMEWORK.md",
    "claude-md/CRO-SECTION.md", "claude-md/EXAMPLE-CLAUDE-MD.md",
    "commands/COMMANDS.md",
    "examples/README.md",
}

FORBIDDEN_NAMES = (".DS_Store", "Thumbs.db", ".gitkeep", "__MACOSX")
EXTERNAL_NAMES = {"CLAUDE.md", "wrangler.jsonc", "astro.config.mjs",
                  "docs/measurement-plan.md", "docs/finding-log.md"}

SECRET = re.compile(
    r"AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{36}|shp(at|ss|ca|pa)_[0-9a-fA-F]{32}"
    r"|AIza[0-9A-Za-z_-]{35}|-----BEGIN [A-Z ]*PRIVATE KEY-----")

# A predicted lift. Matches "will increase conversions by 12%",
# "expect a 15% lift", "boost revenue by 20%" and the shapes around them.
# Deliberately narrow: the toolkit discusses percentages constantly (measured
# rates, MDEs, confidence intervals), so only forward-looking prediction
# phrasing is caught.
PREDICTED_LIFT = re.compile(
    r"(?:will|should|can|could|expect(?:\s+a)?|projected?(?:\s+to)?|estimated?"
    r"(?:\s+to)?)\s+(?:\w+\s+){0,3}?"
    r"(?:increase|improve|boost|lift|raise|grow)\s+(?:\w+\s+){0,3}?"
    r"by\s+(?:approximately\s+|around\s+|about\s+|roughly\s+)?\d+(?:\.\d+)?\s*%",
    re.IGNORECASE)

# A manipulative tactic in a recommending sentence rather than a prohibiting
# one. The tactic words appear legitimately throughout the toolkit inside
# prohibition lists, so the verb is what distinguishes the two.
RECOMMEND_VERB = (r"(?:add|use|implement|introduce|include|display|show|create|"
                  r"place|insert|enable|apply)")
DARK_PATTERN = re.compile(
    RECOMMEND_VERB + r"\s+(?:a\s+|an\s+|the\s+|some\s+)?(?:\w+\s+){0,2}?"
    r"(?:countdown timer|fake urgency|false urgency|artificial scarcity|"
    r"fake scarcity|urgency timer|scarcity indicator|scarcity message|"
    r"exit-intent popup|confirmshaming)",
    re.IGNORECASE)

# Every workflow declares a mode. The convention is the product's spine; a file
# without one has been written outside it.
MODE = re.compile(r"^> \*\*Mode: (AUDIT|PLAN|IMPLEMENT|VALIDATE)\*\*", re.M)

# Both patterns above fire on the toolkit's own prohibitions, because the
# clearest way to prohibit "add a countdown timer" is to write the phrase down.
# A match is only a defect if nothing in the run-up to it negates the sentence.
NEGATION = re.compile(
    r"\b(?:not|never|no|nor|avoid|refuse|prohibit\w*|exclude\w*|without|"
    r"instead of|rather than|cannot|can't|don't|doesn't|won't|stop)\b",
    re.IGNORECASE)


def negated(body, start):
    """True if the sentence leading up to `start` negates what follows.

    Looks back to the previous sentence boundary or line break, capped at 160
    characters. Anything further away is a different thought and should not
    excuse the match.
    """
    window = body[max(0, start - 160):start]
    window = re.split(r"[.!?\n]", window)[-1]
    if NEGATION.search(window):
        return True
    # A prohibition often introduces its example on the previous line:
    #   Do not say:
    #     "this will increase revenue by 7%"
    prev = body[max(0, start - 160):start].rsplit("\n", 2)
    if len(prev) > 1 and NEGATION.search(prev[-2]):
        return True
    return False


def walk(root):
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if not d.startswith(".")]
        for fn in fns:
            yield os.path.join(dp, fn)


def check(root):
    bad = []
    if not os.path.isdir(root):
        return ["bundle directory missing: %s" % root]

    files = sorted(walk(root))
    rel = [os.path.relpath(f, root).replace(os.sep, "/") for f in files]

    bodies = {}
    for f, r in zip(files, rel):
        base = os.path.basename(f)
        if base in FORBIDDEN_NAMES or base.startswith("._"):
            bad.append("development artefact: %s" % r)
        if base.endswith((".pyc", ".tmp", ".bak", ".orig", ".swp")):
            bad.append("temporary file: %s" % r)
        try:
            # newline="" disables universal-newline translation, without which
            # text mode converts CRLF to LF before the check can see it.
            body = io.open(f, encoding="utf-8", newline="").read()
        except (UnicodeDecodeError, IOError):
            bad.append("unreadable or non-text file: %s" % r)
            continue
        bodies[r] = body
        if SECRET.search(body):
            bad.append("credential pattern in %s" % r)
        if "\r\n" in body:
            bad.append("windows line endings in %s" % r)

        for m in PREDICTED_LIFT.finditer(body):
            if not negated(body, m.start()):
                bad.append("%s: predicted percentage lift: %r" % (r, m.group(0)))
        for m in DARK_PATTERN.finditer(body):
            if not negated(body, m.start()):
                bad.append("%s: recommends a prohibited tactic: %r" % (r, m.group(0)))

    for name in ("START-HERE.md", "README.md", "LICENSE.md", "VERSION.md",
                 "CHANGELOG.md"):
        if name not in rel:
            bad.append("missing required file: %s" % name)

    workflows = [r for r in rel if WORKFLOW_DIR.match(r)]
    if len(workflows) < 60:
        bad.append("only %d workflow(s); the product promises substantially more"
                   % len(workflows))
    checked = [r for r in workflows if r not in NOT_WORKFLOWS]
    for r in checked:
        body = bodies.get(r, "")
        for h in REQUIRED:
            if h not in body:
                bad.append("%s: missing section %r" % (r, h))
        if not MODE.search(body):
            bad.append("%s: no mode declared" % r)
        if len(body.split()) < 400:
            bad.append("%s: only %d words, too thin to be useful"
                       % (r, len(body.split())))

    # The command library's stated count must be true. The product page quotes
    # it, and a page saying 68 for a library of 61 is the kind of drift nobody
    # notices until a customer does.
    commands = 0
    for r, body in bodies.items():
        if r.startswith("commands/") and r != "commands/COMMANDS.md":
            commands += len(re.findall(r"^## C-\d+", body, re.M))
    index = bodies.get("commands/COMMANDS.md", "")
    for claim in re.findall(r"(\d+) commands", index):
        if int(claim) != commands:
            bad.append("commands/COMMANDS.md claims %s commands; %d exist"
                       % (claim, commands))
    if commands < 50:
        bad.append("only %d commands; the product promises at least 50" % commands)
    ids = []
    for r, body in bodies.items():
        if r.startswith("commands/"):
            ids += re.findall(r"^## (C-\d+)", body, re.M)
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    if dupes:
        bad.append("duplicate command ids: %s" % ", ".join(dupes))

    # Internal references must resolve. A START-HERE pointing at a file that
    # does not exist is the first thing a buyer sees.
    known = set(rel)
    dirs = {os.path.dirname(r) + "/" for r in rel if os.path.dirname(r)}
    for r, body in bodies.items():
        if not r.endswith(".md"):
            continue
        here = os.path.dirname(r)

        def resolve(ref):
            return os.path.normpath(os.path.join(here, ref)).replace(os.sep, "/")

        for ref in re.findall(r"`([0-9A-Za-z_./-]+\.md)`", body):
            if ref in EXTERNAL_NAMES or (
                    os.path.basename(ref) in EXTERNAL_NAMES and "/" not in ref):
                continue
            if resolve(ref) not in known and ref not in known:
                bad.append("%s: references a file that does not exist: %s" % (r, ref))
        for ref in re.findall(r"`((?:\.\./)?(?:[0-9]{2}-[a-z-]+|commands|examples|claude-md)/)`", body):
            if resolve(ref).rstrip("/") + "/" not in dirs and ref not in dirs:
                bad.append("%s: references a directory that does not exist: %s" % (r, ref))
    return bad


def counts(root):
    files = sorted(walk(root))
    rel = [os.path.relpath(f, root).replace(os.sep, "/") for f in files]
    modules = sorted({r.split("/")[0] for r in rel
                      if "/" in r and re.match(r"^\d{2}-", r.split("/")[0])})
    commands = 0
    words = 0
    for f, r in zip(files, rel):
        try:
            body = io.open(f, encoding="utf-8").read()
        except (UnicodeDecodeError, IOError):
            continue
        words += len(body.split())
        if r.startswith("commands/") and r != "commands/COMMANDS.md":
            commands += len(re.findall(r"^## C-\d+", body, re.M))
    workflows = [r for r in rel if WORKFLOW_DIR.match(r)]
    templates = [r for r in rel if r.startswith("13-templates/")]
    examples = [r for r in rel if r.startswith("examples/")
                and not r.endswith("README.md")]
    return {"files": len(rel), "modules": len(modules), "commands": commands,
            "workflows": len(workflows), "templates": len(templates),
            "examples": len(examples), "words": words}


def main():
    if "--self-test" in sys.argv:
        return self_test()
    bad = check(BUNDLE)
    for b in bad:
        print("  FAIL %s" % b)
    c = counts(BUNDLE)
    print("%d file(s), %d module(s), %d workflow(s), %d command(s), %d "
          "template(s), %d example(s), %s words, %d failure(s)"
          % (c["files"], c["modules"], c["workflows"], c["commands"],
             c["templates"], c["examples"], format(c["words"], ","), len(bad)))
    return 1 if bad else 0


def self_test():
    import shutil
    import tempfile
    tmp = tempfile.mkdtemp()
    root = os.path.join(tmp, "kit")
    shutil.copytree(BUNDLE, root)
    fails = 0

    def run(name, mutate, restore=None):
        nonlocal fails
        mutate()
        found = check(root)
        ok = bool(found)
        print("  %s  detects: %s" % ("PASS" if ok else "FAIL", name))
        if not ok:
            fails += 1
        if restore:
            restore()

    w = os.path.join(root, "02-page-audits", "HOMEPAGE-AUDIT.md")
    original = io.open(w, encoding="utf-8").read()
    write = lambda p, s: io.open(p, "w", encoding="utf-8").write(s)
    restore = lambda: write(w, original)

    run("a workflow missing a required section",
        lambda: write(w, original.replace("## Common mistakes", "## Gotchas")), restore)
    run("a workflow with no mode declared",
        lambda: write(w, original.replace("> **Mode: AUDIT**", "Analysis only.")), restore)
    run("a workflow too thin to be useful",
        lambda: write(w, "# x\n\n> **Mode: AUDIT**\n\n## Goal\n\n## Common mistakes\n"), restore)
    run("a predicted percentage lift",
        lambda: write(w, original + "\nThis change will increase conversions by 12%.\n"), restore)
    run("a prediction phrased as an expectation",
        lambda: write(w, original + "\nExpect a lift of 15% within a month.\n"
                                    "\nYou should improve revenue by 20% here.\n"), restore)
    run("a recommended countdown timer",
        lambda: write(w, original + "\nAdd a countdown timer to the product page.\n"), restore)
    run("a recommended scarcity indicator",
        lambda: write(w, original + "\nImplement a low stock scarcity indicator.\n"), restore)
    # The negation guard must not be a blanket excuse: a prohibition earlier in
    # the file cannot license a recommendation later in it.
    run("a recommendation later in a file that also prohibits it",
        lambda: write(w, original
                      + "\nDo not add a countdown timer anywhere on the site.\n"
                      + ("filler " * 60) + "\n\nAdd a countdown timer above the price.\n"),
        restore)

    sh = os.path.join(root, "START-HERE.md")
    orig_sh = io.open(sh, encoding="utf-8").read()
    run("a reference to a file that does not exist",
        lambda: write(sh, orig_sh + "\nSee `01-core/NOPE.md`.\n"),
        lambda: write(sh, orig_sh))
    run("a reference to a directory that does not exist",
        lambda: write(sh, orig_sh + "\nSee `99-nope/`.\n"),
        lambda: write(sh, orig_sh))
    run("a missing required file",
        lambda: os.rename(sh, sh + ".moved"),
        lambda: os.rename(sh + ".moved", sh))

    idx = os.path.join(root, "commands", "COMMANDS.md")
    orig_idx = io.open(idx, encoding="utf-8").read()
    run("a command count that is no longer true",
        lambda: write(idx, orig_idx.replace("68 commands", "94 commands")),
        lambda: write(idx, orig_idx))

    dup = os.path.join(root, "commands", "10-DUP.md")
    run("a duplicate command id",
        lambda: write(dup, "# x\n\n## C-01 · duplicate\n\n```\nx\n```\n"),
        lambda: os.remove(dup))

    art = os.path.join(root, ".DS_Store")
    run("a development artefact", lambda: write(art, "x"), lambda: os.remove(art))

    leak = os.path.join(root, "commands", "leak.md")
    run("a credential pattern",
        lambda: write(leak, "# x\n\n## C-99 · x\n\nAKIA" + "A" * 16 + "\n"),
        lambda: os.remove(leak))

    crlf = os.path.join(root, "commands", "crlf.md")
    run("windows line endings",
        lambda: io.open(crlf, "w", encoding="utf-8", newline="").write(
            "# x\r\n\r\n## C-98 · x\r\n"),
        lambda: os.remove(crlf))

    clean = check(root)
    print("  %s  stays silent on the real bundle%s"
          % ("PASS" if not clean else "FAIL",
             "" if not clean else " -> %s" % clean[:5]))
    if clean:
        fails += 1
    shutil.rmtree(tmp)
    print("\n%d self-test failure(s)" % fails)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
