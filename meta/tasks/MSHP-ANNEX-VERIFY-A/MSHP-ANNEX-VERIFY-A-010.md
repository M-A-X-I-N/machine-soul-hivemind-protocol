# MSHP-ANNEX-VERIFY-A-010 — Investigate installation manifest origin expectations

## Description

Design provenance/expected-source checking when installers/manifests resolve download URLs unexpectedly, including exact WinGet identity and Contour's expected official GitHub release namespace.

## Requirements

- Determine authoritative data availability before install, redirect chains, URL allowlists, signatures/digests, publisher certificates, warning versus hard-failure policy, source substitutions and TOCTOU limitations.

## Constraints / non-goals

- Do not present hostname/prefix matching as cryptographic assurance; avoid breaking offline installs without a policy decision.

## Acceptance criteria

- A threat model and integration design state what can be checked and what cannot.

## Validation

- Inspect current source/architecture and authoritative references relevant to the task.
- Record reproducible findings or targeted validation evidence; explicitly flag untestable claims.
