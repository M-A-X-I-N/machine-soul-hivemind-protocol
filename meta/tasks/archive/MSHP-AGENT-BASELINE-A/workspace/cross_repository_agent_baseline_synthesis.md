
# MSHP-AGENT-BASELINE-A-070 — Cross-repository agent baseline synthesis

Research date: 2026-10-04.

## Status

This document is a **research recommendation, not an implemented architecture**.

No repository other than MSHP was modified during MSHP-AGENT-BASELINE-A. In particular, `M-A-X-I-N/template` remained read-only throughout the research block.

## Executive recommendation

Use a **hybrid, versioned baseline** with two repository roles:

1. **`M-A-X-I-N/template` — copied baseline / GitHub template**
   - stays a GitHub template repository;
   - contains only files that should actually appear in newly generated consumer repositories;
   - is the authoritative Git tree for copied baseline releases;
   - exposes a latest-stable default baseline through its template/default branch;
   - carries no project-specific MSHP content.

2. **Future shared agent-infrastructure/tooling repository — live shared implementation**
   - name intentionally undecided;
   - contains reusable workflows/actions and baseline update/adoption tooling;
   - is referenced by consumers with exact commit SHAs;
   - is not itself used as the GitHub template, so implementation/source files are not copied into every consumer.

The consumer repository remains the ultimate authority. The remote template/infrastructure repositories only propose updates or supply explicitly pinned executable dependencies.

The baseline should be a **small governance kernel plus a repository-local profile**, not “copy Machine-Soul’s agent folder everywhere.”

## Why two repository roles

### Why the GitHub template matters

A GitHub template is ideal for initial bootstrap:

- copies the repository’s files/directory structure;
- can generate a new independent repository through GitHub UI/CLI/API;
- starts the consumer as a new single-commit history rather than a fork;
- requires no custom bootstrap tool for the common/default case.

That makes the existing `M-A-X-I-N/template` repository directly useful.

### Why the template should not also be the live shared runtime

GitHub reusable workflows must live under `.github/workflows` in the repository that provides them.

GitHub template generation copies the template repository’s files.

If live reusable workflow/action/updater implementation lived in the same default-branch tree as the GitHub template, every generated repository would receive local copies of implementation that are supposed to be centrally shared. That would create:

- dead/duplicate local workflow implementations;
- unclear authority between the copied version and the centrally referenced version;
- needless baseline-update churn;
- coupled release cadence between copied policy files and executable runtime;
- source/tooling files in consumers that do not belong to the project.

Possible hacks such as keeping runtime files on a special non-default branch are technically imaginable but operationally opaque and contrary to the fresh-agent discoverability goal.

Therefore the copied baseline and live shared implementation should be separate repository roles.

## Role of `M-A-X-I-N/template`

### What should eventually live there

Only consumer-visible baseline material.

Conceptual categories:

- thin root `AGENTS.md` entry contract;
- generic agent-memory/read-order guidance;
- generic work/task/recovery protocol;
- generic provenance policy/skeleton;
- reminder/initiative lifecycle skeletons;
- task/index/archive skeletons;
- repository-local profile placeholder/skeleton;
- baseline manifest/state skeleton;
- thin GitHub workflow callers required in the consumer;
- optional Dependabot configuration for pinned shared GitHub Actions/reusable workflow dependencies;
- generic documentation/source-of-truth skeletons that truly belong in every selected profile.

### What must not be copied from MSHP

- Machine-Soul thematic directory taxonomy such as `autonomic_affairs`, `annexation_procedures`, etc.;
- Machine-Soul configuration/symlink safety laws;
- existing MSHP tasks/reminders/initiatives;
- MSHP CI check IDs/path classifier;
- application/runtime/platform memories;
- dated investigations or migration history;
- scrcpy/tool-specific notes;
- implementation of the central shared runtime/updater.

The future baseline should use **neutral generic paths/names**. The exact path layout remains an implementation-design question; the research does not bless MSHP’s thematic control-plane names as generic.

## Template release discipline

