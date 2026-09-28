# Windows native toolchain annexation

Machine-Soul models the Windows native C/C++ toolchain as two distinct ownership layers:

1. a Visual Studio Setup **instance** that may already exist and remain human-owned;
2. exact Visual Studio **component IDs** that Machine-Soul explicitly adds inside an adopted instance.

This deliberately does not equate “Visual Studio 2026” with one compiler version. Multiple MSVC toolsets and Windows SDKs may coexist in one setup instance.

## Discovery

Native toolchain discovery uses the installed Visual Studio Setup surface through `vswhere` and includes all products so Build Tools-only instances are visible.

The normalized instance model preserves:

- setup instance ID;
- installation path and product identity;
- installation version/channel observations;
- complete/launchable/prerelease state;
- installed package/component IDs;
- installed MSVC version directories when observable.

Build Tools does not need to be IDE-launchable to satisfy a native compiler prerequisite. A setup instance must, however, be complete before Machine-Soul will adopt or modify it.

## Prerequisite queries

Callers can ask for an exact capability without relying on ambient `PATH` or whichever `cl.exe` happens to resolve.

Requirements can include:

- exact required Visual Studio component IDs;
- an exact Windows SDK component ID;
- an MSVC version prefix;
- host/target architecture;
- prerelease policy.

The result returns all matching complete setup instances. Discovery alone never makes an instance Machine-Soul-owned.

## Adoption

Component mutation requires explicit instance adoption.

Adoption records the setup instance ID and installation path in machine/host-scoped scratch state. It does **not** claim any component that already existed in the instance.

This is an important ownership boundary: a pre-existing compiler, SDK, CMake component, workload, or other setup package remains unowned unless Machine-Soul itself later adds that exact component.

## Component reconciliation

For an adopted instance, Machine-Soul can reconcile a desired set of exact component IDs using Visual Studio Installer `modify --add` / `--remove`.

The conservative rules are:

- missing desired components may be added;
- components added by Machine-Soul become owned;
- an owned component removed from desired state may be removed;
- pre-existing/unowned components are preserved;
- “Latest” component IDs and pinned version-specific component IDs are distinct desired policies;
- rediscovery verifies the exact instance and component set after mutation;
- observed partial mutation is recorded conservatively even when the installer returns an error.

A dry run reports the exact instance, add/remove component IDs, and installer argv without changing setup or provenance.

## Restart, elevation, and failure

Installer return codes are surfaced rather than hidden.

A successful operation that reports reboot/restart required remains semantically successful and records `restart_required=true`.

Elevation-required, installer-busy, instance-in-use, generic installer failure, incomplete instance, and instance-identity mismatch are explicit result conditions.

## Deliberate non-goals

This capability does not yet:

- provision or uninstall whole Visual Studio/Build Tools instances;
- choose Community/Professional/Enterprise/Build Tools;
- choose Stable/Insiders/custom channels or installation paths;
- treat `.vsconfig` as convergent deletion authority;
- use `InstallCleanup.exe`;
- edit project `PlatformToolset`, Windows SDK selection, CMake, Unreal/SML, or solution configuration;
- persist an activated developer shell;
- silently install toolchain components as a side effect of pip/npm/LuaRocks/runtime operations.

Project/build/package backends should query this capability for prerequisites and report missing requirements unless an explicit native-toolchain reconciliation operation was requested.
