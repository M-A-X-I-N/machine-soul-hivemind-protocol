# MSHP-DISC-B-070 — Implement shell startup verification

## Description

Implement reusable read-only startup verification for Bash, Zsh, and Fish by observing controlled ordinary shell startup rather than manually sourcing the configured file.

Support Linux and the Windows POSIX compatibility environment established by MSHP-DISC-B-050.

## Requirements

- Implement a reusable shell-startup verification strategy with shell-specific adapters where trace/debug controls genuinely differ.
- Bash: validate a controlled interactive startup/xtrace technique that attributes execution to the expected .bashrc, with a negative control such as startup-disabled mode where useful.
- Zsh: experimentally validate exact xtrace/source attribution for supported versions before treating it as runtime evidence.
- Fish: experimentally validate fish_trace/debug/profile behavior and exact config.fish attribution; downgrade honestly to weaker evidence if exact runtime attribution cannot be proven.
- Run verification in the target account/environment used by configuration resolution.
- On Windows, run inside the same supported MSYS2/Cygwin-style environment selected for the configured shell.
- Keep subprocess verification persistent-state read-only and avoid history/cache writes where native options permit.
- Retain all observations and evidence strength in the shared verification assessment.
- Wire Bash, Zsh, and Fish declarations to VERIFY_CONFIG with the strongest verified strategy per platform.
- Never treat manual source/config execution as proof of normal startup selection.
- Use ../MSHP-DISC-A/workspace/effective_configuration.md for experiment targets and evidence ceilings.

## Constraints / non-goals

- Do not modify shell configs to insert temporary markers.
- Do not start interactive user-facing terminal windows.
- Do not claim runtime evidence if the trace cannot identify normal startup consumption.
- Do not implement Oh My Posh theme verification; that is MSHP-DISC-B-090.

## Acceptance criteria

- Bash has runtime-strength normal-startup evidence where supported.
- Zsh/Fish report runtime evidence only after exact attribution is validated; otherwise their evidence level is downgraded explicitly.
- Linux and Windows POSIX environment semantics remain distinct and correct.
- Verification leaves persistent config/deployment state unchanged.

## Validation

- Unit/integration-test positive startup consumption, startup-disabled/alternate-path negative cases, environment overrides, and backend/process failures.
- Verify repeated verification does not mutate tracked configs, symlinks, or Machine-Soul state.
- Run Linux and Windows POSIX tests plus full CI.
