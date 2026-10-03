# Additional developer runtime/toolchain survey findings

Durable findings from `MSHP-DEV-A-060` (2026-09-28):

- The survey should not turn Machine-Soul into a generic language catalog. Current maintainer relevance remains the deciding filter.
- **MSVC / Visual Studio Build Tools / Windows SDK** is the strongest additional near-term investigation subject. The maintainer already works in native Windows/C++ contexts, and current Visual Studio tooling supports multiple MSVC toolset versions side-by-side. Toolset, IDE instance, Windows SDK, architecture, and selected project toolset are distinct state.
- **.NET SDK/runtime** is a strong structured future candidate. Multiple SDK/runtime versions are normal; the `dotnet` host selects SDKs using installed state plus `global.json` / roll-forward policy. SDK inventory, runtime inventory, and project target framework must not be collapsed into one version.
- **Java/JDK** is a strong structured future candidate. Windows JDK installations may coexist across feature releases, while `JAVA_HOME` / `PATH` select the ambient default and vendor identity is materially relevant. Do not assume “Java 21” uniquely identifies a distribution.
- **Rust** is a strong structured future candidate with unusually clean manager delegation. `rustup` natively owns multiple toolchains, global defaults, directory/project overrides, components, and targets. A future Machine-Soul implementation should probably delegate rather than reimplement toolchain management.
- **Go** is a credible structured future candidate. Go documents official side-by-side installs using versioned launcher commands, so multiversion state is real even without choosing a third-party manager.
- **Ruby** and **PHP** remain plausible but low-priority Windows subjects absent a concrete maintainer workload. RubyInstaller/rvm-windows and official PHP Windows builds mean they are supportable, but “common somewhere” is not enough to create tasks.
- **Perl** is not a current priority for the maintainer environment. Record it only as a possible future dependency-driven subject.
- Cross-runtime managers such as mise remain relevant to `MSHP-DEV-A-070`, but this survey does not select one. Native ecosystem managers/backends may still be better for some runtimes.
- No new executable runtime tasks should be created from this survey alone. The synthesis/roadmap task can promote only the candidates justified by combined evidence.

Detailed bounded survey lives in `autonomic_affairs/tasks/MSHP-DEV-A/workspace/additional_runtime_candidates.md`.
