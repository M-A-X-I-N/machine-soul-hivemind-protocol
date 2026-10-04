# MSHP-AGENT-BASELINE-A-050 — Baseline versus repository-local ownership boundaries

Research date: 2026-10-04.

## Executive conclusion

The best way to make baseline updates safe is to **avoid mixed ownership wherever possible**.

A consumer repository should have three visibly different classes of tracked material:

1. **baseline-owned kernel** — generic procedure/schemas/loaders intended to track baseline evolution;
2. **repository-local policy/configuration** — explicit project-specific choices/extensions/deviations;
3. **repository-local state/knowledge** — tasks, reminders, initiatives, project memory, architecture, check definitions, etc.

Baseline updates may replace/reconcile class 1, may validate interfaces against class 2, and must not silently rewrite class 3.

The consumer repository remains authoritative at all times. A remote/shared baseline is a source of proposed updates, not a runtime authority over already-merged repository policy.

## Why file ownership matters

The hardest synchronization case is a file that simultaneously contains:

- generic rules copied from baseline;
- project-specific policy;
- mutable execution state.

Every future generic edit then becomes a merge problem.

Current MSHP has several such files because it evolved organically. A fresh baseline can reduce this problem by splitting stable protocol from local data early.

General preference:

> one file, one ownership class whenever practical.

When a platform forces a specific file/path, keep that file as thin/stable as possible and delegate local detail to clearly referenced local files.

## Proposed authority model

Authority within a consumer should be explicit:

1. human instruction for the current work;
2. tracked consumer-repository policy/state;
3. explicit repository-local deviation/extension policy;
4. copied baseline defaults as merged into the consumer;
5. remote baseline/template state has **no direct authority** until a baseline update is reviewed/merged.

This avoids a dangerous model where `template@main` changes behavior in consumers without a consumer commit.

A baseline update that discovers a local rule conflicting with a new baseline rule should:

- report/merge-conflict it;
- allow the repo to adopt the new baseline rule or declare a deliberate deviation;
- never silently let whichever text happened to be rendered last win.

## Root `AGENTS.md`

### Problem

`AGENTS.md` is the obvious bootstrap entry point but current MSHP's file mixes:

- generic startup/recovery/Git/task rules;
- Machine-Soul source-of-truth map;
- thematic directory contract;
- configuration safety laws;
- project-specific CI details.

Copying that structure to other repos would guarantee update conflicts.

### Strong layering candidate

Make root `AGENTS.md` a **thin baseline-owned loader/entry contract** whose main responsibilities are:

- repository state beats remembered chat state;
- read baseline procedure;
- read repository-local profile/policy;
- read task Dispatch/spec before substantive work;
- read only relevant memory/docs;
- state the generic precedence/recovery rules.

Repository mission, directory ownership, product safety laws, local CI/check policy, and other project-specific rules live in a clearly named local policy/profile document.

Benefits:

- root entry point changes rarely;
- local project policy can evolve freely without becoming baseline drift;
- a fresh agent can still discover everything from one obvious file;
- baseline updater can safely treat the thin loader as baseline-owned.

### Alternative: marked generated regions

A single AGENTS file with `BEGIN BASELINE` / `END BASELINE` and local regions could reduce file count.

Rejected as primary model because:

- textual markers create fragile partial-file ownership;
- human edits can move/delete markers;
- merge tools do not understand semantic ownership automatically;
- authority is less obvious to a fresh agent.

Use only if a tool/platform later requires single-file semantics that cannot delegate.

## `.agents/`

### Baseline-owned candidates

Generic procedure files are good baseline-kernel material:

- memory placement/read-order doctrine;
- task/recovery workflow protocol;
- generic lineage/recovery rules;
- generic provenance format/semantics.

However, current file names need not remain monolithic. A cleaner baseline might separate generic protocol from local extension, for example conceptually:

- baseline workflow protocol;
- repository workflow/profile extension;
- baseline provenance policy;
- repository provenance registrations/deviations.

No exact path layout is selected yet.

### Always repository-local

