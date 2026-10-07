# Cross-repository agent baseline architecture

> **Status:** v1 implemented by `MSHP-AGENT-BASELINE-B`. The broader synchronization/runtime architecture researched in archived block `MSHP-AGENT-BASELINE-A` is deliberately deferred.

## Goal

Make the agent collaboration behavior that works well in MSHP reusable across repositories without copying MSHP-specific policy everywhere and without making repository-local policy subordinate to invisible remote state.

The implemented v1 optimizes for:

- strong generic agent workflow instructions;
- explicit separation of generic policy, repository-local policy, and non-normative memory;
- a clean GitHub-template bootstrap path;
- manual, reviewable adoption and updates;
- ordinary Git history as recovery/provenance;
- minimal machinery until real maintenance pain justifies more.

## Canonical repository roles

### `M-A-X-I-N/baseline`

`M-A-X-I-N/baseline` is the canonical Git tree for the current consumer-visible generic agent baseline and is configured as a GitHub template repository.

It contains:

- a thin root `AGENTS.md` seed;
- generic routing under `.agents/README.md`;
- generic normative policy under `.agents/baseline/`;
- repository-owned local-policy and memory seed structure;
- the reserved exact lowercase top-level `meta/` project-control namespace and seed state.

A repository generated from the GitHub template has independent Git history. The template is a bootstrap/canonical-copy source, **not** an upstream Git merge relationship or runtime dependency.

### MSHP

MSHP is the demanding reference consumer used to develop and validate the baseline architecture.

Its repository-specific policy, memory, tasks, CI, configuration architecture, and thematic paths remain local. MSHP's current generic baseline-managed files are kept aligned with `M-A-X-I-N/baseline` through the same manual lifecycle expected of other consumers.

### Future shared tooling/runtime

No shared runtime/tooling repository exists in v1.

Reusable workflows/actions, updater tooling, repository-setting synchronization, schema/migration helpers, or fleet orchestration remain possible future work only if real manual-maintenance experience demonstrates clear value.

## Ownership model

The baseline is a **generic governance kernel plus repository-owned state**, not a parent repository whose entire tree should stay synchronized.

### Baseline-managed

The generic synchronized surface is:

```text
.agents/README.md
.agents/baseline/*
```

These files define generic routing and normative workflow behavior.

A consumer adopting a complete baseline update should normally end with these files matching the canonical baseline source.

Repository-specific policy must not be hidden inside these files. If such policy appears there, move it into the local instruction surface during reconciliation.

### Seed-once / repository-owned

These are provided by the template/adoption process but become repository-owned:

```text
AGENTS.md
.agents/local/*
.agents/memory/*
meta/*
```

The root `AGENTS.md` may contain small repository-specific orientation.

`.agents/local/` owns repository-specific normative policy and explicit overrides.

`.agents/memory/` owns non-normative knowledge, rationale, investigations, and scar tissue.

`meta/` owns project-control/collaboration state such as tasks, workspaces, reminders, and initiatives.

### Reserved structural contract

The exact lowercase top-level path:

```text
meta/
```

is reserved for the baseline project-control integration.

Do not rename or recase it merely because a repository uses snake_case, kebab-case, PascalCase, or another naming convention elsewhere. Keeping this neutral path stable avoids cross-repository update churn over local casing style.

The contents are repository-owned; the integration path is stable.

## Instruction topology

The implemented v1 topology is:

```text
AGENTS.md

.agents/
├── README.md
├── baseline/
│   ├── WORKFLOW.md
│   ├── GIT.md
│   ├── PROVENANCE.md
│   ├── KNOWLEDGE.md
│   └── MAINTENANCE.md
├── local/
│   ├── README.md
│   └── repository-specific policy...
└── memory/
    └── repository-specific non-normative knowledge...

meta/
└── repository-owned project-control state...
```

The generic router knows only stable generic files and the local entry point. Arbitrary repository-specific local instruction files are discoverable through `.agents/local/README.md` without editing baseline routing.

Applicable local policy explicitly overrides conflicting generic baseline behavior. Silence leaves the generic rule active.

Memory never becomes normative merely because it exists.

## Task/work governance

The reusable workflow preserves the MSHP concepts that proved useful:

- explicit task lifecycle states;
- Dispatch as executable authorization/priority;
- Active claims as coordination locks;
- dependency and blocker distinction;
- recoverable agent lineages;
- interrupted-session recovery from repository evidence;
- task workspaces for temporary tracked cross-context knowledge;
- terminal block archival;
- reminders and initiatives as explicitly non-executable intent;
- deliberate promotion into executable tasks.

Static lifecycle semantics live in generic baseline policy. Mutable task state remains repository-owned.

## Git, lineage, and provenance

Generic defaults include:

- preserve reachable history by default;
- normal correction is additive;
- do not infer authority to adopt an agent lineage merely because it exists;
- recover interrupted work from repository evidence rather than narrated chat state;
- use coherent recoverable checkpoints;
- use explicit agent-authorship provenance for wholly agent-authored substantive commits.

Repository-local policy may explicitly tighten or override generic behavior where a project genuinely differs.

## Manual v1 baseline lifecycle

