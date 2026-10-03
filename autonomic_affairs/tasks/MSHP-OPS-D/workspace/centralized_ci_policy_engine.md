# MSHP-OPS-D — Centralized CI policy-engine investigation

## Executive conclusion

Replace the current "blocking-validation selector plus independent CodeQL workflow" model with one conservative top-level policy workflow whose first job is a small deterministic controller.

The controller should run on relevant repository events, validate control metadata, derive an event-specific change set, classify the change conservatively, apply any explicit validated override, and emit the exact downstream work units to run.

The controller is not expected to be runnerless. Use one `ubuntu-slim` job for policy computation; the optimization target is avoiding unnecessary Linux/Windows/fresh-clone/CodeQL runner provisioning after that small job.

Changed paths become **evidence**, not authority. Any uncertainty, incomplete diff, unsupported event shape, force-push ambiguity, classifier bug, or unknown path falls back to the safe superset of downstream work.

## Current repository baseline

Current blocking validation is a dispatcher workflow plus four reusable validation sets:

- `linux`
- `windows`
- `fresh-linux`
- `fresh-windows`

The current selector:

- defaults main pushes to all four blocking sets;
- reads a single `CI:` line from the pushed tip commit;
- accepts `all`, `none`, or an explicit blocking-set subset;
- fails malformed selectors visibly while selecting all blocking sets;
- defaults PRs to all blocking sets;
- allows manual exact selection;
- deliberately ignores changed paths.

CodeQL is currently independent:

- push to `main`;
- PR targeting `main`;
- weekly schedule;
- manual dispatch;
- two Ubuntu matrix jobs: `actions` and `python`;
- `build-mode: none`;
- default high-precision query suite;
- deferred rather than advancement-blocking.

Repository experiments from OPS-A/OPS-B already proved:

- non-main pushes can remain quiet;
- `CI: none` still provisions only the small selector job;
- exact blocking subsets work;
- malformed blocking selectors fail safe to all blocking sets;
- manual selected-ref dispatch works;
- CodeQL advanced setup can run independently and with reduced permissions;
- correctly formatted native `skip-checks: true` suppresses both checked-in push workflows.

## Authoritative external findings

### Event and diff semantics

GitHub Actions documents the path-filter comparison model as:

- existing-branch push: two-dot comparison of before/head;
- pull request: three-dot comparison using the merge base;
- new branch: special two-dot ancestry handling.

The push webhook payload provides `before`, `after`, `created`, `deleted`, and `forced`. The Actions push payload does not include full added/removed/modified file arrays.

GitHub's REST compare endpoint exposes changed files, but responses are capped at 300 files for the whole comparison. The PR-files endpoint is capped at 3000 files. Built-in Actions path filtering also has limits/timeouts and can behave conservatively only within its own trigger mechanism.

References:

- https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#git-diff-comparisons
- https://docs.github.com/en/webhooks/webhook-events-and-payloads#push
- https://docs.github.com/en/rest/commits/commits#compare-two-commits
- https://docs.github.com/en/rest/pulls/pulls#list-pull-requests-files

### Runner choice

GitHub's current hosted-runner reference exposes `ubuntu-slim` as a one-CPU, 5-GB, x64 container runner intended for lightweight automation, with a 15-minute job limit.

The current slim image includes Bash, Git, Python 3.12, Node, jq, and GitHub CLI, which is sufficient for checkout, Git-range inspection, and the existing Python policy style.

References:

- https://docs.github.com/en/actions/reference/runners/github-hosted-runners
- https://github.com/actions/runner-images/blob/main/images/ubuntu-slim/ubuntu-slim-Readme.md

### Reusable workflows and permissions

Reusable workflows remain suitable downstream units. A caller can set permissions on a reusable-workflow call job; token permissions may be maintained or reduced through nesting, not elevated by the callee.

This permits CodeQL call jobs to receive `security-events: write` without granting that permission to the small controller job.

Reference:

- https://docs.github.com/en/actions/reference/workflows-and-actions/reusing-workflow-configurations

### Ruleset metadata restrictions

