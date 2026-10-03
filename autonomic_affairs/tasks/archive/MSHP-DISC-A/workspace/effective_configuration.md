# Effective configuration verification investigation

Status: completed research output for MSHP-DISC-A-030.

This file preserves the application-by-application evidence map used by later DISC-A synthesis. It is workspace material, not the permanent architecture contract.

## Core distinction

There are at least three useful questions below "effective":

1. Did the application resolve/select the expected configuration location?
2. Did the application actually read/execute/parse that configuration?
3. Are the intended settings/behavior from that configuration observable?

A probe may prove one level without proving the next. Verification must report the evidence actually obtained.

Configuration validity is also separate from effectiveness. A JSON/YAML/script may parse correctly yet not be selected by the application.

## Evidence levels used by this investigation

- runtime: a controlled application process demonstrates that the expected config was executed/selected or that a setting produced by it is active.
- application: application-native introspection, rendering, or config diagnostics process the expected config.
- resolution: application rules plus observed target environment/path establish which config should be selected.
- convention: only documented/default placement supports the inference.
- none: no meaningful non-GUI verification is available.

These align with DISCOVERY_SEMANTICS.md.

## Shell startup tracing as a reusable strategy

Bash, Zsh, and Fish can potentially reach runtime-strength evidence without modifying the canonical configuration by tracing a controlled child shell startup.

### Bash

GNU Bash documents that an interactive non-login shell reads ~/.bashrc unless --norc is used, and --rcfile can override it.

A controlled verifier can:

- launch the same Bash executable/environment relevant to the target account;
- force interactive startup;
- enable xtrace before startup;
- configure PS4 to include source filename/line information;
- capture stderr;
- establish that commands from the expected ~/.bashrc path were executed.

Combined with structural check_config proving that ~/.bashrc is the Machine-Soul symlink, this is runtime evidence that the canonical file was consumed.

Use a negative control such as --norc when valuable. Avoid sourcing the file manually: explicit source proves only that the file can execute, not that normal startup selects it.

Source:
- https://www.gnu.org/software/bash/manual/html_node/Bash-Startup-Files

### Zsh

Zsh documents that interactive startup reads $ZDOTDIR/.zshrc (HOME is used when ZDOTDIR is unset), subject to the RCS/GLOBAL_RCS options.

A controlled interactive xtrace process can analogously capture startup execution and identify the expected .zshrc. Implementation should validate the exact trace/file-name format on supported Zsh versions rather than assuming Bash-compatible output.

Source:
- https://zsh.sourceforge.io/Doc/Release/Files.html

### Fish

Fish documents that user config is normally $XDG_CONFIG_HOME/fish/config.fish (default ~/.config/fish/config.fish) and that config files execute on shell startup.

Fish exposes fish_trace execution tracing, debug-output routing, --no-config, and startup profiling options. A controlled process can enable tracing before normal startup, capture startup execution, and compare against --no-config where useful.

Implementation must validate the strongest reliable way to identify the config.fish source path in trace/profile output for supported Fish versions. If exact source-path attribution is unavailable, fall back honestly to runtime-side-effect or resolution evidence rather than claiming runtime proof.

Sources:
- https://fishshell.com/docs/current/cmds/fish.html
- https://fishshell.com/docs/current/ (configuration language documentation)

### Windows POSIX compatibility shells

For Bash/Zsh/Fish on Windows, verification must run inside the same MSYS2/Cygwin-compatible environment used by destination resolution. A native Windows PATH lookup is not proof about the configured shell environment.

The same shell-trace concepts can be reused if the target shell version/environment supports them.

## PowerShell

PowerShell exposes $PROFILE and its CurrentUserCurrentHost path for the current host. Machine-Soul already resolves its destination by launching the declared PowerShell executable with -NoProfile and querying that value.

That gives strong resolution evidence, but not proof the profile executed.

Current Machine-Soul PowerShell configuration conditionally initializes Oh My Posh. Oh My Posh init scripts establish runtime state including the selected theme (commonly POSH_THEME). Therefore, when Oh My Posh is installed and MACHINE_SOUL is available, a controlled PowerShell process with profiles enabled can inspect the resulting OMP runtime state and compare the selected theme to the expected canonical theme path. That can provide runtime evidence for the current profile content.

If OMP is absent, the current profile intentionally has little observable behavior. In that case profile-path resolution remains the honest evidence level unless a future generic profile-execution marker or trace mechanism is adopted.

Important current caveat: PowerShellProfileDestination defaults to powershell.exe. Verification must use the same declared host/executable; pwsh and Windows PowerShell have different profile paths/semantics and must not be conflated.

Source:
- https://learn.microsoft.com/powershell/module/microsoft.powershell.core/about/about_profiles

## CMD

Microsoft documents that cmd.exe executes HKLM/HKCU Command Processor AutoRun values on startup unless /d disables AutoRun.

Machine-Soul's structural CMD check already verifies both the managed command-file link and the expected HKCU AutoRun command. That establishes strong deterministic resolution evidence.

Proving actual runtime execution requires an observable effect from the command file. The current cmdrc.cmd contains only @echo off plus a comment, so there is no stable Machine-Soul-specific marker to query generically.

Possible later implementation choices:
- accept resolution evidence as the strongest non-invasive baseline;
- add an intentionally harmless process-local verification marker to cmdrc and query it from a controlled child cmd;
- use a content-specific probe such as echo state, but that is brittle and should not become generic policy.

Do not mutate AutoRun during verification.

Source:
- https://learn.microsoft.com/windows-server/administration/windows-commands/cmd

## Oh My Posh