Because GitHub template generation uses the template repository’s branch contents rather than a release parameter, the default branch used for generation should represent a **stable baseline**, not arbitrary unreleased development state.

Recommended operational principle:

- baseline development happens on ordinary feature/agent branches;
- a release checkpoint advances the template’s default branch to the new stable baseline;
- that release is tagged/released;
- consumers generated from the GitHub template therefore receive the latest stable baseline rather than an arbitrary development snapshot.

The exact release automation is future implementation work.

## Ownership model inside consumers

Every tracked baseline-related artifact should fall into a clear ownership class.

### 1. Baseline-managed

Generic files/components whose evolution should be reconciled from later baseline releases.

Examples:

- thin root agent loader;
- generic workflow/recovery protocol;
- generic task protocol/schema;
- generic memory doctrine;
- generic provenance protocol;
- thin CI callers.

### 2. Seed-once local

Files created by bootstrap to give a repository a starting structure, but whose contents become repository-local immediately.

Examples:

- repository mission/profile;
- initial empty task ledger/state;
- reminder contents;
- initiative contents;
- project-specific policy extension;
- local CI check declaration.

The baseline may validate their schema but should not overwrite their repository-specific content.

### 3. Always local state/knowledge

Never synchronized from the baseline.

Examples:

- task rows/specs/workspaces/archive history;
- claims/Dispatch;
- reminders and initiative files;
- project architecture;
- project `.agents` memories/investigations/decisions;
- local check/path/runner definitions;
- project safety rules;
- explicit deviations.

### 4. Shared executable dependency

Not copied as implementation. Consumer stores only a pinned reference/caller.

Examples:

- reusable CI policy workflow;
- generic metadata/provenance validator;
- baseline status/audit action;
- other deterministic shared workflow/action components.

This “seed-once” distinction is a distribution behavior, not a new source-of-truth authority: after bootstrap, those files are local.

## Root agent entry architecture

The current MSHP root `AGENTS.md` is too project-specific to copy.

The future root file should be thin and stable. Conceptually it should tell an agent:

1. tracked repository state beats remembered conversation state;
2. read the generic baseline procedure;
3. read the repository-local profile/policy;
4. inspect executable-work Dispatch/state before substantive work;
5. read only task-relevant memory/docs;
6. follow generic recovery/Git/authority precedence.

Repository mission, directory ownership, product safety laws, application architecture, and local CI policy belong in the repository-local profile rather than the generic root loader.

Avoid partial-file ownership markers such as “BEGIN BASELINE” where separate files can express ownership cleanly.

## Work/task system architecture

The generic baseline should preserve the strongest MSHP governance ideas:

- explicit task states;
- Dispatch as executable authorization;
- Active claims as coordination locks;
- dependency/order semantics;
- task workspaces for temporary tracked cross-context knowledge;
- terminal block archival;
- immutable task IDs;
- reminders and initiatives as non-executable context;
- explicit promotion from non-executable context into tasks;
- recovery lookup/read order.

But **static task protocol and dynamic task state should be separated more cleanly than current MSHP**.

Recommended future shape:

- baseline-managed task protocol/schema document;
- seed-once/local task index/state file;
- local task block/spec/workspace/archive contents.

This prevents every baseline task-protocol improvement from becoming a merge conflict with a repository’s live task state.

## Agent-memory architecture

Baseline-managed:

- what belongs in durable agent memory;
- what belongs in temporary task workspace;
- startup reading order;
- historical investigations are on-demand;
- promote durable human-relevant facts to human docs;
- never store secrets.

Repository-local:

- every actual project investigation;
- decisions;
- architecture scar tissue;
- platform/application/tool notes;
- host-specific facts.

The baseline may seed empty directory conventions but must not ship MSHP’s memory contents.

## Provenance architecture

Baseline-managed:

- provenance trailer semantics;
- distinction between authoring agent and accountable operator;
- behavior when a model/designation is unknown;
- generic registry format.

Open policy question for implementation:

- whether stable designations such as `Gippity` are global maintainer-wide registrations or repository-local data.

Research preference:

- if the identity is meant to represent the same authoring agent across the maintainer’s repositories, keep a baseline-wide registry plus optional local additions;
- otherwise keep registrations local.

