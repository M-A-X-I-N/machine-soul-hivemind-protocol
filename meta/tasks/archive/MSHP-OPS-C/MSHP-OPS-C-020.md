# MSHP-OPS-C-020 — Add active task claims to the task ledger

## Description

Add a separate live-claims section inside the authoritative task ledger rather than creating another ledger file.

## Requirements

- Add an `Active claims` section outside task tables with enough fields for agents to coordinate safely; choose the exact compact schema based on agent usefulness.
- Define claim creation, update, release, FROZEN/BLOCKED/AWAITING_DEFERRED_CI behavior, and stale-claim handling.
- Treat claims as coordination locks only; explicitly prohibit using claim presence as lineage-adoption authority.
- Update claim/complete/recovery workflow instructions and any validation/parsers that need the new section.

## Constraints / non-goals

- Do not create a second claims file or competing ledger.
- Do not turn completed claims into a permanent museum if Git history already provides sufficient archaeology.
- Do not make the claims section human-ceremonial at the expense of agent usability.

## Acceptance criteria

- Agents can determine currently owned work from one ledger read.
- Claim lifecycle is explicit.
- Claim semantics reinforce, rather than weaken, recovery authority.

## Validation

- Exercise representative claim/release transitions in tests or controlled ledger edits.
- Search for consumers of the ledger structure.
