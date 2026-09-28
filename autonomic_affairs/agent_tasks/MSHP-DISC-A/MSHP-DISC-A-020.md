# MSHP-DISC-A-020 — Investigate installation discovery

## Description

Investigate how much reliable information Machine-Soul can discover about existing application installations across the currently supported Windows and Linux environments.

Start from the ideal of maximum useful granularity, then reduce only where operating-system/application reality requires it.

## Requirements

- Inventory the installation mechanisms relevant to current applications and platforms, including preferred mechanisms and plausible non-preferred/foreign mechanisms.
- Investigate what evidence each mechanism exposes for at least:
  - application presence;
  - exact package/product identity;
  - installation mechanism/provider;
  - version;
  - executable/path locations;
  - user/system scope where meaningful;
  - package-manager registration;
  - uninstall identity/mechanism where discoverable;
  - whether the installation matches the preferred Machine-Soul install strategy;
  - whether Machine-Soul state records ownership;
  - ambiguity or multiple simultaneous candidates.
- On Windows, investigate relevant sources such as WinGet registration/correlation, MSI/installed-product registration where appropriate, PATH/known executable locations, Store/package identities, and other mechanisms actually relevant to the current application set.
- On Linux, investigate relevant package-manager metadata, executable resolution, package ownership queries, upstream/manual/portable installations, and other mechanisms actually relevant to the current application set.
- Distinguish evidence that proves an installation mechanism from evidence that merely suggests one.
- Identify which discovery capabilities are generic by platform/mechanism and which genuinely require application-specific hints/hooks.
- Design with future installation takeover in mind: preserve enough identity/provenance/scope/uninstall information that a later takeover feature is not blocked by an impoverished discovery model.
- Record substantial intermediate research in the DISC-A workspace rather than bloating permanent `.agents/` memory.
- Distill durable reusable platform/application findings into `.agents/` or normal documentation where appropriate.

## Constraints / non-goals

- This is an investigation/design task, not the implementation of a complete detector.
- Do not uninstall, reinstall, adopt, migrate, or otherwise mutate existing software installations.
- Do not treat an installation found by a non-preferred mechanism as broken merely because it is foreign.
- Do not equate preferred mechanism with Machine-Soul ownership.
- Do not promise a level of provenance certainty that the underlying platform cannot supply.
- Do not implement the future installation-takeover reminder.

## Acceptance criteria

- The investigation provides a capability/evidence map for the current Windows/Linux installation mechanisms relevant to Machine-Soul.
- The resulting proposed data model can represent preferred/unpreferred mechanism, managed/unmanaged ownership, locations, versions, scope, ambiguity, and evidence quality independently.
- Generic library responsibilities and app-specific discovery hints are separated.
- Unknown/ambiguous installations have explicit semantics rather than being forced into absent/present.
- The investigation identifies concrete implementation seams/tasks to be synthesized by `MSHP-DISC-A-050`.

## Validation

- Apply the proposed model to representative current applications on both Windows and Linux.
- Check at least one preferred-package-manager installation, one manually/foreign installed hypothetical or reproducible case, and one ambiguous/multiple-candidate case.
- Verify the model retains information useful to a future safe takeover workflow without performing takeover.
