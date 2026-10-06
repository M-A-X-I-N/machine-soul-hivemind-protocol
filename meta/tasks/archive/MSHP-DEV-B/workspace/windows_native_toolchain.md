# Windows native toolchain annexation investigation

Status: completed research output for `MSHP-DEV-B-020`.

Research date: 2026-09-28.

## Executive conclusion

The Windows native C/C++ toolchain is safe enough to promote one bounded implementation task, but only if Machine-Soul models **Visual Studio instances and exact installed components separately from MSVC/SDK/tool selection**.

Current Microsoft tooling provides:

- programmatic Visual Studio / Build Tools instance discovery through `vswhere` / Setup Configuration;
- stable per-instance identity and installation path;
- machine-readable installed package/component inventory;
- exact workload/component IDs;
- programmatic `setup.exe modify --add ... --remove ...`;
- explicit side-by-side MSVC toolsets and Windows SDKs;
- explicit compiler/toolset selection at build-shell/CMake/MSBuild level.

That is sufficient for conservative discovery, prerequisite checking, and ownership-aware reconciliation of explicitly declared component IDs inside a known Visual Studio/Build Tools instance.

It is **not** sufficient reason to invent the maintainer's desired Visual Studio edition/channel/workload/component set.

## Current 2026 baseline

As of 2026-09-28:

- Visual Studio 2026 is the current 18.x product family.
- The latest documented stable release is 18.10.1, released 2026-09-15.
- Visual Studio 2026 uses the Stable channel `VisualStudio.18.Stable` and an Insiders channel `VisualStudio.18.Insiders`.
- Visual Studio 2026 follows a modern annual-release cadence. Annual releases are in-place updates within the 2026-era product model rather than a new side-by-side major family every year.
- Visual Studio 2022 remains a distinct 17.x family and can coexist with 2026.
- Product IDs remain distinct for Community, Professional, Enterprise, Build Tools, and Team Explorer.

Sources:

- https://learn.microsoft.com/visualstudio/releases/2026/release-notes
- https://learn.microsoft.com/en-us/visualstudio/releases/2026/release-rhythm
- https://learn.microsoft.com/en-us/lifecycle/products/visual-studio-2026
- https://learn.microsoft.com/en-us/visualstudio/install/workload-and-component-ids?view=visualstudio
- https://learn.microsoft.com/visualstudio/install/install-visual-studio-versions-side-by-side?view=vs-2026

## Instance identity

Visual Studio setup exposes a first-class instance model.

Useful identity/observation fields include:

- `instanceId`;
- product ID / edition;
- installation version;
- installation path;
- installation name;
- channel/update source properties;
- product package;
- installed package/component references;
- completeness/launchability/error state.

The Setup Configuration API documents `GetInstanceId()` as an instance identifier, and `ISetupInstance2` exposes installation path/version/product/packages/state.

`vswhere.exe` is installed at a fixed location under:

```text
%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\vswhere.exe
```

for modern Visual Studio installs. It can query all products, filter by version/product/component, include prereleases, return JSON, and include installed package references.

Useful discovery shape:

```text
vswhere -all -products * -format json -utf8 -include packages
```

and prerequisite queries can use `-requires` / `-requiresAny`.

Sources:

- https://learn.microsoft.com/en-us/dotnet/api/microsoft.visualstudio.setup.configuration.isetupinstance2
- https://github.com/microsoft/vswhere/wiki/
- https://github.com/microsoft/vswhere/wiki/Examples
- https://github.com/Microsoft/vswhere/blob/main/src/vswhere.lib/vswhere.lib.rc

### Identity decision

Machine-Soul should preserve both:

- setup instance ID as the stable setup-instance key;
- installation path as the exact mutation target required by setup commands.

Product/channel/version are attributes and policy inputs, not substitutes for instance identity.

## Full IDE versus Build Tools

Build Tools is a distinct product:

```text
Microsoft.VisualStudio.Product.BuildTools
```

and can carry native C++ workloads/components without the Visual Studio IDE.

This matters because package/runtime native-build prerequisites should not imply that a full IDE is necessary.