Oh My Posh does not use one global config automatically; the consuming shell's init command selects a config with --config.

Two distinct things can be verified:

1. The expected theme is usable by OMP: application-native commands such as print preview/config export can parse/render a specified config. This is application-level evidence.
2. A shell actually selected that config during startup: inspect OMP runtime state in a controlled shell (for example the selected POSH_THEME value generated by init) and/or the installed prompt function. This is runtime evidence and depends on the consuming shell.

Directly running oh-my-posh with --config proves the theme works, not that the user's shell is currently using it.

Therefore OMP verification should be able to return multiple observations: config parse/render validity and consumer-shell selection. The final semantic conclusion must not silently upgrade the former into the latter.

Sources:
- https://ohmyposh.dev/docs/installation/customize
- https://ohmyposh.dev/docs/installation/prompt
- https://ohmyposh.dev/docs/configuration/data

## Windows Terminal

Microsoft documents distinct settings.json locations for packaged stable/preview/canary and unpackaged distributions.

Machine-Soul currently resolves the stable packaged path when its package directory exists and otherwise the unpackaged path. This can provide deterministic resolution evidence when paired with installation/package discovery.

No documented headless wt.exe command was found that reports the active/effective settings object or the exact settings file consumed by a running instance. Launching the GUI merely to infer a setting is undesirable and still weak without UI inspection.

JSON/schema validation can prove syntax/schema quality but is config validity, not effectiveness.

Therefore the strongest planned baseline is resolution evidence:
- identify the actual Terminal distribution/package;
- resolve its documented settings path;
- structural check proves Machine-Soul owns that path.

Runtime verification should remain unsupported/indeterminate until a trustworthy native inspection interface exists. Do not add computer/UI automation just to manufacture a stronger answer.

Sources:
- https://learn.microsoft.com/windows/terminal/install
- https://learn.microsoft.com/windows/terminal/faq
- https://learn.microsoft.com/windows/terminal/command-line-arguments

## Contour

Contour documents its default config locations:
- Unix: ~/.config/contour/contour.yml with XDG_CONFIG_HOME respected;
- Windows: %LocalAppData%/contour/contour.yml.

It also supports explicit config selection and has application-native config/info commands; recent releases document contour info config and runtime config reload.

This gives at least deterministic resolution evidence and likely application-level parsing/introspection evidence through a headless Contour CLI command. The implementation task should experimentally verify the exact output/exit semantics of the installed supported version before promising runtime-level proof.

There is no need to launch the GUI merely to prove the default config path.

Sources:
- https://contour-terminal.org/configuration/
- https://contour-terminal.org/release-notes/

## Current application matrix

| Application | Platform(s) | Strongest practical baseline | Notes |
|---|---|---|---|
| Bash | Linux + Windows POSIX env | runtime | Controlled interactive startup trace can prove .bashrc execution. |
| Zsh | Linux + Windows POSIX env | runtime candidate | Controlled interactive xtrace should prove .zshrc; exact trace attribution needs implementation validation. |
| Fish | Linux + Windows POSIX env | runtime candidate | fish_trace/startup diagnostics can trace startup; exact file attribution needs validation. |
| PowerShell | Windows | runtime when OMP observable; otherwise resolution | Must use same declared PowerShell host/executable as destination resolution. |
| CMD | Windows | resolution | AutoRun startup contract + structural registry state; runtime needs a stable observable marker. |
| Oh My Posh | Windows/Linux | application + runtime via consuming shell | Direct render proves theme usability; shell runtime state proves actual selection. |
| Windows Terminal | Windows | resolution | No trustworthy headless effective-settings query found. |
| Contour | Windows/Linux | application candidate | Native config/info CLI likely validates/inspects config; exact semantics require implementation experiment. |

## Reusable verification strategy candidates

The evidence suggests reusable strategies rather than one custom verifier per app:

1. ShellStartupTrace
   - executable/host kind plus expected startup destination;
   - adapters for Bash/Zsh/Fish trace controls;
   - controlled target environment/account;
   - read-only subprocess, no config mutation.

2. ResolvedPathVerification
   - ask application/native resolver or use documented deterministic resolution plus observed environment;
   - useful for PowerShell profile path, Windows Terminal, Contour, and as fallback for shells.

3. ApplicationConfigProbe
   - app-native command parses/renders/inspects a specified config;
   - useful for Oh My Posh and likely Contour;
   - proves usability, not necessarily selection.

4. RuntimeStateProbe
   - controlled process emits a stable runtime value caused by startup config;
   - useful for PowerShell/OMP and potentially CMD if a future marker is adopted;
   - application-specific probe command/expected relation may be declared without embedding app IDs in generic engines.

A declaration may compose more than one verification observation. The assessment chooses the strongest supported evidence while retaining weaker observations.

## Side effects and isolation

Verification should be read-only with respect to persistent Machine-Soul/application state.

Launching a shell or CLI is a process side effect but acceptable when:
- it uses controlled non-interactive/private options where possible;
- it does not rewrite history/config/cache unnecessarily;
- unavoidable cache writes are identified and avoided where a no-write/private mode exists.

GUI launch is not required by the current investigation and should not be the default verification path.

## Applied but ineffective example

A correct symlink can coexist with ineffective config when:
- XDG_CONFIG_HOME/ZDOTDIR/HOME differs from Machine-Soul's assumed target environment;
- a different PowerShell host/profile is launched;
- Bash is invoked as sh or with --norc;
- cmd.exe uses /d;
- Windows Terminal distribution differs from the settings path selected;
- OMP init points to a different theme;
- a running application has not reloaded changed config.

verify_config exists precisely to represent these states separately from check_config.
