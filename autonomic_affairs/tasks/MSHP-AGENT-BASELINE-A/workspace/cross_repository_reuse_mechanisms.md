# MSHP-AGENT-BASELINE-A-030 — Cross-repository distribution and reuse mechanisms

Research date: 2026-10-04.

## Executive conclusion

No single GitHub mechanism naturally owns the whole agent baseline.

The mechanisms split by artifact type:

- **repository template** — bootstrap/copy file-based structure into a new repository;
- **reusable workflow** — centrally execute shared job/workflow logic while the caller remains local;
- **composite action** — centrally execute shared step-level logic;
- **personal/organization `.github` default community files** — live account-level fallback for a narrow GitHub-defined set of community-health files;
- **organization workflow templates** — assisted copying of workflow starter files, organization-only;
- **organization rulesets/custom properties** — live organization governance/metadata, organization-only and plan-constrained;
- **repository/API automation** — can configure repository-side settings but is orchestration, not inheritance/reuse by itself.

For the current personal-account repository fleet, the strongest serious candidates are template bootstrap + reusable workflows/actions + an explicit update/migration mechanism researched in A-040.

## Mechanism comparison

| Mechanism | Shares | Live link after adoption? | Version/pin model | Local customization | Current personal-account fit |
|---|---|---|---|---|---|
| GitHub repository template | Files/directories; default branch or all branch snapshots | **No update link**; generated repo is independent single-commit history | Template snapshot at generation time | Full local freedom after copy | **Strong for bootstrap** |
| Reusable workflow | Complete Actions jobs/workflows callable through `workflow_call` | **Yes**, caller resolves referenced repository/ref at run time | Full SHA, tag, or branch; SHA safest | Inputs/secrets/caller wrappers; caller retains event routing | **Strong for live shared CI/control** |
| Composite action | Reusable sequence of workflow steps | **Yes**, `uses: OWNER/REPO[/path]@ref` | SHA/tag/branch; full SHA safest | Inputs/outputs plus surrounding caller steps | **Strong for shared deterministic step logic** |
| Workflow template | Starter workflow YAML offered in GitHub UI | No; configured workflow is copied into consumer | Snapshot at configuration time | User edits generated/copied workflow | **Organization-only; not current personal solution** |
| Default community-health `.github` repo | Supported GitHub community files such as CONTRIBUTING/CODE_OF_CONDUCT/SECURITY/support/issue templates | Yes as fallback; repo-local supported file overrides it | Central file HEAD | Explicit repo-local file overrides default | **Available to personal account but too narrow for agent baseline** |
| Organization ruleset | Branch/tag/push governance across targeted repos | Yes, centrally enforced | Organization setting state | Repo rules can add stricter rules; organization rule remains authority | **Not personal-account cross-repo mechanism** |
| Organization custom properties | Structured metadata across org repositories | Yes | Organization schema/values | Repo values within org policy | **Not personal-account mechanism** |
| Repository-side settings via REST/GraphQL/CLI | Arbitrary supported repository settings/resources | Only if an external reconciler keeps applying desired state | Script/tool version + API behavior | Can diff/merge intentionally | **Potential future updater/orchestrator, not passive reuse** |
| Shared script/package/library | Arbitrary executable logic | Yes when fetched/installed/referenced | Package/ref/release-specific | API/config inputs | **Possible, but adds runtime/package-distribution complexity** |

## GitHub reusable workflows

A reusable workflow:

- lives in `.github/workflows/`;
- declares `on: workflow_call`;
- is called at job level with `jobs.<job>.uses`;
- may live in the same repository or another repository;
- cross-repository syntax is `{owner}/{repo}/.github/workflows/{file}@{ref}`;
- `{ref}` may be a commit SHA, tag, or branch;
- GitHub explicitly describes a commit SHA as the safest reference for stability/security.

Reusable workflows can accept typed inputs and declared secrets. `secrets: inherit` is supported in relevant ownership contexts.

Important authority/security behavior:

- the `github` context is associated with the caller repository/workflow;
- nested reusable workflows cannot elevate `GITHUB_TOKEN` permissions above the caller chain;
- private shared workflows require explicit Actions access from the source repository;
- a private repository owned by a personal account can expose actions/workflows to other **private** repositories owned by the same user;
- sharing a private workflow gives runners time-limited read access to the source repository and can indirectly expose source through logs to collaborators, so this is a real trust boundary.

Official references:

- https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows
- https://docs.github.com/en/actions/reference/workflows-and-actions/reusing-workflow-configurations
- https://docs.github.com/en/actions/how-tos/reuse-automations/share-across-private-repositories
- https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository

### Fit for this baseline

Strong for logic such as:

- generic repository policy validation;
- reusable CI orchestration mechanics that can accept local declarations;
- provenance/control-metadata checking;
- generic audit jobs;
- CodeQL/shared security-analysis wrappers;
- update-check jobs, if later architecture chooses Actions for update discovery.

Poor fit for:

- `AGENTS.md` itself;
- task/reminder/initiative state;
- durable local `.agents` memory;
- repository-specific path/check declarations unless passed explicitly from the consumer.

## Composite actions

Composite actions package a series of workflow **steps** into one action. They can be stored in a separate repository and consumed with a repository/ref reference, including a full commit SHA.

They are narrower than reusable workflows:

- composite action = step-level building block inside a job;
- reusable workflow = workflow/job-level orchestration.

This makes composite actions plausible for shared deterministic helpers such as:

- parse/validate baseline manifests;
- run a generic policy script;
- normalize metadata;
- collect standard diagnostic output.

They are not a natural home for multi-job runner selection, matrices, workflow event routing, or the whole centralized selector graph.