These should never be synchronized from the generic baseline:

- `architecture/` project implementation memories;
- `investigations/` findings;
- `decisions/` project decisions;
- application/platform/tool scar tissue;
- host/account facts;
- any history specific to the consumer.

The baseline can supply directory conventions/README guidance, but not contents.

## Task system

### Generic baseline-owned protocol

- task states and semantics;
- Dispatch model;
- Active claims;
- dependency/authorization rules;
- block archival policy;
- task-spec/workspace/archive layout conventions;
- task ID immutability;
- recovery lookup procedure.

### Repository-local state

- every actual task row/block/spec/workspace;
- claims and Dispatch contents;
- task summaries/dependencies;
- archived project task history.

### Current mixed-ownership problem

`autonomic_affairs/tasks.md` currently contains both static protocol text and dynamic task state.

For a reusable baseline, serious candidates are:

1. split static task protocol/schema into a baseline-owned document and keep `tasks.md` mostly local state/index;
2. keep the current combined human-friendly file but teach updater a structural merge format;
3. generate a section while preserving local tables.

Candidate 1 has the clearest ownership and lowest long-term merge cost.

The same principle applies to `tasks/README.md` and archive README: generic schema/navigation can be baseline-owned, but repository archived contents are local.

## Reminders and initiatives

The **lifecycle semantics** are baseline-owned; the **contents** are local.

To minimize mixed ownership:

- reminder policy/format should live in generic lifecycle documentation or a stable header/schema;
- reminder entries remain local;
- initiative README/schema may be baseline-owned;
- initiative files remain local.

Baseline updates must never promote/delete/modify a consumer reminder or initiative simply because the baseline changed.

## Provenance

Current `.agents/PROVENANCE.md` mixes generic trailer policy with a registry of known stable agent designations.

Preferred conceptual split:

- generic provenance rules/schema — baseline-owned;
- known baseline-wide agent/tool registrations — possibly baseline-owned;
- repository-specific or human-selected registrations — local extension;
- commit history itself — local state.

If the same agent designation is meant to be universal across the maintainer's repositories, centralizing that registry is attractive. If designation is repository-scoped, it must remain local. A-070 should make this policy explicit.

## Git / lineage / recovery

Generic default rules can be baseline-owned:

- additive history by default;
- no force/rewrite without explicit authority;
- lineage discovery is not recovery authority;
- explicit lineage namespace convention;
- claim/checkpoint/recovery discipline.

Repository-local extension should carry intentional deviations such as:

- different default branch;
- no agent-branch policy;
- stricter release branch handling;
- monorepo-specific worktree/branch rules.

A local deviation should be **explicit**, not implemented by editing the generic baseline copy invisibly.

## Documentation style / source-of-truth discipline

Generic baseline candidates:

- durable docs use generic roles instead of incidental identities;
- current authority vs historical evidence labeling;
- avoid duplicate source-of-truth files;
- promote human-relevant durable facts out of agent-only memory.

Repository-specific extension:

- project-specific style rules;
- terminology/glossary;
- local humor/formality decisions;
- document taxonomy.

## CI policy

CI is where a clean generic/local boundary offers the most value.

### Generic shared core

Potential baseline/shared implementation:

- event-type normalization;
- Git push/PR range derivation;
- explicit override parsing framework;
- fail-safe unknown/ambiguous behavior;
- commit metadata validation framework;
- check registry input validation;
- check-to-runner grouping machinery;
- run-history/coverage primitives;
- generic output contract;
- generic reusable workflow/action wrappers.

### Repository-local declaration

Must remain local:

- check IDs;
- commands each check executes;
- path→check relevance mapping;
- runner/OS requirements;
- destructive/isolation requirements;
- security-analysis languages;
- schedules/cadence if repository differs;
- local CI exceptions.

The ideal shared CI engine consumes a local declarative policy rather than importing MSHP's classifier.

### Thin local workflow

GitHub event triggers must exist in the consumer repository, so a good layering model is:

- small local workflow owns events and minimal permissions;
- it calls a pinned shared reusable workflow/core;
- local policy file/inputs describe repository checks;
- generic shared implementation executes/returns decision;
- repository-local callable check workflows/commands perform project-specific work.

This also leaves a consumer commit controlling which shared version it executes.

## Repository-side settings

Settings such as rulesets, Actions permissions, variables, environments, and protections cannot be layered as files unless GitHub itself supports file configuration.

For these, ownership should be declarative in a baseline manifest/profile:

- baseline **default** setting;
- local explicit override/deviation;
- reconciler compares actual GitHub setting;
- proposed update shows setting diff separately from file diff;
- local deviation prevents repeated attempts to 'fix' an intentional difference.

Never infer ownership from 'it currently matches the baseline'.

## Baseline manifest/profile

A-040 established value in a manifest. A-050 adds an important distinction: it should record **ownership/intent**, not only a version.

Conceptual fields may include:

- baseline source/version/schema;
- enabled baseline modules/features;
- template/render answers;
- local repository profile pointer;
- intentional deviations/disabled components;
- detached files/components that baseline no longer manages;
- shared executable component versions/pins;
- optional repository-setting policy choices.

This gives update tooling a machine-readable reason why two repositories legitimately differ.

## Multiple profiles

Not every repository needs identical machinery.

Possible baseline profiles/features might include:

- core agent governance only;
- core + task system;
- core + centralized CI;
- core + CodeQL/security policy;
- research-heavy memory taxonomy;
- minimal repository without long-running task blocks.

Feature/profile selection is preferable to maintaining several divergent templates if differences remain composable.

Do not over-modularize: every option increases migration/test complexity. Profiles should reflect real repository classes, not hypothetical flexibility.

## Fresh-agent discoverability test

A layered baseline is acceptable only if a fresh agent can answer quickly:

1. What generic protocol governs me?
2. What is this repository specifically?
3. What local rules override/extend the generic defaults?
4. Where is executable work authorized?
5. Which files are state versus policy versus historical memory?
6. What baseline version/profile does this repo implement?

If answering those requires reverse-engineering generated files or knowing the updater tool, the layering is too opaque.

## Anti-patterns

### Remote policy as invisible runtime authority

Do not make a remote `template@main` instruction file dynamically control consumers. Policy changes should appear as consumer commits/PRs.

### Whole-file ownership where local edits are expected

Do not declare AGENTS/task ledgers 'generated; never edit' if repository-specific rules/state naturally belong there.

### Silent local fork

Do not let maintainers customize baseline-owned files without recording that they are now deviated/detached; otherwise every future update rediscoveries the same conflict.

### Duplicate effective authority

Do not place full generic rules in both root AGENTS and a baseline workflow doc and a local profile. One owns detail; other files should summarize/navigate.

### Hyper-modular file maze

Do not solve merge conflicts by splitting every paragraph into another file. Human/agent readability remains a first-class constraint.

## Recommended ownership direction entering synthesis

### Baseline-owned/copied

- thin root agent entrypoint;
- generic memory/read-order guidance;
- generic work/recovery/task protocol;
- task/reminder/initiative schemas and empty skeletons;
- provenance protocol;
- generic Git/checkpoint rules;
- baseline manifest schema;
- thin CI caller/update-check files where required locally.

### Shared executable

- generic CI/policy helper logic;
- generic baseline status/update planning helpers if justified;
- deterministic validation/audit helpers.

### Repository-local policy/data

- project profile/mission/directory contract/product safety rules;
- project documentation/architecture;
- actual tasks/reminders/initiatives;
- `.agents` project knowledge;
- CI checks/path relevance/runner requirements;
- explicit baseline deviations;
- project-specific provenance additions where needed.

## A-050 conclusion

The baseline should behave like a **kernel plus local profile**, not a parent repository whose files are expected to remain identical.

Maximize clean file/component ownership boundaries first; use three-way synchronization only for the unavoidable copied surfaces.

This reduces both migration complexity and the risk that central baseline evolution silently erases repository identity.