Do not duplicate the same designation independently in every repo without an ownership rule.

## Git, lineage, and recovery architecture

Strong baseline-managed defaults:

- additive Git history;
- no force/rebase/drop/squash of established history without explicit authority;
- coherent recoverable checkpoints;
- agent lineage namespace;
- branch discovery is never recovery authority;
- recovery requires explicit human/current-conversation lineage authority;
- task claims do not themselves confer recovery authority.

Repository-local profile may explicitly opt out or tighten:

- default branch name;
- whether agent lineages are used;
- release/maintenance branch rules;
- monorepo-specific worktree conventions.

Deviations must be explicit rather than hidden edits to baseline protocol.

## CI architecture

### Consumer-local event shell

GitHub event triggers and repository permissions live in the consumer.

A thin local workflow should:

- declare push/PR/manual/schedule events chosen by that repository/profile;
- request minimal permissions;
- call a pinned shared reusable workflow;
- pass/reference the local CI policy declaration.

### Shared generic CI core

Future live shared implementation can own:

- event normalization;
- push/PR Git range mechanics;
- explicit selector parser;
- fail-safe unknown/ambiguous behavior;
- metadata/provenance validation framework;
- logical-check registry validation;
- runner coalescing machinery;
- generic Actions-history/coverage primitives;
- generic output/interface contract.

### Repository-local CI declaration

Must define:

- logical checks;
- commands/workflows;
- relevant paths/rules;
- runner/platform requirements;
- isolation/destructiveness;
- security analysis languages;
- optional schedule/cadence deviations;
- local exceptions.

Never ship MSHP’s check registry/path map as the generic baseline.

## Future shared-infrastructure/tooling repository

This repository is recommended but **not created by this research**.

Conceptual responsibilities:

- reusable workflows;
- composite actions;
- baseline updater/adopter/status tooling;
- migration engine/schema tooling;
- deterministic baseline validation helpers;
- possibly machine-readable release metadata.

It should be public unless later security/private-source needs argue otherwise; a public source gives straightforward reusable-workflow access from public/private consumers without personal-account private-sharing constraints.

Exact name/visibility/package language remain future decisions.

## Baseline manifest

Every managed consumer should eventually carry local machine-readable baseline state.

Conceptual fields:

- baseline source repository;
- baseline release;
- baseline schema;
- selected profile/modules;
- baseline source commit or resolvable immutable release identity;
- intentionally detached/disabled components;
- explicit local deviations;
- shared executable pins/expected component versions where diagnostically useful;
- updater/tool version used for the latest migration where relevant.

Important subtlety:

A GitHub template repository cannot trivially commit a file containing the SHA of **that same commit**.

Therefore pure template bootstrap should not rely on self-embedded current SHA.

Recommended options:

- template file records stable release + schema; updater resolves the immutable release/tag to exact SHA;
- first managed `status/adopt/update` can record/cache the resolved exact source SHA;
- a future external release-rendering process could stamp a source SHA if architecture later changes to source-repo → rendered-template-repo.

The research recommends the simpler first model unless implementation evidence demands a generated mirror.

## Version model

Use separate identities.

### Baseline release

Human/orderable release, likely semantic-style `vMAJOR.MINOR.PATCH`.

Potential compatibility semantics:

- MAJOR — baseline contract/schema compatibility break or significant manual migration;
- MINOR — backward-compatible capability/profile addition;
- PATCH — compatible fixes/documentation/implementation changes.

Exact policy must be written before first release.

### Exact source identity

Immutable Git commit SHA resolved from the baseline release/ref.

### Baseline schema

Monotonic structural/interface schema used by updater/migration logic.

### Shared executable components

Full-length Git SHA in `uses:` references.

Optionally annotate SHA with release/tag comment for humans/Dependabot.

GitHub Dependabot can raise PRs updating Actions and reusable-workflow refs.

### Immutable releases

Where practical, enable GitHub immutable releases for stable tags/assets, while still using exact SHA provenance.

## New repository bootstrap flow

