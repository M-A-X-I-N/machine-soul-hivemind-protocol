# MSHP-DEV-B-025 — Implement Windows native toolchain discovery and component ownership

## Description

Implement conservative Windows Visual Studio/Build Tools native-toolchain annexation for existing explicitly adopted setup instances. Provide exact instance/component discovery, native prerequisite queries, and ownership-aware add/remove reconciliation without choosing or silently provisioning a Visual Studio product instance.

## Requirements

- Discover modern Visual Studio and Build Tools instances through the installed `vswhere` / Visual Studio Setup surface.
- Include all products so Build Tools-only instances are visible.
- Normalize and preserve setup instance ID, installation path, product ID, installation version, channel/update identity where available, completeness/launchability state, and installed package/component IDs.
- Model exact installed native capabilities separately from the containing Visual Studio instance, including multiple simultaneous MSVC toolset component IDs and Windows SDK components.
- Provide prerequisite queries capable of answering whether a complete candidate satisfies explicit component/toolset, host/target architecture, and SDK constraints without relying on ambient PATH.
- Support explicit adoption of an existing instance as a component-ownership target; discovery alone must never imply adoption.
- Reconcile explicitly desired exact component IDs with Visual Studio Installer `modify --add` / `--remove` operations.
- Persist provenance for exact components Machine-Soul adds so only owned components can later be removed automatically.
- Preserve pre-existing/unowned components and tolerate intentional side-by-side toolsets/SDKs.
- Distinguish floating “Latest” component IDs from pinned version-specific component IDs without substituting between them.
- Rediscover and verify the exact instance/component set after mutation.
- Surface elevation, pending-restart, incomplete-instance, and installer failures explicitly.
- Provide dry-run plans that identify the exact instance and component IDs to add/remove.
- Add fake-runner/unit coverage for full IDE + Build Tools instances, multiple toolsets/SDKs, explicit adoption, owned/unowned components, exact add/remove, missing prerequisites, incomplete instances, and instance identity mismatch.

## Constraints / non-goals

- Do not automatically install or uninstall an entire Visual Studio/Build Tools instance.
- Do not choose Community/Professional/Enterprise/Build Tools, Stable/Insiders/custom channel, installation path, or desired workload/component inventory for the maintainer.
- Do not treat `.vsconfig` as convergent deletion authority; import semantics are additive.
- Do not delete pre-existing/unowned components merely because they are absent from Machine-Soul desired state.
- Do not use `InstallCleanup.exe` for normal reconciliation.
- Do not edit project `PlatformToolset`, `WindowsTargetPlatformVersion`, CMake toolset settings, Unreal/SML project configuration, or solution-local `.vsconfig`.
- Do not persist an activated Developer Command Prompt/PowerShell environment as desired state.
- Do not make package-manager/runtime operations silently install native toolchain components.

## Acceptance criteria

- Machine-Soul can enumerate exact Visual Studio/Build Tools instances and their installed component IDs deterministically.
- Multiple compiler toolsets and SDKs are represented as healthy simultaneous capabilities.
- An explicitly adopted instance can gain/remove Machine-Soul-owned exact components without touching unowned components.
- Native-build consumers can ask for a satisfying toolchain candidate without invoking ambient `cl.exe`/PATH.
- No product instance is provisioned or adopted implicitly.

## Validation

- Use current Microsoft Visual Studio 2026 setup, MSVC, Windows SDK, and vswhere behavior as the contract.
- Exercise at least one full-IDE fixture and one Build Tools-only fixture with overlapping toolsets/SDKs.
- Exercise pinned versus Latest component semantics and exact owned-component removal.
- Exercise missing/incomplete instance and restart/elevation result paths.
- Run the repository Python validation suite and inspect GitHub Actions before completion.
