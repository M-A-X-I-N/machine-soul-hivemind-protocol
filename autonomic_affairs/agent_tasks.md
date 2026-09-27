# Machine-Soul Hivemind Protocol — Experimental v2 Agent Tasks

This file is the authoritative source of truth for sufficiently specified/executable agent work and the current next action.

It is deliberately not a catch-all roadmap. Longer-horizon roadmap items, objectives, and reminders are separate concepts and should receive their own artifacts only when they become useful.

## Status legend

- [ ] Pending
- [~] In progress
- [x] Complete
- [!] Blocked

## Next task

**MSHP-META-A-020 — Establish the canonical agent-task index/detail/archive system.**

## Task history and queue

- [x] **V2-01 — Inspect existing repository**
  - Inspect branches/history, directory tree, scripts, configs, `$MACHINE_SOUL`, deployment logic, conventions, and reusable ideas.
  - Checkpoint: concise state summary; no mutation during inspection.

- [x] **V2-02 — Preserve v1 and clean `main`**
  - Preserve former `main` as `experimental/v1`.
  - Establish intentionally clean `main` additively, without rewriting history.
  - Checkpoint: v1 recoverable; main is clean restart point.

- [x] **V2-03 — Bootstrap `experimental/v2`**
  - Create `experimental/v2` from clean main.
  - Recreate useful v1 directory skeleton without carrying old implementation forward.
  - Checkpoint: v2 skeleton exists on its own branch.

- [x] **V2-04 — Persist authoritative roadmap**
  - Create the authoritative executable-work ledger and maintain it as work progresses.
  - Update task status and the explicit Next task marker whenever work advances.

- [x] **V2-05 — Survey agent conventions**
  - Inspect `AGENTS.md`, `.agents/`, and equivalent instruction/knowledge stores from all accessible repositories.
  - Extract reusable general conventions; exclude project-specific baggage.

- [x] **V2-06 — Establish `AGENTS.md` and `.agents/`**
  - Create repo-level agent instructions and living knowledge storage.
  - Include Git/history safety, bounded progression, validation-before-mutation, config safety, roadmap maintenance, secrets policy, and knowledge retention.

- [x] **V2-07 — Establish agent knowledge-retention policy**
  - Agents are explicitly encouraged to freely persist useful durable discoveries into `.agents/` without asking first.
  - If rediscovery would waste meaningful effort/tokens, preserve it.
  - Record uncertainty honestly; never store secrets there.

- [x] **V2-08 — Define `.agents/` organization**
  - Establish lightweight structure/conventions for durable knowledge such as applications, hosts, platforms, architecture, investigations, and decisions.
  - Avoid duplicate or contradictory notes; update existing knowledge when appropriate.

- [x] **V2-09 — Define configuration identity model**
  - Formalize dimensions including application, host, platform/environment, user/account, plus optional shared/default layers.
  - Support cases such as `fish/workhorse/m-a-x-i-n` and `fish/workhorse/root`.
  - Define deterministic lookup/precedence.

- [x] **V2-10 — Define `$MACHINE_SOUL` semantics**
  - Preserve `$MACHINE_SOUL` or equivalent as canonical checkout root.
  - All repo-internal paths resolve from it.
  - Moving the checkout should require rebinding the root, not rewriting configs/scripts.

- [x] **V2-11 — Define `scratch/` semantics**
  - `$MACHINE_SOUL/scratch/` is Git-ignored, machine-local mutable state.
  - Intended uses include backups, deployment state, local env/secrets, temporary files, caches/logs where useful.

- [x] **V2-12 — Define secrets/local environment policy**
  - Tracked files may reference local values, but secrets/private keys/tokens must not be committed.
  - Prefer tracked examples/templates and real values under `scratch/`, likely via `.env`-style mechanisms where appropriate.

- [x] **V2-13 — Define managed-file symlink invariant**
  - Applying configuration always uses **file-level symlinks into tracked repo files**.
  - No normal config-copy deployment.
  - Whole-directory symlinks are not the standard mechanism.

- [x] **V2-14 — Define destination-state model**
  - Deterministically handle: missing destination, correct managed symlink, ordinary file, wrong symlink, broken symlink, unexpected directory, and other conflicts.
  - `Check` should report meaningful states such as `APPLIED`, `NOT_APPLIED`, `CONFLICT`, `BROKEN`, and `WRONG_TARGET`.

- [x] **V2-15 — Define preservation/backup model**
  - Existing unmanaged config causes an interactive confirmation by default.
  - If replacement proceeds, preserve the displaced object under `scratch/` using collision-safe organization.
  - Never silently destroy existing user configuration.