Recommended future flow:

1. Human chooses **Use this template** on `M-A-X-I-N/template` for the standard/default profile.
2. New independent repository contains only consumer-facing baseline skeleton.
3. Repository-local profile/state is filled in.
4. Baseline manifest records release/schema/profile.
5. Shared runtime callers, if enabled, use full-SHA-pinned dependencies.
6. Initial repository-specific task/CI/profile setup happens as ordinary consumer commits.

A future CLI may offer richer profile/parameter selection than GitHub’s native template UI, but native template creation should remain usable for the common case.

## Existing repository adoption flow

Never fake template ancestry.

Recommended future `adopt` process:

1. inspect existing agent/governance infrastructure;
2. choose target baseline release/profile;
3. render/read target baseline separately;
4. classify existing files as matching baseline, local policy/state, compatible customization, or conflict;
5. produce an adoption plan/diff;
6. migrate generic/local boundaries where needed;
7. open/review a normal adoption PR;
8. only after successful reconciliation record baseline manifest/version/pins.

A repository does not become “managed” merely because a manifest was written.

## Ongoing update flow

Separate detection from mutation.

### Read-only status

`status/check-update`:

- read manifest;
- resolve current release/provenance;
- discover supported newer release;
- report schema/migration path;
- report shared component updates;
- make no changes.

### Plan

`plan-update/diff`:

- reconstruct old baseline-managed state;
- compare consumer local evolution;
- load target baseline;
- compute three-way reconciliation;
- list structural migrations and settings changes;
- show conflicts/deviations;
- make no authoritative change.

### Apply

`update`:

- run on clean/recoverable branch/worktree;
- reconcile baseline-managed files;
- apply ordered structural migrations;
- leave semantic conflicts for review;
- never touch local/detached components silently;
- update manifest/pins only on successful transformation;
- run repository validation;
- deliver as ordinary PR/checkpoint.

### Scale-up

Start with manual human-invoked updates.

Later, if fleet size warrants:

- scheduled read-only update checks;
- Dependabot for shared refs;
- a GitHub App/controller that creates baseline update PRs.

Do not begin with a privileged fleet-wide bot.

## Reconciliation semantics

Adopt a Copier-like model conceptually:

- reconstruct old baseline;
- calculate local evolution;
- obtain new baseline;
- reapply/reconcile local evolution;
- surface conflicts normally.

Copier is a serious implementation candidate/reference, but **not selected as mandatory architecture**.

Reason:

The recommended baseline/local separation may be simple enough that a smaller direct Git-tree three-way updater fits better and preserves the GitHub-template-as-authoritative-tree model.

A future prototype should compare:

1. Copier-backed lifecycle;
2. simpler direct baseline-release tree reconciliation.

Do not reinvent merge semantics casually; use existing proven machinery where it fits.

## Repository-side GitHub settings

GitHub template does not provide a general repository-settings inheritance system.

Future settings reconciliation should be explicit and secondary to file baseline:

- desired default in baseline/profile;
- local explicit deviation;
- inspect actual GitHub resource;
- report desired-vs-observed diff;
- apply only through authorized migration/update;
- record rollback information where possible.

Examples:

- Actions permissions;
- rulesets/branch protection;
- repository variables;
- security settings;
- repository environments.

For the current personal-account fleet, do not design around organization-only central rulesets/custom properties.

## Account-level `.github` defaults

A public personal-account `.github` repository can provide supported default community-health files.

This is useful but orthogonal.

Future work may use it for:

- CONTRIBUTING;
- SECURITY;
- support/issue templates;
- other GitHub-supported defaults.

Do not confuse it with the agent baseline; it cannot centrally overlay arbitrary `AGENTS.md` or task/memory files.

## Profiles/modules

Avoid making every capability mandatory.

Initial conceptual profile recommendation:

### Standard baseline

- root agent entry;
- memory doctrine;
- Git/recovery/lineage;
- task/Dispatch/claims/archive;
- reminders/initiatives;
- provenance;
- baseline manifest/local profile.

### Optional modules

