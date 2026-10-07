# Effective configuration verification

Effective configuration verification is separate from structural deployment checking.

`check_config` answers whether Machine-Soul has structurally applied the expected configuration at the expected native destination. `verify_config` answers how strongly Machine-Soul can establish that the application actually selects, reads, or reflects that configuration.

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


## First-class operation surface

`verify_config` is now a first-class atomic operation with the same direct/imported wrapper shape as every other Machine-Soul operation.

Every application exposes a `verify_config.py` wrapper. Platform capability remains explicit:

- `SUPPORTED` requires a declared `ConfigurationVerificationPlan`;
- `NOT_IMPLEMENTED` means verification is desired but no trustworthy plan exists yet;
- `UNSUPPORTED` means verification is intentionally inapplicable.

A supported plan may still produce an `indeterminate` assessment. That is an observed semantic result, not the same thing as missing implementation.

The shared engine maps assessments to stable operation codes:

- `config_effective`;
- `config_not_effective`;
- `verification_indeterminate`.

Structured evidence remains under `OperationResult.data["assessment"]`.


## Shell startup verification implementation

Bash, Zsh, and Fish now use the shared `ShellStartupVerification` declaration strategy on Linux and supported Windows POSIX compatibility environments.

### Bash

Machine-Soul runs a controlled interactive Bash startup with xtrace enabled and a `PS4` that includes `BASH_SOURCE` and line number. Runtime evidence is granted only when:

- ordinary startup trace names the expected `.bashrc`; and
- a matching `--norc` negative control does **not** name it.

This tests ordinary startup selection rather than manually sourcing the file.

### Zsh

Zsh uses the same semantic approach with native xtrace and `PS4=+%N:%i:`, paired with `-f` (NO_RCS) as the negative control. Runtime evidence requires expected `.zshrc` source attribution in ordinary startup and its absence when rc loading is disabled.

### Fish

Fish deliberately remains at **resolution** evidence.

The current native tracing/debug surfaces do not provide a sufficiently stable source-file attribution contract for Machine-Soul to claim that `config.fish` itself was observed executing. Verification therefore confirms the resolved default config path, executable presence, and whether the target config path exists, but does not label that evidence runtime-strength.

This is an intentional evidence ceiling, not an unfinished boolean check.

### Windows POSIX environments

Bash/Zsh trace matching translates the native Windows configuration destination back into the active compatibility environment's POSIX path with `cygpath -u`. The shell executable and translation tool are resolved from the same context PATH used by Windows POSIX discovery/configuration resolution.

Verification does not scan arbitrary native Windows shells and does not mutate shell config/history. POSIX runs direct history output to the null device where applicable.


## Native application verification implementation

### PowerShell

PowerShell verification uses the exact `PowerShellProfileDestination` resolver declared by the application. The resolver launches that declared host with `-NoProfile` and reads `$PROFILE.CurrentUserCurrentHost`; verification then reports whether that resolved profile path exists.

This is **resolution** evidence. It intentionally does not claim the profile executed. Oh My Posh runtime state may strengthen this in the separate OMP verification layer.

The current declaration uses `powershell.exe`; `pwsh.exe` discovery does not silently change which profile Machine-Soul configures or verifies.

### CMD

CMD verification compares the declared command-file destination to the current HKCU Command Processor `AutoRun` value and requires the command-file path to exist.

This is resolution evidence grounded in CMD's documented startup contract. Verification does not invoke `cmd.exe` with a temporary marker and does not mutate AutoRun.

### Windows Terminal

Windows Terminal verification uses the same `WindowsTerminalSettingsDestination` resolver as structural configuration. It distinguishes the packaged stable settings location when that package directory exists from the unpackaged settings location otherwise, and requires `wt.exe` to be discoverable before claiming a positive resolution result.

No GUI automation or headless-effective-settings fiction is used; the evidence ceiling remains **resolution**.

### Contour

Contour uses the application-native `contour info config` command against its ordinary resolved config environment.

Contour release notes document `contour info config` as a CLI command that inspects the config file and lists missing entries:
https://contour-terminal.org/release-notes/

A successful probe with the resolved config path present is **application** evidence. A missing config path is not-effective at resolution strength. A nonzero probe is **indeterminate** at application strength rather than automatically meaning the config is broken, because CLI/version failures can also produce nonzero status.


## Oh My Posh two-layer verification

Oh My Posh verification deliberately keeps two different observations separate.

### Theme usability

Machine-Soul resolves the canonical tracked OMP theme source through normal host/account precedence and invokes the OMP print-primary command with the canonical theme and the universal shell renderer.

A successful render is **application** evidence that OMP can consume the intended theme. It does not prove any shell selected that theme.

A clearly reported configuration/parse failure is not_effective at application strength. An otherwise unexplained nonzero CLI result is indeterminate, because CLI/version failure is not proof that the theme itself is invalid.

### Consumer-shell selection

For the current target account only, Machine-Soul may start controlled ordinary consumer shells and inspect the POSH_THEME runtime state produced by OMP initialization.

Supported consumer probes are Bash, Zsh, Fish, and Windows PowerShell where applicable. The probe:

- does not source a startup file manually;
- sets Machine-Soul host/account/repository context for the child process;
- reads a unique marker containing POSH_THEME;
- compares the selected theme with the **canonical resolved tracked source**, not the deployed OMP theme symlink;
- reports matching or mismatching selection as **runtime** evidence.

This canonical-source comparison is intentional because the tracked Machine-Soul shell profiles initialize OMP with paths under MACHINE_SOUL/assimilation/oh_my_posh.

If no supported consumer is installed, a successful theme render remains the strongest application evidence. If a consumer starts but exposes no POSH_THEME, that produces weaker indeterminate resolution evidence and does not erase a stronger successful application probe.

If one consumer selects the intended theme and another selects a different theme, the equal-strength runtime evidence conflicts and the overall verification result is indeterminate; the individual observations remain available.

Non-current target accounts are not impersonated for runtime probing. Theme usability may still be assessed against the target account's canonical configuration, but consumer startup is skipped.
