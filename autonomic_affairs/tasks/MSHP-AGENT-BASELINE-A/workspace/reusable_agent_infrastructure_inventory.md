# MSHP-AGENT-BASELINE-A-020 — Reusable agent infrastructure inventory

Research date: 2026-10-04.

## Classification vocabulary

- **Generic baseline** — broadly useful repository-agent governance that can plausibly ship with little or no project-specific meaning.
- **Generic with parameters/extensions** — reusable mechanism/policy whose concrete values must be supplied by each repository.
- **MSHP-specific** — tightly coupled to Machine-Soul's domain, directory taxonomy, runtime, applications, or current tests.
- **Historical/scar tissue** — useful evidence/rationale but not something a new repository should inherit as baseline behavior.
- **Not worth sharing as-is** — concept may inspire future work, but copying the current artifact would create more coupling than value.

## Executive finding

The reusable baseline is primarily a **governance protocol**, not MSHP's project architecture.

A future shared baseline should not copy all of `.agents/` or `autonomic_affairs/`. It should extract a comparatively small set of contracts and skeletons, then let each repository supply local mission, architecture, validation, directory ownership, and technical memory.

## Component inventory

| Component | Current MSHP surface | Classification | Why / consumer-local input |
|---|---|---|---|
| Fresh-session startup/read order | `AGENTS.md`, `.agents/README.md` | **Generic baseline** | Reading repo authority before remembered chat state is universally useful. Consumer mainly needs correct local paths to its task/docs surfaces. |
| Repository state over remembered conversation | `AGENTS.md`, `.agents/README.md` | **Generic baseline** | Core recovery invariant; no MSHP domain dependency. |
| Explicit source-of-truth ownership | `AGENTS.md` | **Generic with parameters/extensions** | The rule 'one authority per concern' is generic; exact directories/docs differ by repo. |
| Executable task ledger | `autonomic_affairs/tasks.md`, `tasks/README.md` | **Generic baseline + local contents** | Lifecycle/index/storage protocol is reusable; actual tasks/blocks are always local. |
| Dispatch | `tasks.md`, `.agents/WORKFLOW.md` | **Generic baseline** | Single explicit authorization queue materially reduces accidental autonomous work. |
| Active claims coordination locks | `tasks.md`, `.agents/WORKFLOW.md` | **Generic baseline** | Useful for multi-agent/recovery coordination; claim contents are local ephemeral state. |
| Task states / dependency semantics | `tasks.md`, `.agents/WORKFLOW.md` | **Generic baseline** | `QUEUED`, `IN_PROGRESS`, `AWAITING_DEFERRED_CI`, `FROZEN`, terminal states, etc. are reusable lifecycle semantics if the baseline keeps this task model. |
| Terminal block archival | `.agents/WORKFLOW.md`, `tasks/README.md`, `tasks/archive/README.md` | **Generic baseline** | Archive-all-terminal-blocks and stable immutable task IDs are project-neutral. |
| Task-workspace vs permanent-memory distinction | `AGENTS.md`, `.agents/README.md`, task docs | **Generic baseline** | Strong general mechanism for cross-context work without bloating permanent agent memory. |
| Reminders lifecycle | `autonomic_affairs/reminders.md`, `AGENTS.md` | **Generic baseline** | Non-executable idea parking is generic; reminder contents local. |
| Initiatives lifecycle | `autonomic_affairs/initiatives/README.md`, `AGENTS.md`, WORKFLOW | **Generic baseline** | Structured non-executable unfinished context is generic; initiative contents local. |
| Reminder / initiative / task promotion boundary | same surfaces | **Generic baseline** | Prevents context from silently becoming authorization. |
| Agent-memory placement doctrine | `.agents/README.md`, `AGENTS.md` | **Generic baseline** | Durable expensive-to-rediscover memory vs temporary workspace vs human docs is widely useful. |
| Historical memory on-demand rule | `.agents/README.md` | **Generic baseline** | Prevents old investigations from becoming mandatory startup context. |
| Proactive durable-memory capture | `AGENTS.md`, `.agents/README.md` | **Generic baseline** | 'Preserve expensive rediscovery' is broadly useful; exact taxonomy can remain local. |
| `.agents/` directory taxonomy | `.agents/README.md` | **Generic with parameters/extensions** | `architecture/`, `investigations/`, `decisions/`, platform/app notes are useful conventions, but empty taxonomy should not be forced and local categories may differ. |
| Agent lineage namespace | `.agents/WORKFLOW.md`, CI doc | **Generic baseline candidate** | Recoverable `agent/{identifier}/...` branches and explicit recovery authority are project-neutral if consumers use GitHub/Git similarly. Exact naming grammar is policy, not technical necessity. |
| Recovery authority rule | `.agents/WORKFLOW.md` | **Generic baseline** | Discovering a branch must not itself authorize adoption; explicit human/current-conversation authority is broadly useful. |
| Git additive-history default | `AGENTS.md`, WORKFLOW | **Generic baseline** | Safe default across repos: no silent force/rebase/drop/squash of established history. |
| Checkpoint discipline | `AGENTS.md`, WORKFLOW | **Generic baseline** | Coherent/recoverable commits and smallest meaningful validation are project-neutral. |
| Isolated one-commit no-task exception | WORKFLOW | **Generic baseline candidate** | Useful anti-ceremony rule if the shared task model is adopted; consumers might parameterize how strict they want taskification. |
| Commit summary grammar | `AGENTS.md`, CI selector | **Generic with parameters/extensions** | Bracketed kind/scope format is reusable, but allowed kinds and enforcement may be customized. |
| Agent provenance registry/trailer | `.agents/PROVENANCE.md`, `AGENTS.md` | **Generic with parameters/extensions** | Provenance mechanism is broadly reusable; stable agent names/operator requirements and registered variants are maintained data. |
| Human-vs-agent provenance separation | `.agents/PROVENANCE.md` | **Generic baseline** | Distinguishing authorship from operation is generic. |
| Documentation style avoiding incidental identities | `autonomic_affairs/docs/DOCUMENTATION_STYLE.md` | **Generic baseline candidate** | Role-based durable docs are broadly helpful. Optional internal humor policy is maintainer preference and should not be imposed universally. |
| Centralized CI selector/event entry point | workflows + selector | **Generic architecture concept** | Single policy entry point, explicit overrides, fail-safe unknowns, and check-vs-runner separation are reusable concepts; current implementation is deeply parameterized by local checks and paths. |
| `CI:` override grammar | selector / CI docs | **Generic with parameters/extensions** | `auto/all/none` plus named checks/groups is reusable if a consumer opts into the CI policy engine. Registered checks/groups are local. |
| Git event-range semantics | selector | **Generic reusable logic candidate** | push `before..after`, PR three-dot, manual explicit selection, forced/missing evidence fail-safe are not MSHP-specific. |
| Commit-metadata validation across event range | selector | **Generic reusable logic candidate** | Generic mechanism; exact grammar is local/configurable. |
| Path-to-check relevance classifier | selector | **MSHP-specific implementation pattern** | Algorithm/pattern is reusable, but every actual path/check mapping is repository-specific. Never copy MSHP mappings as baseline. |
| Check-to-runner coalescing | selector/workflows | **Generic architecture concept** | Selecting logical checks before provisioning compatible runners is broadly useful. Runner groups/checks remain local. |
| Scheduled coverage reconciliation | selector/history | **Generic with parameters/extensions** | Prior-success/relevance-aware reconciliation is reusable; cadence, check identities, and whether a repo needs it are local policy. |
| Adaptive CodeQL cadence | selector/history | **Generic optional pattern** | Exact-HEAD daily→weekly behavior is not required by an agent baseline, but could be an opt-in reusable CI component. |
| CodeQL callable workflow pattern | `.github/workflows/codeql.yml` | **Generic reusable execution candidate** | Language input/build mode/category pattern may generalize, but language set/security policy remain repo-specific. |
| Repository-side task/CI tests | `autonomic_affairs/tests/**` | **Mixed** | Task/selector contract tests illustrate generic governance testing; most current tests are coupled to MSHP layout/check IDs and should not be copied wholesale. |
| Top-level directory contract | `AGENTS.md` | **MSHP-specific** | The thematic domains encode Machine-Soul architecture and should not appear in an unrelated baseline. |
| Configuration safety laws / symlink doctrine | `AGENTS.md` | **MSHP-specific** | Core Machine-Soul product behavior, not agent infrastructure. |
| Annexation/assimilation/runtime/application architecture | `autonomic_affairs/docs/*`, `.agents/architecture/*` | **MSHP-specific** | Project/domain architecture. |
| Developer annexation memory | `.agents/DEVELOPER_ANNEXATION.md` + investigations | **MSHP-specific** | Technical work for this repository. |
| Installation/discovery scope memories | `.agents/platforms/*`, investigations | **MSHP-specific** | Platform/product behavior, useful only here unless another repo genuinely shares the product. |
| Scrcpy tool memory | `.agents/scrcpy_virtual_screen_manager.md` | **MSHP-specific** | Standalone tool scar tissue; not baseline governance. |
| Dated investigations | `.agents/investigations/*` | **Historical/local knowledge** | Do not template them. Their organizational convention may be reusable, not their content. |
| V2 migration/decision snapshots | `.agents/decisions/*` historical files | **Historical/scar tissue** | Preserve here; never bootstrap into new repos. |
| GitHub Actions experiment record | `.agents/GITHUB_ACTIONS_CONTROL.md` | **Historical/local evidence + small generic lessons** | Current summary/lessons matter, but the whole experiment log is not baseline content. |
| Current task/reminder/initiative contents | autonomic task surfaces | **Repository-specific state** | Schemas may be reusable; contents never are. |

