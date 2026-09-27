# Legacy implementation migration map

This document is the V2-57 audit of the working Bash/PowerShell implementation. Its purpose is to tell V2-58 and later migration work where each existing responsibility belongs in the Python/declarative architecture, and which behavior should disappear instead of being ported.

The current shell implementation remains a behavioral reference until parity is proven. Classification here is about the **destination architecture**, not permission to delete working code early.

## Classification vocabulary

Each legacy responsibility is classified as one of:

1. **generic Python policy/helper** — portable shared Machine-Soul behavior;
2. **declarative application data** — application identity, config leaf, capability, destination/install strategy selection;
3. **reusable strategy/handler** — generic executable behavior selected by a declaration;
4. **application-specific hook** — genuinely exceptional procedural behavior behind the normal operation contract;
5. **platform-specific Python helper / possible native primitive** — platform-specific mechanics kept below policy; native process code is used only if Python is materially worse or unsafe;
6. **delete / do not port** — legacy scaffolding, duplication, stale assumptions, or workaround superseded by the new architecture.

## Shared configuration runtimes

### Repository-root discovery

Legacy locations:

- `configuration_deployment/linux/machine_soul.sh::ms_root`;
- `configuration_deployment/windows/MachineSoul.psm1::Get-MachineSoulRoot`;
- ad-hoc root calculations in nearly every app adapter;
- Linux/Windows-POSIX dispatcher ancestry searches.

Destination: **generic Python policy/helper** under discovery/runtime-root support.

Rules:

- honor an explicit repository root only after validating the stable `.machine_soul_root` marker;
- otherwise walk ancestors from the executing/importing repository path;
- expose one resolved repository root through `OperationContext`;
- wrappers and applications do not independently rediscover it.

Delete:

- the stale Linux `app_config.sh` search for root `TASKS.md`;
- repeated `../../..` root calculations after Python wrappers use the standardized repository bootstrap.

### Host discovery

Legacy:

- `ms_host`;
- `Get-MachineSoulHost`;
- repeated `hostname`, `COMPUTERNAME`, and environment-fallback logic in app adapters.

Destination: **generic Python discovery helper**.

Keep an explicit override only for tests/unusual environments. Remove concrete-machine fallback names.

Host identity selects real host-specific canonical configuration variants; it is not a tracked inventory.

### Account discovery and cross-account identity

Legacy:

- `ms_account`;
- `Get-MachineSoulAccount`;
- `MACHINE_SOUL_ACCOUNT` overrides;
- direct `id -un` / `USERNAME` use in app scripts.

Destination: **generic Python target-account resolver + OperationContext**, according to `ACCOUNT_TARGETING.md`.

The target account is resolved before app logic. Execution/elevation identity remains separate.

Legacy environment overrides may survive only as migration/test compatibility inputs until the new common account option/context is fully in use.

### Scratch/state paths and path hashing

Legacy:

- `ms_scratch_path` / `Get-MachineSoulScratchPath`;
- SHA-256 destination hashes;
- host/account/application state-key layout.

Destination: **generic Python state helper** using `pathlib`, `hashlib`, and resolved context.

Preserve state lineage and collision safety. Do not duplicate state-path construction in install/config engines.

### Symlink inspection/classification

Legacy:

- `ms_abs_path_no_follow`, `ms_resolve_link_target`, `ms_link_info`, `ms_config_state`, `ms_link_points_to_expected`;
- equivalent PowerShell link helpers.

Destination: **generic Python config/filesystem helper**.

Preserve the critical rule already learned by the legacy implementation: canonicalize the destination parent without dereferencing the final symlink object.

The semantic states `APPLIED`, `NOT_APPLIED`, `CONFLICT`, `WRONG_TARGET`, and `BROKEN` become stable result codes/statuses rather than shell text protocols.

No current evidence requires a native primitive merely to inspect file symlinks.

### Apply / backup / verification / rollback

Legacy:

- `ms_apply_file`;
- `Invoke-MachineSoulApplyFile`;
- duplicate shell/PowerShell conflict prompting and filesystem mutation.

Destination: **generic Python apply-config engine + state/backup helpers**.

Required behavior to preserve:

