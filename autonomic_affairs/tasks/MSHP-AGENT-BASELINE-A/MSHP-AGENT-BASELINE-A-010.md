# MSHP-AGENT-BASELINE-A-010 — Investigate GitHub template repository mechanics

## Description

Research GitHub template repository behavior as a possible bootstrap mechanism for a reusable cross-repository agent baseline. Treat the existing `M-A-X-I-N/template` repository as a read-only research subject only.

## Requirements

- Use current official GitHub documentation as the primary authority.
- Inspect `M-A-X-I-N/template` read-only where useful; do not modify it.
- Determine what repository contents are copied when creating from a template, including branch-selection behavior and Git history semantics.
- Determine which repository settings/metadata are inherited or not inherited, including template status, Actions/workflow files, branch/ruleset settings, secrets/variables, issues/discussions, labels, protections, and other relevant repository-level configuration where documented.
- Determine public/private and owner/account constraints relevant to the maintainer's repositories.
- Determine whether repositories created from a template retain any machine-readable relationship to the source template and whether GitHub provides any native update/synchronization mechanism afterward.
- Determine relevant UI, CLI, REST/GraphQL, or other GitHub-native creation/update capabilities where they materially affect architecture.
- Preserve durable findings in the MSHP task workspace and promote expensive-to-rediscover generic GitHub behavior into appropriate MSHP agent/human-facing documentation if justified.

## Constraints / non-goals

- Research only. Do not create repositories, branches, commits, files, workflows, settings changes, or experiments outside MSHP.
- Do not write to `M-A-X-I-N/template`.
- Do not assume template repositories solve ongoing synchronization.
- Do not design the final baseline architecture yet; establish mechanism facts first.

## Acceptance criteria

- Template-repository bootstrap semantics and limitations are documented with authoritative sources.
- The distinction between initial repository generation and ongoing synchronization is explicit.
- Unknown/undocumented GitHub behavior is identified as uncertain rather than guessed.

## Validation

- Cross-check material claims against current official GitHub documentation.
- Re-read the findings specifically for accidental implementation recommendations presented as proven facts.
