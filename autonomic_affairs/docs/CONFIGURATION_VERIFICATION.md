# Effective configuration verification

Effective configuration verification is separate from structural deployment checking.

`check_config` answers whether Machine-Soul has structurally applied the expected configuration at the expected native destination. The future `verify_config` operation answers how strongly Machine-Soul can establish that the application actually selects, reads, or reflects that configuration.

See [`DISCOVERY_SEMANTICS.md`](DISCOVERY_SEMANTICS.md) for the common discovery/assessment model.

## Evidence strength

Verification reports the strongest evidence actually obtained:

1. **runtime** — a controlled application process demonstrates startup/config behavior traceable to the intended configuration;
2. **application** — an application-native introspection/render/config interface processes or identifies the expected configuration;
3. **resolution** — native resolution rules plus observed environment/path facts establish which configuration should be selected;
4. **convention** — only documented/default placement supports the inference;
5. **none** — no meaningful verification evidence is available.

Evidence strength is independent of the semantic conclusion. A runtime probe may prove `not_effective`; a resolution-only probe may support `effective` at resolution strength.

## Reusable verification strategies

Prefer shared mechanisms over application-ID branches.

### Shell startup trace

Run a controlled child shell with its ordinary startup semantics while enabling native tracing/debug facilities. Attribute startup execution to the expected configuration path.

This is the preferred direction for Bash, Zsh, and Fish. Platform adapters may differ, but the semantic strategy is shared.

Do not manually source the configuration and call that proof of normal startup selection.

### Resolved path verification

Use an application-native resolver where available, or deterministic documented resolution rules combined with observed target-account/environment facts.

This is a useful baseline for PowerShell profile location, Windows Terminal settings, Contour, and shell fallback cases.

### Application config probe

Use an application-native command that parses, renders, exports, or otherwise inspects a specified configuration.

This proves that the application can consume the file, but not necessarily that normal startup selected it.

Oh My Posh and Contour are current candidates.

### Runtime state probe

Launch a controlled application/shell process and inspect a stable runtime value created by the configuration.

This can strengthen PowerShell/Oh My Posh verification and may support other applications when they expose a harmless observable marker.

A declaration may compose multiple observations. The assessment retains all useful evidence and reports the strongest justified conclusion.

## Current application ceiling

| Application | Strongest practical baseline | Important caveat |
|---|---|---|
| Bash | runtime | Use normal interactive startup tracing; `--norc`/alternate invocation can intentionally bypass config. |
| Zsh | runtime candidate | Exact trace/source attribution must be validated against supported versions. |
| Fish | runtime candidate | Native trace/debug facilities exist; exact config-file attribution must be validated. |
| PowerShell | runtime when current OMP initialization is observable; otherwise resolution | Verification must use the same PowerShell host/executable as destination resolution; Windows PowerShell and `pwsh` profiles differ. |
| CMD | resolution | AutoRun plus structural state is strong resolution evidence; current command file has no stable process-local marker for runtime proof. |
| Oh My Posh | application plus runtime through consuming shell | Explicit render/parse proves theme usability, not that a shell selected it. |
| Windows Terminal | resolution | No trustworthy headless effective-settings query is currently part of the supported design; do not use GUI automation to manufacture proof. |
| Contour | application candidate | Native config/info CLI looks promising; exact supported output/exit semantics need implementation validation. |

Windows Bash/Zsh/Fish verification must execute inside the same MSYS2/Cygwin-compatible environment used by destination resolution.

## Read-only rule

Verification is observational. It must not rewrite configuration, deployment metadata, package state, registry startup configuration, or other persistent Machine-Soul/application state merely to make verification easier.

Launching a controlled subprocess is acceptable. Prefer private/no-history/no-write modes where the application offers them.

A persistent verification marker may be introduced only as an intentional configuration/design decision, not injected temporarily by `verify_config`.

## Applied does not imply effective

A structurally correct deployment may still be ineffective because of environment or runtime differences, including:

- `XDG_CONFIG_HOME`, `ZDOTDIR`, or `HOME` selecting another location;
- launching a different PowerShell host/profile;
- Bash invoked as `sh` or with startup disabled;
- CMD invoked with `/d`;
- a different Windows Terminal distribution selecting another settings path;
- Oh My Posh initialization selecting another theme;
- a long-running application not yet reloading changed configuration.

That separation is the reason `verify_config` exists as a distinct future operation.