- validate canonical source;
- classify destination before mutation;
- prompt or honor explicit conflict policy;
- preserve file/symlink prior state;
- create a file-level managed symlink;
- verify after creation;
- roll back on intermediate failure where safe;
- record state only after verified success;
- idempotent already-applied result;
- never silently destroy unmanaged state.

Presentation/prompt plumbing belongs above the core engine; the engine receives resolved conflict policy/interaction decisions through common operation interfaces.

### Checkout-relocation repair

Legacy:

- special stale-owned-link repair branches in both shared runtimes;
- relocation tests preserving original backup lineage.

Destination: **generic Python config/state policy**, not app-specific code.

State continues to store a repository-relative logical source plus enough prior-target/applied-target information to prove ownership of the stale link before repair.

This behavior is part of Apply, not a separate user operation.

### Unapply / restore

Legacy:

- `ms_unapply_file`;
- `Invoke-MachineSoulUnapplyFile`.

Destination: **generic Python unapply-config engine + shared state helper**.

Preserve:

- ownership verification before unlink;
- conflict instead of overwriting externally changed state;
- restoration of displaced file or symlink when recorded and safe;
- relocation-safe backup resolution;
- idempotent not-applied behavior.

### Legacy state serialization

Linux currently writes a bespoke line-oriented/base64 state format; Windows writes JSON.

Destination: **one Python-owned versioned state schema**, preferably JSON using stdlib serialization.

Migration requirement:

- V2-58 must either read legacy state while the migration is in progress or provide an explicit safe transition path before legacy runtimes are retired;
- do not strand backups/restoration lineage created by the old runtime.

Delete once safely superseded:

- Bash base64 field parser/encoder;
- separate PowerShell JSON writer;
- platform-specific state schema divergence.

## Dispatchers and generic app adapters

### Linux `app_config.sh`

Current role:

- root discovery;
- source path assembly;
- action switch;
- calls shared Bash apply/check/unapply.

Destination: **delete after Python dispatcher/engines + atomic wrappers are proven**.

Its generic action switch becomes the Python `perform_operation(...)` dispatcher. Its source construction belongs to configuration resolution.

Do not port the obsolete `TASKS.md` root sentinel.

### Windows `invoke_app_config.ps1`

Current role mirrors Linux generic dispatch.

Destination: **delete after Python engines/wrappers are proven**.

Its semantic responsibilities become Python operation dispatch; it is not a justified native primitive.

### Windows POSIX `posix_config.sh`

Current role:

- verify `cygpath` and `powershell.exe`;
- translate compatibility-shell paths to Windows paths;
- propagate POSIX-shell `HOME`/host/account context;
- invoke PowerShell symlink runtime.

Destination: **reusable Windows/POSIX environment compatibility helper/strategy**, with final mechanics chosen during V2-58/V2-60.

Audit conclusion:

- the *need to respect the compatibility shell's home/config location* is real;
- the current Bash → `cygpath` → PowerShell chain is implementation scaffolding, not a desired architecture;
- prefer Python/environment/path handling first;
- use `cygpath` as an external platform helper only if required for correct Windows/POSIX path translation;
- do not retain PowerShell merely because the old adapter happened to use it.

## Per-application configuration adapters

### Common host-specific source selection

Most adapters construct:

```text
assimilation_directives/<app>/hosts/<host>/common/<leaf>
```

Destination: **generic Python configuration resolver + declarative `ConfigurationFile.source_leaf`**.

Host/account precedence is shared policy. Application code should not concatenate host paths.

### Account-specific source precedence

Legacy Oh My Posh adapters explicitly try:

1. host/user/account leaf;
2. host/common leaf.

Destination: **generic Python configuration resolution policy**, not OMP-specific code.

This is evidence that the shared resolver must implement the documented host/account precedence directly.

### Home-relative destinations

Legacy examples:

- shell rc files;
- Fish config;
- Contour config;
- Oh My Posh theme.

Destination: **declarative `HomeRelativeDestination` + shared destination handler**.

Use the resolved logical target account home/config environment. Do not use the execution process's `HOME` after elevation to infer the target.

### LocalAppData-relative Windows destinations

Legacy examples include Contour and Oh My Posh.

Destination: **reusable declarative destination strategy**, e.g. a target-account/local-app-data-relative descriptor interpreted by shared Windows discovery.

Do not leave raw `LOCALAPPDATA` path construction duplicated in application wrappers.