- centralized CI policy;
- CodeQL/security analysis;
- scheduled coverage reconciliation;
- repository-setting reconciliation;
- specialized research-memory taxonomy.

Do not create profile explosion before real repositories demonstrate meaningful classes.

## Update conflict rules

Unknown state must fail visible, not choose baseline by default.

At minimum distinguish:

- baseline-only change;
- local-only change;
- clean independent merge;
- semantic conflict;
- intentionally detached/local-owned component;
- mandatory structural migration;
- removed baseline component with local data.

A consumer’s explicit local deviation outranks the remote baseline until a reviewed migration changes that decision.

## Rollback

Baseline update should land as one coherent consumer checkpoint/PR containing:

- baseline-derived file changes;
- manifest version/schema/provenance;
- shared executable pin changes;
- migration outputs;
- repository-setting declarations/changes where included.

Primary rollback is normal Git revert.

External GitHub setting migrations must separately record before/after state and manual rollback when automatic reversal is impossible.

## Security model

### Shared runtime

- full SHA pins;
- least-privilege workflow permissions;
- reviewed Dependabot/update PRs;
- optional immutable releases/tags for human release identity;
- public source preferred if no secrecy requirement.

### Baseline updates

- remote baseline is untrusted proposal until reconciled/reviewed;
- migration code is trusted executable code and must be pinned/reviewed;
- no direct scheduled mutation of `main`;
- no automatic deletion of unique local content;
- no hidden remote runtime policy through moving `@main` references.

## Why not make `template` itself the only repository?

Rejected as the primary recommendation.

Co-locating consumer-visible template files with reusable workflow/action/updater implementation would cause GitHub template creation to copy those implementation files into consumers.

It also couples two different concerns:

- copied policy/schema release lifecycle;
- live executable dependency lifecycle.

A separate runtime/tooling role costs another repository but produces materially clearer ownership and consumer trees.

If future implementation proves the runtime is tiny enough to copy intentionally, this decision can be revisited; the current evidence favors separation.

## Why not introduce an authoritative source repo plus generated `template` mirror immediately?

Also not the initial recommendation.

A source → rendered-template mirror becomes valuable when:

- strong parameterized rendering is required;
- template source files should not appear in consumers;
- multiple rendered profiles are required;
- a tool such as Copier fundamentally needs a different source shape.

But it adds another synchronization/release step and makes the existing `template` repo a generated artifact rather than the simple baseline source.

The A-050 ownership split aims to reduce parameterization enough that `template` can remain the authoritative copied file tree.

Future implementation should only add a third/source-render split if a prototype proves it necessary.

## Research traceability

### A-010 — Template mechanics

Established:

- bootstrap copy, not fork;
- one-commit independent history;
- default/all branch semantics;
- no native template sync;
- file content vs repository settings distinction.

### A-020 — Reuse inventory

Established:

- generic governance kernel;
- parameterized CI concepts;
- MSHP-specific product/domain material excluded;
- dependency clusters among task/memory/recovery/provenance rules.

### A-030 — Distribution mechanisms

Established:

- template for bootstrap;
- reusable workflow/action for live execution;
- account `.github` defaults are narrow;
- org-only rulesets/workflow templates/custom properties are not current personal-account solution.

### A-040 — Synchronization

Established:

- provenance/version state is required;
- three-way/replay reconciliation beats overwrite;
- PR delivery beats silent mutation;
- Copier/Cruft are strong prior art;
- existing repos require explicit adoption;
- Dependabot can update shared Actions refs.

### A-050 — Ownership boundaries

Established:

- baseline kernel + local profile + local state;
- thin root loader;
- static protocol separate from dynamic task state;
- CI generic core + local declaration;
- explicit deviations/detachment.

### A-060 — Version/migration

Established:

- human release + exact SHA + schema;
- exact SHA pins for shared executable code;
- intentional lag is supported;
- structural migrations explicit/ordered;
- ordinary Git revert as primary rollback.

## Unresolved questions requiring future implementation experiments

These are **not research failures**; they require actually building/using the system.

