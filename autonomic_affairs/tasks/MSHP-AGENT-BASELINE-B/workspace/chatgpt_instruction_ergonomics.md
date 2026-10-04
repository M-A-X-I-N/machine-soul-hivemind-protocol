# MSHP-AGENT-BASELINE-B-050 — ChatGPT Chat instruction ergonomics validation

## Scope

Validate the v1 instruction graph as consumed by ChatGPT Chat-style repository work.

Primary goals:

- make the correct instruction path obvious from root `AGENTS.md`;
- keep generic baseline instructions and repository-local instructions independently owned;
- allow arbitrary local instruction files without editing baseline-owned files;
- avoid indiscriminate loading of all agent files;
- group high-frequency coupled rules and demand-load lower-frequency policy;
- keep memory non-normative and demand-loaded;
- avoid dependence on Codex-only nested instruction discovery.

B-050 was reopened after initial completion when the human identified an ownership defect: the supposedly generic `.agents/README.md` still contained MSHP-specific local routing, task paths, and memory categories. The corrective rerun below is the final B-050 result.

## Final live topology

```text
AGENTS.md

.agents/
├── README.md                 # baseline-owned generic router
├── baseline/
│   ├── WORKFLOW.md
│   ├── GIT.md
│   ├── PROVENANCE.md
│   └── KNOWLEDGE.md
├── local/
│   ├── README.md             # repository-owned local router/index
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

Root `AGENTS.md` may contain small repository-local orientation/navigation. The strict generic/local ownership boundary applies inside `.agents/`.

## Ownership contract

### Baseline-owned

- `.agents/README.md`;
- everything under `.agents/baseline/`.

The generic router may know only the stable local entry point:

```text
local/README.md
```

It must not enumerate repository-specific local instruction filenames, task/control paths, or memory categories.

### Repository-owned

- `.agents/local/README.md`;
- all other files under `.agents/local/`;
- everything under `.agents/memory/`.

`local/README.md` owns discovery/read triggers for arbitrary repository-specific instruction files.

A local instruction does **not** need a baseline counterpart.

For example, adding:

```text
.agents/local/DARK_SORCERY.md
```

requires only:

1. creating the local file;
2. adding its read trigger to `.agents/local/README.md`.

No baseline-owned file changes.

This is the dry-run case that exposed and then verified the corrected ownership model.

## Precedence

Applicable repository-local policy overrides conflicting baseline policy.

Silence in local policy leaves baseline policy in force.

A local override should identify the baseline behavior it changes clearly enough that an agent need not infer the conflict from filename symmetry or diff history.

Memory remains non-normative and cannot override current baseline/local policy.

## File size / retrieval observations

Measured during the corrective B-050 rerun:

| File | Lines | Characters | Retrieval |
|---|---:|---:|---|
| `AGENTS.md` | 18 | 1,093 | entrypoint |
| `.agents/README.md` | 37 | 2,518 | substantial work / generic routing |
| `baseline/WORKFLOW.md` | 195 | 8,500 | substantial planned/task work |
| `baseline/GIT.md` | 77 | 2,407 | branch/history/checkpoint/commit |
| `baseline/PROVENANCE.md` | 96 | 3,441 | wholly agent-authored substantive commit |
| `baseline/KNOWLEDGE.md` | 92+ | ~3,100 | context-placement decisions |
| `local/README.md` | 45 | 2,245 | local routing/index |
| `local/REPOSITORY.md` | 59 | 2,787 | substantial MSHP work |
| `local/LAYOUT.md` | 33 | 3,761 | file/domain placement |
| `local/CONFIGURATION.md` | 19 | 1,159 | configuration/state safety |
| `local/CI.md` | 101 | 2,855 | CI/control-plane |
| `autonomic_affairs/tasks.md` | 85 | ~6,900 | task-governed execution/state |

Character counts are only a context-cost proxy, not a model-token guarantee.

## Context-cost result

Before the B-050 split work, the ordinary substantial-task path was about **27,120 characters** before task-spec/domain context.

The first B-050 completion reduced that to about **22,136 characters**, but achieved part of that reduction by leaking local routing into the baseline-owned router.

After correcting ownership, the ordinary substantial-task path is approximately:

- `AGENTS.md`: 1,093;
- generic `.agents/README.md`: 2,518;
- `baseline/WORKFLOW.md`: 8,500;
- `local/README.md`: 2,245;
- `local/REPOSITORY.md`: 2,787;
- task ledger: about 6,928;

for roughly **24,071 characters**.

That is still about **3,049 characters / 11% smaller** than the pre-B-050 path while providing a substantially cleaner ownership/update boundary.

The extra local-router hop is therefore accepted.

## Representative read paths

### Trivial isolated edit

Read:

- root `AGENTS.md`;
- directly relevant target/context.

Do not load unrelated instruction files merely for ceremony.

### Substantial multi-step task

Read:

- root `AGENTS.md`;
- generic `.agents/README.md`;
- `baseline/WORKFLOW.md`;
- `local/README.md`;
- `local/REPOSITORY.md`;
- task ledger + linked task specification;
- only relevant workspace/memory/docs.

Read Git/provenance later when the work reaches those operations.

### Taskification / task-state change

Read:

- root + generic router;
- `baseline/WORKFLOW.md`;
- local router/repository policy;
- local task ledger/storage docs.

The task ledger records current local state and schema while generic lifecycle semantics live in baseline WORKFLOW.

### Interrupted recovery

Read the substantial-work set plus:

- `baseline/GIT.md`;
- task/archive/workspace evidence relevant to recovery.

Claims, lineages, recovery authority, and interrupted-session recovery remain together in WORKFLOW because they are strongly coupled.

### Git / provenance checkpoint

Add:

- `baseline/GIT.md`;
- `baseline/PROVENANCE.md` for wholly agent-authored substantive commits.

### CI work

Add:

- `local/CI.md`.

MSHP check IDs, selector behavior, schedule, and deferred CodeQL details remain local.

### Repository layout work

Add:

- `local/LAYOUT.md`.

### Configuration/application-state work

Add:

- `local/CONFIGURATION.md`.

### Architecture research

Use the normal task path when task-governed, then load only applicable human architecture and relevant `memory/architecture/`, `memory/decisions/`, or `memory/investigations/`.

Read KNOWLEDGE when deciding where findings should be retained.

### Memory lookup

Use root/router as needed, then only relevant memory.

The existence of a memory file never makes it mandatory or normative.

## Deliberate file-boundary choices

### WORKFLOW remains one larger file

Task lifecycle, Dispatch, claims, lineages, recovery authority, interrupted recovery, completion, and validation remain tightly coupled. Splitting them would save context in some cases but increases the risk of missing a coordination/recovery invariant.

### PROVENANCE remains separate from GIT

Its detailed registry/trailer rules are needed principally at commit time.

### KNOWLEDGE remains separate

Knowledge placement is important when creating/reorganizing retained context but unnecessary for ordinary implementation.

### Local policy is not mirrored

The local tree is allowed to contain any repository-specific normative subject.

Current MSHP local files happen to be:

- `REPOSITORY.md`;
- `LAYOUT.md`;
- `CONFIGURATION.md`;
- `CI.md`.

Future repositories may have completely different local files. Discovery is owned by `local/README.md`, not by baseline filename symmetry.

## Platform-dependence review

The final v1 uses plain Markdown and explicit relative navigation.

It does not depend on:

- nested `AGENTS.md` precedence;
- `AGENTS.override.md`;
- Codex-only recursive instruction injection;
- generated includes;
- model-specific repository config;
- baseline manifests/update tooling.

Root `AGENTS.md` is the deliberate OpenAI-oriented convention because it has high practical value and remains understandable as ordinary Markdown elsewhere.

## Validation performed

- reopened B-050 rather than inventing a follow-up task because the discovered issue invalidated B-050's own ownership/ergonomics conclusion;
- verified generic `.agents/README.md` contains no MSHP name, MSHP task path, or MSHP-only local filenames;
- verified the only stable local entry point required by the generic router is `local/README.md`;
- verified `local/README.md` owns current local policy triggers and MSHP task/memory navigation;
- dry-ran a novel unmatched local file (`DARK_SORCERY.md`) and confirmed only local-owned routing would need modification;
- retained explicit local-over-baseline precedence and silence semantics;
- measured the corrected default read path and accepted the ~11% reduction versus the pre-split state;
- verified old live `.agents/WORKFLOW.md` / `.agents/PROVENANCE.md` authorities remain absent;
- verified baseline/local/memory separation remains intact.

## Final conclusion

The corrected v1 ownership model is:

```text
AGENTS.md                        small entry/orientation; may contain local facts

.agents/README.md                baseline-owned generic router
.agents/baseline/*               baseline-owned generic rules

.agents/local/README.md          repository-owned local router/index
.agents/local/*                  repository-owned normative policy

.agents/memory/*                 repository-owned non-normative knowledge
```

This architecture supports arbitrary local instruction files without modifying the baseline.

The validated baseline source for future B-060 template population is the live MSHP baseline-owned surface, **not** the historical B-020 candidate workspace.

B-050 does not authorize B-060. `M-A-X-I-N/template` must remain untouched until B-060 is separately authorized.