### PowerShell profile destination

Legacy PowerShell adapter uses `$PROFILE.CurrentUserCurrentHost`.

Classification: **reusable/specialized destination strategy or narrow application hook**, not generic wrapper logic.

Preferred first implementation: a declarative destination descriptor interpreted by a Windows/PowerShell-aware shared resolver. Use custom application code only if the profile selection cannot be represented cleanly.

### Windows Terminal packaged versus unpackaged destination

Legacy adapter probes packaged LocalState, otherwise uses the unpackaged path.

Classification: **reusable/specialized destination strategy**.

The declaration describes the Windows Terminal destination strategy; a shared handler performs deterministic path selection. This is not orchestration logic and not a native primitive.

### Windows compatibility-shell destinations

Fish/Bash/Zsh on Windows intentionally use the POSIX shell's `HOME`.

Classification: **reusable compatibility-environment destination strategy/platform helper**.

The existing pure-PowerShell `NOT_IMPLEMENTED` stubs are **delete/do not port** once platform-neutral Python wrappers and declarations accurately express support.

### CMD file + AutoRun registry integration

CMD is the one substantial config exception.

Current behavior combines:

- managed symlinked `cmdrc.cmd`;
- HKCU `Command Processor\AutoRun` inspection;
- prior-value preservation;
- transactional link + registry mutation;
- ownership/conflict detection;
- restore on unapply.

Classification:

- file-link lifecycle → **generic Python config engine**;
- Windows registry access → **platform-specific Python helper** using stdlib `winreg` where sufficient;
- coordinated CMD AutoRun behavior → initially **application-specific config hook/composite strategy** reusing the generic link engine and registry helper.

Do not create a PowerShell native primitive merely because the legacy code used PowerShell. Promote the CMD behavior into a reusable registry/startup strategy later only if another application demonstrates the same need.

## Installation lifecycle

### Fish on Linux

Legacy behavior:

- detect `fish` executable;
- distinguish managed/unmanaged via state;
- require `apt-get`;
- support dry-run;
- run apt directly as root or narrowly through sudo;
- verify executable after install/remove;
- record/remove install provenance.

Classification:

- package identity `fish` → **declarative `AptPackage` data**;
- package availability/install/remove/verify → **shared AptPackage strategy handler**;
- dry-run/elevation/result semantics → **generic Python operation policy**;
- provenance → **generic Python install-state helper**.

Delete per-app shell installer once parity exists.

### Oh My Posh on Windows

Legacy behavior uses exact WinGet ID/source and verifies the executable.

Classification:

- package ID/source/executable verification → **declarative WingetPackage/verification data**;
- WinGet invocation → **shared WinGet strategy handler**;
- install ownership/provenance → **generic install-state helper**.

PowerShell implementation is not itself a required native primitive.

### Unmanaged installations

Legacy Fish/OMP behavior deliberately refuses to claim/remove pre-existing installs.

Destination: **generic Python install/uninstall policy**.

This is a project safety invariant, not app-specific logic.

### Install state format

Current Linux text state and Windows JSON state differ.

Destination: **one versioned Python JSON provenance schema** shared across install strategies.

As with config state, preserve/read legacy provenance until transition is safe.

## Native primitives: audit conclusion

V2-57 found **no current legacy script that must automatically survive as a native primitive solely because it is written in Bash/PowerShell**.

Likely Python-first replacements exist for:

- file/symlink inspection and mutation;
- hashing/state serialization;
- apt/WinGet subprocess invocation;
- Windows registry access via `winreg`;
- environment/root/account discovery.

Potential native/process boundaries that remain legitimate to investigate during implementation:

- narrow elevation helpers if privilege transitions cannot be expressed safely through direct subprocess invocation;
- `cygpath` or equivalent compatibility-environment translation where Windows/POSIX path semantics genuinely require it;
- any Windows symlink edge case proven by tests to be materially safer through a native helper.

The rule from V2-55 still applies: native primitives are earned by a demonstrated platform need, not grandfathered from legacy language choice.

## Legacy wrappers and duplicate platform trees

Current app trees contain:

- platform-specific `manage_config.*`;
- tiny apply/check/unapply forwarding files;
- Windows pure-PowerShell NOT_IMPLEMENTED stubs for compatibility-shell apps.

