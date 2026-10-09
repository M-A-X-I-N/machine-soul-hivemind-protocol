# MSHP-WINGET-A-030 — Design a Store-first WinGet package selection policy

## Description

Design how Machine-Soul should prefer an equivalent Microsoft Store package when safely available, while still invoking WinGet as its installation interface.

## Requirements

- Define app equivalence, Store listing/identity stability, licensing/account requirements, user/machine scope, offline availability, source trust, user override, fallback and provenance. Ensure compatibility with the frozen Store investigation.

## Constraints / non-goals

- Research only; do not thaw the WinGet block without explicit maintainer authorization; do not silently switch an already-owned non-Store install.

## Acceptance criteria

- A reviewed algorithm selects or safely declines a Store candidate with explicit reasons.

## Validation

- Cross-check against current WinGet and Microsoft Store documentation and supported real installation scenarios.
- Record research/validation and explicit unsafe ambiguities.
