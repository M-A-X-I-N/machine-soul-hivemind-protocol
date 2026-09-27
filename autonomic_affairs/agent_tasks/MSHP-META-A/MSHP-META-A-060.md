# MSHP-META-A-060 — Codify optional idiot-maintainer language

## Description

Permit internal/developer-facing material to humorously call the repository developer/maintainer `the idiot`, `the idiot human`, or equivalent, while protecting end users and formal interfaces from that convention.

## Requirements

- Make the convention optional seasoning rather than mandatory vocabulary.
- Limit it to the developer/maintainer context, including the human directing this repository.
- Explicitly exclude end users, callers, customers, community members, and unrelated people.
- Keep user-facing errors, public API/protocol terminology, safety instructions, and formal interfaces neutral unless separately justified.
- Put the rule somewhere agents will discover without bloating unrelated human-facing docs.

## Constraints / non-goals

- Technical clarity always wins over the joke.
- Do not create a quota or require agents to use the wording.
- Do not use the convention as a generic label for software users.

## Acceptance criteria

- Future agents can distinguish allowed maintainer-directed humor from prohibited user-directed insults.
- The rule is discoverable from normal agent reading order.

## Validation

- Review the wording against representative internal docs, user-facing messages, and protocol/API examples.
- Verify `AGENTS.md` or linked agent guidance makes the boundary discoverable.
