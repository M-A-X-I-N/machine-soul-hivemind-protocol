# Extending Machine-Soul v2

## Add a host

1. Add hosts/<hostname>.env.
2. Declare host, platform, OS family, and relevant accounts.
3. Add only configs that genuinely differ for that host.
4. Extend matrix validation where practical.
5. Update collective_affairs/docs/SUPPORT_MATRIX.md.

Keep host facts declarative instead of scattering raw hostname checks through shared configuration-deployment runtime code.

## Add an application

Create the canonical configuration under `assimilation_directives/<application>/` and the matching operational entry points under `annexation_procedures/<application>/`.

### Define canonical config

Prefer the least-specific location that is still correct: default/common, default/users/<account>, hosts/<host>/common, or hosts/<host>/users/<account>.

Do not duplicate files merely to satisfy a directory pattern.

### Identify native destinations

Document where the application expects each file. If the path or symlink semantics depend on a runtime such as MSYS2 versus Cygwin, model that distinction explicitly instead of guessing.

### Reuse shared deployment primitives

Linux shared runtime lives under accumulated_instruments/configuration_deployment/linux/. Windows shared runtime lives under accumulated_instruments/configuration_deployment/windows/.

Application adapters should resolve application identity, tracked source, and native destination, then delegate symlink/backup/state behavior to the shared runtime.

Do not hand-roll backup behavior unless the application genuinely has extra non-file native state.

### Expose operations

Configured targets normally provide `apply_config`, `unapply_config`, and `check_config` under `annexation_procedures/<application>/<platform>/`. Safe installation support may additionally provide install and uninstall.

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