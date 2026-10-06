# Extending Machine-Soul v2

## Add a host-specific configuration variant

There is no central tracked host inventory.

1. Let Machine-Soul discover ordinary host/platform/account facts at runtime.
2. Add configuration under `assimilation_directives/<application>/hosts/<hostname>/...` only when that host genuinely needs a different canonical file.
3. Add account-specific files only for accounts explicitly targeted by a management operation.
4. Extend matrix validation where practical.
5. Update `autonomic_affairs/docs/SUPPORT_MATRIX.md` when the supported target set changes.

If a machine needs a genuinely non-discoverable local value, keep it in ignored machine-local state under `scratch/` rather than inventing a tracked host registry.

## Add an application

Create the canonical configuration under `assimilation_directives/<application>/` and the matching operational entry points under `annexation_procedures/<application>/`.

### Define canonical config

Prefer the least-specific location that is still correct: default/common, default/users/<account>, hosts/<host>/common, or hosts/<host>/users/<account>.

Do not duplicate files merely to satisfy a directory pattern.

### Identify native destinations

Document where the application expects each file. If the path or symlink semantics depend on a runtime such as MSYS2 versus Cygwin, model that distinction explicitly instead of guessing.

### Reuse the shared Python operation core

Generic operation behavior lives under `annexation_procedures/`.

Application declarations select reusable source/destination/install strategies; platform-neutral atomic wrappers call the shared dispatcher. Do not add a per-application Bash/PowerShell policy engine or hand-roll backup/state/account behavior.

Use a native process helper only when a demonstrated platform operation is materially safer or clearer outside Python, and make it obey the native-primitive protocol.

### Expose operations

Applications expose platform-neutral Python wrappers such as `apply_config.py`, `unapply_config.py`, and `check_config.py` directly under `annexation_procedures/<application>/`. The declared capability state, not platform-specific wrapper-file presence, determines support. Installation surfaces may additionally include `install.py`, `uninstall.py`, and `check_installed.py`.

Unsupported or unfinished operations should say so explicitly.

### Non-file native state

CMD is the initial example: startup integration uses a registry AutoRun value plus a symlinked tracked command file.

For similar applications, keep canonical content tracked as files where possible, preserve existing native state, verify ownership before removal, keep restoration metadata under scratch/, and restore prior state when safe.

### Test the lifecycle

At minimum exercise Check → Apply → Check → Apply again → Unapply → Check → Unapply again, plus app-specific conflict paths.

### Add installers separately

Choose an explicit platform/upstream-supported install mechanism. Never make config deployment depend on installation when the app may already exist. Never claim a pre-existing install as Machine-Soul-owned just because it was detected. Record owned installation provenance under scratch/state/install/.

## Add an account override

Add only the final file that differs under `assimilation_directives/<application>/hosts/<host>/users/<account>/`.

OMP root configs are the initial example.

## Persist discoveries

If support work required meaningful investigation, preserve reusable findings under .agents/. Promote human-relevant architecture to normal documentation too.