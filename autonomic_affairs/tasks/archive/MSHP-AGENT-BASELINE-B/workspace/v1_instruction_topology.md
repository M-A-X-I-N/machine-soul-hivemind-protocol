# MSHP-AGENT-BASELINE-B-010 — v1 instruction topology and precedence

## Design goal

Optimize the repository instruction graph for the agent that actually uses it today: **OpenAI ChatGPT Chat**.

Use ordinary Markdown, explicit navigation, and semantic filenames so the structure remains understandable to other capable repository agents. Do not depend on Codex-only automatic nested-`AGENTS.md` discovery, `AGENTS.override.md`, or similar harness magic.

The design should minimize mandatory context without making important policy hard to discover.

## Core ownership classes

The v1 instruction tree has three intentionally different classes:

1. **Baseline instructions** — generic normative rules copied from the template and manually maintained across repositories.
2. **Local instructions** — repository-specific normative rules. These may extend, tighten, or explicitly override baseline rules without modifying baseline files.
3. **Memory** — repository-specific knowledge, rationale, investigation results, scar tissue, and history. Memory is **not normative policy** merely because it exists under `.agents/`.

Task/workspace state and normal human-facing documentation remain outside those three instruction namespaces and keep their own source-of-truth roles.

## Target tree

Starting v1 topology:

```text
AGENTS.md

.agents/
├── README.md
├── baseline/
│   ├── WORKFLOW.md
│   ├── GIT.md
│   ├── PROVENANCE.md
│   └── KNOWLEDGE.md
├── local/
│   ├── REPOSITORY.md
│   └── <additional local policy only when justified>
└── memory/
    └── <repository-specific knowledge categories only when useful>
```

This is a functional topology, not a symmetry requirement. Do not create matching local files for every baseline file. Do not create empty memory categories for appearance.

## Root `AGENTS.md`

### Purpose

Root `AGENTS.md` is the universal entry point and routing seed.

It should be short enough to be cheap in every repository interaction and contain only information with very high cross-task value.

### Expected contents

- one or two sentences identifying the repository/purpose;
- tracked repository state outranks remembered conversation state;
- where to find the instruction router (`.agents/README.md`);
- local instructions explicitly outrank conflicting baseline instructions;
- silence in local policy leaves baseline policy in force;
- executable task state must be inspected before planned/substantive task execution;
- relevant memory is demand-loaded rather than preloaded;
- a tiny source-of-truth/navigation statement if universally useful.

### What does not belong in root

- full task lifecycle;
- branch/recovery edge cases;
- provenance grammar;
- detailed repository directory taxonomy;
- application/runtime architecture;
- CI check IDs;
- historical decisions;
- large safety/policy sections that are only relevant to specific work.

Small local repository description/orientation is allowed when it genuinely helps nearly every agent interaction.

## `.agents/README.md`

### Purpose

`.agents/README.md` is primarily a **routing table**, not a second policy manual.

It teaches an agent what instruction or memory to load for a given kind of work.

### Read requirement

For **substantial repository work**, root `AGENTS.md` directs the agent to read `.agents/README.md`.

A tiny isolated edit may be handled from root/local context without loading the full routing graph when no task/Git/policy concern is involved.

### Routing model

Expected conceptual table:

| Work/concern | Read |
|---|---|
| substantial planned/repository work | `baseline/WORKFLOW.md` + `local/REPOSITORY.md` |
| taskification, Dispatch, claims, recovery | `baseline/WORKFLOW.md` |
| branches/history/checkpoints/commit grammar | `baseline/GIT.md` |
| agent-authored commit provenance | `baseline/PROVENANCE.md` |
| deciding where learned information belongs | `baseline/KNOWLEDGE.md` |
| repository-specific concern | applicable `local/*.md` |
| technical/rationale/history lookup | relevant `memory/**` only |
| current executable work | task ledger + linked task/spec/workspace |
| durable human architecture/policy | applicable human-facing docs |

The exact router may include repository-local paths, but generic routing semantics belong to the baseline.

## Baseline file grouping

File boundaries follow **access patterns**, not conceptual purity.

### `baseline/WORKFLOW.md`

Read for substantial planned/repository work and always for task lifecycle/recovery work.

Owns generic:

- autonomous progression and when to interrupt;
- taskification/granularity;
- Dispatch authorization;
- claims;
- task states/dependencies/holds;
- checkpoint/validation progression;
- terminal archival;
- lineage/recovery authorization;
- interrupted-session recovery;
- reminders versus initiatives versus tasks;
- completion/advancement semantics.

Task governance, recovery, and lineages stay together because they are tightly coupled in actual execution.

### `baseline/GIT.md`

Read when work will manipulate branches/history or produce substantive commits.

Owns generic:

- additive-history default;
- no destructive rewrite without explicit authority;
- branch/checkpoint safety;
- fast-forward/recovery expectations;
- commit summary grammar;
- smallest meaningful validation/checkpoint discipline where specifically Git-related.

It is split from WORKFLOW because many planning/research interactions need workflow/task semantics without detailed Git policy, while actual Git operations should load both.

### `baseline/PROVENANCE.md`

Read before wholly agent-authored substantive commits or when provenance questions arise.

Owns:

- agent variant/designation concepts;
- provenance trailer grammar;
- `UNNAMED` behavior;
- operator/accountability trailer semantics;
- stable designation registry when the maintainer intends it to apply across repositories.

This remains separate because it is rarely needed until commit time and is comparatively detailed.

### `baseline/KNOWLEDGE.md`

Read when creating/reorganizing agent notes, task research, durable documentation, or deciding what context should be retained.

