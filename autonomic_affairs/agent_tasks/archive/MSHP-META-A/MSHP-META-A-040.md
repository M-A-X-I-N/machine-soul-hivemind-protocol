# MSHP-META-A-040 — Formalize agent provenance identities and commit-trailer policy

## Description

Create one canonical provenance registry and trailer grammar that distinguishes agent variants, stable designations, optional honorifics, and an accurate per-commit official identity.

## Requirements

- Register `OpenAI ChatGPT Chat` with stable designation `Gippity`.
- Leave `OpenAI ChatGPT Work` and `OpenAI Codex` as `UNNAMED` until the maintainer assigns designations.
- Require assigned stable designations to be unique by agent/product surface variant rather than model revision.
- Require every wholly agent-authored substantive commit trailer to end with a parenthesized official identity chosen accurately by the authoring agent at commit time.
- Official identity should identify organization/product/surface and include the model when meaningfully known; unknown details must never be fabricated.
- Allow optional, encouraged honorific material before and/or after the stable designation.
- Honorifics may be serious, funny, grandiose, mundane, or otherwise arbitrary; slur-containing honorifics require explicit human permission.
- An unnamed agent must use `Agent-authored-by: UNNAMED (<official identity>)`, may not invent a stable designation, and may not use honorifics.
- An unnamed agent promptly notifies the maintainer and asks for a designation when it can do so without losing/restarting active work.
- Newly assigned designations apply prospectively; do not rewrite prior commits merely to retrofit them without separate authorization.
- Keep the full policy in one durable canonical location; keep `AGENTS.md` concise and point to it.

## Constraints / non-goals

- Do not fix the official identity to one model revision in the registry.
- Do not assign names to Work or Codex on their behalf.
- Do not rewrite existing commit history as part of this task.

## Acceptance criteria

- Known and unknown agent variants can derive an unambiguous trailer.
- ChatGPT Chat uses stable designation `Gippity`.
- Unnamed agents are visibly `UNNAMED` and cannot hide behind honorifics.
- Current provenance references point to the canonical policy.

## Validation

- Review `AGENTS.md`, `.agents/`, and provenance documentation for conflicting rules.
- Verify examples conform to the grammar.
- Verify the policy explicitly handles unknown model/runtime details and unnamed agents.