Machine-Soul must model:

- full Visual Studio IDE instances;
- Build Tools-only instances;

through the same setup-instance discovery surface while preserving their product identities.

Source:

- https://learn.microsoft.com/en-us/visualstudio/install/workload-and-component-ids?view=visualstudio

## Workloads versus components

Visual Studio setup has explicit workload IDs and component IDs.

For native C++ Build Tools, the desktop workload is:

```text
Microsoft.VisualStudio.Workload.VCTools
```

but a workload is a bundle whose required/recommended/optional composition can change as Visual Studio updates.

Therefore Machine-Soul should not use a workload name as the only durable identity for every compiler/SDK prerequisite.

For exact native tooling, component IDs are the stronger desired-state units.

Examples documented in the current 2026 component catalog include:

```text
Microsoft.VisualStudio.Component.VC.Tools.x86.x64
Microsoft.VisualStudio.Component.VC.14.50.18.0.x86.x64
Microsoft.VisualStudio.Component.VC.14.44.17.14.x86.x64
Microsoft.VisualStudio.Component.Windows11SDK.26100
```

The first is a moving “Latest” component. The latter examples pin a specific toolset family/version.

Source:

- https://learn.microsoft.com/en-us/visualstudio/install/workload-component-id-vs-build-tools?view=visualstudio
- https://learn.microsoft.com/cpp/overview/acquire-msvc

### Desired-state decision

Distinguish:

- workload intent;
- exact component intent;
- moving “latest” components;
- pinned toolset/SDK components.

Do not silently replace a pinned component with “Latest”.

## MSVC toolsets are now explicitly decoupled from Visual Studio

Visual Studio 2026 strengthens a boundary that Machine-Soul needs to preserve.

Microsoft documents:

- VS 2026 18.0 introduced platform toolset `v145`;
- MSVC Build Tools 14.50 is the first VS 2026-era long-term toolset;
- 14.51 is a separately serviced standard release;
- 14.52 is preview at research time;
- MSVC versioning/lifecycle is decoupled from Visual Studio versioning beginning with 2026;
- older v143 / 14.44 tooling can remain installed and targeted from newer Visual Studio.

Current compiler lifecycle documentation lists:

- 14.50: long-term, EOL November 2028;
- 14.51: standard, EOL February 2027;
- 14.52: preview as of research time.

Sources:

- https://learn.microsoft.com/en-us/cpp/overview/compiler-versions
- https://learn.microsoft.com/en-us/visualstudio/releases/2026/servicing-vs
- https://learn.microsoft.com/cpp/overview/acquire-msvc
- https://learn.microsoft.com/visualstudio/releases/2026/port-migrate-and-upgrade-visual-studio-projects

### Toolset identity decision

Do not model “Visual Studio 2026” as implying one MSVC compiler version.

An exact native build environment may need:

```text
setup instance
+ component/toolset identity
+ selected MSVC version
+ host architecture
+ target architecture
+ Windows SDK version
```

## Side-by-side MSVC selection

Microsoft supports explicit pinned toolset installation and selection.

Current examples include a `.vsconfig` with:

```text
Microsoft.VisualStudio.Component.VC.Preview.Tools.x86.x64
Microsoft.VisualStudio.Component.VC.Tools.x86.x64
Microsoft.VisualStudio.Component.VC.14.50.18.0.x86.x64
```

CMake can select a toolset version explicitly:

```text
cmake -G "Visual Studio 18 2026" -T "version=14.50" ...
cmake -G "Visual Studio 18 2026" -T "version=14.51" ...
```

and developer environments can select a supported compiler version with:

```text
vcvars64.bat -vcvars_ver=14.50
```

Source:

- https://learn.microsoft.com/cpp/overview/acquire-msvc

This is direct evidence that simultaneous toolset versions are healthy intended state.

## Windows SDK coexistence

Windows SDKs are independently versioned.

At research time Microsoft's download catalog exposes, among others:

- Windows 11 SDK 10.0.28000.2705 (August 2026);
- Windows 11 SDK 10.0.26100.9169 (August 2026);
- earlier supported SDK families.

