# Agent lineages and CI control

This policy defines how Machine-Soul agent work is isolated, recovered, integrated, and validated.

## Agent lineage identity

An agent work lineage uses:

```text
{name}_YYMMDD-HHmmss
```

- `name` is exactly four lowercase ASCII letters forming a short female, neutral, or fantasy-style human-readable name.
- Prefer a first letter not already in active/recent lineage use when practical.
- Do not maintain a canonical name list.
- The timestamp is the lineage creation time in UTC with second precision and never changes.
- The complete identifier, not the name alone, is the lineage identity.

A chat/session interruption does not create a new lineage. However, the existence of a lineage branch is **not** authority to adopt it. Recovery adoption requires explicit human authorization naming that lineage/branch, or an unambiguous continuation instruction in a conversation where ownership of that lineage was already established.

An unrelated agent may inspect an existing lineage and ask whether recovery is desired, but must not mutate or adopt it autonomously. Task state or claim metadata can coordinate ownership but does not confer recovery authority.

After authorized adoption, the agent must verify the actual lineage head against the expected checkpoint. Unexpected unrelated work is a stop condition requiring explicit reconciliation; it must not be silently absorbed, overwritten, or used as evidence that the recovering agent now owns that work.

## Branch ownership

A lineage owns:

```text
agent/{identifier}/*
```

Its canonical working branch is:

```text
agent/{identifier}/main
```

Additional branches inside that namespace are unrestricted apart from normal Git ref validity.

## Active task claims

The authoritative task ledger contains a live **Active claims** section outside task tables. Each row identifies the task, authorized lineage, canonical branch, claim time, and any short coordination note.

Claims are exclusive coordination markers for active execution, not lineage-recovery credentials. Finding a claim does not authorize another chat/agent to become that lineage.

Claims normally persist through `IN_PROGRESS`, `BLOCKED`, and `AWAITING_DEFERRED_CI` while the same lineage owns continuation. A task frozen from active work normally releases its claim unless retained ownership is made explicit. Terminal states do not keep active claims.

Suspected stale or inconsistent claims are reconciliation problems: inspect task state and branch history and obtain/confirm authority rather than stealing or silently deleting the claim.

Normal substantive development should prefer the lineage namespace. This is not a prohibition on direct `main` work: coordination state, task bookkeeping, policy/control-plane changes, and other small changes whose natural home is `main` may land there directly.

## Validation philosophy

The goal is to reduce **wasted CI**, not CI usage. Validation should run whenever it has useful information value, while checks that have no relevance to the changed state should not consume runner work merely because they share an operating system.

The centralized policy engine distinguishes three layers:

1. **Evidence** — event SHAs, Git diffs, commit/control metadata, and prior successful run history.
2. **Checks** — the logical validations that are actually relevant.
3. **Runner groups** — Linux, Windows, fresh-clone, and CodeQL jobs onto which compatible selected checks are coalesced.

Changed paths are conservative evidence for automatic selection. They are not trusted to suppress validation when classification is unknown or evidence is incomplete: uncertainty selects the complete registered check set.

## Registered checks and runner groups

Blocking check IDs:

- `linux-python`
- `linux-applications`
- `linux-install`
- `linux-session`
- `linux-matrix`
- `windows-python`
- `windows-applications`
- `windows-posix`
- `windows-install`
- `fresh-linux`
- `fresh-windows`

Deferred security-analysis check IDs:

- `codeql-python`
- `codeql-actions`

`linux` and `windows` are convenience aliases that expand to their current OS check families. `all` means every registered check; `none` means no downstream check; `auto` explicitly requests automatic classification.

Selection happens at check granularity. Compatible Linux checks share one Linux job, compatible Windows checks share one Windows job, and so on. A selected runner does not imply every check runnable there must execute.

## Centralized event routing

`.github/workflows/machine_soul_validation.yml` is the sole checked-in CI event entry point:

- push to `main`;
- pull request targeting `main`;
- `workflow_dispatch`;
- daily schedule `9 6 * * *` (06:09 UTC).

The downstream Linux, Windows, fresh-clone, and CodeQL workflows are callable execution machinery only.

Ordinary pushes to non-main branches, including `agent/**`, remain quiet. Manual dispatch targets the selected ref and uses explicit selection; it does not invent an automatic diff range.

### Pushes and pull requests

For an existing-branch push, automatic evidence is the event `before..after` range. For a PR, automatic evidence is the three-dot base/head range using the merge base.

The policy engine validates the introduced commit/control metadata when the range can be established. Forced pushes, missing objects, missing merge bases, unclassified files, and similar ambiguity fail safe to the complete check set rather than silently suppressing work.

A valid explicit `CI:` line on the pushed/PR head overrides automatic classification:

```text
CI: auto
CI: all
CI: none
CI: linux,windows
CI: linux-python,codeql-python
```

Whitespace/duplicates normalize. `all`, `none`, and `auto` must be standalone. Multiple `CI:` lines, unknown names, empty tokens, or other malformed selectors make the policy job fail visibly while its already-emitted fail-safe outputs select every registered check.

Native GitHub trailer syntax remains the harder bypass:

```text
skip-checks: true
```

`CI: none` still instantiates the small policy job so GitHub records the decision. Correctly formatted native `skip-checks: true` prevents the checked-in push/PR workflow from starting at all. A skipped event does not permanently mark its tree as covered; scheduled reconciliation may later run stale checks.

## Scheduled coverage reconciliation

The policy workflow runs daily at 06:09 UTC and asks which checks current default-branch HEAD still lacks meaningful successful coverage for.

For ordinary blocking checks:

1. exact-HEAD success covers the check;
2. an older successful SHA can continue to cover current HEAD when no path relevant to that check changed afterward;
3. if a relevant path changed, the check becomes due;
4. missing run history, an unreachable old SHA, or comparison ambiguity makes the affected check due.

Skipped/failed/cancelled steps do not count as successful coverage. Stable `Check <check-id>` step identities are the historical check keys.

CodeQL deliberately uses stricter exact-HEAD coverage, independently for Python and Actions:

- no successful run on current HEAD → run now;
- current HEAD younger than 168 hours → due when the language's last success on that HEAD is at least 24 hours old;
- current HEAD at least 168 hours old → due when the language's last success on that HEAD is at least 168 hours old.

Thus an actively changing default branch receives daily CodeQL rescans, while a quiet HEAD settles to weekly cadence without requiring a separate weekly workflow.

## Blocking and deferred CI

Blocking checks remain the advancement gate for implementation work.

CodeQL launch selection is centralized in the same policy engine, but CodeQL remains **deferred security analysis**. Its stable policy remains:

- languages `python` and `actions`;
- `build-mode: none`;
- default high-precision/default security query suite;
- stable result category `/language:<language>`;
- least-privilege upload permissions scoped to the CodeQL call jobs.

If blocking validation succeeds while completion-required CodeQL is still pending, use:

```text
AWAITING_DEFERRED_CI
```

A task in that state may yield active implementation to the next task, but it cannot become `COMPLETE` until its required deferred checks succeed. Within an ordered workstream, later tasks must not be marked `COMPLETE` past an unresolved earlier deferred task. Substantive deferred-analysis failures reopen/block originating work; infrastructure-only failures are retried or investigated separately.

## Frozen work

`FROZEN` records an intentional priority/policy pause. It is not a dependency and does not imply a technical or human blocker. Thawing restores the prior executable checkpoint unless repository evidence requires a different state.