GitHub rulesets can enforce commit-message metadata patterns using RE2 regexes. However, current GitHub documentation describes commit-metadata restrictions as an additional capability for organizations on GitHub Enterprise.

This repository is a personal public repository, and its current repository ruleset list is empty. Therefore the CI architecture must **not depend on metadata rulesets** for correctness.

If the repository later moves into an eligible organization/plan, a ruleset can become a useful pre-ref-update grammar guard, but the controller should still validate its own control metadata.

References:

- https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/creating-rulesets-for-a-repository
- https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets

### CodeQL periodic value

CodeQL/default-setup documentation explicitly retains weekly rescanning because query/model evolution can reveal findings without repository source changes. Advanced setup gives ordinary Actions control over the schedule.

The existing weekly CodeQL behavior therefore still has value and should survive consolidation.

References:

- https://docs.github.com/en/code-security/concepts/code-scanning/setup-types
- https://docs.github.com/en/code-security/how-tos/find-and-fix-code-vulnerabilities/configure-code-scanning/configuring-advanced-setup-for-code-scanning

## Target architecture

### One top-level policy workflow

Use one top-level workflow as the event/control plane.

Recommended triggers:

- `push` to `main`;
- `pull_request` targeting `main`;
- `workflow_dispatch`;
- weekly `schedule`.

Do not add ordinary non-main push triggers.

The first job is `policy`, running on `ubuntu-slim`.

Its responsibilities:

1. check out enough Git history to determine the event range;
2. validate event/control metadata;
3. determine the exact change range;
4. enumerate changed paths with local Git;
5. classify conservatively;
6. parse and validate any explicit `CI:` override;
7. emit booleans/selections for all downstream units;
8. explain the decision in logs and outputs;
9. return nonzero for malformed control metadata while still emitting a safe downstream superset.

Local Git is preferred over depending solely on the compare/PR-files REST endpoints because it avoids their changed-file count caps. API/event fields remain authoritative for selecting the intended SHAs.

Use full-enough checkout/fetch. If the needed commits/merge base cannot be obtained, select the safe superset.

### Downstream work units

Treat these as independently selectable policy units:

Blocking:

- `linux`
- `windows`
- `fresh-linux`
- `fresh-windows`

Deferred security:

- `codeql-python`
- `codeql-actions`

`all` is the union of all six units.

CodeQL remains deferred in lifecycle semantics even though its launch decision comes from the same controller.

A practical implementation can replace the current CodeQL matrix workflow with a reusable per-language CodeQL workflow, then have the top-level controller call it once for Python and once for Actions. The existing stable category convention should remain unchanged.

### Event-range model

#### Push to existing `main`

Use event `before` and `after`.

Changed files:

```text
git diff --name-status <before> <after>
```

The pushed range is the whole integration event, not merely the tip commit.

If `forced == true`, if `before` is all-zero/missing, if either object cannot be fetched, or if Git reports an unexpected relationship, classify as uncertain and run the safe superset.

The explicit override source remains the **tip commit** for compatibility and clear human intent, but metadata validation may inspect every newly introduced commit.

#### Pull request

Use the PR base SHA and head SHA and derive the merge base.

Changed files should represent what the PR introduces:

```text
git diff --name-status <base>...<head>
```

This mirrors GitHub's documented three-dot PR model.

If the merge base cannot be established, fall back to the safe superset.

An explicit `CI:` override may be read from the PR head commit if the project chooses to permit PR overrides. The implementation should apply the same parser and fail-safe rules as main push.

#### Manual dispatch

There is no unambiguous automatic diff range.

Manual runs should therefore be **explicit-selection only**. Default to `all`; do not silently invent an `auto` range.

The selected ref continues to come from GitHub's manual workflow ref selector.

#### Schedule

The schedule is not a source-change event.

Select exactly:

- `codeql-python`
- `codeql-actions`

Do not launch blocking validation merely because the weekly security rescan occurred.

### Explicit override semantics

Keep the existing `CI:` spelling but deliberately supersede its old blocking-only meaning.

