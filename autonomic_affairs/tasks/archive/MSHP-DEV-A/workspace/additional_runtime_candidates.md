# Additional runtime/toolchain candidate survey

Status: completed research output for `MSHP-DEV-A-060`.

Research date: 2026-09-28.

## Decision rule

This is a prioritization survey, not a promise to support every language. Candidates are ranked by:

1. evidence that they fit the maintainer's actual or adjacent Windows development environment;
2. whether installation/version lifecycle has enough nontrivial state to benefit from Machine-Soul;
3. whether multiversion coexistence or manager/backend selection is materially relevant;
4. whether current ecosystem tooling gives a sane implementation path.

## Candidate matrix

| Candidate | Current relevance | Multiversion / manager material? | Classification | Why |
|---|---|---|---|---|
| MSVC / Visual Studio Build Tools / Windows SDK | Direct | Yes — supported toolsets and VS instances can coexist; projects select platform toolsets/SDKs | **Near-term deep investigation** | Native Windows/C++ work already exists around the maintainer. This is not hypothetical. |
| .NET SDK/runtime | Adjacent Windows ecosystem | Yes — SDKs/runtimes coexist; `global.json` and roll-forward control SDK selection | **Initiative tracking** | Strong future annexation fit, but no current workload justifies interrupting the existing block. |
| Java/JDK | Common adjacent ecosystem | Yes — feature releases coexist; vendor + `JAVA_HOME`/`PATH` selection matter | **Initiative tracking** | Important once Java/Gradle/Android appears; vendor identity makes lifecycle more than a scalar version. |
| Rust | Plausible systems/tooling ecosystem | Yes — `rustup` directly manages toolchains/defaults/overrides/components/targets | **Initiative tracking** | Very clean delegation story; promote when there is an actual Rust workload. |
| Go | Plausible tooling/backend ecosystem | Yes — official versioned side-by-side installation exists | **Initiative tracking** | Straightforward future support, but no present need. |
| Ruby | Low current relevance | Yes — Windows-specific installer/version-manager choices exist | **Deferred / no task** | Supportable, but no maintainer workload currently earns investigation cost. |
| PHP | Low current relevance | Yes — side-by-side binaries/config are possible, but selection is installation-layout dependent | **Deferred / no task** | Common web runtime, but not relevant enough here to prioritize. |
| Perl | Very low current relevance | Potentially, but ecosystem choice would be niche | **Not useful now** | Keep dependency-driven only. |

## MSVC / Windows native toolchain

This is the clearest omission from the first runtime list because the maintainer already works with Windows-native C++/Unreal/SML tooling.

Microsoft currently documents:

- multiple MSVC Build Tools versions installable side-by-side through Visual Studio Installer;
- current and older supported toolsets selectable as individual components;
- native multi-targeting, where newer Visual Studio can build using older installed toolsets;
- side-by-side Visual Studio major/channel instances.

Sources:

- https://learn.microsoft.com/en-us/cpp/overview/acquire-msvc
- https://learn.microsoft.com/en-us/cpp/overview/compiler-versions
- https://learn.microsoft.com/en-us/cpp/porting/use-native-multi-targeting
- https://learn.microsoft.com/visualstudio/install/install-visual-studio-versions-side-by-side

Future investigation should treat at least these as distinct:

- Visual Studio / Build Tools instance identity;
- MSVC toolset versions;
- Windows SDK versions;
- host/target architectures;
- workloads/components;
- project-selected platform toolset and SDK;
- Machine-Soul ownership versus externally installed components.

This deserves dedicated research, but task creation belongs in the roadmap synthesis rather than being silently spawned here.

## .NET SDK/runtime

.NET is a strong annexation candidate because side-by-side state and selection are first-class behavior rather than accidental leftovers.

Microsoft documents that `global.json` chooses the .NET SDK used by CLI commands independently from the runtime version a project targets, with roll-forward rules over installed SDKs. Multiple runtimes can also exist side-by-side.

