# Machine-Soul Hivemind Protocol — Experimental v2 Roadmap

This file is the authoritative source of truth for v2 progress and next actions.

## Status legend

- [ ] Pending
- [~] In progress
- [x] Complete
- [!] Blocked

## Next task

**V2-31 — Implement Apply / Unapply / Check for initial applications**

## Roadmap

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
  - Create this file and maintain it as work progresses.
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

- [x] **V2-23 — Build shared runtime/framework**
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

- [ ] **V2-31 — Implement Apply / Unapply / Check for initial applications**
  - Required config operations for all initial integrations.
  - Validate idempotency with: Check → Apply → Check → Apply again → Unapply → Check → Unapply again.

- [ ] **V2-32 — Add conflict/destructive-path tests**
  - Test declined/accepted replacement, wrong/broken symlinks, missing source, manually replaced managed destination, partial failure, rollback, and restoration.
  - No tested path may silently destroy unknown state.

- [ ] **V2-33 — Add installation lifecycle progressively**
  - Implement Install/Uninstall where sensible according to V2-20.
  - Installation remains independent of configuration application.
  - Demonstrate complete lifecycle on at least one Windows and one Linux integration.

- [ ] **V2-34 — Validate privilege/elevation behavior**
  - Test admin/root boundaries explicitly.
  - Avoid running whole workflows elevated merely because one step needs privilege.

- [ ] **V2-35 — Validate SSH / sudo / root semantics**
  - Test local → SSH remote shell and normal-user → sudo/root shell scenarios.
  - Validate Fish/Bash/Zsh/OMP and account-specific config resolution.
  - Never assume shell/process/config state crosses SSH or sudo boundaries.

- [ ] **V2-36 — Validate repo relocation**
  - Move or simulate moving `$MACHINE_SOUL`.
  - Check must detect stale link targets; Apply must safely repair them.
  - No hidden hard-coded checkout paths.

- [ ] **V2-37 — Validate fresh-clone/bootstrap experience**
  - From a clean environment or faithful simulation: clone repo, establish `$MACHINE_SOUL`, inspect status, apply configs, and recover/unapply.
  - Detect hidden prerequisites.

- [ ] **V2-38 — End-to-end host matrix validation**
  - Validate apps × hosts × accounts × operations across spaceship/workhorse/runar.
  - Maintain pass / unsupported / pending results and resolve failures before baseline completion.

- [ ] **V2-39 — Document architecture and extension workflow**
  - Document repo layout, config resolution, scratch, secrets, `$MACHINE_SOUL`, operation contract, symlink lifecycle, backup/restore, host/account model, SSH/sudo implications, and how to add apps/hosts/users.

- [ ] **V2-40 — Establish stable experimental v2 baseline**
  - Clean up proven scaffolding, validate Git/CI/state, update `TASKS.md` and `.agents/`, and record the first stable `experimental/v2` checkpoint.
  - Do not promote/merge to `main` without separate authorization.

## Project laws accepted before implementation

1. Tracked repository configuration files are the source of truth.
2. Native application config paths are connected to those files using **file-level symlinks**.
3. `$MACHINE_SOUL/scratch/` contains mutable local state and is never committed.
4. Apply follows preserve → link → verify.
5. Unapply follows verify ownership → unlink → restore when safe.
6. Check explains actual state rather than returning only a boolean.
7. Installation of an application is distinct from applying its configuration.
8. Expensive-to-rediscover project knowledge belongs in `.agents/`.
