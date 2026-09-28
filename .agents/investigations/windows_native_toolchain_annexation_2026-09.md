# Windows native toolchain annexation findings

Durable findings from `MSHP-DEV-B-020` (2026-09-28):

- Visual Studio 2026 is the current 18.x family; at research time the latest documented stable release is 18.10.1 (2026-09-15). VS 2026 uses the Stable/Insiders channel model and annual in-place releases, while major families such as VS 2022 and VS 2026 remain separately installable.
- Visual Studio/Build Tools **instance identity is not compiler identity**. Preserve setup instance ID + installation path + product/channel/version attributes.
- `vswhere` / Setup Configuration provide exact instance discovery plus installed package/component inventory. Build Tools must be included with `-products *`.
- Build Tools is a distinct product and is sufficient for native compilation; do not require a full IDE merely because a native compiler is needed.
- Workloads are mutable bundles. Exact component IDs are the safer durable ownership units for pinned native prerequisites.
- Visual Studio 2026 decouples MSVC servicing/versioning from the IDE. v145/14.50, 14.51, preview toolsets, older v143 components, and multiple Windows SDKs may legitimately coexist.
- “Latest” component identity and pinned versioned component identity represent different desired policies; never rewrite one into the other.
- Windows SDK version is independent of Windows OS and project-local SDK selection. Multiple installed SDKs are healthy state.
- Developer command shells / vcvars selection are derived session state. Host architecture, target architecture, compiler version, and SDK selection should not be conflated with installation identity.
- Visual Studio Installer supports exact `modify --add` / `--remove` component operations. `.vsconfig` import is additive and must not be treated as convergent deletion authority.
- Conservative ownership means Machine-Soul removes only exact components it previously owns inside an explicitly adopted instance; pre-existing/unowned components are preserved.
- Whole Visual Studio/Build Tools instance creation/removal remains preference-dependent because product, channel, licensing, install path, and adoption policy are not selected.
- Never use `InstallCleanup.exe` as ordinary reconciliation; Microsoft documents it as a last-resort destructive recovery tool.
- Runtime/package native-build backends should query for a satisfying toolchain and report missing prerequisites rather than silently installing arbitrary Visual Studio components.
- Promote `MSHP-DEV-B-025` for non-speculative instance/component discovery, prerequisite queries, explicit instance adoption, and conservative owned-component reconciliation.

Detailed research lives in `autonomic_affairs/agent_tasks/MSHP-DEV-B/workspace/windows_native_toolchain.md`.