## Generic dependency clusters

### 1. Executable-work governance cluster

These components depend on each other and should not be extracted independently without care:

- task ledger/storage schema;
- task lifecycle states;
- Dispatch authorization semantics;
- Active claims;
- dependencies/order;
- block completion/terminal archival;
- task workspace rules;
- recovery/read-order rules.

For example, copying Dispatch without Active claims/recovery authority would not reproduce the coordination safety MSHP relies on. Copying task specs without the workspace/archive contract would create storage drift.

### 2. Non-executable context cluster

- reminders;
- initiatives;
- promotion rules into tasks;
- source-of-truth ownership.

The important reusable behavior is **non-executable by default**. The exact names `reminders` and `initiatives` are useful conventions but not the deeper invariant.

### 3. Agent-memory cluster

- `.agents/README.md` memory doctrine;
- durable-vs-temporary knowledge split;
- on-demand historical notes;
- startup reading order;
- human-doc promotion rule.

This cluster depends on the task workspace distinction: without a temporary tracked workspace, agents will tend either to lose intermediate research or pollute permanent memory.

### 4. Git/recovery/provenance cluster

- lineage namespace;
- recovery authority;
- additive-history default;
- checkpoint discipline;
- commit grammar;
- provenance registry/trailers.

Lineage alone is not enough; its safety derives from recovery-authority rules and task claims. Provenance is separate from lineage identity but shares commit/checkpoint policy.