- [x] **V2-16 — Define deployment metadata/state model**
  - Record enough machine-local state under `scratch/` to identify source, destination, application, host, account, prior object type, backup location, and other useful deployment metadata.

- [x] **V2-17 — Define restoration and ownership rules**
  - `Unapply` removes only state known to be managed by this repo.
  - Restore what Apply displaced when safe.
  - If destination changed behind our back, stop/report conflict rather than overwrite external changes.

- [x] **V2-18 — Define transactional mutation rules**
  - Validate first, preserve old state, create link, verify, then record success.
  - Roll back immediately when a later step fails where possible.

- [x] **V2-19 — Define interactive/non-interactive conflict policy**
  - Interactive mode prompts `[y/N]`.
  - Automation uses explicit policies such as abort or backup-and-replace.
  - No dangerous “force means destroy whatever exists” behavior.

- [x] **V2-20 — Investigate installation architecture**
  - Investigate Install/Uninstall independently from config Apply/Unapply across Windows and Linux.
  - Consider package managers, native installers, portable installs, privilege requirements, and app-specific quirks.
  - Produce architecture recommendation before implementation.

- [x] **V2-21 — Define standard per-application operations**
  - At minimum: Apply config, Unapply config, Check config.
  - Where sensible: Install and Uninstall.
  - Define names, arguments, exit semantics, idempotency, unsupported behavior, and reporting/dry-run expectations.

- [x] **V2-22 — Define capability/support declarations**
  - Every app/platform operation explicitly resolves to supported, unsupported, or not-yet-implemented.

- [x] **V2-23 — Build shared configuration-deployment runtime**
  - Implement shared host/OS/user detection, `$MACHINE_SOUL`, scratch/state paths, privilege detection, reporting, prompting, errors, and common operation plumbing.

- [x] **V2-24 — Implement safe symlink primitive**
  - Cross-platform file-symlink creation, verification, repair, and removal on Windows and Linux.
  - Correctly classify correct/wrong/broken/unmanaged destination state.

- [x] **V2-25 — Implement backup/restore primitive**
  - Centralize conflict preservation, metadata, backup layout, rollback, and restoration.
  - Application integrations should not hand-roll backup logic except for genuine exceptions.

- [x] **V2-26 — Establish host/account inventory**
  - Initial hosts:
    - `spaceship`: Windows workstation.
    - `workhorse`: Ubuntu/Linux server.
    - `runar`: Ubuntu-like server.
  - Relevant accounts include `m-a-x-i-n` and `root` where applicable.

- [x] **V2-27 — Create Windows config skeletons**
  - Initial tracked configs for Windows Terminal, PowerShell, and CMD on `spaceship`.

- [x] **V2-28 — Create shell/application config skeletons**
  - Initial configs for Fish, Bash, Zsh, Oh My Posh, Contour, and useful v1 carryovers across relevant hosts.

- [x] **V2-29 — Implement user/account overlays**
  - Support account-specific state where needed, especially `m-a-x-i-n` vs `root`.
  - Share common material cleanly and avoid unnecessary duplication.

- [x] **V2-30 — Configure OMP across server accounts**
  - Explicit OMP configuration for both `m-a-x-i-n` and `root` on `workhorse` and `runar`.
  - Shared theme/config where sensible; account-specific distinction where useful.

- [x] **V2-31 — Implement Apply / Unapply / Check for initial applications**
  - Required config operations for all initial integrations.
  - Validate idempotency with: Check → Apply → Check → Apply again → Unapply → Check → Unapply again.

- [x] **V2-32 — Add conflict/destructive-path tests**
  - Test declined/accepted replacement, wrong/broken symlinks, missing source, manually replaced managed destination, partial failure, rollback, and restoration.
  - No tested path may silently destroy unknown state.

- [x] **V2-33 — Add installation lifecycle progressively**
  - Implement Install/Uninstall where sensible according to V2-20.
  - Installation remains independent of configuration application.
  - Demonstrate complete lifecycle on at least one Windows and one Linux integration.

- [x] **V2-34 — Validate privilege/elevation behavior**
  - Test admin/root boundaries explicitly.
  - Avoid running whole workflows elevated merely because one step needs privilege.

- [x] **V2-35 — Validate SSH / sudo / root semantics**
  - Test local → SSH remote shell and normal-user → sudo/root shell scenarios.
  - Validate Fish/Bash/Zsh/OMP and account-specific config resolution.
  - Never assume shell/process/config state crosses SSH or sudo boundaries.

