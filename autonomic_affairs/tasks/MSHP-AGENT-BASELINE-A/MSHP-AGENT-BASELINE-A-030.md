# MSHP-AGENT-BASELINE-A-030 — Investigate cross-repository distribution and reuse mechanisms

## Description

Research the available mechanisms for sharing generic repository/agent infrastructure across many repositories, treating GitHub templates as one candidate rather than the assumed complete solution.

## Requirements

- Investigate GitHub template repositories, reusable workflows, composite actions, reusable workflow repositories, shared scripts/packages, and other GitHub-native mechanisms that could materially serve this use case.
- Investigate whether repository rulesets, organization/user-level settings, repository custom properties, Actions variables, or other GitHub features can carry reusable policy/configuration without copying files, where applicable to personal repositories.
- For each mechanism, document what kind of artifact it can share, whether consumers remain linked, update/rollback behavior, versioning support, access/visibility constraints, security/trust implications, and repository-local customization options.
- Distinguish mechanisms suitable for bootstrap files from mechanisms suitable for live shared execution/runtime behavior.
- Identify combinations of mechanisms that plausibly compose well rather than forcing one mechanism to own everything.
- Use current official documentation as primary authority for GitHub behavior.
- Preserve durable findings in MSHP.

## Constraints / non-goals

- Research only. Do not create reusable workflows/actions/packages or modify any external repository.
- Do not assume `M-A-X-I-N/template` must ultimately host all reusable machinery.
- Do not assume a second infrastructure repository is necessary either.
- Do not select a final architecture in this task.

## Acceptance criteria

- A mechanism comparison exists with explicit strengths, limitations, update semantics, and security/access constraints.
- Bootstrap-oriented and live-reuse-oriented mechanisms are clearly distinguished.
- The research identifies which mechanisms merit deeper consideration for the concrete components inventoried in A-020.

## Validation

- Cross-check current GitHub claims against authoritative documentation.
- Verify mechanism recommendations are framed as research findings/candidates rather than implementation decisions.