The SDK determines compile-time Windows API surface and is independent from the Windows App SDK package.

Sources:

- https://learn.microsoft.com/en-us/windows/apps/windows-sdk/downloads
- https://learn.microsoft.com/en-us/windows/apps/windows-sdk/
- https://learn.microsoft.com/en-us/windows/apps/get-started/versioning-overview

### SDK identity decision

The desired Windows SDK set may contain multiple versions. Project-selected SDK version is project state; installed SDK component presence is machine state.

Do not infer desired SDK from the current Windows OS version.

## Host and target architecture

Developer command environments explicitly distinguish host architecture from target architecture.

Current Developer Command Prompt / Developer PowerShell support architecture selectors such as:

```text
-arch=<target>
-host_arch=<host>
```

and native C++ setup exposes architecture-specific component choices.

Sources:

- https://learn.microsoft.com/en-us/dotnet/framework/tools/developer-command-prompt-for-vs
- https://learn.microsoft.com/en-us/cpp/build/how-to-enable-a-64-bit-visual-cpp-toolset-on-the-command-line

### Environment decision

Developer shell activation is **derived build-session state**, not installed-state identity.

Machine-Soul may later provide a helper that resolves an exact instance/toolset/SDK/host/target tuple and constructs the appropriate environment, but it should not persist an activated shell as desired state.

## Installation and modification automation

The Visual Studio Installer supports programmatic install/modify operations.

Important current command-line capabilities include:

- `--installPath`;
- `--productId`;
- `--channelId` / `--channelUri`;
- repeatable `--add <workload-or-component-id>`;
- repeatable `--remove <component-id>`;
- `--includeRecommended` / `--includeOptional`;
- `--config <file.vsconfig>`;
- `--quiet` / `--passive`;
- `--wait`;
- `--norestart`;
- update-settings and out-of-support component policies.

Most install/update/modify operations require elevation by default.

Sources:

- https://learn.microsoft.com/en-us/visualstudio/install/use-command-line-parameters-to-install-visual-studio
- https://learn.microsoft.com/visualstudio/install/command-line-parameter-examples?view=visualstudio
- https://learn.microsoft.com/en-us/visualstudio/install/modify-visual-studio

## .vsconfig is useful but not a convergent ownership primitive

A `.vsconfig` file can list component IDs and is excellent for:

- bootstrapping a new installation;
- adding missing components to an existing installation;
- sharing project/team prerequisites;
- exporting an existing selection.

However, Microsoft explicitly documents import/modify with `--config` as installing items listed in the file that are missing.

It does **not** mean “remove everything not in this file”.

Therefore Machine-Soul must not treat:

```text
observed components - vsconfig components
```

as authorized removals.

Source:

- https://learn.microsoft.com/en-us/visualstudio/install/import-export-installation-configurations

## Conservative component ownership

Exact `--remove <component-id>` exists, but a safe Machine-Soul policy must still distinguish ownership.

Initial implementation should:

- discover every installed component/package;
- record which exact components Machine-Soul explicitly added/owns;
- ensure desired owned components are present;
- remove a Machine-Soul-owned component only when it leaves desired state;
- preserve pre-existing/unowned components;
- rediscover after mutation;
- refuse/flag an operation if exact instance identity changed or disappeared.

Do not use workload absence/presence alone as deletion authorization because workloads expand to shared components and their composition evolves.

## Instance lifecycle

Installing or deleting entire Visual Studio/Build Tools instances is more policy-heavy than component reconciliation.

Unknowns/preferences include:

- desired product (Community/Professional/Enterprise/Build Tools);
- licensing/sign-in expectations;
- Stable versus Insiders/custom channel;
- installation path;
- whether an existing human-owned instance should be adopted;
- whether a full IDE is desired at all.

The current repo has not selected these.

Therefore this investigation does **not** taskify automatic creation/removal of Visual Studio instances.

Initial implementation should discover instances and optionally explicitly adopt a target instance for component ownership.

Whole-instance provisioning can be promoted later when desired product/channel/path state is supplied.

## Uninstall and destructive cleanup