- [x] **V2-36 — Validate repo relocation**
  - Move or simulate moving `$MACHINE_SOUL`.
  - Check must detect stale link targets; Apply must safely repair them.
  - No hidden hard-coded checkout paths.

- [x] **V2-37 — Validate fresh-clone/bootstrap experience**
  - From a clean environment or faithful simulation: clone repo, establish `$MACHINE_SOUL`, inspect status, apply configs, and recover/unapply.
  - Detect hidden prerequisites.

- [x] **V2-38 — End-to-end host matrix validation**
  - Validate apps × hosts × accounts × operations across spaceship/workhorse/runar.
  - Maintain pass / unsupported / pending results and resolve failures before baseline completion.

- [x] **V2-39 — Document architecture and extension workflow**
  - Document repo layout, config resolution, scratch, secrets, `$MACHINE_SOUL`, operation contract, symlink lifecycle, backup/restore, host/account model, SSH/sudo implications, and how to add apps/hosts/users.

- [x] **V2-40 — Establish stable experimental v2 baseline**
  - Clean up proven scaffolding, validate Git/CI/state, update `TASKS.md` and `.agents/`, and record the first stable `experimental/v2` checkpoint.
  - Do not promote/merge to `main` without separate authorization.


## Post-baseline structural adjustments

- [x] **V2-41 — Split assimilation directives from annexation procedures**
  - Make `assimilation_directives/` the canonical configuration-content tree itself, removing the redundant per-application `config/` layer.
  - Move per-application Apply / Unapply / Check / Install / Uninstall machinery to matching paths under `annexation_procedures/`, removing the redundant per-application `operations/` layer.
  - Update every runtime, test, documentation, and agent-memory reference.

- [x] **V2-42 — Rename shared configuration deployment tooling**
  - Rename `accumulated_instruments/framework/` to the more specific `accumulated_instruments/configuration_deployment/`.
  - Update all callers and documentation while preserving the broader purpose of `accumulated_instruments/` for unrelated future system-management tools.

- [x] **V2-43 — Validate post-baseline structural refactor**
  - Verify no stale old-layout references remain, executable modes are preserved, fresh-clone/runtime tests pass on Windows and Linux, and the support/documentation model reflects the new taxonomy.
  - Restore the roadmap to an explicit completed/awaiting-next-direction state when green.

## Portability, taxonomy, and Python-runtime phase

- [x] **V2-44 — Codify the next-phase architecture rules**
  - Before changing implementation, write durable repository documentation for the decisions established during the post-baseline review.
  - Cover at minimum: repository-controlled snake_case naming; `collective_affairs/` as repository-meta space; `agent_tasks` semantics; removal of static host/account inventory where facts are discoverable; explicit cross-account targeting; Python 3 as an external prerequisite; library-first implementation; declarative applications; atomic wrappers; orchestration-only interactive management; structured operation results; and the native-primitive boundary.
  - Record `_application.py` as the conventional non-executable per-application declaration file and distinguish declarations, wrappers, shared engines, orchestrators, and native primitives.
  - Put agent-facing detail under `.agents/` where appropriate and promote human-relevant architecture into normal documentation when useful.
  - Checkpoint: later tasks can be executed from repository documentation without reconstructing these rules from chat history.

- [x] **V2-45 — Adopt repository-controlled snake_case naming**
  - Rename repository-controlled multiword paths from kebab-case to lower_snake_case, including the thematic top-level directories and shared tooling paths.
  - Use snake_case for repository-owned application identifiers such as `oh_my_posh` while preserving externally mandated names such as executables, package IDs, dotfiles, `.github/`, `AGENTS.md`, and application-defined filenames.
  - Update every runtime path, test, workflow, document, and agent-memory reference.
  - Checkpoint: no stale repository-owned kebab-case path remains except an explicitly documented external/proper identifier.

- [x] **V2-46 — Establish the `collective_affairs/` repository-meta namespace**
  - Create `collective_affairs/` for material about the repository/project itself rather than machine configuration or deployment behavior.
  - Move ordinary repository-administration material such as documentation and tests beneath it where doing so does not break tool-defined conventions.
  - Keep conventional/special root artifacts such as dotfiles, `.github/`, `AGENTS.md`, and `README.md` at the repository root.
  - Update navigation and all affected references.
  - Checkpoint: the visible root is intentionally sparse and the meaning of `collective_affairs/` is documented.