Official reference:

- https://docs.github.com/en/actions/tutorials/create-actions/create-a-composite-action

## Workflow templates

GitHub workflow templates are created in an **organization** `.github` repository under `workflow-templates/`. They are presented in the Actions workflow creation UI and copy/configure starter YAML into a repository.

They support `$default-branch` substitution and metadata such as categories/file patterns.

Key limitation for current architecture:

- this is an organization feature, while the maintainer's repositories currently live under a personal account;
- once configured, the resulting workflow is repository-local copied content rather than a live central implementation;
- GitHub's own guidance notes that workflow templates can themselves call reusable workflows, which is a useful bootstrap/live-reuse composition if an organization becomes relevant later.

Official references:

- https://docs.github.com/en/actions/how-tos/reuse-automations/create-workflow-templates
- https://docs.github.com/en/actions/how-tos/write-workflows/use-workflow-templates

## Personal-account `.github` default community-health repository

GitHub supports a public repository literally named `.github` under either a personal account or organization for **supported default community-health files**.

Useful properties:

- defaults apply to account-owned repositories that lack their own supported file;
- repo-local supported files override the account default;
- central defaults do not appear in consumer file browsers, Git history, clones, packages, or downloads;
- changes are made once in the `.github` repo and become the account default.

This is a genuine live central inheritance mechanism, but only for GitHub's supported community files. It is **not** a generic file-overlay feature.

Therefore it may eventually centralize things like CONTRIBUTING/SECURITY/issue templates, but cannot carry arbitrary `AGENTS.md`, `.agents/`, task machinery, or generic scripts.

Official reference:

- https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file

## Rulesets

Repository-level rulesets can enforce branch/tag/push policy per repository.

Cross-repository central rulesets are an **organization-level** capability. Organization rulesets can target all, selected, named-pattern, or custom-property-selected repositories depending on plan/features.

Current implication:

- useful architecture if repositories later live in an organization;
- not a personal-account-wide governance mechanism for the current fleet;
- per-repository rulesets could be configured by an updater/orchestrator but are then synchronized settings, not central inheritance.

Official references:

- https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets
- https://docs.github.com/en/organizations/managing-organization-settings/creating-rulesets-for-repositories-in-your-organization

## Organization custom properties

Custom properties are structured repository metadata whose schema is owned at organization level. They can drive search/governance and target organization rulesets.

They are potentially attractive for concepts such as `agent_baseline_version`, baseline profile, or ownership classification **if** repositories move to an organization.

They are not currently a personal-account baseline mechanism and should not be assumed in a design targeting the existing `M-A-X-I-N/*` personal repositories.

Official reference:

- https://docs.github.com/en/organizations/managing-organization-settings/managing-custom-properties-for-repositories-in-your-organization

## Repository configuration through API/CLI

GitHub exposes repository-side state through APIs: Actions settings, secrets/variables, rulesets, branch protection, repository settings, and many other resources.

Therefore a future updater could reconcile repository-side state from a desired baseline.

But this is not a built-in shared-baseline feature. It requires an actor to:

1. know desired state/version;
2. authenticate to each repository;
3. inspect current state;
4. distinguish baseline-owned state from local policy;
5. propose/apply changes;
6. handle conflicts and rollback.

That belongs to A-040's synchronization investigation rather than being treated as solved here.

## Shared scripts/packages/libraries

A central repository/package can share arbitrary deterministic implementation outside Actions YAML. This could reduce duplication for a policy engine that is difficult to express purely as reusable-workflow inputs.

Tradeoffs:

- introduces download/install/runtime dependency;
- requires its own versioning/release/distribution model;
- may be easier to test than repeated generated files;
- may work both locally and in CI, unlike reusable workflows;
- can become over-engineering if the shared logic is only a few small files.

No package mechanism is selected by this task.

## Security / trust implications

Live shared executable components are supply-chain dependencies.

GitHub's current Actions secure-use guidance says pinning actions to a **full-length commit SHA** is the only way to consume an immutable action release. The same trust principles apply to reusable workflows.

Mutable branch/tag references make central rollout easier but mean a consumer can execute new shared code without a repository-local commit/review. This is an architectural tradeoff to resolve in A-060, not a reason to choose one today.

Reference:

- https://docs.github.com/en/actions/reference/security/secure-use

## Fit against the A-020 inventory

### Bootstrap-copy candidates

Likely template/file-bootstrap territory:

- root `AGENTS.md` skeleton;
- `.agents/README.md`, WORKFLOW, provenance skeleton/registry seed;
- task/reminder/initiative directory/schema skeletons;
- task archive README;
- repository-local baseline manifest/config if later selected;
- thin caller workflows that point at shared live logic;
- generic documentation/source-of-truth skeletons.

### Live shared-execution candidates

Likely reusable-workflow/composite/script territory:

- generic metadata/provenance validators;
- generic CI event/range policy mechanics;
- baseline-version/update checks;
- generic repository audits;
- optional standard security-analysis wrappers.

### Always local

- task/reminder/initiative contents;
- `.agents` project knowledge;
- human-facing project architecture;
- local CI checks/path relevance;
- local product safety laws;
- local directory/domain taxonomy.

## A-030 conclusion

The evidence supports a **hybrid distribution model** as the serious candidate space:

- template/copied skeleton for files that must exist locally and be readable/editable as repository truth;
- reusable workflows/actions or another shared executable surface for deterministic logic that benefits from central maintenance;
- explicit synchronization/migration machinery for copied baseline files and repository-side settings.

This is not yet the final architecture. A-040 must determine whether ongoing synchronization can be made safe enough without turning local policy into generated-file hell.