Owns generic:

- baseline instructions versus local instructions versus memory;
- memory is knowledge, not policy;
- task workspace versus durable memory;
- promote human-relevant design to human docs;
- on-demand historical memory;
- no secrets;
- avoid duplicate authorities;
- preserve expensive-to-rediscover information.

This is intentionally not mandatory for every edit.

## Local policy

### `local/REPOSITORY.md`

Default repository-specific normative policy.

It should contain high-value local rules such as:

- repository mission/identity beyond the tiny root orientation;
- source-of-truth map;
- repository/directory ownership contract;
- local safety laws;
- local technical constraints that govern agent behavior;
- paths to local task/reminder/initiative systems if they differ from generic assumptions;
- explicit deviations from baseline behavior.

For substantial repository work, this file is normally read alongside `baseline/WORKFLOW.md`.

### Additional local files

Create only when a local policy has a distinct retrieval pattern or enough size to make `REPOSITORY.md` noisy.

For MSHP, `local/CI.md` is expected to be justified because its centralized selector/check/cadence rules are large and relevant mainly to CI/control-plane work.

Do **not** create `local/GIT.md`, `local/WORKFLOW.md`, etc. merely to mirror baseline filenames.

## Override semantics

### Precedence

Within repository policy, use:

```text
applicable repository-local instruction
    >
applicable baseline instruction
```

Higher-priority system/developer/current-user instructions remain above repository files as normal.

Tracked repository implementation/human architecture may own technical facts, but normative agent behavior is resolved through the instruction graph above.

### Explicit override rule

A local rule that changes baseline behavior must be explicit enough to identify the behavior it replaces or tightens.

Good:

> **Overrides baseline lineage requirement:** this repository works directly on `main`; do not create agent lineage branches unless the human explicitly asks.

Bad:

> We usually use main.

Local policy does not need to quote the entire baseline rule.

### Silence

If local policy does not mention a baseline rule, the baseline rule remains applicable.

Absence of `local/GIT.md` does not mean Git policy is disabled.

### Conflict handling

If an agent cannot determine whether a local rule truly overrides a baseline rule, treat the conflict as ambiguous and resolve it rather than silently choosing whichever file was read last.

## Memory

All repository-specific non-normative agent knowledge lives under `.agents/memory/` when it belongs in agent memory.

Examples:

- architecture implementation notes;
- decisions/rationale;
- investigations;
- platform quirks;
- tool/application scar tissue;
- historical migration evidence.

The existence of a memory file is **never an instruction to preload it**.

Read memory only when the current task/problem makes it relevant or when another instruction/task explicitly links it.

A memory file may describe a historical rule, but it does not override current baseline/local policy.

## Always-read versus triggered reads

### Every repository interaction

- root `AGENTS.md` entry/orientation.

### Substantial repository work

- `.agents/README.md`;
- `.agents/baseline/WORKFLOW.md`;
- `.agents/local/REPOSITORY.md`;
- active task ledger/spec when work is task-governed.

### Subject-triggered

- Git/history/commit → `baseline/GIT.md`;
- provenance/agent-authored commit → `baseline/PROVENANCE.md`;
- knowledge placement/memory work → `baseline/KNOWLEDGE.md`;
- CI/control-plane work in MSHP → `local/CI.md`;
- technical domain question → relevant memory/docs.

## Scenario read-path validation

### Trivial isolated edit

Read:

- root `AGENTS.md`;
- local file/context necessary for the edit.

Do not automatically load all baseline policy.

If the edit becomes a substantive repository/Git checkpoint, route into the relevant files before committing.

### Substantial planned task

Read:

- `AGENTS.md`;
- `.agents/README.md`;
- `baseline/WORKFLOW.md`;
- `local/REPOSITORY.md`;
- task ledger/spec;
- only relevant workspace/memory/docs;
- `GIT.md` and `PROVENANCE.md` when reaching commit/checkpoint operations.

### Taskification/task-state change

Read:

- root/router;
- `baseline/WORKFLOW.md`;
- `local/REPOSITORY.md` for local task paths/conventions;
- task ledger/schema.

No need to read unrelated memory.

### Interrupted recovery

Read:

- root/router;
- `baseline/WORKFLOW.md`;
- local repository policy;
- task ledger/spec/archive lookup;
- relevant Git policy;
- only recovery-relevant workspace/memory.

### Architecture investigation

Read:

- root/router;
- workflow/local repository policy if task-governed;
- applicable human architecture docs;
- relevant memory/investigations on demand;
- `KNOWLEDGE.md` when deciding how findings are retained.

No need to load provenance until a commit is actually being authored.

## ChatGPT Chat optimization

The design assumes ChatGPT Chat can read repository files when explicitly routed to them; it does **not** depend on automatic recursive instruction injection.

Optimizations chosen for ChatGPT Chat:

- semantic filenames;
- explicit routing;
- high-frequency rules grouped together;
- low-frequency/detailed rules demand-loaded;
- memory distinguished structurally from policy;
- thin root entry point;
- local overrides stated in natural language rather than hidden generated state.

These choices remain understandable to other repository-capable agents and therefore do not create material platform lock-in.

## B-010 conclusion

Use:

```text
AGENTS.md
.agents/README.md
.agents/baseline/{WORKFLOW,GIT,PROVENANCE,KNOWLEDGE}.md
.agents/local/REPOSITORY.md
.agents/local/<only justified extra policy>.md
.agents/memory/<only useful knowledge categories>
```

The v1 contract deliberately prefers **explicit semantic routing over automatic harness discovery** and **separate ownership over partial-file overrides**.
