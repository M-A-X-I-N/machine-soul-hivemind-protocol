# MSHP-AGENT-BASELINE-B-050 — ChatGPT Chat instruction ergonomics validation

## Scope

Validate the refactored v1 instruction graph as it is actually consumed by ChatGPT Chat-style repository work.

Primary goals:

- make the correct instruction path obvious from root `AGENTS.md`;
- avoid indiscriminate loading of all agent files;
- keep high-frequency coupled rules together;
- split low-frequency policy when the context savings justify another routing hop;
- preserve explicit local-over-baseline precedence;
- keep memory demand-loaded and non-normative;
- avoid depending on Codex-only nested instruction discovery.

## Final live topology

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
│   ├── LAYOUT.md
│   ├── CONFIGURATION.md
│   └── CI.md
└── memory/
    ├── architecture/
    ├── decisions/
    ├── investigations/
    ├── platforms/
    └── tools/
```

The B-030 expectation of only two local files was intentionally revised during ergonomics testing: directory-placement policy and configuration safety have sufficiently distinct retrieval triggers to justify separate local files.

## File size / access observations

| File | Lines | Characters | Retrieval |
|---|---:|---:|---|
| `AGENTS.md` | 18 | 1,053 | every interaction / entrypoint |
| `.agents/README.md` | 52 | 2,566 | substantial work / routing |
| `baseline/WORKFLOW.md` | 195 | 8,500 | substantial planned/task work |
| `baseline/GIT.md` | 77 | 2,407 | branch/history/checkpoint/commit operation |
| `baseline/PROVENANCE.md` | 96 | 3,441 | wholly agent-authored substantive commit |
| `baseline/KNOWLEDGE.md` | 92 | 3,078 | knowledge placement/retention decisions |
| `local/REPOSITORY.md` | 67 | 3,136 | substantial MSHP work |
| `local/LAYOUT.md` | 33 | 3,761 | adding/moving/classifying repository material |
| `local/CONFIGURATION.md` | 19 | 1,159 | configuration/state-management safety |
| `local/CI.md` | 101 | 2,855 | CI/control-plane work |
| `autonomic_affairs/tasks.md` | 85 | 6,881 | task-governed execution/state |

Character counts are used only as a simple context-cost proxy; they are not a model-token guarantee.

## Context reduction from B-040

Before B-050 tuning, a normal substantial-task read path required approximately:

- root `AGENTS.md`: 1,053 chars;
- router: 2,391 chars;
- baseline workflow: 8,500 chars;
- local repository policy: 7,347 chars;
- task ledger: 7,829 chars;

for about **27,120 characters** before task-spec/domain context.

After B-050 tuning:

- root: 1,053;
- router: 2,566;
- workflow: 8,500;
- local repository policy: 3,136;
- task ledger: 6,881;

for about **22,136 characters**.

That is a reduction of roughly **4,984 characters / 18%** in the default substantial-task instruction/state path.

The removed policy remains available through explicit subject routing rather than being deleted.

## Scenario validation

### 1. Trivial isolated edit

Minimum read:

- `AGENTS.md`;
- directly relevant target/context.

Expected baseline overhead: about **1,053 characters**.

Do not read workflow/Git/provenance/memory solely for ceremony. If the edit expands into substantial/task-governed or Git-sensitive work, route into the relevant files before performing that part.

**Result:** satisfactory.

### 2. Substantial multi-step task

Read:

- `AGENTS.md`;
- `.agents/README.md`;
- `baseline/WORKFLOW.md`;
- `local/REPOSITORY.md`;
- `autonomic_affairs/tasks.md`;
- linked task specification;
- only task-linked/relevant workspace/memory/docs.

Instruction/state routing overhead before the task spec: about **22,136 characters**.

Read `GIT.md` / `PROVENANCE.md` when the workflow reaches branch/checkpoint/commit operations rather than front-loading them.

**Result:** satisfactory.

### 3. Taskification / task-state change

Read:

- root/router;
- `baseline/WORKFLOW.md`;
- `local/REPOSITORY.md`;
- task ledger/storage docs as needed.

The live task ledger now delegates generic state/lifecycle semantics to `baseline/WORKFLOW.md` instead of re-explaining them. It retains MSHP-specific ID/schema/storage ownership.

**Result:** satisfactory; duplication reduced.

### 4. Interrupted recovery

Read:

- root/router;
- `baseline/WORKFLOW.md`;
- `local/REPOSITORY.md`;
- `baseline/GIT.md`;
- task ledger/spec/archive lookup;
- only recovery-relevant task workspace/memory.

Approximate fixed instruction/state path before task-specific recovery evidence: **24,543 characters**.

Recovery remains in WORKFLOW rather than being split into a separate file because claim/lineage/recovery semantics are tightly coupled and mistakes here are costlier than the modest context saving from another hop.

**Result:** satisfactory.

### 5. Git / provenance checkpoint

When the repository/task context is already understood, the Git-specific instruction addition is:

- `baseline/GIT.md`;
- `baseline/PROVENANCE.md` for wholly agent-authored substantive commits.

A standalone Git/provenance routing set from root/router is about **9,467 characters**.

Provenance stays separate from Git because its detailed registry/trailer rules are only needed at commit time.

**Result:** satisfactory.

### 6. CI change or CI diagnosis

Read normal substantial-task set plus:

- `local/CI.md`.

Approximate fixed instruction/state path before task/domain evidence: **24,991 characters**.

MSHP check IDs, schedule, selector behavior, hard bypass grammar, and CodeQL cadence remain local and therefore do not contaminate the reusable baseline.

**Result:** satisfactory.

### 7. Repository layout change

Read normal substantial-task set plus:

- `local/LAYOUT.md`.

Approximate fixed path: **25,897 characters**.

This is still smaller than the pre-B-050 default substantial path even though the full directory-placement contract is now loaded deliberately.

**Result:** split justified.

### 8. Configuration/application-state change

Read normal substantial-task set plus:

- `local/CONFIGURATION.md`.

Approximate fixed path: **23,295 characters**.

The safety laws are therefore present for the work that can violate them without taxing unrelated research/CI/task work.

**Result:** split justified.

### 9. Architecture research / investigation

For task-governed work:

- normal substantial-task set;
- applicable human-facing architecture;
- relevant `memory/architecture/`, `memory/decisions/`, or `memory/investigations/` only on demand.

Read `baseline/KNOWLEDGE.md` when deciding where findings should be retained, not merely because research is happening.

Read Git/provenance only when reaching the checkpoint.

**Result:** satisfactory.

### 10. Memory lookup

For a direct factual/rationale lookup:

- root;
- router when location is not already known;
- relevant memory file(s).

Memory existence does not make it normative or mandatory startup context.

Historical memory may explain past behavior but cannot override current baseline/local policy.

**Result:** satisfactory.

## Deliberate non-splits

### WORKFLOW remains one larger file

At 8,500 characters, WORKFLOW is the largest baseline instruction file.

It was **not** split further because:

- task lifecycle, Dispatch, claims, lineages, recovery authority, interrupted recovery, completion, and validation are strongly coupled;
- substantial planned work needs most of this contract;
- recovery/claim mistakes are high-cost;
- another routing layer would save relatively little compared with the risk of missing a coupled rule.

A future usage pattern showing agents frequently need task mechanics without lineage/recovery would justify revisiting this.

### PROVENANCE remains separate

Although it could be merged into GIT, it is detailed and needed only for wholly agent-authored substantive commits. Keeping it demand-loaded is materially cheaper for planning/research work.

### KNOWLEDGE remains separate

Knowledge-placement policy is important when creating or reorganizing retained context but is unnecessary for ordinary implementation.

## Local split justification

B-050 changed the local topology from:

```text
REPOSITORY.md
CI.md
```

to:

```text
REPOSITORY.md
LAYOUT.md
CONFIGURATION.md
CI.md
```

This is not symmetry-driven fragmentation.

- `REPOSITORY.md` keeps high-frequency project identity, source-of-truth, engineering style, and local task/reminder locations.
- `LAYOUT.md` is required only when file/domain placement matters.
- `CONFIGURATION.md` is required only for configuration/application-state safety.
- `CI.md` is required only for CI/control-plane work.

The router and REPOSITORY policy both advertise these triggers.

## Task-ledger tuning

The live task ledger previously repeated generic state definitions already owned by the new baseline workflow.

B-050 replaced that duplicated section with an explicit pointer to `.agents/baseline/WORKFLOW.md`.

The task ledger still owns:

- current scheduling data;
- Dispatch;
- Active claims;
- task IDs/states/dependencies/titles/summaries;
- MSHP task ID grammar;
- task-spec source ownership;
- local task storage/archive paths.

This keeps mutable local state close to its local schema while leaving generic workflow semantics in the reusable baseline.

## Platform-dependence review

The final v1 structure uses ordinary Markdown and explicit repository-relative navigation.

It does **not** depend on:

- nested `AGENTS.md` precedence;
- `AGENTS.override.md`;
- Codex-only recursive instruction injection;
- generated includes;
- model-specific configuration files;
- baseline manifests/update tooling.

The only deliberate OpenAI-oriented convention is root `AGENTS.md`, which is high-value and broadly understandable even when another agent does not provide identical automatic behavior.

For ChatGPT Chat, explicit routing is treated as authoritative rather than assuming harness auto-loading.

## Local override visibility

Override semantics remain visible at three levels:

- root `AGENTS.md`: applicable local policy overrides conflicting baseline;
- router: baseline/local/memory roles are explicit;
- each local policy: identifies itself as MSHP-specific normative policy and links/routing clarify when it applies.

Silence in local policy never disables baseline behavior.

No current MSHP local file needs to duplicate a generic baseline file merely to override a small rule.

## Memory behavior

The complete moved `.agents` tree passed a relative-link check after migration.

Memory categories are explicitly non-normative and demand-loaded.

The task-storage README now points durable agent knowledge specifically to `.agents/memory/` rather than ambiguously calling the whole `.agents/` tree “memory”.

## Validation performed

- verified live root/baseline/local/memory structure on `main`;
- verified old live `.agents/WORKFLOW.md` and `.agents/PROVENANCE.md` authorities are absent;
- verified all 53 root/`.agents` Markdown files after B-040 had no broken relative Markdown targets;
- verified no non-historical/non-B-workspace live references remained to the old instruction/category paths;
- after B-050 tuning, verified all 12 touched/high-authority Markdown files have no broken relative targets;
- verified router contains explicit LAYOUT/CONFIGURATION/CI triggers;
- verified task ledger points lifecycle semantics to baseline WORKFLOW;
- compared representative read sets and context-cost proxies.

GitHub code-search indexing lagged behind the refactor during validation, so direct branch/tree/file reads were treated as authoritative, consistent with prior MSHP housekeeping practice.

## B-050 conclusion

The v1 instruction graph is ergonomically acceptable for ChatGPT Chat and ready for the next task's template population **when separately authorized**.

The validated live baseline source is now the actual MSHP tree under:

```text
AGENTS.md
.agents/README.md
.agents/baseline/
```

The B-020 workspace candidate is historical drafting evidence, not the post-B-050 source of truth.

B-050 does **not** authorize or perform B-060, and `M-A-X-I-N/template` remains untouched.
