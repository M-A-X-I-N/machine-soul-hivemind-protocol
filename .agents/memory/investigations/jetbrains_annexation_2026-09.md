# JetBrains ecosystem annexation findings

Durable findings from `MSHP-DEV-A-020` (2026-09-28):

- `JetBrains.Toolbox` current WinGet manifest is USER scoped; Toolbox itself is immediately installable through current scoped WinGet machinery.
- Toolbox supports side-by-side IDE versions and stable tool paths, making it conceptually an IDE version manager.
- Toolbox CLI can install exact IDE builds and detect external tools, but JetBrains explicitly marks it work-in-progress and currently distributes it as a JAR requiring a JRE; do not make it a hard lifecycle backend without later validation.
- Toolbox documented settings live in `%LOCALAPPDATA%\JetBrains\Toolbox\.settings.json`; do not assimilate the whole Toolbox data tree.
- Rider/IntelliJ use product+version config directories under `%APPDATA%\JetBrains`, separate cache/system directories under `%LOCALAPPDATA%`, native settings ZIP export/import, and JetBrains Backup and Sync.
- Rider layer-based settings require product-specific treatment; do not assume one generic whole-directory JetBrains config strategy.
- Rider/IntelliJ expose CLI plugin installation by plugin ID. Combined with VS Code evidence, plugins/extensions likely deserve a reusable package-inventory concept rather than file config.

Detailed research lives in `meta/tasks/archive/MSHP-DEV-A/workspace/jetbrains.md`.