# MSHP-OPS-B-010 — Investigate CodeQL advanced-analysis configuration

## Description

Investigate the repository's newly checked-in GitHub CodeQL advanced-mode workflow and the current CodeQL/Actions configuration surface before deciding how Machine-Soul should integrate security analysis with its selective-CI and deferred-validation model.

The task must end with an evidence-based recommended architecture and taskify only the implementation/validation work that the investigation actually justifies.

## Requirements

- Treat the checked-in `.github/workflows/codeql.yml` on current `main` as the exact starting point; distinguish repository-local configuration from GitHub-managed/default-setup behavior observed previously.
- Verify the current supported CodeQL advanced-setup controls from authoritative GitHub/CodeQL sources, including at least:
  - workflow triggers for push, pull request, schedule, and manual dispatch;
  - branch/ref behavior and interaction with native workflow-skip commit messages/trailers;
  - language selection and language-specific build modes;
  - query suites, query packs, query filters, custom queries, and model/threat-model controls where supported;
  - inline `init` options versus dedicated CodeQL configuration files;
  - analysis-path/include/exclude controls and how they differ from Actions trigger routing;
  - result categories and multi-analysis behavior;
  - runner/platform/resource controls;
  - permissions and security-events upload requirements;
  - schedule semantics and reasons for periodic rescanning;
  - concurrency/cancellation behavior available through ordinary Actions;
  - generated-database/source-root/build controls that materially affect this repository.
- Inspect the repository's existing selective-CI architecture and evaluate CodeQL against it rather than designing in isolation.
- Explicitly investigate whether CodeQL should:
  - remain a separate deferred analysis workflow;
  - become a registered normal validation set;
  - share only control conventions with normal validation while remaining separately scheduled/gated;
  - or use another design justified by evidence.
- Investigate whether normal main-push analysis, pull-request analysis, explicit agent-branch/manual analysis, and scheduled deeper analysis should use the same or different query profiles.
- Investigate whether a dedicated CodeQL config file improves maintainability versus keeping the full policy inline in workflow YAML.
- Investigate whether path analysis filters have any legitimate use for this repository while preserving the existing rule that changed paths do not decide whether CI launches.
- Experimentally verify material GitHub behavior where documentation alone leaves meaningful ambiguity and the experiment can be performed without destructive repository changes or wasteful runner use.
- Record durable findings in a task workspace/synthesis artifact with links/references sufficient for later implementation without repeating the whole research.
- Produce a concrete recommended target architecture with explicit rationale, defaults, deferred/blocking semantics, and non-goals.
- At task completion, create only the follow-up executable tasks actually justified by the investigation. Do not pre-decide their number or shape.

## Constraints / non-goals

- Do not redesign or modify the CodeQL workflow merely because a setting exists.
- Do not treat "more queries" as automatically better.
- Do not collapse CodeQL into blocking CI unless the evidence supports that lifecycle.
- Do not reintroduce changed-path routing for whether a workflow launches.
- Do not disable useful security analysis merely to reduce runner usage.
- Do not invent custom CodeQL queries or model packs without a concrete repository need.
- Do not modify Git history or replace the maintainer's `910dc99...` CodeQL commit.
- Preserve the current Lyra lineage; fast-forward it to current `main` before substantive branch work.

## Acceptance criteria

- The stock advanced-mode workflow is fully characterized against current repository CI policy.
- Material CodeQL advanced-setup options are mapped, including useful controls not present in the generated template.
- Relevant distinctions between workflow routing, analysis scoping, query selection, build mode, and result categorization are documented clearly.
- A concrete recommended MSHP CodeQL architecture exists and addresses automatic main/PR behavior, explicit branch analysis, schedules, query policy, concurrency, skip behavior, and deferred-CI semantics.
- Tradeoffs and intentionally unused controls are documented rather than silently omitted.
- Any material uncertain behavior relied upon by the recommendation has been verified or explicitly marked uncertain.
- Follow-up tasks reflect the resulting architecture rather than assumptions made before investigation.

## Validation

- Cross-check recommendations against the current checked-in CI policy and workflow files.
- Prefer current official GitHub/CodeQL documentation and the current `github/codeql-action` implementation/docs for behavior claims.
- Verify repository state after any experiment and avoid leaving temporary experimental workflow churn behind.
- Reread created follow-up tasks against the synthesis before completing this task.
