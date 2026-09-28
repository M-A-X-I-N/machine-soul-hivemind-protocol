# MSHP-DISC-B-090 — Implement Oh My Posh verification

## Description

Implement Oh My Posh verification as two explicit layers: whether the intended theme is usable by OMP, and whether a consuming shell actually selected that theme during startup.

Do not silently upgrade theme parse/render success into proof that a shell uses it.

## Requirements

- Add an application-native OMP config probe that parses/renders/exports the expected theme using a stable supported CLI surface and reports application evidence.
- Add runtime-state verification through controlled consuming-shell startup where OMP exposes a stable selected-theme/runtime value such as the effective theme path.
- Support relevant Bash, Zsh, Fish, and PowerShell consumers using the reusable controlled-process infrastructure from earlier verification tasks.
- Compare selected theme identity/path against the canonical resolved OMP configuration for the target host/account.
- Retain theme-usability and shell-selection observations separately in the assessment.
- When OMP is available but no supported consumer can prove selection, return the strongest application evidence rather than pretending runtime proof.
- When a consumer selects another theme, report not_effective with the evidence that proves the mismatch.
- Preserve target-account/session boundaries; sudo/SSH/another shell process does not inherit local prompt state automatically.
- Wire OMP VERIFY_CONFIG capability on supported platforms without application-ID branches in generic verification engines.
- Use ../MSHP-DISC-A/workspace/effective_configuration.md and existing SESSION_BOUNDARIES.md.

## Constraints / non-goals

- Do not modify shell startup files or the theme to insert a temporary test marker.
- Do not treat explicit --config rendering as proof that normal shell startup selects the theme.
- Do not require every shell consumer to be installed to verify theme usability.

## Acceptance criteria

- OMP config usability and actual consumer selection are independently observable in result data.
- Runtime evidence is reported only when a controlled consumer process proves selection.
- Wrong-theme and no-consumer cases are represented honestly.
- Existing shell initialization/session semantics are not weakened.

## Validation

- Test valid/invalid theme probe, expected selected theme, alternate selected theme, consumer unavailable, and multi-consumer evidence aggregation.
- Test at least one POSIX shell and PowerShell consumer path through CI-capable fixtures.
- Run full CI.