Destination: **platform-neutral Python atomic wrappers** defined by `ATOMIC_WRAPPERS.md`.

Delete after parity:

- forwarding shell/PowerShell wrappers;
- separate Windows/Linux wrapper implementations for the same semantic operation;
- explicit NOT_IMPLEMENTED script stubs whose capability state is already declarative.

Platform capability remains in `PlatformDeclaration`, not file presence.

## Tests: preserve behavior, migrate harness

### Shared config lifecycle tests

Preserve as Python contract tests:

- destination classification;
- prompt/abort/backup-and-replace policy;
- backup/restore;
- wrong/broken symlinks;
- manual external replacement conflict;
- partial failure/rollback behavior;
- idempotency.

Legacy shell/PowerShell harnesses remain until Python parity; then retire them.

### Application operation tests

Preserve the lifecycle contract:

```text
Check → Apply → Check → Apply again → Unapply → Check
```

Future tests import wrapper `run(...)` functions and separately test direct executable wrappers.

Concrete machine/account identities in old fixtures are test data, not architecture. New tests should prefer synthetic/generic fixture identities.

### Install dry-run/provenance tests

Preserve:

- managed versus unmanaged distinction;
- dry-run has no persistent side effects;
- exact declared package strategy;
- provenance only after verified success;
- unmanaged uninstall refusal.

Move primary testing to strategy/engine contract tests with subprocess runners mocked/faked where appropriate.

### Account/session boundary tests

Preserve the core semantics:

- logical target account is independent of execution identity;
- elevated helpers do not silently retarget config;
- account-specific resolution is deterministic;
- actual sudo/root boundary testing remains valuable on Linux CI where available.

Replace environment-variable account overrides with the new explicit account-context API except where testing legacy compatibility itself.

### Relocation tests

Preserve exactly:

- stale owned link detected after checkout move;
- Apply repairs only when state proves ownership/logical source continuity;
- original backup lineage survives relocation;
- Unapply restores the pre-Machine-Soul object.

Rewrite against Python config/state APIs before retiring legacy tests.

### Windows POSIX adapter tests

Preserve the behavioral requirement that compatibility-shell config destinations resolve correctly.

Do not preserve the current Bash → `cygpath` → PowerShell chain as the thing being tested. Tests should target the final compatibility strategy/helper selected during implementation.

## Migration order implied by the audit

V2-58 should implement shared core in this order unless tests reveal a better dependency sequence:

1. repository/platform/host/target-account discovery and `OperationContext`;
2. common state schema/readers, including safe legacy-state compatibility;
3. filesystem/symlink classification;
4. config source/destination resolution;
5. apply/check/unapply engines with backup/restore/relocation safety;
6. install provenance;
7. Apt and WinGet strategy handlers;
8. Windows destination/platform helpers, including registry support needed by CMD;
9. compatibility-shell path/environment helper only if still needed;
10. common dispatcher and primitive invocation integration.

V2-59 then supplies real declarations using these capabilities. V2-60 introduces uniform wrappers. V2-61 removes/reduces native legacy code only after behavioral parity. V2-62 builds the broad manager over those wrappers. V2-63 completes parity/cleanup.

## Deletion checklist after parity

Do not delete these early. Once replacement behavior is proven, retire:

- `accumulated_instruments/configuration_deployment/linux/app_config.sh`;
- policy-heavy portions/all of `machine_soul.sh`;
- `invoke_app_config.ps1`;
- policy-heavy portions/all of `MachineSoul.psm1`;
- duplicated per-app `manage_config.sh/.ps1` files;
- tiny apply/check/unapply forwarding scripts;
- pure-PowerShell `NOT_IMPLEMENTED` compatibility-shell stubs;
- per-app Fish/OMP install/uninstall scripts after shared strategy parity;
- bespoke Linux base64 state parser/writer;
- duplicated Windows/Linux state schemas;
- concrete-machine fallback defaults embedded in adapters;
- legacy `TASKS.md` root-discovery logic;
- the Bash→PowerShell compatibility chain if the final Python path no longer needs it.

## V2-58 handoff rule

V2-58 must not treat this map as a mandate to delete old code while replacing it.

Implement Python core alongside the working legacy path, prove behavior through contract tests, and leave destructive retirement to V2-61/V2-63 checkpoints after parity is demonstrated.
