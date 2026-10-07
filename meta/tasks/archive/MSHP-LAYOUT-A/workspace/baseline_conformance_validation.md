# MSHP-LAYOUT-A-060 — Final baseline conformance validation

## Scope

Validate MSHP as a consumer of the current canonical agent baseline after the repository layout normalization.

Canonical source inspected for this pass:

```text
M-A-X-I-N/baseline@b5e01f97dd00a44372e2a9d4b81b725eda40af17
```

MSHP consumer lineage:

```text
agent/sera_261003-192400/main
```

The preceding A-050 post-migration validation checkpoint on `main` completed successfully in GitHub Actions run `37555017500`.

## Baseline-managed surface

The current baseline-managed generic surface is:

```text
.agents/README.md
.agents/baseline/WORKFLOW.md
.agents/baseline/GIT.md
.agents/baseline/PROVENANCE.md
.agents/baseline/KNOWLEDGE.md
.agents/baseline/MAINTENANCE.md
```

Blob comparison against `M-A-X-I-N/baseline@main`:

| File | Canonical blob | MSHP blob | Result |
|---|---|---|---|
| `.agents/README.md` | `a6aa9732f1b29af99ef5c4373d927c8c6205486e` | `a6aa9732f1b29af99ef5c4373d927c8c6205486e` | identical |
| `.agents/baseline/WORKFLOW.md` | `08cfdd47ebabf9b90564785ac4adc112455580a8` | `08cfdd47ebabf9b90564785ac4adc112455580a8` | identical |
| `.agents/baseline/GIT.md` | `21caa58693358f230e2647f0331cebe847b24587` | `21caa58693358f230e2647f0331cebe847b24587` | identical |
| `.agents/baseline/PROVENANCE.md` | `a040e776c75bbbbbf02cde048c9992d8f8a71bfd` | `a040e776c75bbbbbf02cde048c9992d8f8a71bfd` | identical |
| `.agents/baseline/KNOWLEDGE.md` | `89a5c0f34b3fd64a69fd069de702df7bdf6f12c0` | `89a5c0f34b3fd64a69fd069de702df7bdf6f12c0` | identical |
| `.agents/baseline/MAINTENANCE.md` | `07ae2329e9f255a56a2a9bb40aaea4da2a63d2eb` | `07ae2329e9f255a56a2a9bb40aaea4da2a63d2eb` | identical |

A content scan of the canonical generic surface found no Machine-Soul/MSHP-specific names, annexation/assimilation policy, MSHP control paths, or layout-task identifiers.

Result: no generic drift and no local-policy leakage into baseline-managed files.

## Repository-owned divergence

MSHP intentionally differs from the template seed in repository-owned files.

### Root AGENTS.md

The baseline seed provides generic startup/navigation behavior.

MSHP's root `AGENTS.md` preserves the same routing contract while adding its repository identity and explicitly naming the MSHP-specific local instructions.

This is correct repository-owned specialization, not baseline drift.

### .agents/local/

The baseline local seed contains placeholders and generic `meta/` navigation.

MSHP's local policy:

- defines the actual Machine-Soul repository purpose and source-of-truth map;
- routes layout/configuration/CI concerns to MSHP-owned local instruction files;
- points executable work to `meta/tasks.md` and `meta/tasks/`;
- points reminders and initiatives to their live MSHP-owned locations;
- documents the normalized `annexation/`, `assimilation/`, `tools/`, `research/`, `experiments/`, `assets/`, and `archive/` responsibilities;
- preserves explicit local-over-baseline precedence.

Those differences are precisely what the local ownership boundary is for.

### meta/

The baseline template seed owns the **path contract**, not consumer state.

Both baseline and MSHP use exact lowercase:

```text
meta/
```

MSHP correctly owns its live contents, including:

- executable task ledger and task specifications;
- task archive/workspaces;
- reminders;
- initiatives;
- human-facing project architecture;
- repository tests;
- CI-control helpers.

The live MSHP task/reminder/initiative state was not replaced by the template's empty seed state.

## Fresh-session navigation walkthrough

The following current surfaces were resolved directly from the consumer branch:

```text
AGENTS.md
  ↓
.agents/README.md
  ↓
.agents/local/README.md
  ↓
.agents/local/REPOSITORY.md
  ↓
meta/tasks.md
  ↓
meta/tasks/MSHP-LAYOUT-A/MSHP-LAYOUT-A-060.md
```

Non-executable state also resolves from the local router:

```text
meta/reminders.md
meta/initiatives/README.md
```

Demand-loaded memory remains separate and reachable; for example:

```text
.agents/memory/architecture/atomic_wrappers.md
```

This preserves the baseline's normative-policy versus non-normative-memory split.

## Reserved meta path

The canonical baseline now reserves exact lowercase `meta/`.

MSHP follows that contract exactly.

Repository-local naming conventions do not recase the path, and the normalized source/domain directories remain independent of the baseline integration path.

The dedicated runtime root sentinel remains:

```text
.machine_soul_root
```

Its role is repository-root discovery and is independent of the `meta/` control-plane path.

## Stale pre-meta baseline documentation

A-050 corrected the remaining live architecture text that still described the old `project/` baseline namespace.

The current durable baseline architecture and maintenance guidance describe `meta/`.

Historical task/archive evidence is intentionally not rewritten merely to erase prior names.

## Validation inheritance

A-050's final post-migration checkpoint (`a19a5bf49727069fe362aea70ec8f6c68fea6af5`) passed the full selected validation matrix:

- policy;
- Linux validation;
- Windows validation;
- fresh-clone Linux;
- fresh-clone Windows;
- CodeQL Python;
- CodeQL Actions.

A-060 introduced no runtime/configuration/CI implementation changes after that checkpoint; it is a consumer-conformance audit and documentation record.

## Conclusion

MSHP is fully aligned with the current canonical baseline contract.

- baseline-managed files are byte-identical;
- generic policy contains no MSHP-specific leakage;
- repository-owned differences are intentional and correctly located;
- exact lowercase `meta/` is used as the shared integration path;
- live MSHP task/reminder/initiative state remains repository-owned;
- fresh-session routing and demand-loaded memory navigation are coherent;
- no hidden exception, manifest, updater, or fake template ancestry is required.

No reconciliation change was necessary during A-060.