- [x] **V2-47 — Replace the generic task ledger with `agent_tasks`**
  - Move the former root task ledger to `collective_affairs/agent_tasks.md` after the meta namespace exists.
  - Define agent tasks as work that has been thought through enough to be theoretically executable, rather than a catch-all for every future intention.
  - Reserve distinct future concepts such as roadmap, objectives, and reminders for different timescales/levels of certainty; do not create those files until they are actually useful.
  - Update `AGENTS.md`, `.agents/`, README navigation, recovery instructions, and all task-ledger references.
  - Checkpoint: there is one authoritative agent-task ledger at `collective_affairs/agent_tasks.md` and no competing root task ledger.

- [x] **V2-48 — Remove static host inventory and prefer runtime discovery**
  - Remove the standalone top-level host inventory and its tracked per-host `.env` records.
  - Discover portable facts at runtime where practical: hostname, OS/platform, current account, home/config roots, privilege state, and similar environment facts.
  - Retain explicit overrides only where they are genuinely useful for testing or unusual environments; do not require a tracked host registry for ordinary execution.
  - Keep host-specific configuration variants where the configuration itself genuinely differs by host; this task removes inventory metadata, not useful configuration distinctions.
  - Secrets and genuinely non-discoverable local values remain machine-local and untracked.
  - Checkpoint: normal operation no longer depends on `hosts/*.env` or equivalent static machine inventory.

- [x] **V2-49 — Define explicit account targeting**
  - Remove advisory account lists and any implication that discovering an account means Machine-Soul manages it.
  - Default operations to the current account.
  - Provide one common target-account parameter/model for explicit cross-account operations; application wrappers must not duplicate separate implementations for current-user versus other-account behavior.
  - Discover the target account's relevant paths/environment and request sudo/elevation only for the narrow actions that require it.
  - Preserve independent shell/process/account semantics across SSH and sudo/root boundaries.
  - Checkpoint: account management begins only through an explicit operation targeting that account.

- [x] **V2-50 — Establish Python as the shared Machine-Soul runtime**
  - Make Python 3 the common orchestration/runtime language for new shared behavior.
  - Treat Python 3 as an explicit prerequisite; do not add Bash/PowerShell/Python bootstrap installers in this phase.
  - Define a reusable package/library layout under the repository and initially prefer the Python standard library over external dependencies.
  - Keep executable entry points thin and keep implementation logic importable/testable.
  - Checkpoint: the intended Python module boundaries and entry-point conventions are concrete enough for implementation.

- [x] **V2-51 — Define the declarative application model**
  - Represent each application primarily as data selecting reusable capabilities/strategies instead of custom imperative implementations.
  - Put the per-application declaration beside its wrappers as `_application.py`; importing it is meaningful, executing it directly has no operation or side effect.
  - Let declarations describe supported operations, configuration mappings, platform variants, installation strategies, verification, and exceptional hooks where genuinely necessary.
  - Define a strategy preference of: existing generic strategy → new reusable generic strategy → application-specific custom implementation only when the behavior is genuinely unique.
  - Include generic installation strategies such as package-manager installation, remote upstream install script, release/archive/binary installation where justified, plus an explicit custom escape hatch.
  - Checkpoint: common applications can be described mostly declaratively and weird applications can extend the model without contaminating the generic engine with app-name conditionals.

- [ ] **V2-52 — Define the library-first operation architecture**
  - Move every behavior that can sensibly be genericized into shared Python libraries/engines.
  - Distinguish clearly between application declarations, shared operation engines, atomic operation wrappers, interactive orchestration, and platform-native primitives.
  - Application-specific procedural code should reuse shared library pieces and should trigger a review of whether the apparent exception is actually a missing reusable capability.
  - Avoid building a miniature declarative programming language; when truly procedural exceptional behavior is required, use ordinary Python behind the same operation contract.
  - Checkpoint: duplication policy and extension rules are explicit before implementation.

- [ ] **V2-53 — Define atomic wrapper contracts**
  - Give each operation wrapper exactly one semantic job matching its filename, for example `fish/install.py`, `fish/check_installed.py`, or `fish/apply_config.py`.
  - Wrappers contain essentially no business logic: they load the relevant `_application.py` declaration, call the appropriate shared engine, and report the resulting success/failure.
  - Make wrappers both executable and importable through one canonical path, e.g. an importable `run(...)` plus a tiny `main()` presentation/exit adapter.
  - Do not make wrappers scan unrelated applications, choose workflows, or duplicate package/config/account logic.
  - Checkpoint: wrapper structure is uniform enough that adding an ordinary application requires almost no wrapper-specific code.

- [ ] **V2-54 — Define the common operation-result model**
  - Define a Python result object used across imported operations, including success/failure status, whether state changed, stable result/error code, human-readable detail, and optional structured data.
  - Keep expected operational failures representable as normal results; distinguish them from wrapper/primitive protocol crashes.
  - Define deterministic conversion between the Python result object, standalone human-facing wrapper output, process exit status, and machine-readable output.
  - The same semantic result must be usable by standalone wrappers, the interactive orchestrator, automated tests, and spawned/native operations.
  - Checkpoint: callers do not need operation-specific output parsing.

