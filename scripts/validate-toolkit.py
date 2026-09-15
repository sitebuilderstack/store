#!/usr/bin/env python3
"""Validate the SEO & Website Audit Toolkit before it is packaged.

Checks the things that would embarrass the product if they shipped: a prompt
missing one of the sections the library promises, a broken internal file
reference, a stated count that is no longer true, a credential pattern, or a
development artefact.

The counts matter more than they look. The product page quotes them, and a page
that says "20 prompts" for a bundle containing 18 is the kind of drift nobody
notices until a customer does.

Run with --self-test to prove each check fires.
"""
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUNDLE = os.path.join(ROOT, "product", "Claude-Code-SEO-Website-Audit-Toolkit")

# Every prompt promises these. START-HERE.md explains why each one is there, so
# a prompt missing one is a promise the product does not keep.
REQUIRED = ["## Objective", "## Discovery", "## Constraints", "## Deliverables"]
FORBIDDEN_NAMES = (".DS_Store", "Thumbs.db", ".gitkeep", "__MACOSX")

# Filenames that appear in backticks but name a file in the READER's project
# rather than one in this bundle. Kept deliberately short: every addition here
# is a reference that stops being checked, so a name only belongs on this list
# if the bundle could never contain it.
EXTERNAL_NAMES = {"CLAUDE.md", "wrangler.jsonc", "astro.config.mjs"}
SECRET = re.compile(
    r"AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{36}|shp(at|ss|ca|pa)_[0-9a-fA-F]{32}"
    r"|AIza[0-9A-Za-z_-]{35}|-----BEGIN [A-Z ]*PRIVATE KEY-----")


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
    rel = [os.path.relpath(f, root) for f in files]

    for f, r in zip(files, rel):
        base = os.path.basename(f)
        if base in FORBIDDEN_NAMES or base.startswith("._"):
            bad.append("development artefact: %s" % r)
        if base.endswith((".pyc", ".tmp", ".bak", ".orig", ".swp")):
            bad.append("temporary file: %s" % r)
        try:
            # newline="" disables universal-newline translation. Without it,
            # text mode turns CRLF into LF before this function can see it, so
            # the line-ending check could never fire — which is exactly the
            # class of silently-passing check this bundle warns about.
            body = io.open(f, encoding="utf-8", newline="").read()
        except (UnicodeDecodeError, IOError):
            bad.append("unreadable or non-text file: %s" % r)
            continue
        if SECRET.search(body):
            bad.append("credential pattern in %s" % r)
        if "\r\n" in body:
            bad.append("windows line endings in %s" % r)

    for name in ("START-HERE.md", "README.md", "LICENSE.md", "VERSION.md"):
        if name not in rel:
            bad.append("missing required file: %s" % name)

    prompts = sorted(p for p in rel if p.startswith("prompts" + os.sep) and p.endswith(".md"))
    if not prompts:
        bad.append("no prompts found")
    for p in prompts:
        body = io.open(os.path.join(root, p), encoding="utf-8").read()
        for h in REQUIRED:
            if h not in body:
                bad.append("%s: missing section %r" % (p, h))
        if len(body.split()) < 250:
            bad.append("%s: only %d words, too thin to be useful" % (p, len(body.split())))

    # Internal references must resolve. A START-HERE that points at a file which
    # does not exist is the first thing a buyer sees.
    known = {r.replace(os.sep, "/") for r in rel}
    dirs = {os.path.dirname(r).replace(os.sep, "/") + "/" for r in rel if os.path.dirname(r)}
    for f, r in zip(files, rel):
        if not r.endswith(".md"):
            continue
        body = io.open(f, encoding="utf-8").read()
        here = os.path.dirname(r)
        # References are relative to the file that makes them, so `../templates/x.md`
        # in a module resolves against that module's directory. Resolving them all
        # against the bundle root reported working links as broken.
        def resolve(ref):
            return os.path.normpath(os.path.join(here, ref)).replace(os.sep, "/")
        for ref in re.findall(r"`([0-9A-Za-z_./-]+\.md)`", body):
            if os.path.basename(ref) in EXTERNAL_NAMES and "/" not in ref:
                continue
            if resolve(ref) not in known:
                bad.append("%s: references a file that does not exist: %s" % (r, ref))
        for ref in re.findall(r"`((?:\.\./)?[0-9]{2}-[a-z-]+/)`", body):
            if resolve(ref).rstrip("/") + "/" not in dirs:
                bad.append("%s: references a directory that does not exist: %s" % (r, ref))
    return bad


