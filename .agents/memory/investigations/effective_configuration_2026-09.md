# Effective configuration verification findings

Durable implementation notes distilled from MSHP-DISC-A-030.

The detailed source/research matrix is preserved in `autonomic_affairs/tasks/archive/MSHP-DISC-A/workspace/effective_configuration.md`.

## Reusable strategy direction

Do not create one bespoke verifier per application by default. The investigation supports four shared strategy families:

- ShellStartupTrace
- ResolvedPathVerification
- ApplicationConfigProbe
- RuntimeStateProbe

Applications may compose several observations. Evidence strength is runtime > application-native > resolution > convention > none, but semantic truth is separate from evidence level.

## Implementation experiments still required

Before committing to specific command parsing, validate:

- Zsh trace output reliably attributes executed startup commands to the expected `.zshrc`;
- Fish trace/debug/profile output can reliably attribute startup execution to `config.fish`, otherwise downgrade to weaker evidence;
- Contour's supported config/info command and exact output/exit semantics on relevant versions;
- Oh My Posh runtime state used to identify the selected theme across the consuming shells we support;
- PowerShell verification uses the exact host selected by `PowerShellProfileDestination`; do not conflate `powershell.exe` and `pwsh`.

## Known evidence ceilings

- CMD currently tops out at resolution evidence without adding a deliberate harmless runtime marker to the tracked command file.
- Windows Terminal currently tops out at resolution evidence; no GUI automation should be introduced just to claim stronger verification.
- Explicitly rendering/parsing an Oh My Posh theme is application evidence only; shell startup state is needed to prove selection.
- Manually sourcing a shell config is not proof that ordinary startup would select it.

The human-facing contract is `autonomic_affairs/docs/CONFIGURATION_VERIFICATION.md`.


## Implemented shell verification — MSHP-DISC-B-070

The reusable `ShellStartupVerification` strategy is now wired for Bash, Zsh, and Fish on Linux and the supported Windows POSIX environment.

Durable evidence rules:

- Bash runtime proof requires ordinary `-i -x` startup attribution to the expected path plus a `--norc` negative control.
- Zsh runtime proof uses source-aware xtrace with `%N/%i` plus `-f` as the NO_RCS negative control.
- Fish remains resolution-strength intentionally; do not upgrade it to runtime evidence unless a supported Fish interface can attribute startup execution to the exact `config.fish` source path.
- On Windows, translate the declared native destination back into the active POSIX path before trace matching and resolve all tools from the same compatibility-environment PATH.
- Missing executable, non-current target account, translation failure, or failed trace produces indeterminate/resolution evidence rather than a false not-effective result.
- Do not replace normal startup with explicit `source`/manual config execution in future tests.


## Implemented native verification — MSHP-DISC-B-080

Reusable strategies now cover:

- `ResolvedPathVerification` — deterministic application/native destination resolution plus path presence;
- `CmdAutoRunVerification` — HKCU Command Processor AutoRun contract without mutation;
- `ApplicationConfigProbe` — read-only application-native config inspection commands.

Current evidence ceilings:

- PowerShell: resolution, using the exact declared `PowerShellProfileDestination` host. Do not substitute pwsh merely because installation discovery found it.
- CMD: resolution from exact expected AutoRun plus command-file existence.
- Windows Terminal: resolution only; packaged-stable versus unpackaged path selection stays in the shared destination resolver. Do not add GUI automation for stronger evidence.
- Contour: application evidence only when `contour info config` succeeds with the ordinary config path present. Nonzero probe is indeterminate, not automatically not-effective.

Contour's CLI command is documented in upstream release notes (0.5.0 and later):
https://contour-terminal.org/release-notes/


## Implemented Oh My Posh verification — MSHP-DISC-B-090

OMP verification is now a dedicated reusable strategy type, OhMyPoshVerification, rather than application-ID branches in the generic engine.

Durable rules:

- Application evidence uses the OMP print-primary command against the canonical source.
- The expected runtime theme is the canonical source selected by resolve_source, **not** the OMP deployment destination. Existing Bash/Zsh/Fish/PowerShell Machine-Soul startup configs pass the tracked assimilation/oh_my_posh theme path directly to oh-my-posh init.
- Runtime consumer probes inspect POSH_THEME after ordinary controlled startup. Matching selection is runtime-effective; an explicit different selected theme is runtime-not-effective.
- Missing consumer executables do not create stronger uncertainty than a valid application-level theme probe.
- A consumer that runs but exposes no POSH_THEME contributes indeterminate resolution evidence only.
- Conflicting equal-strength consumer observations intentionally produce an indeterminate overall assessment while preserving each consumer's evidence.
- Non-current target accounts skip consumer startup; Machine-Soul does not impersonate them merely to obtain verification.
- Do not replace this with explicit oh-my-posh init in the verifier. Explicit init would prove only that OMP can initialize, not that normal shell startup selected the theme.