1. **Direct Git-tree updater vs Copier**
   - Can the ownership split make direct three-way reconciliation small/reliable enough?
   - Does Copier add useful conflict/migration machinery without forcing awkward source layout?

2. **Neutral consumer path layout**
   - Exact generic replacements for MSHP’s thematic `autonomic_affairs` paths.
   - How many generic policy files remain readable without a maze.

3. **Provenance registry scope**
   - Maintainer-global stable agent identities versus repo-local registrations.

4. **First profile boundary**
   - Whether task system is mandatory in the default standard profile.
   - Whether centralized CI begins optional or standard.

5. **Template stable-branch release mechanics**
   - Exact branch/tag/release procedure that guarantees GitHub template creation receives a declared stable baseline.

6. **Updater packaging/runtime**
   - Python CLI/package, standalone script, action, or another form.
   - Manual-first invocation interface.

7. **Settings reconciliation scope**
   - Which GitHub repository-side settings are worth managing in v1 versus deliberately leaving manual.

8. **Legacy adoption**
   - How accurately an existing repository can be classified/adopted without excessive manual mapping.

9. **Shared infrastructure release cadence**
   - One release train for updater + reusable workflows initially, or component-specific versions if real pressure appears.

## Proposed future implementation roadmap

This is a proposal only. **No implementation task is queued or authorized by this research block.**

### Phase B1 — Specify the neutral baseline contract

- choose neutral consumer paths;
- define root loader/local profile;
- define task/memory/provenance schemas;
- define baseline manifest;
- define ownership classes and deviation representation;
- define release/schema semantics.

### Phase B2 — Build the first baseline release in `M-A-X-I-N/template`

- populate only consumer-visible baseline files;
- establish latest-stable branch/release process;
- validate GitHub-template bootstrap output;
- keep project-specific/template-source implementation out of consumer tree.

### Phase B3 — Establish shared tooling/runtime repository

- create repository only after explicit human authorization;
- implement minimal pinned reusable workflow/action core;
- implement or package status/adopt/update tooling;
- publish immutable/versioned releases as appropriate.

### Phase B4 — Prototype lifecycle against controlled consumers

Test separately:

- fresh GitHub-template bootstrap;
- existing repository adoption;
- clean baseline update;
- local customization preserved by update;
- semantic conflict;
- schema migration;
- rollback;
- pinned runtime Dependabot update.

Do not fleet-roll out before these prove the model.

### Phase B5 — Adopt MSHP as an advanced consumer

MSHP is useful as a demanding real consumer because its current governance is the source material, but migration must preserve local thematic/product policy rather than overwrite it.

### Phase B6 — Migrate other repositories deliberately

For each repository:

- classify profile;
- adoption PR;
- explicit deviations;
- validation;
- no bulk blind overwrite.

### Phase B7 — Add automation only after manual lifecycle works

Potentially:

- scheduled baseline update status;
- Dependabot for shared refs;
- central GitHub App/controller for update PRs if fleet size justifies it;
- repository-setting reconciliation.

## Recommended non-executable follow-up

After this research block archives, preserve a reminder such as:

> **Implement cross-repository agent baseline architecture**
>
> Use the MSHP-AGENT-BASELINE-A research/synthesis as the evidence base. Begin with neutral baseline contract/manifest design before modifying `M-A-X-I-N/template` or creating shared infrastructure. No implementation is authorized merely by this reminder.

## Final research conclusion

The original intuition was correct: the GitHub template repository is highly relevant, but it is **the bootstrap surface, not the whole system**.

The recommended architecture is:

```text
                  baseline release/update source
                       M-A-X-I-N/template
                              |
                copied baseline-managed skeleton
                              v
                       consumer repository
                  / local profile + local state \
                 /                              \
       exact-SHA shared runtime           local project knowledge
               |                                  |
 future agent-infrastructure repo       tasks/docs/.agents/checks
```

Evolution happens through reviewable baseline reconciliation/migrations and pinned dependency updates, not through hidden inheritance.

This provides the desired outcome: improve generic agent infrastructure once, make new repositories start with it automatically, and give existing repositories a safe path to adopt later improvements without erasing what makes each repository different.
