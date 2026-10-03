# MSHP-INST-A-030 — Investigate Linux scope extensibility

## Description

Investigate enough Linux installation-scope behavior to ensure the core scope model does not accidentally encode Windows-only assumptions.

This task is intentionally **not** an attempt to support or exhaustively research every Linux package manager. Apt is the current concrete Machine-Soul mutation backend; a small representative set of future user/system mechanisms is used only to test extensibility.

## Requirements

- Treat current Apt/dpkg behavior as the concrete baseline:
  - Apt package installation is effectively system/machine scoped;
  - sudo/root execution is an execution mechanism, not the installation scope itself;
  - current target-account-specific provenance storage may not accurately model a machine-wide package.
- Investigate representative future scope shapes sufficient to stress the model, including where authoritative documentation is available:
  - Flatpak user versus system installations;
  - Homebrew/Linuxbrew prefix/user ownership semantics;
  - pipx or another user-local application package mechanism.
- Add another representative mechanism only if it exposes a genuinely different scope concept needed to test the architecture.
- Identify which semantics are common and belong in the core model versus package-manager-specific:
  - requested scope;
  - inherent/fixed scope;
  - fallback/delegation;
  - actual observed scope;
  - install target/prefix;
  - execution privilege/identity;
  - uninstall selection.
- Determine how current Linux discovery evidence can or cannot distinguish user/system instances.
- Define the extension seam future package-manager strategies should implement without requiring those strategies to exist now.
- Record unsupported/not-yet-investigated managers as structured gaps in `MSHP-INST-SCOPE`, not speculative executable tasks.
- Ensure the model permits Windows/core implementation to proceed while the initiative remains OPEN for future Linux/package-manager coverage.

## Constraints / non-goals

- Do not implement Flatpak, Homebrew/Linuxbrew, pipx, or any new package-manager strategy.
- Do not attempt an exhaustive Linux package-manager matrix.
- Do not block Windows/core scope implementation on future Linux backend work.
- Do not conflate root/sudo execution with machine scope.
- Do not redesign distro support beyond what scope semantics require.
- Do not implement installation takeover.

## Acceptance criteria

- Apt's machine-scoped nature is represented honestly in the proposed model and provenance discussion.
- At least three meaningfully different Linux scope patterns are used to test the model's extensibility.
- Core versus backend-specific responsibilities are explicit.
- Future unsupported package managers can be represented as initiative gaps without incomplete zombie tasks.
- No Linux-specific requirement forces unnecessary complexity into the Windows-first implementation.

## Validation

- Walk representative Apt, Flatpak user/system, Homebrew/Linuxbrew, and user-local package scenarios.
- Verify the model can distinguish privilege/execution identity from installation scope.
- Verify future backend gaps are recorded in the initiative rather than silently forgotten or prematurely taskified.
