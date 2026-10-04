# MSHP-AGENT-BASELINE-A-060 — Versioning, compatibility, and migration policy research

Research date: 2026-10-04.

## Executive conclusion

A cross-repository baseline needs **separate identities for release ordering, exact provenance, and structural compatibility**.

One version string should not be overloaded to mean all three.

Strong candidate model:

1. **baseline release** — human-readable/orderable release identifier (for example `v1.4.0`);
2. **baseline source commit** — immutable Git SHA of the exact baseline source/render used;
3. **baseline schema version** — explicit compatibility/migration schema for consumer structure/interfaces;
4. **shared executable pins** — exact commit SHAs for every live reusable workflow/action component consumed by the repository.

A consumer may intentionally lag at an older release. Nothing remote should mutate its behavior merely because a newer baseline exists.

## GitHub Actions reference semantics

Reusable workflows can be referenced by branch, tag, or commit SHA.

GitHub's secure-use guidance states that pinning an action to a **full-length commit SHA** is the only way to consume an immutable action release. GitHub likewise documents commit-SHA references as the safest choice for reusable workflow stability/security.

Important nuance:

- repository/organization Actions policy can require full-SHA pinning for actions;
- GitHub currently documents that reusable workflows may still be referenced by tag even under that policy;
- therefore the baseline should enforce its own full-SHA policy for centrally shared reusable workflows rather than assuming repository settings will enforce it.

Official references:

- https://docs.github.com/en/actions/reference/security/secure-use
- https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows
- https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository

## Dependabot and pinned shared executable components

GitHub Dependabot version updates support the `github-actions` ecosystem and inspect workflow references.

GitHub explicitly documents that Dependabot:

- updates actions referenced from workflow YAML;
- also checks and updates Git references for called reusable workflows;
- supports references expressed as version/tag or commit identifier;
- can update a full-SHA reference while preserving/updating human-readable version documentation when the comment is on the same line.

This is a strong match for the desired security/review model:

```text
uses: M-A-X-I-N/agent-infrastructure/.github/workflows/policy.yml@<full-sha> # v1.4.0
```

Conceptually:

- SHA controls execution immutably;
- release/tag comment gives humans a readable version;
- Dependabot proposes a normal PR that changes the SHA/comment;
- consumer CI reviews the new shared implementation before merge.

Official references:

- https://docs.github.com/en/code-security/concepts/supply-chain-security/dependabot-version-updates
- https://docs.github.com/en/code-security/how-tos/secure-your-supply-chain/secure-your-dependencies/auto-update-actions

## GitHub immutable releases

GitHub now supports **immutable releases**.

When enabled/published as immutable:

- the associated Git tag cannot be moved or deleted while the release exists;
- release assets cannot be modified/deleted;
- publishing generates a release attestation;
- after deleting the immutable release, the old tag name cannot be reused.

This makes human-readable baseline/runtime release tags materially safer than ordinary mutable tags.

However, consumers should still record/pin the exact commit SHA:

- SHA is the direct immutable content identity;
- it works independently of release-feature configuration;
- it makes diagnostics/recovery exact;
- Actions secure-use guidance already prefers SHA pinning.

Immutable releases are therefore useful release integrity/metadata, not a substitute for SHA provenance.

Reference:

- https://docs.github.com/en/code-security/concepts/supply-chain-security/immutable-releases

## Copied baseline release version

Copied baseline policy/files need an **orderable release identity** so update tools can answer:

- what version is this repository on?
- what version is available?
- what migrations lie between them?
- is the target newer/older?
- is this a prerelease?

Current Copier provides a concrete precedent:

- templates are normally selected from Git tags;
- tags are interpreted/sorted using PEP 440;
- template answers store the selected commit/ref;
- template authors are warned not to move released version tags;
- update can target an explicit VCS ref;
- migrations can be guarded by versions and run when `new >= migration > old`.

References:

- https://copier.readthedocs.io/en/stable/generating/
- https://copier.readthedocs.io/en/stable/configuring/

### Candidate numbering models

#### Semantic-style `vMAJOR.MINOR.PATCH`

Pros:

- universally recognizable;
- compatible with normal GitHub release/dependency tooling;
- stable releases fit Copier/PEP-440-friendly tag expectations;
- can encode a meaningful compatibility contract if this project defines one.

Possible baseline-specific semantics:

- **MAJOR** — baseline contract/schema compatibility break or mandatory manual migration;
- **MINOR** — backward-compatible baseline capability/profile addition, possibly with automated migration;
- **PATCH** — compatible fixes/docs/implementation changes requiring no consumer contract change.