Proposed grammar:

```text
CI: auto
CI: all
CI: none
CI: linux,windows
CI: codeql-python,codeql-actions
CI: linux,codeql-python
```

Rules:

- no `CI:` line on automatic push/PR events means `auto`;
- `auto` explicitly requests classifier output;
- `all` selects all six downstream units;
- `none` selects no downstream unit, but the controller still runs;
- an explicit list selects exactly the named registered units;
- whitespace and duplicate handling may remain normalized;
- `all`, `none`, and `auto` must be standalone;
- multiple `CI:` lines are invalid;
- unknown/malformed values are invalid;
- invalid control metadata logs a clear error, returns controller failure, and emits **all six units** so a typo cannot suppress validation/security analysis.

Native `skip-checks: true` remains the harder bypass when even the controller should not instantiate. Its GitHub-native push/PR behavior remains separate from `CI: none`.

This is an intentional semantic change from OPS-A/OPS-B: `CI:` becomes the single policy override surface for both blocking and deferred units.

### Commit/control metadata validation

The policy job should own validation that is necessary for CI correctness:

- exact `CI:` grammar;
- duplicate/multiple selector rejection;
- registered-unit validation;
- commit-summary grammar required by repository policy;
- any future machine-readable control trailers.

For main pushes, validate the newly introduced commit range rather than only the tip when practical. For PRs, validate commits introduced by the PR.

Do not require GitHub rulesets for this behavior.

A later eligible metadata ruleset could reject malformed commit summaries before ref update, but that would be defense-in-depth and would not replace the policy parser.

## Conservative automatic classifier

The classifier should be a deterministic union of matched risk classes.

A path may contribute multiple classes. Unknown/unclassified paths select the safe superset.

### Class: inert documentation/control text

Examples:

- Markdown documentation;
- task specifications/workspaces;
- agent-memory documentation;
- inert text-only project docs.

Automatic result:

- no downstream blocking validation;
- no CodeQL language analysis.

The control job itself still validates policy metadata.

This class must be narrowly allowlisted. Merely living under a documentation-ish directory must not automatically make an arbitrary executable file inert.

### Class: Python/runtime implementation

Evidence includes Python source or other known runtime/application implementation surfaces that can affect cross-platform behavior.

Automatic result:

- `linux`
- `windows`
- `codeql-python`

Do **not** automatically add fresh-clone validation unless install/bootstrap/environment realization is implicated.

### Class: install/bootstrap/fresh-clone semantics

Evidence includes installer/bootstrap scripts, dependency/bootstrap manifests, application installation machinery, fresh-clone validation machinery, or other files whose correctness specifically depends on clean-machine realization.

Automatic result:

- `linux`
- `windows`
- `fresh-linux`
- `fresh-windows`
- plus language-appropriate CodeQL units (normally `codeql-python` for Python machinery).

### Class: Actions/control workflow semantics

Evidence includes executable GitHub Actions workflow changes or reusable workflow/action implementation.

Automatic result:

- `codeql-actions`;
- all four blocking validation sets when the changed workflow participates in validation/orchestration and therefore could change what those validations actually execute;
- otherwise the narrowest justified blocking subset for a clearly isolated workflow.

Changes to the central policy workflow/selector itself must conservatively run all four blocking sets plus both CodeQL units because a routing defect can suppress other evidence.

### Class: platform-specific known surface

A future classifier may map a path to only Linux or Windows when repository architecture makes that platform exclusivity explicit and testable.

Do not infer platform exclusivity from filename vibes or incidental current implementation.

### Class: unknown / ambiguous

Automatic result:

- all six downstream units.

This is the classifier's most important invariant.

## Decision model

For automatic push/PR events:

1. validate metadata;
2. build event change range;
3. classify each changed path;
4. union all required units;
5. if classification/evidence is incomplete, replace union with `all`;
6. parse tip/head `CI:`;
7. if no override or `auto`, use automatic union;
8. if valid explicit override, use it exactly;
9. if invalid override, mark controller failed and select `all`;
10. launch downstream jobs from controller outputs.