### 5. CI-control cluster

- central event/policy entry point;
- explicit override parser;
- event-range evidence;
- fail-safe fallback;
- logical check registry;
- repository-local relevance mapping;
- runner coalescing;
- optional run-history reconciliation;
- callable execution workflows.

The **architecture** is reusable; the **registry/classifier** is necessarily repository-local. This is a strong candidate for generic core + local declaration rather than copied MSHP source.

## Required repository-local inputs if a baseline were adopted

A consumer would still need to define at least:

- repository purpose/mission;
- human-facing architecture and source-of-truth docs;
- repository-specific directory/layout ownership beyond the generic governance directories;
- local application/runtime/domain memory;
- local task/reminder/initiative contents;
- local CI checks, runner requirements, relevance mapping, and security analysis languages;
- project-specific safety laws;
- local branch/release practices if they intentionally differ from the baseline;
- provenance registrations beyond whatever generic registry seed is chosen;
- any custom commit kinds/scopes if allowed;
- which optional baseline modules (for example centralized CI or scheduled reconciliation) it actually adopts.

## Duplication / layering observations

Several MSHP rules intentionally appear in both a concise root guide and a detailed procedural document. That is **not automatically bad duplication**:

- `AGENTS.md` is a concise startup contract;
- `.agents/WORKFLOW.md` owns detailed execution/recovery procedure;
- human-facing autonomic docs explain durable architecture/policy.

A shared baseline should preserve that layering rather than trying to make one enormous canonical file. The risk to solve later is synchronized generic sections versus repository-local additions, not the existence of summary/detail layers.

Likewise, the CI docs split current policy from historical experiment evidence. A baseline should carry the current contract/mechanism, not historical MSHP experiments.

## Strongest baseline candidates

If forced to choose only the highest-value generic pieces today, they are:

1. concise root agent startup/read-order contract;
2. task/Dispatch/Active-claims/lifecycle/archive protocol;
3. reminder and initiative non-execution protocol;
4. task workspace vs durable agent-memory doctrine;
5. lineage/recovery-authority rules;
6. additive Git/checkpoint discipline;
7. provenance mechanism;
8. documentation/source-of-truth discipline;
9. optional centralized CI-policy framework with repository-local check/relevance declaration.

## Explicit non-candidates

Do **not** treat these as generic baseline content:

- Machine-Soul thematic directory taxonomy;
- symlink/configuration safety laws;
- annexation/assimilation/application/runtime architecture;
- existing MSHP tasks/reminders/initiatives;
- MSHP check IDs/path mapping;
- platform/application research notes;
- migration history;
- tool-specific memories.

## A-020 conclusion

The baseline should be designed as a **small generic governance kernel with local extension points**, not as a snapshot of MSHP.

The task/work/memory/provenance/recovery contracts are the reusable heart. CI is promising as an optional parameterized subsystem. Most technical/project memory and product architecture must remain local.

No distribution or override mechanism is selected by this task.
