# Maintenance prompts for Claude Code

Two prompts, kept separate on purpose: the inspection prompt is read-only and
produces a report; the remediation prompt takes ONE finding from that report
and fixes it with a rollback. Never merge them. The audit that also fixes
things leaves no record of what was wrong.

## 1. Weekly read-only inspection

    Read-only weekly inspection of this website's repository and configuration.
    Do not edit any file, run any command that writes, deploys, installs or
    updates, or submit any form. If a fix seems obvious, write it as a
    recommendation.

    Check and report, with evidence (file:line, command output, URL) for each:
    1. Dependencies: list declared versions vs latest available where a lockfile
       or manifest exists; flag security advisories the tooling reports
       (npm audit --omit=dev, composer audit, pip-audit — run read-only).
    2. Configuration drift: compare deploy/redirect/robots/security-header
       configuration in the repository with docs/BASELINE.md (or say the
       baseline does not exist).
    3. Forms: identify each form's delivery path and every place a failure would
       be silent. Do not submit anything; say that delivery must be tested by
       hand with a marked submission.
    4. Certificates and DNS: report what the repository/config says about
       renewal (certbot timers, platform-managed) — not whether it worked; that
       is checked from outside.
    5. Backup and rollback: report what the repository says exists (scripts,
       workflows, documented steps) and what evidence of a successful RESTORE
       exists. "Job succeeded" is not restore evidence.
    6. Output: a table (check · observed · pass/fail/unknown · evidence),
       then findings by priority with a recommended change and its rollback,
       then "Not checked" with reasons. Do not invent numbers.

## 2. Remediation of one finding

    Fix exactly one finding from the inspection report: [PASTE THE FINDING].

    Before changing anything: state the change, the files it touches, how it
    will be verified, and how it will be rolled back. Then make the change on
    a branch (or the development theme / staging), run the project's checks,
    and show the output. Do not touch anything outside the finding. Do not
    deploy. End with: what changed, what was verified, what was not.