Explicit override is authoritative because it records human/agent intent, but malformed override is never allowed to reduce work.

## CodeQL lifecycle after consolidation

The launch decision becomes centralized; lifecycle semantics do not.

- CodeQL units remain deferred security analysis.
- Blocking units remain advancement gates.
- `AWAITING_DEFERRED_CI` remains valid when implementation can advance while selected CodeQL work is pending.
- Completion still requires relevant selected CodeQL success for a task's final substantive tree.
- Weekly schedule still runs both CodeQL units regardless of source-change classification.
- Stable default query suite, `build-mode: none`, current language categories, and least-privilege upload permissions remain unchanged unless separately justified.

## Policy supersessions required

Implementation must explicitly update the authoritative docs instead of leaving contradictions.

Supersede these OPS-A-era rules:

- "Selection is explicit. Changed paths are not an authority and must not route CI."
  - Replace with: changed paths are conservative evidence for automatic policy; explicit overrides remain authoritative; uncertainty falls back to all.
- "Pushes to main default to all blocking sets."
  - Replace with automatic conservative classification.
- "`CI:` controls only blocking validation."
  - Replace with the unified six-unit policy override.
- "PRs default to all blocking sets."
  - Replace with conservative PR three-dot classification.
- "Do not infer CI selection from changed paths."
  - Replace with the evidence-vs-authority distinction and fail-safe classifier rules.

Supersede these OPS-B-era rules:

- "CodeQL normal routing is deliberately separate from the Machine-Soul blocking dispatcher."
  - Replace with centralized launch policy while retaining deferred lifecycle semantics.
- "`CI:` does not select/subset/suppress CodeQL."
  - Replace with unified unit selection.
- separate CodeQL top-level push/PR/manual routing.
  - Replace with CodeQL as reusable downstream work plus top-level schedule policy.

Preserve from OPS-B:

- deferred lifecycle;
- weekly rescan;
- default query suite;
- Python + Actions;
- `build-mode: none`;
- stable result categories;
- least-privilege permissions;
- ordinary non-main pushes quiet.

## Runner recommendation

Use `ubuntu-slim` for the policy job.

Reasons:

- purpose-built for lightweight automation;
- 1 CPU / 5 GB is ample for Git diff + small Python policy logic;
- Python and Git are present in the current image;
- avoids provisioning a full Ubuntu VM merely to decide whether other runners deserve to exist;
- public repository standard-runner use remains appropriate.

Constraints:

- 15-minute hard job limit;
- unprivileged container;
- smaller installed tool surface.

None conflicts with the intended controller workload.

If policy computation grows until those limits matter, that is evidence the controller has become too complicated and should be reassessed rather than preemptively using a heavier runner.

## Ruleset recommendation

Do not create a ruleset task now.

Reason:

- this repository has no rulesets configured;
- hard commit-metadata rules are currently documented as an Enterprise-organization capability;
- the repository is personal/public;
- the controller can and should validate the grammar it consumes.

If repository ownership/plan changes later, reevaluate a main-targeting metadata ruleset as a pre-ref-update guard.

## Recommended implementation shape

One implementation/validation task is justified.

It should:

1. evolve `ci_validation_selector.py` into a policy engine rather than create competing logic;
2. add deterministic tests for event ranges, classifier unions, overrides, malformed metadata, and fail-safe behavior;
3. convert the top-level validation workflow into the unified policy workflow on `ubuntu-slim`;
4. preserve the four reusable blocking workflows;
5. refactor CodeQL into reusable downstream language analysis callable from the policy workflow;
6. keep scheduled CodeQL through the top-level policy event;
7. update `.agents/WORKFLOW.md`, root `AGENTS.md` if needed, and `autonomic_affairs/docs/AGENT_LINEAGES_AND_CI.md`;
8. validate real GitHub behavior for representative docs-only, Python, workflow/control, explicit subset, invalid override, `none`, manual, and CodeQL schedule/manual semantics where practical;
9. cut over without duplicate workflows or double scans.

A separate research or ruleset task is not justified by current evidence.