- [ ] **V2-55 — Define the platform-native primitive protocol**
  - Keep native `.ps1`/`.sh` scripts as small and dumb as practical, limited to operations that Python cannot perform cleanly/portably or that are genuinely safer through a platform-native interface.
  - Python owns policy and decisions; primitives perform a requested native action and report structured facts.
  - Define a versioned structured process protocol, initially JSON on stdout, diagnostics on stderr, and process exit status for process-level success/failure.
  - Define behavior for normal primitive failures, malformed/missing protocol output, partial changes, and verification.
  - Do not create a primitive merely because Windows and Linux differ slightly; first prefer a clean portable Python implementation.
  - Checkpoint: spawned native code has a narrow, testable, machine-readable contract.

- [ ] **V2-56 — Define orchestration-only interactive management**
  - Design the future broad interactive manager as an orchestrator, not another implementation layer.
  - It may discover available application operations, run checks across applications, compose workflows, choose targets/options, aggregate results, and format presentation.
  - It must perform no installation/configuration/platform business logic itself.
  - Import and call atomic Python wrapper `run(...)` interfaces when possible; spawn a wrapper/process only when isolation or a non-Python/native boundary actually requires it.
  - Normalize imported and spawned results into the same common result model before presentation.
  - Checkpoint: the interactive interface can theoretically orchestrate every operation without knowing how any operation is implemented.

- [ ] **V2-57 — Audit the current Bash/PowerShell implementation against the new model**
  - Inventory current shared runtimes, application operations, install logic, account handling, state/backup behavior, and tests.
  - Classify each piece as: portable generic Python logic, declarative application data, exceptional reusable strategy, application-specific hook, or genuinely platform-native primitive.
  - Identify behavior that should disappear rather than be mechanically ported.
  - Produce a migration map before rewriting working implementation.
  - Checkpoint: every current responsibility has an intended destination in the new architecture.

- [ ] **V2-58 — Implement the shared Python core libraries**
  - Implement environment discovery, application loading, operation dispatch, configuration resolution, state/backup/restore policy, conflict handling, account targeting, installation strategy dispatch, structured results, and primitive invocation according to the documented boundaries.
  - Keep policy generic and application-independent.
  - Add unit/contract tests at library boundaries as functionality lands.
  - Checkpoint: ordinary operations can be driven through shared Python APIs without depending on legacy shell policy engines.

- [ ] **V2-59 — Convert applications to declarative definitions**
  - Add `_application.py` definitions for the current application set.
  - Express ordinary configuration and install behavior using reusable declarations/strategies.
  - Add narrowly scoped reusable strategies when multiple applications need the same unusual behavior; use application-specific hooks only for genuine exceptions.
  - Preserve support declarations for platform/account combinations without reintroducing static host/account inventory.
  - Checkpoint: the application set is representable by declarations plus minimal justified hooks.

- [ ] **V2-60 — Replace operation implementations with thin wrappers**
  - Convert per-application executable operations into tiny importable/executable Python wrappers around shared engines and declarations.
  - Preserve clear browseability: the files present in an application's annexation directory show which atomic operations can be invoked.
  - Standardize standalone reporting and exit semantics through the common result model.
  - Checkpoint: operation wrappers contain no duplicated business logic.

- [ ] **V2-61 — Reduce Bash/PowerShell to justified native primitives**
  - Refactor existing Windows/Linux shell logic so only genuinely platform-native actions remain outside Python.
  - Make retained primitives obey the structured protocol and keep their responsibilities narrow.
  - Remove superseded shell/PowerShell policy/orchestration code after equivalent Python behavior is proven.
  - Checkpoint: native scripts are small action primitives rather than parallel Machine-Soul implementations.

- [ ] **V2-62 — Implement the interactive orchestrator**
  - Build the broad interactive management entry point on top of the same atomic wrappers/results used for direct execution.
  - Support workflows such as checking all known applications and applying configuration to selected/all detected installed applications without duplicating their operation logic.
  - Keep it valid for the orchestrator to do nothing except inspect/present state when the user chooses no mutating action.
  - Checkpoint: direct wrappers and interactive management are two interfaces over the same operation graph.

