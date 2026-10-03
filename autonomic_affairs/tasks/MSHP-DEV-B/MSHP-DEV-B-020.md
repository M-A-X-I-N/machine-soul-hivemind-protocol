# MSHP-DEV-B-020 — Investigate Windows native toolchain annexation

## Description

Deeply investigate the Windows-native C/C++ toolchain stack that current maintainer workloads already depend on: Visual Studio/Build Tools, MSVC toolsets, Windows SDKs, workloads/components, discovery, and side-by-side lifecycle. Produce implementation tasks only where current supported automation is strong enough.

## Requirements

- Research current supported Visual Studio/Build Tools installation and automation surfaces, including Visual Studio Installer/command-line mechanisms and WinGet where relevant.
- Map `vswhere`/installer discovery, exact instance identity, product/channel/version identity, and ownership limits.
- Map side-by-side MSVC toolset versions, Windows SDK versions, workloads/components, host/target architectures, and native multi-targeting.
- Distinguish IDE installation from Build Tools-only installation and component/toolset lifecycle.
- Identify selected/default/environment activation semantics such as developer command environments without treating shell activation as installed-state identity.
- Investigate deterministic add/remove/update behavior for workloads/components and whether exact rollback/uninstall is safe enough for Machine-Soul ownership.
- Map interactions with Unreal/SML/native package builds only as consumers; do not make project-specific build configuration global desired state.
- Update MSHP-DEV-ENV with findings and create bounded follow-on implementation tasks only where evidence supports them.

## Constraints / non-goals

- Do not install or modify Visual Studio, Build Tools, SDKs, or workloads.
- Do not assume the latest toolset is always the desired one.
- Do not collapse Visual Studio instance, MSVC toolset, and Windows SDK into one version field.
- Do not invent desired workloads/components for the maintainer.
- Do not make native-build prerequisites silently install themselves from pip/npm/LuaRocks operations.

## Acceptance criteria

- Exact coexistence/identity and automation boundaries are documented.
- The investigation can represent multiple desired toolsets/SDKs without ambiguity.
- Safe implementation work is taskified only if supported by current tooling.
- Deferred or preference-dependent state remains initiative context rather than zombie tasks.

## Validation

- Use current Microsoft documentation and supported tooling.
- Walk Build Tools-only, full IDE, multiple toolset, multiple SDK, and exact-component removal scenarios.