Risk:

Agent policy is not a conventional library API. A one-line instruction change may be behaviorally significant even when file schema is unchanged. Version increments therefore require an explicit baseline compatibility policy rather than blindly applying software-package intuition.

#### Calendar versioning

Pros:

- easy chronology;
- baseline changes are policy/ops releases rather than a library API;
- no pretense that compatibility impact can always be encoded semantically.

Cons:

- does not by itself tell an updater whether structural migration is required;
- migration logic still needs a separate schema/compatibility dimension;
- ordering is useful but compatibility meaning is weak.

#### Monotonic integer/revision

Pros:

- trivial ordering;
- migration graph is easy.

Cons:

- poor human communication;
- awkward for release notes/prereleases;
- throws away useful compatibility signaling.

### Research preference

Use a human-readable release version (semantic-style is the strongest candidate) **but do not make it the sole compatibility key**. Pair it with an explicit schema version.

## Separate baseline schema version

The consumer manifest should contain a baseline schema version independent of release.

Purpose:

- identify the shape/contracts the consumer implements;
- distinguish structural migration from compatible content/implementation changes;
- let tooling reject a consumer whose schema is too old/new to understand;
- let multiple releases share the same schema;
- allow migration tests to focus on schema transitions.

Example conceptual state:

```yaml
baseline:
  release: v1.7.2
  commit: 0123456789abcdef...
  schema: 3
  profile: standard
```

A release may:

- change generic wording/fix logic without changing schema;
- add optional profile features without changing core schema;
- bump schema when file ownership/layout/manifest/task/CI interfaces change.

Schema version should be intentionally boring and monotonic. It does not need SemVer unless real independent major/minor schema axes emerge.

## Manifest schema versus baseline schema

The manifest file itself also has a parse format.

Two approaches:

1. one `schema` means both baseline contract and manifest syntax;
2. separate `manifest_schema` from `baseline_schema`.

Research preference:

- begin with one schema only if the manifest is deliberately tiny/stable;
- split them when updater compatibility genuinely requires distinguishing 'I cannot parse this manifest' from 'I understand the manifest but cannot migrate this baseline contract'.

Do not add version axes preemptively without a consumer.

## Shared runtime versioning

Live shared executable components should be independently pinnable from the copied baseline release.

Reason:

- copied baseline v1.7 may be compatible with policy engine runtime v2.3;
- a security/bug fix to shared runtime need not require regenerating every baseline document;
- conversely a baseline schema migration may require updating local files before a newer runtime can be used.

Consumer state should therefore be able to record the exact shared component pins actually in effect.

For GitHub workflows/actions, the workflow YAML itself records the SHA. A manifest may duplicate a friendly expected release/component set for diagnostics, but **the executable `uses:` SHA is the runtime source of truth**.

## Compatibility matrix

A serious implementation should define compatibility among:

- baseline release;
- baseline schema;
- updater/tool version;
- shared workflow/action interface version;
- selected profile/modules;
- repository-local policy schema.

Not every combination needs central matrix data if interfaces are self-validating.

Useful rule:

> validate interfaces at the boundary, pin implementations exactly, migrate schemas explicitly.

Examples:

- reusable workflow declares required/optional typed inputs;
- local policy/manifest declares schema;
- updater declares supported schema range;
- migration target declares resulting schema;
- consumer pins exact runtime SHA.

## Intentionally lagging repositories

Repositories must be allowed to stay behind deliberately.

Required behavior:

- current pinned baseline/runtime continues to function;
- update-check may report newer versions but does not mutate;
- no remote moving branch changes behavior;
- security policy may separately flag an obsolete/vulnerable runtime;
- migration tooling can plan from the old supported version to a target version;
- if the old version falls outside supported migration range, tooling must stop with an explicit manual-adoption requirement.

This strongly argues against consumers referencing `@main` for shared policy machinery.

## Compatibility support window

A future baseline should explicitly state how far back automatic migration is supported.

Candidate models:

- every historical release forever — simplest promise, potentially unbounded maintenance;
- every schema version forever — still grows indefinitely;
- last N major/schema generations — bounded, old consumers require staged/manual adoption;
- migration checkpoints/squashed baselines — preserve selected old anchors rather than every patch.

No window is selected by research. The first implementation should avoid promising infinite support before real fleet experience exists.

## Migration model

Migrations should be **ordered, version-aware, idempotent where practical, and reviewable**.

Two different migration classes:

### File/content reconciliation

