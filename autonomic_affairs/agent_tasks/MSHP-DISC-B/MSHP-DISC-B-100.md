# MSHP-DISC-B-100 — Integrate discovery status

## Description

Compose the three independent discovery questions into one useful orchestrator/status surface after their individual engines are proven:

- installation existence/provenance;
- structural configuration deployment;
- effective configuration verification.

Keep the underlying atomic operations independent even though the human view presents them together.

## Requirements

- Add a read-only broad-manager status workflow that invokes CHECK_INSTALLED, CHECK_CONFIG, and VERIFY_CONFIG for each applicable discovered application.
- Present the three dimensions separately; do not collapse them into one health boolean or score.
- Human output should make preferred/foreign installation, Machine-Soul ownership, structural applied state, effective conclusion, and evidence strength understandable without dumping raw JSON.
- Machine-readable output must preserve full assessment/result data for all three operations.
- Treat unsupported/not-implemented dimensions as explicit information rather than hiding the application or failing the whole status view.
- Preserve multiple/ambiguous installation candidates in machine output and summarize them honestly for humans.
- Keep existing mutating workflows and safety behavior unchanged.
- Validate representative combinations from DISCOVERY_SEMANTICS.md, including foreign-but-effective, applied-but-ineffective, absent-but-config-staged, ambiguous installation, and unverifiable runtime.
- Update support matrix, interactive orchestration docs, extension guidance, and agent memory for the completed discovery architecture.
- Distill any remaining durable DISC-A workspace conclusions before later archival; leave raw historical research in the workspace.
- Do not implement the separate installation-takeover reminder.

## Constraints / non-goals

- Do not invent an overall good/bad score.
- Do not make status mutate packages, config, registry, or Machine-Soul state.
- Do not hide uncertainty to make output cleaner.
- Do not fold the three atomic operations back into one engine.

## Acceptance criteria

- One manager status workflow answers all three questions per application while retaining independent semantics.
- Direct atomic wrappers remain usable and produce the same underlying results as orchestration.
- Human and JSON output both expose uncertainty/evidence/provenance honestly.
- Existing apply/install workflows remain green.
- The DISC-B implementation can be understood from durable docs without depending on raw DISC-A research.

## Validation

- Add orchestrator tests for mixed result statuses/capabilities and representative three-dimension scenarios.
- Validate direct wrapper versus orchestrated result parity.
- Run Linux, Windows, Windows POSIX, installation, configuration, fresh-clone, and full CI.


## Notes

Completed with the read-only broad-manager `status` workflow, grouped human and JSON presentation, representative mixed-state contract tests, and durable documentation/memory closure for the DISC-A/DISC-B architecture.

The implementation preserves direct-wrapper parity: `check_installed`, `check_config`, and `verify_config` remain independent atomic operations and their original `OperationResult` payloads are retained by status orchestration.

Installation takeover remains a separate non-executable reminder.
