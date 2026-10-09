# MSHP-WINGET-A-040 — Implement Store-first selection through WinGet

## Description

After source-identity research and selection policy approval, add Store-priority discovery and safe exact WinGet source/package invocation.

## Requirements

- Do not mutate pre-existing install ownership; preserve explicit package scope, opt-outs, developer trust warnings, unique package identity and dry-run reporting; test account/licensing and unavailable-Store fallback.

## Constraints / non-goals

- Requires the preceding Store investigation and design, plus an explicit go-ahead for implementation through Dispatch; queuing does not authorize implementation.

## Acceptance criteria

- A candidate with suitable Store offering installs via winget's msstore source by default, with safe fallback or refusal.

## Validation

- Cross-check against current WinGet and Microsoft Store documentation and supported real installation scenarios.
- Record research/validation and explicit unsafe ambiguities.
