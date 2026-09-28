# DISC-A synthesis and implementation traceability

Status: synthesis output for MSHP-DISC-A-050.

## Durable conclusions already promoted

- Discovery semantics and the separation of installation / structural config / effective config: autonomic_affairs/docs/DISCOVERY_SEMANTICS.md
- Structural check ownership/state vocabulary: autonomic_affairs/docs/CONFIGURATION_MODEL.md and DEPLOYMENT_CONTRACT.md
- Installation discovery architecture correction: autonomic_affairs/docs/INSTALLATION_ARCHITECTURE.md
- Effective verification evidence/strategy model: autonomic_affairs/docs/CONFIGURATION_VERIFICATION.md
- Durable agent notes: .agents/decisions/discovery_semantics.md, .agents/investigations/install_mechanisms_2026-09.md, and .agents/investigations/effective_configuration_2026-09.md

Raw detailed evidence remains in installation_discovery.md and effective_configuration.md in this workspace.

## Why DISC-B is split this way

The investigations produced two implementation tracks sharing only the assessment/evidence model.

Installation discovery needs:
- typed assessment model -> B-010;
- decoupled declaration/engine surface -> B-020;
- Linux native package evidence -> B-030;
- native Windows registration/catalog evidence -> B-040;
- Windows POSIX-environment evidence -> B-050.

Effective configuration needs:
- the same typed evidence model -> B-010;
- first-class verify_config plumbing -> B-060;
- shell startup traces -> B-070;
- native resolution/application probes -> B-080;
- OMP's two-layer app/runtime verification -> B-090.

Only after both tracks are concrete does B-100 compose them into one status view.

## Finding-to-task traceability

- WinGet/dpkg correlation is not historical frontend provenance -> B-010/B-020/B-030/B-040 data model and backend semantics.
- check_installed must work without Install capability -> B-020 and application wiring in B-030/B-040/B-050.
- Linux dpkg, executable, manual and optional Flatpak evidence -> B-030.
- Windows ARP/MSI, MSIX/AppX, WinGet correlation, side-by-side candidates -> B-040.
- MSYS2/Cygwin shell identity must match configured environment -> B-050.
- verify_config must be distinct from check_config -> B-060.
- Bash/Zsh/Fish can use controlled ordinary startup tracing -> B-070.
- PowerShell/CMD/Windows Terminal/Contour have different resolution/application evidence ceilings -> B-080.
- OMP theme usability is weaker than actual consumer-shell selection -> B-090.
- User-visible desire to see installed/applied/effective together without conflating them -> B-100.

## Installation takeover boundary

The takeover/adoption/migration concept remains exclusively in autonomic_affairs/reminders.md. DISC-B must preserve information that makes future takeover possible but is not authorized to implement it.
