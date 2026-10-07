# Linux installation scope findings

Durable findings from `MSHP-INST-A-030` (2026-09-28).

- Apt/dpkg is a fixed machine-scoped mutation backend for current Machine-Soul; sudo/root is execution privilege, not scope.
- Flatpak maps cleanly to USER/MACHINE but also has named system installations (`--installation=NAME`), proving exact backend identity must accompany coarse scope.
- pipx maps to user versus `--global`, but user/global roots are configurable, so resolved directories remain backend-specific provenance/evidence.
- Homebrew/Linuxbrew is intentionally not forced into a new core enum: official docs describe one owning account and a prefix, possibly a dedicated owner, while other users may execute installed binaries. Prefix + owner are essential backend identity.
- Core scope vocabulary does not need expansion for these examples. The extension seam is backend-specific native selector + exact installation identity + scope discovery/verification.
- Do not create Flatpak/Homebrew/pipx implementation tasks until Machine-Soul actually supports or needs those managers.

Detailed scenario/source notes live in `meta/tasks/archive/MSHP-INST-A/workspace/linux_scope.md`.