Sources:

- https://learn.microsoft.com/en-us/dotnet/core/tools/global-json
- https://learn.microsoft.com/en-us/dotnet/core/versions/selection

Implication: a future model must distinguish installed SDK set, installed runtime set, ambient SDK selection, and project target frameworks. Do not model “.NET version” as one scalar.

Classification: initiative tracking, not an executable task yet.

## Java / JDKs

Windows Java lifecycle has at least three independent dimensions:

- JDK feature/version;
- vendor/distribution;
- ambient selection through `JAVA_HOME` and `PATH`.

Microsoft's OpenJDK documentation publishes distinct WinGet identities by major feature release and permits EXE/MSI/ZIP installation. Oracle's Windows installer documentation likewise makes feature-release identity explicit; same-feature patch installers replace the prior patch rather than representing arbitrary parallel patch instances.

Sources:

- https://learn.microsoft.com/en-us/java/openjdk/install
- https://learn.microsoft.com/en-us/windows/dev-environment/java
- https://docs.oracle.com/en/java/javase/24/install/installation-jdk-microsoft-windows-platforms.html

This makes Java a real multiversion/vendor-management problem, but not one that needs solving before a Java/Gradle/Android workload exists.

Classification: initiative tracking.

## Rust

Rust has the cleanest ecosystem-native delegation story in this survey.

`rustup` manages:

- multiple stable/beta/nightly/versioned/date-pinned toolchains;
- default toolchain;
- command-line, environment, directory, and `rust-toolchain.toml` overrides;
- components and cross-compilation targets;
- Windows MSVC/GNU host variants.

Sources:

- https://rust-lang.github.io/rustup/concepts/toolchains.html
- https://rust-lang.github.io/rustup/overrides.html
- https://rust-lang.github.io/rustup/devel/installation/windows.html

Machine-Soul should almost certainly delegate Rust toolchain lifecycle to `rustup` if Rust becomes desired rather than reproduce this machinery.

Classification: initiative tracking.

## Go

The Go project explicitly documents multiple Go versions on one machine using versioned commands installed through `golang.org/dl/goX.Y.Z`, plus exact discovery and removal of those downloaded versions.

Source:

- https://go.dev/doc/manage-install

This proves that desired installed version sets can matter for Go even without a third-party manager. The currently selected/default `go` command and additional versioned launchers are separate concepts.

Classification: initiative tracking.

## Ruby / PHP / Perl

### Ruby

RubyInstaller remains the main Windows-native distribution and currently advertises both current Ruby releases and a Windows Ruby Version Manager.

Source:

- https://rubyinstaller.org/

That makes future annexation feasible, but there is no current workload evidence. Defer.

### PHP

PHP continues to publish official Windows builds and Windows installation guidance.

Source:

- https://www.php.net/manual/en/install.windows.php

Side-by-side PHP is primarily an installation-layout/PATH/config selection concern. Defer until a concrete PHP workload exists.

### Perl

Perl remains possible on Windows, but there is no current maintainer signal strong enough to justify cataloguing Windows distributions/version managers now.

Classification: not useful now; dependency-driven only.

## Cross-runtime manager note

The existence of .NET/JDK/Rust/Go does not itself prove Machine-Soul should adopt a universal runtime manager.

`MSHP-DEV-A-070` should compare:

- native first-party/ecosystem managers where strong;
- backend-specific managers;
- cross-runtime managers such as mise;
- direct Machine-Soul lifecycle only where ecosystem tooling is genuinely inadequate.

The desired model should allow multiple backend strategies without forcing every runtime through one manager.

## Outcome

Only one candidate is strong enough to call a near-term research priority from this survey: **the Windows native C/C++ toolchain stack**.

Everything else remains structured initiative context until actual usage or the final roadmap synthesis promotes it. This satisfies the “option of multiversion” preference without creating zombie work merely because an ecosystem exists.
