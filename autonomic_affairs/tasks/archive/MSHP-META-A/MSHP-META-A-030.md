# MSHP-META-A-030 — Genericize concrete machine identities in durable documentation

## Description

Make durable human- and agent-facing documentation describe hosts/accounts/machines generically unless a concrete identity is materially necessary to the fact being documented.

## Requirements

- Replace incidental concrete host/account/home-path examples with conceptual terms such as `<linux_host>`, `<target_account>`, `<privileged_account>`, or clear prose.
- Apply the rule to README/docs, durable `.agents/` notes, and historical task prose where identities are merely examples.
- Retain concrete identities in actual configuration, host-specific configuration paths, runtime/test fixtures, persisted state formats, and investigations where identity is genuinely the subject.
- Preserve accurate explanations of host/account selection, configuration precedence, SSH/sudo boundaries, and platform differences.

## Constraints / non-goals

- Do not rewrite Git history.
- Do not genericize technical identifiers whose concrete value is required for implementation or testing.
- Do not make documentation vague merely to avoid a name.

## Acceptance criteria

- Durable docs do not casually enumerate the maintainer's concrete machines/accounts.
- Every remaining concrete machine/account identity in durable documentation has a technical reason to remain.

## Validation

- Search durable documentation and `.agents/` for known concrete identities.
- Review each retained occurrence for necessity.
- Run link/path checks where edited documentation contains navigation.
