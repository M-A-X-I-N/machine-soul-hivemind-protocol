# MSHP-AGENT-BASELINE-B-070 — Manual maintenance/adoption validation

## Scope

Validate the implemented v1 manual lifecycle defined in `.agents/baseline/MAINTENANCE.md`.

The procedure must work without:

- shared Git ancestry with the GitHub template;
- a baseline-version file;
- a manifest/schema marker;
- an updater bot;
- Copier/Cruft state;
- a shared runtime repository.

## Canonical generic surface

At validation time the baseline-managed surface is:

```text
.agents/README.md
.agents/baseline/WORKFLOW.md
.agents/baseline/GIT.md
.agents/baseline/PROVENANCE.md
.agents/baseline/KNOWLEDGE.md
.agents/baseline/MAINTENANCE.md
```

All six files are blob-identical between `M-A-X-I-N/baseline@main` and the MSHP Sera consumer checkpoint.

| File | Blob |
|---|---|
| `.agents/README.md` | `a6aa9732f1b29af99ef5c4373d927c8c6205486e` |
| `.agents/baseline/WORKFLOW.md` | `08cfdd47ebabf9b90564785ac4adc112455580a8` |
| `.agents/baseline/GIT.md` | `21caa58693358f230e2647f0331cebe847b24587` |
| `.agents/baseline/PROVENANCE.md` | `a040e776c75bbbbbf02cde048c9992d8f8a71bfd` |
| `.agents/baseline/KNOWLEDGE.md` | `89a5c0f34b3fd64a69fd069de702df7bdf6f12c0` |
| `.agents/baseline/MAINTENANCE.md` | `a8e492ce1fd58ce6d2273ee47dac7e462ab121b9` |

Repository-owned MSHP files remain different by design.

## Update walkthrough

B-070 itself exercised a real consumer update equivalent to the required hypothetical.

### Starting condition

Assume a consumer already has the previous baseline:

- the five older generic files are current;
- `MAINTENANCE.md` does not exist;
- the generic router has no maintenance route;
- local policy, memory, and live project/task state contain consumer-specific content.

### Canonical change

A generic maintenance lifecycle is developed in `M-A-X-I-N/baseline`:

1. add `.agents/baseline/MAINTENANCE.md`;
2. add an on-demand maintenance/adoption route to `.agents/README.md`;
3. validate the generic change there.

No local consumer files are edited to define the generic rule.

### Consumer comparison

The consumer comparison classifies:

- existing five generic files: **identical**;
- `.agents/baseline/MAINTENANCE.md`: **missing generic file**;
- `.agents/README.md`: **generic baseline change**;
- `.agents/local/*`, `.agents/memory/*`, and task state: **repository-owned; not baseline drift**.

No shared template ancestry is required to reach this classification.

### Consumer reconciliation

The consumer:

1. adds the canonical `MAINTENANCE.md`;
2. replaces the generic router with the canonical router;
3. leaves local policy/memory/task state untouched;
4. validates the generic blobs against the canonical baseline;
5. commits through ordinary consumer history.

That exact sequence was performed for MSHP during B-070.

### Result

All baseline-managed blobs match the canonical source and MSHP's local files remain MSHP-specific.

This proves the normal update path without a version/manifest/updater mechanism.

## Local-leakage conflict walkthrough

Assume a consumer had previously edited generic `WORKFLOW.md` to add:

> Releases in this repository require a local staging-machine check.

The comparison must **not** preserve that line as an unexplained generic fork.

Instead:

1. Git history/blame establishes that the line was a consumer-specific addition;
2. the rule is moved into a suitable `.agents/local/` instruction file and routed from `.agents/local/README.md`;
3. generic `WORKFLOW.md` is refreshed from the canonical baseline;
4. the local rule remains authoritative through explicit local-over-baseline precedence.

Result: the local behavior survives while the generic surface becomes comparable again.

## Legacy-repository adoption walkthrough

Assume an existing repository did not originate from the template and currently has:

```text
AGENTS.md                 # mixed generic + repository-specific instructions
notes/agent_history.md    # useful non-normative investigation history
TODO.md                   # live project work tracking
src/...
```

There is no baseline metadata or template ancestry.

### 1. Inspect

Read the repository's current agent instructions, work tracking, project documentation, and relevant Git history.

Do not assume any relationship to `M-A-X-I-N/baseline`.

### 2. Classify

Split existing material semantically:

- generic workflow/recovery behavior → candidate baseline overlap;
- repository mission/safety/build/release rules → local normative policy;
- historical investigation/rationale → memory or human documentation;
- live TODO/task state → repository-owned project-control state;
- source/project files → unrelated to baseline adoption.

### 3. Introduce the topology

Add the canonical baseline-managed files from `M-A-X-I-N/baseline`.

Create/adapt repository-owned:

```text
AGENTS.md
.agents/local/
.agents/memory/
project/
```

The exact lowercase `project/` name is retained regardless of source-code casing conventions.

### 4. Preserve local semantics

Repository-specific instructions from the old mixed `AGENTS.md` move into `.agents/local/`.

Useful historical agent notes move to appropriate non-normative memory/documentation.

The existing `TODO.md` is **not** overwritten by empty template `project/tasks.md` state. Its work is mapped deliberately into the new task model (or preserved until such mapping can be done safely).

### 5. Do not fake ancestry

Do not:

- merge template history;
- record a fictitious template parent;
- create a baseline-version/manifest marker;
- claim that the repository was generated from the template.

The adoption commit is ordinary new history in the legacy repository.

### 6. Validate

Confirm:

- canonical generic files are present;
- local policy remains explicit and discoverable;
- existing project state was preserved;
- root → generic router → local router → project/memory navigation resolves;
- no repository-specific rules leaked into baseline-managed files;
- no step requires automation/version state.

### Result

The repository has adopted the same current baseline contract while retaining truthful independent history and repository-specific behavior.

## Architecture/reminder consistency

The durable architecture document now:

- marks manual v1 as implemented;
- names `M-A-X-I-N/baseline` as the canonical generic source;
- records the exact baseline-managed/local ownership boundary;
- records exact lowercase `project/` as the reserved project-control integration path;
- explicitly rejects manifest/version/schema state for v1;
- points to `.agents/baseline/MAINTENANCE.md`;
- parks broader synchronization/runtime research behind evidence-based triggers.

The reminder now describes future automation only as an evidence-driven follow-up after implemented manual v1, rather than as unfinished B-block work.

## Conclusion

B-070 acceptance criteria are satisfied.

Manual comparison/adoption is explicit, recoverable through ordinary Git, preserves local overrides, does not depend on template ancestry, and has a defined evidence threshold for reopening the broader A-block automation research.
