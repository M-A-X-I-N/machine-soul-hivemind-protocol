# Installation scope semantic investigation

Status: completed design output for `MSHP-INST-A-010`.

## Scenario walk

| Scenario | Required interpretation |
|---|---|
| Current account + user-scoped install | Target and execution identity coincide; provenance belongs to that host/account and records actual user scope. |
| Current account + machine-scoped install | Target account requested it, but provenance ownership belongs to the host/machine installation. Elevation may change execution identity only. |
| Non-current target + user-scoped request | Refuse unless the backend has a proven target-user/impersonation mechanism. Do not install for the executor and record it for the target. |
| Same package at user + machine scope | Retain separate candidates. Scope + subject/native identity must select the exact managed instance. |
| Package-manager default changes | No effect on fixed/required Machine-Soul scope; ambient defaults are not policy. |
| Legacy provenance lacks scope | Treat as unknown/unreconciled. Do not authorize uninstall until safely matched/upgraded. |
| Discovered actual scope differs from required scope | Installation verification fails; do not write authoritative ownership provenance for the mismatched candidate. |

## Model pressure points for later tasks

- A mutation-side scope policy type is separate from discovery-side `InstallationScope`.
- `InstallState` needs a schema migration and actual/requested scope fields.
- Current `install_state_path()` account nesting is wrong for machine-scoped ownership.
- `_is_installed()`/legacy mutation checks are too coarse when dual-scope candidates can coexist; scoped implementation should use discovery assessments rather than one boolean.
- WinGet needs explicit scope in both mutation and exact uninstall targeting.
- Apt can declare fixed machine scope without adding user-scope machinery.
- Execution identity detection/enforcement is needed before user-scope mutation can safely claim cross-account support.

## Deliberately unresolved until platform research

- Exact WinGet behavior if `--scope` conflicts with available installers/manifest scope.
- Whether WinGet uninstall `--scope` sufficiently disambiguates dual-scope instances in all relevant package forms.
- Exact Windows discovery evidence that proves user versus machine scope for correlated WinGet packages.
- Whether a future `PREFERRED`+controlled-fallback policy is justified by a real backend.
- Exact state-file path/schema migration mechanics.
