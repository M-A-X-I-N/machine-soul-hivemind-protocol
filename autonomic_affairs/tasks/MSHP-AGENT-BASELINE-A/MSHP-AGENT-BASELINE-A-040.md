# MSHP-AGENT-BASELINE-A-040 — Investigate ongoing synchronization and baseline evolution

## Description

Investigate the hard part that template repositories do not automatically solve: evolving already-existing repositories as the generic agent baseline changes.

## Requirements

- Research practical synchronization/update models applicable to file-based repository baselines, including updater scripts/tools, pull-request automation, bots/Actions, generated/vendor/subtree-like approaches, patch/migration systems, manifests/version markers, and other relevant mechanisms.
- Determine how each approach detects local modifications versus baseline-owned content.
- Determine conflict behavior, reviewability, rollback/recovery, provenance, and whether updates can be applied incrementally rather than replacing whole files.
- Research ways a repository can declare which baseline version/schema it currently implements.
- Research whether GitHub template provenance or APIs provide useful metadata for update discovery; do not assume they do.
- Consider both newly templated repositories and pre-existing repositories that never originated from the template.
- Identify models that permit human-reviewed migrations rather than silent overwrites.
- Preserve findings only in MSHP.

## Constraints / non-goals

- Read-only inspection of other repositories is permitted when relevant to research. Do not modify any repository other than MSHP; within MSHP, writes are limited to normal task bookkeeping and storing relevant research/findings.
- Research only. Do not build an updater, bot, Action, migration tool, or synchronization prototype.
- Do not modify `M-A-X-I-N/template` or any consumer repository.
- Do not recommend destructive overwrite-based synchronization unless conflict/local-override safety is convincingly addressed.
- Do not assume Git history rewriting is acceptable.

## Acceptance criteria

- The research explains credible ways an existing repository could learn about and adopt baseline changes.
- Local-modification/conflict semantics are explicit for each serious candidate.
- The analysis covers repositories both created from the template and adopted later.

## Validation

- Check that every serious synchronization candidate has documented ownership, conflict, rollback, and review semantics.
- Separate proven platform capabilities from proposed higher-level workflows.
