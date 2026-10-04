
# Cross-repository agent baseline architecture

> **Status:** Research recommendation from `MSHP-AGENT-BASELINE-A`. This architecture is **not implemented**. No external repository modification is authorized by this document.

## Goal

Make generally useful agent infrastructure reusable across the maintainer's repositories without copying Machine-Soul-specific policy everywhere or making repository-local policy subordinate to invisible remote state.

The target outcome is:

- new repositories start with a strong generic agent baseline;
- existing repositories can deliberately adopt the baseline later;
- generic improvements can be proposed across consumers;
- repository-specific policy, tasks, knowledge, and CI remain locally authoritative;
- updates are reviewable and recoverable.

## Recommended repository roles

### `M-A-X-I-N/template` — bootstrap/copy baseline

Keep the existing GitHub template repository as the authoritative Git tree for **consumer-visible copied baseline files**.

It should eventually contain only material that genuinely belongs in generated repositories, such as:

- a thin root `AGENTS.md` entry contract;
- generic memory/read-order guidance;
- generic task/recovery protocol and empty state skeletons;
- provenance policy/skeleton;
- reminder/initiative lifecycle skeletons;
- repository-local profile placeholder;
- baseline manifest/state skeleton;
- thin consumer workflow callers where needed.

It should **not** contain:

- Machine-Soul's thematic/project directory taxonomy;
- Machine-Soul tasks, architecture, application/runtime knowledge, or CI check mapping;
- live shared workflow/action/updater implementation that should remain centrally maintained.

GitHub templates create independent repositories with new history. They are bootstrap snapshots, not an upstream synchronization relationship.

### Future shared agent-infrastructure/tooling repository

A separate future repository is recommended for **live shared implementation**:

- reusable workflows;
- composite actions;
- baseline status/adopt/update tooling;
- migration/schema helpers;
- generic validation/audit helpers.

Exact name, implementation language, and visibility are future decisions.

This role is deliberately separate because reusable workflows must live under the provider's `.github/workflows` tree, while GitHub template generation copies the template repository's files. Co-locating the roles would copy shared implementation into every consumer and create duplicate authority.

## Baseline philosophy

The baseline is a **governance kernel plus repository-local profile**, not a parent repository whose files must remain identical.

Prefer clear ownership over aggressive deduplication.

Every baseline-related artifact should fit one of these categories:

### Baseline-managed

Generic protocol expected to evolve with baseline releases.

Examples:

- root loader;
- generic workflow/recovery rules;
- generic task protocol/schema;
- memory doctrine;
- provenance protocol;
- thin CI callers.

### Seed-once local

Created during bootstrap, then owned locally.

Examples:

- repository mission/profile;
- initial task state/index;
- reminder contents;
- initiative contents;
- project-specific policy extension;
- local CI declaration.

### Always local

Never synchronized from the generic baseline.

Examples:

- actual tasks/claims/Dispatch/workspaces/archive history;
- project architecture/documentation;
- project `.agents` investigations/decisions/scar tissue;
- local CI checks/path relevance;
- product safety laws;
- intentional deviations.

### Shared executable dependency

Implementation stays central; consumer keeps a pinned reference.

Examples:

- generic CI policy workflow;
- provenance/metadata validator;
- baseline status/audit action.

## Root agent entry

The root `AGENTS.md` should be deliberately thin and stable.

Its generic responsibility is to tell an agent to:

1. trust tracked repository state over remembered conversation state;
2. read generic baseline procedure;
3. read repository-local profile/policy;
4. inspect executable-work state before substantive work;
5. load only task-relevant memory/documentation;
6. follow generic recovery/Git/authority precedence.

Repository mission, directory ownership, product rules, architecture, and local CI belong in local policy rather than the generic loader.

Avoid partial-file ownership markers when separate files can express ownership cleanly.

## Task/work governance

The reusable protocol should preserve the strongest MSHP concepts:

- explicit task lifecycle states;
- Dispatch as executable authorization;
- Active claims as coordination locks;
- dependencies/order;
- task workspaces for temporary tracked cross-context knowledge;
- immutable task IDs;
- terminal block archival;
- reminders and initiatives as explicitly non-executable context;
- deliberate promotion into executable tasks.

Future baseline design should separate **static task protocol** from **dynamic repository task state** more cleanly than current MSHP so protocol updates do not repeatedly conflict with live task rows.

## Agent memory

Baseline-managed:

- durable-memory placement rules;
- temporary task-workspace distinction;
- fresh-session reading order;
- historical notes are on-demand;
- promote human-relevant durable facts to human documentation;
- never store secrets.

Repository-local:

- every actual project investigation, decision, architecture note, platform/application quirk, and scar-tissue record.

The baseline may provide structure, not project memory.

## Git, lineage, and provenance

Strong generic defaults:

- additive history;
- no destructive rewrite of established history without explicit authority;
- recoverable agent lineage namespaces;
- discovering a lineage does not authorize adopting it;
- task claims are coordination locks, not recovery credentials;
- coherent checkpoint discipline;
- explicit agent-authorship provenance.

Repository-local profiles may explicitly tighten or opt out of conventions when a project genuinely differs.

## CI

Treat the current MSHP selector as a reusable **architecture pattern**, not reusable local policy.

### Shared core candidate

