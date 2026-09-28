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

A chat/session interruption does not create a new lineage. A recovery agent may adopt the existing identifier when continuing the same work.

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

Normal substantive development should prefer the lineage namespace. This is not a prohibition on direct `main` work: coordination state, task bookkeeping, policy/control-plane changes, and other small changes whose natural home is `main` may land there directly.

## Validation philosophy

The goal is to reduce **wasted CI**, not CI usage. Run validation whenever it has useful information value, including repeated intermediate checks when they materially improve confidence or regression localization.

Selection is explicit. Changed paths are not an authority and must not route CI.

## Registered blocking validation sets

The initial registered blocking validation sets are:

- `linux` — Linux Python/model and Linux application/install/session/matrix validation.
- `windows` — Windows Python/model and Windows application/POSIX/install validation.
- `fresh-linux` — Linux fresh-clone application validation.
- `fresh-windows` — Windows fresh-clone application validation.

`all` means all registered blocking sets; it is an alias, not a fifth set.

## Main integration

A push to `main` runs all registered blocking validation sets by default.

The pushed tip commit may override the default with a commit trailer:

```text
CI: all
CI: none
CI: shared,windows
```

The dispatcher owns the exact registered set names. Whitespace is normalized and duplicate set names are harmless. Unknown or malformed selectors fail safe: the selector control job reports failure while all registered validation sets still run, so a typo can never silently reduce validation.

When multiple commits arrive in one push, the pushed `main` tip controls that integration event.

For a commit that should instantiate no normal checked-in push workflow at all, native GitHub trailer syntax may be used:

```text
skip-checks: true
```

This is especially suitable for pure coordination/bookkeeping. It is a hard bypass, distinct from the dispatcher-level `CI:` selector. `CI: none` still runs the small selector/control job so GitHub records the intentional decision; use `skip-checks: true` when even that control-plane run would be wasteful.

## Non-main development

Ordinary pushes to non-main branches, including `agent/**`, do not automatically launch normal blocking validation.

Validation can be explicitly dispatched against any chosen ref/agent branch. The caller may request all registered sets or a useful subset. Intermediate CI is encouraged whenever it is valuable; it is simply not automatic per commit.

## Blocking and deferred CI

Blocking validation is the advancement gate for implementation work.

Explicitly deferred repository analysis may remain pending after blocking validation succeeds. While that happens, the task enters:

```text
AWAITING_DEFERRED_CI
```

A task in that state may yield active implementation to the next task, but it cannot become `COMPLETE` until its required deferred checks succeed.

Within an ordered workstream, later tasks must not be marked `COMPLETE` past an unresolved earlier `AWAITING_DEFERRED_CI` task. A substantive deferred-analysis failure reopens/blocks the originating work and prevents later completion until resolved. Infrastructure-only failures are retried or investigated without being misclassified as code defects.

Specific analysis products such as CodeQL are classified separately; the lifecycle state is intentionally product-agnostic.

## Frozen work

`FROZEN` records an intentional priority/policy pause. It is not a dependency and does not imply a technical or human blocker. Thawing restores the prior executable checkpoint unless repository evidence requires a different state.