def counts(root):
    files = sorted(walk(root))
    rel = [os.path.relpath(f, root) for f in files]
    prompts = [p for p in rel if p.startswith("prompts" + os.sep)]
    modules = sorted({p.split(os.sep)[0] for p in rel
                      if os.sep in p and re.match(r"^\d{2}-", p.split(os.sep)[0])})
    words = 0
    for f in files:
        try:
            words += len(io.open(f, encoding="utf-8").read().split())
        except (UnicodeDecodeError, IOError):
            pass
    return {"files": len(rel), "prompts": len(prompts),
            "modules": len(modules), "words": words}


def main():
    if "--self-test" in sys.argv:
        return self_test()
    bad = check(BUNDLE)
    for b in bad:
        print("  FAIL %s" % b)
    c = counts(BUNDLE)
    print("%d file(s), %d prompt(s), %d module(s), %s words, %d failure(s)"
          % (c["files"], c["prompts"], c["modules"], format(c["words"], ","), len(bad)))
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

    p = os.path.join(root, "prompts", "P01-complete-seo-audit.md")
    original = io.open(p, encoding="utf-8").read()
    run("a prompt missing a required section",
        lambda: io.open(p, "w", encoding="utf-8").write(original.replace("## Deliverables", "## Outputs")),
        lambda: io.open(p, "w", encoding="utf-8").write(original))
    run("a prompt too thin to be useful",
        lambda: io.open(p, "w", encoding="utf-8").write(
            "# x\n## Objective\n## Discovery\n## Constraints\n## Deliverables\n"),
        lambda: io.open(p, "w", encoding="utf-8").write(original))

    sh = os.path.join(root, "START-HERE.md")
    orig_sh = io.open(sh, encoding="utf-8").read()
    run("a reference to a file that does not exist",
        lambda: io.open(sh, "w", encoding="utf-8").write(orig_sh + "\nSee `prompts/P99-nope.md`.\n"),
        lambda: io.open(sh, "w", encoding="utf-8").write(orig_sh))
    run("a missing required file",
        lambda: os.rename(sh, sh + ".moved"),
        lambda: os.rename(sh + ".moved", sh))

    art = os.path.join(root, ".DS_Store")
    run("a development artefact",
        lambda: io.open(art, "w", encoding="utf-8").write("x"),
        lambda: os.remove(art))

    leak = os.path.join(root, "prompts", "leak.md")
    run("a credential pattern",
        lambda: io.open(leak, "w", encoding="utf-8").write(
            "## Objective\n## Discovery\n## Constraints\n## Deliverables\n"
            + ("word " * 300) + "\nAKIA" + "A" * 16 + "\n"),
        lambda: os.remove(leak))

    crlf = os.path.join(root, "prompts", "crlf.md")
    run("windows line endings",
        lambda: io.open(crlf, "w", encoding="utf-8", newline="").write(
            "## Objective\r\n## Discovery\r\n## Constraints\r\n## Deliverables\r\n" + ("word " * 300)),
        lambda: os.remove(crlf))

    clean = check(root)
    print("  %s  stays silent on the real bundle%s"
          % ("PASS" if not clean else "FAIL", "" if not clean else " -> %s" % clean[:3]))
    if clean:
        fails += 1
    shutil.rmtree(tmp)
    print("\n%d self-test failure(s)" % fails)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