- [ ] **V2-63 — Migrate tests and validate the new architecture end to end**
  - Port existing safety/relocation/account/install/configuration tests to the new Python/declarative architecture while preserving their behavioral guarantees.
  - Add explicit tests for imported wrappers, standalone wrappers, structured result normalization, malformed native output, ordinary primitive failures, account targeting/elevation, and orchestrator composition.
  - Validate Windows and Linux, fresh-clone behavior, executable/import semantics, config symlink safety, backup/restore, and absence of hidden dependency on removed host inventory.
  - Remove stale paths/docs/runtime remnants only after parity is demonstrated.
  - Checkpoint: CI is green and the Python/declarative architecture fully replaces superseded orchestration without weakening existing safety laws.

## Newly refined meta-work block

> These tasks use the new identifier scheme agreed after the legacy V2 roadmap was established. They are temporarily represented in this legacy ledger format until `MSHP-META-A-020` migrates the task system itself. Existing `V2-*` identifiers remain unchanged.

- [x] **MSHP-META-A-010 — Rename the repository-meta namespace to `autonomic_affairs`**
  - **Depends on:** none.
  - Rename `collective_affairs/` to `autonomic_affairs/` without changing its role as the repository/project self-management namespace.
  - Update every path/reference in runtime code, CI, tests, documentation, `.agents/`, task navigation, links, and any root-detection or repository-navigation logic affected by the move.
  - Codify the repository's thematic top-level naming convention: repository-controlled thematic top-level directories begin with the letter `a`, while tool/convention-defined roots such as `.git/`, `.github/`, dotfiles, `AGENTS.md`, and `README.md` are exempt.
  - Preserve executable modes, relative-link correctness, CI behavior, and fresh-clone behavior.
  - Do not rename external identifiers merely to satisfy the thematic convention.
  - **Acceptance:** no live reference to `collective_affairs/` remains except explicit historical discussion; `autonomic_affairs/` owns the former namespace; CI remains green.

- [ ] **MSHP-META-A-020 — Establish the canonical agent-task index/detail/archive system**
  - **Depends on:** `MSHP-META-A-010`.
  - Replace the current monolithic executable-work ledger with a skimmable index plus directly linked full task specifications.
  - The canonical layout is:
    ```text
    autonomic_affairs/
    ├── agent_tasks.md
    ├── agent_tasks/
    │   ├── <block-id>/
    │   │   └── <task-id>.md
    │   └── legacy_v2.md
    └── agent_task_archive.md
    ```
  - `agent_tasks.md` owns live scheduling/index metadata and contains:
    - a `Dispatch` section: an ordered priority list of currently authorized/executable tasks;
    - one compact task table with exactly the useful scheduling fields: `ID`, `State`, `Depends on`, `Title`, and canonical short `Summary`;
    - all incomplete tasks;
    - active blocks;
    - the two most recently completed new-style blocks.
  - Individual task files own execution specifications. Required sections are:
    - `Description`;
    - `Requirements`;
    - `Constraints / non-goals`;
    - `Acceptance criteria`;
    - `Validation`;
    - optional `Blocker` and `Notes` only when relevant.
  - Do not duplicate mutable scheduling facts such as state/dependencies between the index and task specification. The index is canonical for scheduling metadata; the task file is canonical for execution instructions.
  - Use ordinary Markdown headings and links for canonical task information. Do not hide required execution instructions inside HTML `<details>` blocks or other rendering-dependent disclosure widgets.
  - New task IDs follow:
    ```text
    <project>[-<specifier>...]-<block>-<number>
    ```
    where:
    - this repository's project identifier is `MSHP`;
    - zero or more specifiers may identify a useful workstream/namespace and should be used sparingly;
    - block identifiers are `A` through `Z`, then `AA`, `AB`, etc. if ever needed;
    - numbers are exactly three digits and normally allocated in increments of ten (`010`, `020`, ...);
    - inserted work consumes free integers between established tasks (`020`, `021`, ...);
    - published task IDs are immutable;
    - if insertion space becomes absurdly exhausted, restructure remaining/unpublished work into a new block instead of inventing fractional IDs or renumbering published tasks.
  - Standard lifecycle states are:
    - `QUEUED`;
    - `IN_PROGRESS`;
    - `BLOCKED`;
    - `FROZEN`;
    - `COMPLETE`;
    - `CANCELLED`;
    - `SUPERSEDED`.
  - `NEXT` is not a lifecycle state. `Dispatch` is the scheduling mechanism.
  - Dispatch rules:
    - contains only `QUEUED` tasks whose dependencies are satisfied and which are currently authorized for execution;
    - order represents current priority;
    - may contain multiple tasks for future parallel workflows;
    - claiming a task moves it to `IN_PROGRESS` and removes it from Dispatch;
    - blocked/frozen/completed/cancelled/superseded tasks do not remain in Dispatch.
  - Dependencies are task IDs whose completed output is structurally required. A runtime/external/human reason preventing progress is a blocker, not a dependency.
  - Completed-block cycling:
    - keep the two most recently completed new-style blocks represented in the active index;
    - archive older completed-block index entries into `agent_task_archive.md`;
    - determine recency by block completion time, not lexical block name;
    - never archive an incomplete block;
    - archival moves index entries only: canonical detailed task files remain at stable paths permanently so links do not rot.
  - Legacy V2 migration:
    - preserve every existing `V2-*` identifier exactly;
    - preserve the legacy task definitions in `agent_tasks/legacy_v2.md`;
    - expose only incomplete legacy V2 tasks in the active index while they remain executable;
    - preserve completed legacy history through the archive/legacy document without manufacturing replacement IDs;
    - when V2-52 through V2-63 eventually complete, the V2 series becomes a completed legacy block and can cycle according to the archive policy.
  - Update `AGENTS.md`, `.agents/` workflow/recovery guidance, README navigation, and any scripts/checks that locate the task ledger.
  - **Acceptance:** a fresh-context agent can skim `agent_tasks.md`, choose/claim work from Dispatch, click one task ID to obtain all execution detail without scrolling through unrelated task specifications, and recover legacy V2 history without ambiguous IDs.