The authoritative detailed procedure is:

```text
.agents/baseline/MAINTENANCE.md
```

### Why manual

The current fleet is small enough that transparent human-plus-agent review is preferable to synchronization machinery.

Git already provides substantial useful evidence:

- current file contents and blob identity;
- per-repository history;
- path history;
- blame/line provenance;
- ordinary diffs and commits;
- additive rollback/revert.

That is sufficient for v1 when combined with explicit ownership boundaries.

### Generic change flow

A generic improvement may be discovered in any consumer.

Before propagation:

1. separate the generic rule from the consumer-specific circumstance;
2. express and validate the generic change in `M-A-X-I-N/baseline`;
3. adopt the canonical change into desired consumers through the manual update procedure.

This makes the baseline repository authoritative without making it an invisible runtime dependency.

### Existing consumer update

A consumer update is a semantic/content comparison, not a template merge:

1. inspect canonical baseline and consumer state/history;
2. compare every baseline-managed file;
3. classify identical content, generic drift, local-policy leakage, semantic conflicts, and added/removed generic files;
4. propose the transformation;
5. move repository-specific policy into local instructions;
6. refresh baseline-managed files from the canonical source;
7. preserve repository-owned policy, memory, tasks, reminders, initiatives, CI, architecture, and source;
8. validate routing/ownership;
9. commit through ordinary repository history.

Because GitHub-template children have independent histories, the procedure does not assume a shared merge base.

### Legacy repository adoption

Do not fake template ancestry.

Adoption:

1. inventories existing instructions/work state/history;
2. classifies generic policy, local policy, memory, and executable state;
3. introduces the baseline/local/memory separation;
4. copies current baseline-managed files from `M-A-X-I-N/baseline`;
5. builds repository-specific root/local routing;
6. reserves exact lowercase `meta/` and maps existing project-control state deliberately;
7. preserves existing local semantics rather than overwriting them with template seed state;
8. validates and commits adoption as ordinary new history.

## No baseline manifest/version/schema in v1

v1 deliberately has **no**:

- baseline-version file;
- source-commit manifest;
- schema version;
- profile/module manifest;
- updater lock state;
- migration registry.

Do not add these merely to answer which baseline revision a consumer has.

Instead, inspect canonical and consumer Git history plus current baseline-managed contents.

A source commit may appear naturally in historical discussion or a commit message, but it is not maintained repository state and is not required by the protocol.

## New repository bootstrap

Current default bootstrap:

1. create the repository from `M-A-X-I-N/baseline`;
2. retain the exact lowercase `meta/` integration path;
3. fill in repository-specific `.agents/local/` policy and root orientation;
4. preserve generic files under `.agents/baseline/`;
5. begin project work through ordinary Git history.

There is no release/schema registration step.

## Validation expectations

For baseline updates/adoption, verify at least:

- baseline-managed generic files match the intended canonical source;
- repository-specific rules remain explicit under local policy;
- generic files contain no repository-specific path/policy leakage;
- root → generic router → local router → meta/memory navigation resolves;
- exact lowercase `meta/` remains stable;
- live task/project state was not replaced by template seed data;
- no step depends on nonexistent updater/version machinery.

Repository-specific tests/CI remain local concerns.

## Rollback

A baseline adoption/update is ordinary repository history.

Primary rollback is:

- Git revert; or
- another additive corrective commit.

No special baseline rollback metadata exists in v1.

## Deferred broader architecture

Archived block `MSHP-AGENT-BASELINE-A` researched a substantially broader system involving:

- shared reusable workflow/action runtime;
- automated or semi-automated synchronization;
- baseline releases/manifests/schema versions;
- Copier/Cruft-style lifecycle reconciliation;
- migration machinery;
- repository-setting reconciliation;
- updater bots/GitHub Apps;
- fleet management.

That research remains useful context, but none of it is part of v1.

### Reopen triggers

Revisit that broader research only when real usage repeatedly shows problems such as:

- old baseline state becoming expensive or ambiguous to reconstruct;
- enough consumers existing that manual comparison is materially burdensome;
- updates requiring ordered structural migrations/schema compatibility;
- shared runtime pins creating lifecycle state that ordinary content comparison handles poorly;
- repeated baseline/local leakage making reconciliation error-prone;
- repository-setting synchronization becoming a real requirement;
- manual mistakes/review effort becoming a recurring cost.

The existence of the old research is not itself authorization to build automation.

## Non-goals

v1 does not:

- synchronize whole repositories;
- maintain a hidden remote policy dependency;
- overwrite repository-local policy during baseline updates;
- fake Git template ancestry;
- keep version/schema/manifest state;
- use updater bots;
- use Copier/Cruft;
- create a shared runtime repository;
- reconcile repository settings;
- migrate arbitrary existing repositories automatically;
- require repository-local source naming conventions to affect the reserved `meta/` path.

## Evidence and history

The broad research basis is preserved with archived task block `MSHP-AGENT-BASELINE-A`.

Implementation/validation history is preserved with `MSHP-AGENT-BASELINE-B`.

The most relevant durable generic behavior lives directly in the baseline-managed Markdown rather than in this architecture summary.