Use old-render → local evolution → new-render three-way semantics from A-040.

This handles ordinary baseline text/file evolution while preserving local changes.

### Structural migration

Use explicit migration steps when ownership/layout/interface changes, for example:

- split monolithic `AGENTS.md` into thin loader + local profile;
- move task protocol out of dynamic task index;
- rename baseline manifest field;
- replace local copied CI engine with a pinned reusable workflow;
- introduce/remove a profile/module.

Migrations should:

- declare applicable from/to version/schema boundaries;
- validate preconditions;
- refuse unknown state;
- preserve/back up content needed for rollback/recovery;
- produce a normal Git diff;
- update the manifest only after the transformation succeeds;
- be testable against fixtures representing older baseline states.

Copier's ordered versioned migrations are useful precedent, but executable template migrations are trusted code and must be reviewed/pinned accordingly.

## Migration graph

Prefer a **linear supported migration path** unless evidence demands branching.

Example:

```text
schema 1 -> schema 2 -> schema 3
```

A repo on schema 1 targeting release on schema 3 applies/validates both transitions.

Avoid writing every pairwise migration (`1->3`, `1->4`, `2->4`) unless performance proves necessary.

Profiles/modules may add conditional migration steps, but the core schema progression should remain understandable.

## Rollback model

Because updates should land as ordinary consumer pull requests/commits, primary rollback is ordinary Git revert.

A baseline-update commit/PR should change together:

- baseline-derived files;
- manifest release/commit/schema;
- shared runtime pins if changed;
- repository-side setting declarations/migrations where applicable;
- migration notes.

Reverting that checkpoint restores a coherent previous baseline state.

Structural migrations that mutate external GitHub repository settings must:

- record before/after desired/observed state;
- use reversible operations where API permits;
- document manual rollback when automatic rollback is impossible.

Do not delete unique repository data as part of a baseline migration without explicit human approval.

## Failed update recovery

Updater should distinguish:

- planning failure — no working-tree mutation;
- merge conflict — leave explicit conflict/reject artifacts, manifest remains old version;
- migration failure — stop before marking target applied;
- validation failure — proposed update remains unmerged/revertible;
- post-merge shared-runtime failure — revert baseline update or pin back to known-good SHA.

Never record `release=vNext` merely because update started.

## Release artifacts and notes

Every baseline release should eventually carry machine- and human-readable information:

- release identifier;
- exact source commit SHA;
- baseline schema;
- supported updater/runtime ranges if constrained;
- migration notes;
- changed baseline components;
- whether changes are policy-behavioral, structural, shared-runtime-only, or documentation-only;
- known manual review points.

GitHub Releases are a good human/distribution surface; immutable releases are attractive when available.

## Development refs and prereleases

Moving branches are appropriate for baseline **development**, not consumer production pins.

Potential flow:

- `main` = current development/integration;
- prerelease tags/releases = opt-in testing;
- stable release tag + recorded SHA = consumer update target;
- shared workflow/action consumer uses exact SHA, optionally annotated with release tag.

Copier similarly defaults to latest stable version tag and ignores prereleases unless requested.

This cleanly separates experimenting with baseline development from repositories adopting it.

## Baseline release and shared runtime repository split

Versioning research also reveals an architectural consideration for A-070:

If copied baseline source and live shared runtime reside in different repositories, they can release independently while the baseline release records compatible runtime pins.

If they reside in one repository, a single commit SHA can identify both, but:

- every runtime release also advances template source;
- every template-policy release also advances runtime source;
- GitHub template generation copies live reusable workflow files into consumers;
- release cadence is coupled even when the artifacts have different compatibility needs.

This is evidence favoring a role split, though A-070 must weigh it against operational simplicity.

## Recommended identifiers entering A-070

A consumer should be able to answer at least:

- baseline source repository;
- applied baseline release;
- exact baseline source commit;
- baseline schema;
- selected profile/features;
- intentional deviations/detached components;
- exact shared executable pins;
- updater/tool version used for last migration when diagnostically useful.

## A-060 conclusion

The safest version model is **human release + immutable SHA + explicit schema**, with live shared executable components separately full-SHA pinned.

Updates are proposed migrations between known consumer states, not pulls from a moving branch.

Dependabot can provide PR-based updates for pinned GitHub Actions/reusable workflow dependencies, while the baseline updater handles copied policy/schema changes.

Repositories may intentionally lag; compatibility must be validated rather than silently upgraded. Ordinary Git revert is the primary rollback mechanism because baseline adoption should land as one coherent consumer checkpoint.