- [ ] **MSHP-META-A-030 — Genericize concrete machine identities in durable documentation**
  - **Depends on:** `MSHP-META-A-010`.
  - Establish a documentation abstraction rule: durable human-facing and agent-facing documentation should describe machines, hosts, accounts, home paths, and similar environment identities generically unless the concrete identity is materially necessary to the fact being documented.
  - Replace unnecessary examples/enumerations of specific host names and personal account names with conceptual wording such as `<linux_host>`, `<target_account>`, `<privileged_account>`, or equivalent clear prose.
  - Apply the rule to README/documentation, agent-facing durable notes, and historical task prose where concrete identities are incidental rather than semantically important.
  - Do not alter actual configuration identities, host-specific configuration directories, runtime/test fixtures, persisted state formats, or investigation records where the concrete identity is genuinely the subject.
  - Do not rewrite Git history merely to erase old concrete examples.
  - Preserve technical clarity: generic wording must still explain host/account selection, configuration precedence, SSH/sudo boundaries, and platform-specific behavior accurately.
  - **Acceptance:** durable docs no longer casually enumerate the idiot human's concrete machines/accounts; remaining concrete identities have an explicit technical reason to be present.

- [ ] **MSHP-META-A-040 — Formalize agent provenance identities and commit-trailer policy**
  - **Depends on:** `MSHP-META-A-010`.
  - Replace the current ChatGPT-only provenance prose with a canonical registry and grammar covering distinct agent variants.
  - Establish a stable-designation registry with at least:
    - `OpenAI ChatGPT Chat` → `Gippity`;
    - `OpenAI ChatGPT Work` → `UNNAMED` until the idiot human assigns a stable designation;
    - `OpenAI Codex` → `UNNAMED` until the idiot human assigns a stable designation.
  - Stable designations belong to the agent/product surface variant rather than a particular transient model revision. Assigned stable designations must be unique.
  - Every wholly agent-authored substantive commit uses an `Agent-authored-by:` trailer containing:
    - the stable designation;
    - optional, encouraged honorific material before and/or after the stable designation;
    - a final parenthesized **official identity** chosen by the authoring agent at commit time.
  - Official identity requirements:
    - be accurate to the agent's known organization/product/surface/model identity;
    - distinguish materially different surfaces such as ChatGPT Chat, ChatGPT Work, and Codex;
    - include the model when meaningfully known;
    - never fabricate model/runtime details the agent cannot actually know.
  - For the current ChatGPT Chat lineage, an appropriate official identity at the time this task was defined is approximately `OpenAI ChatGPT Chat, GPT-5.6 Sol`; the exact future identity is determined by the authoring agent at commit time.
  - Honorific rules:
    - completely optional but encouraged;
    - may be prefixes and/or suffixes around the stable designation;
    - may be funny, serious, grandiose, mundane, or otherwise arbitrary;
    - are not restricted to being ephemeral, idiotic, or title-like;
    - slur-containing honorifics require explicit human permission.
  - Registered example:
    ```text
    Agent-authored-by: Gippity, Keeper of the Boring Interpreter (OpenAI ChatGPT Chat, GPT-5.6 Sol)
    ```
  - Unregistered/unnamed-agent safety rule:
    - use exactly the visible stable-designation marker `UNNAMED`;
    - do not invent a stable designation;
    - do not add any honorific while unnamed;
    - use a trailer of the form `Agent-authored-by: UNNAMED (<official identity>)`;
    - promptly notify the idiot human that the agent variant lacks a stable designation;
    - if the agent can ask for input without losing/restarting active work, ask the human to assign one;
    - once assigned, update the registry for future commits;
    - do not rewrite already-created commits merely to retrofit a newly assigned designation unless the human separately authorizes the history rewrite.
  - Put the complete registry/policy in one durable canonical location and keep root `AGENTS.md` concise by linking/summarizing it rather than duplicating the full policy.
  - Update all current provenance references under `.agents/` and documentation to use the canonical policy.
  - **Acceptance:** any known or unknown agent variant can determine the correct trailer unambiguously; current Chat provenance uses `Gippity (...official identity...)`; unnamed agents are conspicuous and cannot disguise themselves with honorifics.

