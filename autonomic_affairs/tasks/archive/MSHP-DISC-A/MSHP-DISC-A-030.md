# MSHP-DISC-A-030 — Investigate effective configuration

## Description

Investigate how Machine-Soul can verify that the intended configuration is actually being consumed/effective in each current application, rather than merely proving that the expected symlink/deployment exists.

The strength and mechanism of proof may vary substantially by application.

## Requirements

- Inventory every currently managed application and determine the strongest practical evidence available for effective configuration use.
- Consider evidence classes such as:
  - controlled runtime probe;
  - application-native resolved/effective-config query;
  - origin/source reporting;
  - deterministic documented resolution/path lookup;
  - indirect behavioral probe;
  - convention-only inference;
  - unsupported/unverifiable.
- For each application/platform combination, identify whether verification can be side-effect free, whether launching the application is required, and what environmental/session context matters.
- Distinguish proof that the intended file is selected from proof that expected settings from that file are effective.
- Identify cases where verification depends on shell/session startup boundaries, target account, environment variables, registry integration, include chains, application caches/reloads, or other runtime context.
- Determine which verification mechanisms can be reusable generic strategies and which require narrow application-specific hooks.
- Propose evidence/confidence semantics that honestly distinguish runtime proof from weaker resolution/convention inference.
- Preserve useful investigation artifacts in the DISC-A workspace and promote durable findings where appropriate.
- Produce concrete implementation recommendations for later synthesis rather than prematurely coding every probe.

## Constraints / non-goals

- Do not redefine structural `check_config` to mean runtime effectiveness.
- Do not claim certainty from documented path convention when runtime behavior can diverge.
- Do not add GUI/computer automation merely to force runtime verification where a safer/native inspection method exists.
- Do not require every application to support the same verification strength.
- Do not implement the entire verification framework in this task.

## Acceptance criteria

- Every current application has a documented strongest-feasible verification approach or an explicit explanation of why meaningful verification is unsupported.
- The investigation defines evidence-strength categories that can be represented by the shared discovery model.
- Reusable strategy candidates are separated from genuine application-specific probes.
- Runtime/session/account caveats are explicit.
- The investigation identifies concrete implementation seams/tasks to be synthesized by `MSHP-DISC-A-050`.

## Validation

- Walk representative applications with different styles of configuration resolution, including shells, Oh My Posh, CMD integration, Windows Terminal, and at least one ordinary file-config application.
- Ensure the proposed checks are read-only or clearly classify unavoidable side effects.
- Verify that an applied-but-ineffective scenario can be represented distinctly from structural deployment success.
