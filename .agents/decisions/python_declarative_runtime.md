# Python/declarative next-phase decision

## Decision

The post-baseline redesign will converge on a Python 3, library-first, declarative application architecture.

The human-facing target architecture is documented in [`../../collective_affairs/docs/next_phase_architecture.md`](../../collective_affairs/docs/next_phase_architecture.md). Read that document before implementing V2-45 through V2-63.

## Agent-critical rules

- Python 3 is a prerequisite; do not add Python bootstrap installers unless separately authorized later.
- Discover host/platform/account/environment facts at runtime when practical rather than requiring tracked host inventory.
- Do not infer account management from account existence or config availability. Cross-account work is explicit, carried as a logical target in operation context, and kept distinct from process/elevation identity.
- Generic behavior belongs in shared libraries.
- Each application gets a non-executable declarative `_application.py` beside its wrappers.
- Atomic wrappers do one named thing, contain essentially no business logic, and share one importable/executable implementation path.
- The broad interactive manager orchestrates wrappers; it does not implement application/platform behavior.
- Prefer imported Python calls in-process. Spawn only where a real process/native boundary is useful.
- Normalize all operations into one structured result model.
- Native `.ps1`/`.sh` scripts are small platform primitives, not parallel policy engines.
- Native process results use a structured protocol (initially versioned JSON on stdout, diagnostics on stderr, exit status for process-level outcome).
- Prefer an existing generic declarative strategy, then add a reusable strategy, then use custom application Python as the final escape hatch.
- Do not invent a declarative mini-language for arbitrary procedural workflows.
- Preserve all existing symlink/backup/ownership/conflict safety guarantees through the migration.

## Naming/meta decisions

- Repository-controlled multiword names migrate to `lower_snake_case`.
- Externally dictated names stay exact where required.
- `AGENTS.md` stays at root for agent discovery.
- Dotfiles/tool-defined roots may stay at root.
- Repository meta material moves toward `collective_affairs/`.
- The executable-work ledger is `collective_affairs/agent_tasks.md`.
- Agent tasks mean sufficiently specified/executable work; future roadmap/objectives/reminders are semantically separate concepts.

## Historical design note

Haxe was considered as a unified cross-platform implementation language, including generated Python/native build branches. It was rejected for this project phase because Python directly satisfies the desired shared-script/runtime role with substantially less build/distribution machinery. Do not reintroduce Haxe merely to obtain one cross-platform codebase unless new constraints materially change that tradeoff.

## Transition warning

The stable v2 implementation still contains substantial Bash/PowerShell orchestration. That does not contradict this decision: V2-45 through V2-63 are the migration plan. Do not delete working behavior before its replacement is proven.