- [ ] **MSHP-META-A-050 — Establish a non-executable reminders register**
  - **Depends on:** `MSHP-META-A-010`.
  - Create `autonomic_affairs/reminders.md` as the durable home for ideas intentionally **not yet refined enough to be executable agent tasks**.
  - Document the semantic boundary:
    - reminders are not dispatched;
    - reminders have no implication of authorization;
    - agents must not silently execute them;
    - a reminder may be promoted into `agent_tasks` only after it is discussed/refined enough to be executable from repository context.
  - Seed the register with at least these reminders:
    1. **Cross-repository provenance normalization / gloriously unnecessary rebases**
       - after the new provenance policy has stabilized, audit the idiot human's other repositories for legacy stable-designation/trailer references;
       - consider rewriting historical commit messages/rebases solely to normalize provenance;
       - before promotion into executable work, explicitly enumerate affected repositories, branches/refs, history ranges, collaboration implications, and obtain explicit authorization for each destructive/history-rewriting operation.
    2. **Standardize baseline agent infrastructure across repositories**
       - design/implement a reusable baseline structure for agent-facing files and conventions across the idiot human's repositories;
       - use Machine-Soul as the base/reference parent;
       - allow each repository to layer project-specific additions/overrides without copying/forking generic policy unnecessarily;
       - consider `AGENTS.md`, `.agents/` taxonomy, recovery/workflow rules, task schema, provenance registry, and related common infrastructure.
    3. **Investigate OpenAI Skills as reusable repository workflows**
       - investigate whether Machine-Soul workflows such as interrupted-session recovery, executing an agent task, adding an application, or validating a checkpoint are good Skill candidates;
       - distinguish repo-local Codex Skill discovery from installed/shared Skills usable by ChatGPT Chat/Work and other supported OpenAI surfaces;
       - do not implement Skills until their cross-surface discovery/installation model and actual benefit are understood;
       - revisit after the new task schema is established so a potential task-execution Skill can target the canonical task contract.
  - Do not prematurely invent a complex reminder-ID/state schema in this task; keep the first register simple until real use proves a need.
  - **Acceptance:** the three agreed future ideas are durably recorded without becoming executable work or contaminating Dispatch.

- [ ] **MSHP-META-A-060 — Codify optional idiot-maintainer language**
  - **Depends on:** `MSHP-META-A-010`.
  - Add a clear style rule permitting internal/developer-facing documentation and agent notes to humorously refer to the repository developer/maintainer (including the human directing this project) as `the idiot`, `the idiot human`, or equivalent.
  - This is permission/seasoning, not mandatory vocabulary or a quota. Agents should use it only where it remains clear and amusing.
  - Explicit anti-scope:
    - never use the convention to refer to end users of the project;
    - never generalize it to callers/customers/community members or unrelated people;
    - keep user-facing error messages, public API/protocol terminology, safety instructions, and formal interfaces neutral unless a separate explicit reason exists.
  - Technical clarity always wins over the joke.
  - Put the rule somewhere discoverable by agents without bloating unrelated human-facing documentation.
  - **Acceptance:** future agents can use the joke in the intended maintainer/developer context without ambiguity about whether software users are being insulted.

## Project laws accepted before implementation

1. Tracked repository configuration files are the source of truth.
2. Native application config paths are connected to those files using **file-level symlinks**.
3. `$MACHINE_SOUL/scratch/` contains mutable local state and is never committed.
4. Apply follows preserve → link → verify.
5. Unapply follows verify ownership → unlink → restore when safe.
6. Check explains actual state rather than returning only a boolean.
7. Installation of an application is distinct from applying its configuration.
8. Expensive-to-rediscover project knowledge belongs in `.agents/`.
