# MSHP-DISC-A-010 — Define discovery semantics

## Description

Define the conceptual discovery/check model before expanding implementation.

Machine-Soul must distinguish at least three different questions:

1. is the application installed, and what can be learned about that installation?
2. is the intended Machine-Soul configuration structurally applied at the expected destination?
3. is the application actually consuming/effectively using that configuration?

These questions may share discovery machinery but must not collapse into one ambiguous `Check` concept.

## Requirements

- Define separate semantics for installation discovery, applied-configuration checking, and effective-configuration verification.
- Define what facts belong to raw discovery versus what conclusions belong to operation/check interpretation.
- Define shared result/value semantics rich enough to represent uncertainty, partial knowledge, unsupported verification, conflicting evidence, and multiple discovered candidates without reducing every answer to a boolean.
- Preserve the distinction between installation mechanism/provenance and Machine-Soul ownership.
- Preserve the distinction between structurally applied configuration and effective/runtime configuration.
- Define how confidence/evidence strength should be represented when a check cannot provide equally strong proof on every application/platform.
- Define the generic-library versus application-specific extension boundary for discovery and verification.
- Decide whether effective verification warrants a separate atomic operation name such as `verify_config` rather than overloading `check_config`.
- Use tracked task workspace material when useful for intermediate design notes that later DISC-A tasks need.
- Promote durable architecture conclusions into appropriate human-facing docs and/or `.agents/`.

## Constraints / non-goals

- Do not implement broad installation-provenance discovery in this task.
- Do not implement application-specific effective-config probes in this task.
- Do not force every application into the same evidence strength or pretend unsupported verification is failure.
- Do not design installation takeover behavior here; only ensure the discovery model does not preclude later takeover work.
- Do not create a declarative mini-language for arbitrary checks.

## Acceptance criteria

- The repository has an explicit model for installed, structurally applied, and effectively used configuration as separate concepts.
- Future tasks can tell which layer owns raw facts, semantic interpretation, application-specific probing, and presentation.
- The model can express uncertainty/unsupported/ambiguous states without lying through booleans.
- Installation mechanism and Machine-Soul ownership are explicitly orthogonal.
- The decision on whether effective verification is a distinct atomic operation is durable and discoverable.

## Validation

- Walk representative scenarios including preferred managed install, preferred unmanaged install, foreign install, absent install, ambiguous multiple installs, applied-but-not-effective config, effective config with foreign installation, and unverifiable config effectiveness.
- Verify none of the three concepts implies another accidentally.
- Review current operation/result architecture to ensure the proposed model fits without application-ID conditionals in generic engines.
