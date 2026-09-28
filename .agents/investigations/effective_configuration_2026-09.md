# Effective configuration verification findings

Durable implementation notes distilled from MSHP-DISC-A-030.

The detailed source/research matrix remains in `autonomic_affairs/agent_tasks/MSHP-DISC-A/workspace/effective_configuration.md` until the block archives.

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