- event normalization;
- push/PR Git-range derivation;
- override parsing;
- fail-safe ambiguity behavior;
- commit/provenance validation framework;
- check-registry validation;
- check-to-runner coalescing;
- run-history/coverage primitives.

### Repository-local declaration

- check IDs;
- commands;
- path relevance;
- runner/platform requirements;
- destructive/isolation requirements;
- security-analysis languages;
- cadence/exceptions.

A thin local workflow should own the consumer's GitHub events/permissions and call a **full-SHA-pinned** shared reusable workflow.

## Baseline state and versioning

A managed consumer should be able to identify:

- baseline source;
- baseline release;
- exact source commit or an immutable release identity resolvable to it;
- baseline schema;
- selected profile/modules;
- intentional deviations/detached components;
- exact shared executable pins.

Use separate concepts for:

- **release version** — human/orderable, likely semantic-style;
- **Git SHA** — exact immutable provenance;
- **schema version** — structural/migration compatibility.

Shared Actions/reusable workflows should be pinned to full SHAs. Human-readable release tags may be documented alongside them, and Dependabot can propose reviewed update PRs.

## New repository bootstrap

Future default flow:

1. create repository from `M-A-X-I-N/template`;
2. fill in repository-local profile/state;
3. record baseline release/schema/profile;
4. configure optional pinned shared runtime modules;
5. commit project-specific setup normally.

The template's default branch should represent a stable baseline release, not arbitrary unreleased development state.

## Existing repository adoption

Do not fake template ancestry.

Future adoption should:

1. inspect current governance;
2. select target baseline/profile;
3. compare target baseline with existing files;
4. classify baseline-compatible, local, and conflicting material;
5. produce a reviewable adoption diff/PR;
6. apply necessary structural migrations;
7. only then record the repository as baseline-managed.

## Ongoing baseline updates

Separate read-only detection from mutation.

### Status

Report current baseline, available target, schema/migration path, and shared dependency updates.

### Plan

Reconstruct old baseline state, compare local evolution, load target baseline, and produce proposed changes/conflicts.

### Apply

On a recoverable branch/worktree:

- three-way reconcile baseline-managed content;
- apply ordered migrations;
- preserve local/detached content;
- surface semantic conflicts;
- update manifest/pins only after successful transformation;
- validate;
- merge through ordinary repository history.

The research strongly favors Copier-like three-way lifecycle semantics, but does not yet choose Copier over a simpler direct Git-tree implementation.

## Rollback

A baseline update should be one coherent consumer checkpoint/PR containing:

- baseline-derived changes;
- manifest release/schema/provenance;
- shared executable pin changes;
- migration results;
- setting changes where included.

Primary rollback is ordinary Git revert.

External repository-setting migrations require separate before/after recovery information where automatic reversal is not guaranteed.

## GitHub repository-side settings

Template generation does not provide a generic settings-inheritance system.

Future reconciliation of settings such as Actions permissions, rulesets, variables, environments, or security settings should be explicit:

- baseline default;
- local intentional deviation;
- observed current setting;
- proposed diff;
- authorized apply;
- rollback information.

Do not design the current personal-account fleet around organization-only rulesets/custom properties.

## Profiles/modules

Start small.

Conceptual **standard baseline**:

- agent entry/read order;
- memory doctrine;
- Git/recovery/lineage;
- task/Dispatch/claims/archive;
- reminders/initiatives;
- provenance;
- baseline manifest/local profile.

Potential optional modules:

- centralized CI;
- CodeQL/security;
- scheduled coverage reconciliation;
- repository-setting reconciliation.

Avoid profile explosion until real repositories prove distinct needs.

## Research-backed non-goals

Do not:

- copy MSHP wholesale;
- use remote `template@main` as invisible runtime policy;
- overwrite local policy during updates;
- synchronize whole repositories;
- make baseline history an upstream Git merge topology;
- put every historical investigation into startup context;
- silently modify `main` from scheduled update automation;
- depend on organization-only GitHub features for the current personal-account repository fleet.

## Implementation questions still requiring experiments

1. direct Git-tree three-way updater versus Copier;
2. neutral generic consumer paths/names;
3. maintainer-global versus repo-local provenance registry entries;
4. exact default profile/module boundary;
5. stable template branch/tag release mechanics;
6. updater packaging/runtime;
7. v1 scope for repository-setting reconciliation;
8. adoption behavior for heavily customized existing repositories;
9. whether shared updater/workflow components need independent release trains.

## Proposed future implementation order

1. Specify neutral baseline contract, ownership model, manifest, and local profile.
2. Build the first stable consumer-visible baseline in `M-A-X-I-N/template`.
3. Create shared tooling/runtime repository only with separate human authorization.
4. Prototype bootstrap, adoption, update, conflict, migration, rollback, and pinned-runtime updates.
5. Adopt MSHP as a demanding consumer without erasing MSHP-specific policy.
6. Migrate other repositories deliberately through adoption PRs.
7. Add fleet automation only after the manual lifecycle is proven.

## Evidence

Full research and source references are preserved with archived task block `MSHP-AGENT-BASELINE-A`.

The most important research inputs were:

- GitHub repository-template mechanics;
- reusable workflow/action distribution and access;
- account/organization-level GitHub governance capabilities;
- Copier/Cruft template lifecycle models;
- Git submodule/subtree alternatives;
- Dependabot GitHub Actions reference updates;
- GitHub full-SHA secure-use guidance;
- immutable GitHub releases.

