# MSHP-OPS-C-010 — Harden lineage recovery authority

## Description

Fix the recovery-policy flaw that allowed an unrelated agent session to adopt an existing lineage merely because its branch existed.

## Requirements

- Define explicit authority for lineage adoption: branch/task discoverability alone is never sufficient.
- Require an explicit human recovery request identifying the lineage/branch, or an unambiguous current-conversation referent to already-established lineage ownership.
- Permit an unrelated agent to inspect an existing lineage and ask whether recovery is desired, but not mutate/adopt it autonomously.
- Require authorized recovery to stop when the lineage contains unexpected unrelated work relative to the expected checkpoint.
- Update root/agent recovery instructions consistently and preserve direct-main coordination exceptions.

## Constraints / non-goals

- Do not invent cryptographic/session identity that the platform does not provide.
- Do not treat an active claim as a recovery credential.
- Do not mutate the already-contaminated Lyra lineage merely to demonstrate the rule.

## Acceptance criteria

- Recovery authority is explicit and consistent across agent docs.
- The known hijack scenario is clearly prohibited.
- Authorized recovery remains possible after a real chat/session interruption.

## Validation

- Reread all lineage/recovery instructions for contradictions.
- Use the observed Lyra divergence as a policy test case without rewriting it.