Normal Visual Studio Installer uninstall removes an instance.

`InstallCleanup.exe` is documented as a **last resort** and Microsoft warns that it can remove features shared by other Visual Studio installations/products.

Machine-Soul must never use InstallCleanup as ordinary uninstall/reconciliation machinery.

Source:

- https://learn.microsoft.com/en-us/visualstudio/install/uninstall-visual-studio

## Update semantics

Visual Studio product/channel updates and MSVC toolset updates are separate policy decisions.

Important 2026 implications:

- the IDE may move through monthly 18.x updates;
- MSVC 14.50/14.51/etc have their own support windows;
- a “Latest” component intentionally moves;
- a pinned MSVC component intentionally does not mean Latest;
- older v143 components can coexist for project compatibility.

A Machine-Soul desired component must therefore preserve whether it is:

- floating by component identity such as Latest;
- pinned by exact versioned component identity.

Do not rewrite one policy into the other.

## Project state versus machine state

Machine-Soul may own installed machine capabilities.

Project files remain project-owned, including:

- `PlatformToolset`;
- `WindowsTargetPlatformVersion`;
- CMake generator/toolset selection;
- Unreal/SML project-specific compiler requirements;
- solution-local `.vsconfig` files.

A project may ask for a prerequisite, but its project configuration should not silently become global machine desired state.

## Native package/runtime consumers

DEV-A package research identified native-build consumers in:

- Lua/LuaRocks;
- pip;
- npm/native addons.

These backends should consume a **prerequisite query** such as:

```text
find a complete native toolchain candidate satisfying:
  MSVC/toolset constraint
  host/target architecture
  SDK constraint
```

They should not install arbitrary Visual Studio components as a hidden side effect.

If no candidate satisfies the prerequisite:

- report the missing requirement;
- optionally point at an explicit Machine-Soul native-toolchain reconciliation operation if the user has configured one.

## Implementation promotion

Promote one task: `MSHP-DEV-B-025`.

It should implement:

- `vswhere`-backed exact instance/package discovery;
- normalized native-toolchain observations;
- prerequisite queries;
- explicit adoption of an existing instance for component ownership;
- conservative exact-component add/remove reconciliation through Visual Studio Installer;
- provenance for components Machine-Soul owns;
- dry-run/elevation/restart-aware results.

It should **not** choose or automatically provision a Visual Studio product instance.

That boundary is useful immediately for native builds and safe without inventing maintainer preferences.

## Scenario walkthroughs

### Existing Build Tools instance, missing pinned compiler

Observed:

- Build Tools 2026 instance exists;
- MSVC 14.51/latest exists;
- desired explicit owned component includes 14.50.

Machine-Soul may add exact 14.50 component to the adopted instance, verify with vswhere packages, and preserve 14.51.

### Existing human-owned component

Observed component existed before adoption and is absent from Machine-Soul desired owned set.

Machine-Soul leaves it alone.

### Remove Machine-Soul-owned toolset

A previously added exact component leaves desired state.

Machine-Soul may invoke exact `--remove <component-id>` against the same adopted instance, then rediscover. Shared/unowned components remain untouched.

### Project requests old v143

Project prerequisite check can detect whether a compatible v143/14.44 component is present. It does not edit the project or install anything unless an explicit native-toolchain reconciliation operation is separately authorized.

### No Visual Studio instance

Prerequisite discovery reports no suitable instance.

Initial implementation does not silently install Community or Build Tools because desired product/channel/path policy is absent.

## Final architectural decision

Model the native Windows toolchain as:

```text
Visual Studio/Build Tools setup instance
  ├─ product/channel/version/path identity
  ├─ installed component/package set
  ├─ MSVC toolset components (many may coexist)
  ├─ Windows SDK components (many may coexist)
  └─ derived build-session selection
       ├─ compiler/toolset version
       ├─ host architecture
       ├─ target architecture
       └─ SDK
```

The setup instance is a host/container for components, not the same thing as the compiler.

The compiler/toolset/SDK are machine capabilities, not the same thing as project selection.

This separation is the safe annexation boundary.
