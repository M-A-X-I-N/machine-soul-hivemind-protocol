# MSHP-DISC-B-080 — Implement native config verification

## Description

Implement honest resolution/application-native effective-configuration verification for PowerShell, CMD, Windows Terminal, and Contour, respecting the evidence ceiling discovered for each application.

## Requirements

- PowerShell: verify the same declared host/executable and CurrentUserCurrentHost profile resolution used by destination resolution; do not conflate Windows PowerShell with pwsh.
- PowerShell may report resolution evidence without OMP; OMP-specific runtime evidence lands in MSHP-DISC-B-090.
- CMD: use the documented AutoRun startup contract plus current structural registry/path facts as resolution evidence without mutating AutoRun.
- Do not introduce a persistent CMD marker merely for this task; runtime evidence remains unavailable unless separately justified later.
- Windows Terminal: identify the relevant installed distribution/package and resolve its documented settings path, using installation discovery from MSHP-DISC-B-040 where useful.
- Keep Windows Terminal at resolution evidence unless a trustworthy native effective-settings interface is proven; do not use GUI automation.
- Contour: experimentally validate its supported config/info command and exact output/exit semantics, then use application-native evidence where it truly proves config processing/selection; otherwise retain resolution evidence.
- Wire application declarations/capabilities to VERIFY_CONFIG with reusable ResolvedPathVerification or ApplicationConfigProbe-style strategies rather than application-ID branches.
- Keep config syntax/parse validity distinct from actual config selection.
- Use ../MSHP-DISC-A/workspace/effective_configuration.md for the evidence map.

## Constraints / non-goals

- Do not launch GUI applications merely to obtain verification.
- Do not modify registry/config files to create evidence.
- Do not claim application/runtime evidence when only a documented path rule was established.
- Do not implement OMP consumer-shell verification here.

## Acceptance criteria

- PowerShell, CMD, Windows Terminal, and Contour expose the strongest honestly supported verification evidence.
- Each result clearly communicates evidence level and semantic conclusion.
- Windows Terminal can remain resolution-only without being misrepresented as unsupported if meaningful resolution verification succeeds.
- Contour's application-level claim is backed by verified command behavior, not assumed documentation wording.

## Validation

- Add unit tests for expected path, alternate host/distribution, disabled CMD AutoRun, absent application, and native probe failure.
- Add an experimentally grounded Contour probe test fixture.
- Run Windows and Linux relevant application tests plus full CI.
