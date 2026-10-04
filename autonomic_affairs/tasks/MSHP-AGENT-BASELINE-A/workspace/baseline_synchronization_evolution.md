# MSHP-AGENT-BASELINE-A-040 — Ongoing synchronization and baseline evolution

Research date: 2026-10-04.

## Executive conclusion

The safest serious synchronization family is **versioned provenance + reproducible baseline rendering + reviewable reconciliation**, preferably delivered as a normal pull request rather than silent overwrite.

GitHub's repository-template feature does not provide this lifecycle. Existing tools such as Copier and Cruft demonstrate that the missing state is normally:

- which template/baseline source was used;
- which baseline version/commit was last applied;
- which parameter/answer values produced the consumer-specific result;
- enough information to reconstruct the old generated state and compare it with both the evolved consumer and new baseline.

This enables a three-way-style update:

1. reconstruct old baseline output;
2. compare old baseline output to current repository to understand local evolution;
3. render new baseline output;
4. replay/reconcile local evolution onto the new baseline;
5. surface conflicts for human review;
6. record the newly applied baseline version.

This is much safer than overwriting 'baseline-owned files', because even apparently generic files such as `AGENTS.md` will acquire legitimate repository-local edits.

## Existing tool precedent: Copier

Current Copier is specifically designed for lifecycle management of generated projects.

Important documented behavior:

- consumer records template answers in `.copier-answers.yml`;
- Git-versioned/tagged templates support `copier update`;
- update can target latest version or an explicit Git ref;
- it preserves the prior answers that generated the project;
- its update algorithm reconstructs/regenerates the prior template state, computes the project's local diff/evolution, renders the newer template, and reapplies local evolution;
- unresolved hunks become inline conflict markers or `.rej` files for manual review;
- template authors can define versioned migrations;
- `copier check-update` can report whether a newer template version exists, including automation-friendly JSON/exit-code modes;
- deleted template-generated paths have explicit update semantics;
- `recopy` exists as a less-smart recovery path when normal update reconstruction cannot work.

This is very close to the desired semantics for copied agent baseline files.

Official/current docs:

- https://copier.readthedocs.io/en/stable/updating/
- https://copier.readthedocs.io/en/stable/configuring/

### Copier implications for this project

Strong ideas worth potentially borrowing even if Copier itself is not adopted:

- generated-project manifest/answers file;
- baseline Git version/tag tracking;
- three-way/replay update rather than replacement;
- explicit conflicts left for normal Git review;
- ordered version migrations;
- update-availability check separate from update application;
- clean/recoverable Git state as a precondition.

Potential concerns:

- baseline is not a normal software-project template: many files are policy documents that humans/agents may edit heavily;
- template engines add Jinja/rendering complexity even when many files need little parameterization;
- Copier's version conventions and executable migrations create a trusted-code boundary;
- adoption of already-existing repos needs a carefully established base version/answers rather than pretending they were originally rendered by the template.

## Existing tool precedent: Cruft

Cruft adds lifecycle management to Cookiecutter templates.

Documented behavior includes:

- `.cruft.json` stores template source, template Git commit, and template variables/context;
- `cruft check` detects whether template updates exist and is suitable for CI;
- `cruft diff` shows drift;
- `cruft update` applies template changes with review;
- skip patterns allow files that are poor update candidates to be excluded;
- `cruft link TEMPLATE_REPOSITORY` can associate an existing project with a template and an assumed last-consistent template commit.

References:

- https://cruft.github.io/cruft/
- https://github.com/cruft/cruft

### Cruft implications

The explicit **link existing project** operation is especially relevant to the maintainer's existing repositories, which were not created from a future baseline.

However, 'linking' is only safe if the declared old template version genuinely represents the consumer's baseline state. A future adoption tool must validate/diff before recording that assertion.

## Git submodules

A Git submodule records a precise commit of another repository and can fetch/track upstream changes.

Strengths:

- exact immutable version pointer;
- native Git provenance/history;
- no generated-copy ambiguity;
- updating the gitlink is a small reviewable consumer commit.

Weaknesses for this use case:

- shared content lives in a subdirectory as a nested repository;
- root-level files such as `AGENTS.md`, `.github/workflows/*`, and local task skeletons cannot naturally be 'provided' from a submodule without wrappers/symlinks/copy steps;
- local modification of shared files occurs inside the submodule repository rather than naturally as consumer-local overrides;
- cloning/checking out requires submodule awareness;
- consumers still need local bridge files to expose shared policy in GitHub-required/root locations.

Conclusion: useful for a library, poor as the primary agent-baseline distribution model.

Reference:

- https://git-scm.com/docs/git-submodule

## Git subtree / vendored subtree

`git subtree` can copy another repository into a consumer subdirectory and later pull/merge upstream changes while keeping ordinary files in the main repository.

Strengths:

- no special clone step for consumers;
- upstream history/update flow exists;
- local modifications are ordinary repository changes;
- can merge upstream changes.

Weaknesses:

- fundamentally subdirectory-oriented;
- the most important baseline files need root/GitHub-defined paths;
- pulling baseline changes into a heavily customized policy subtree can produce Git merge complexity without understanding semantic ownership;
- splitting/pushing local changes back upstream risks accidentally treating repo-specific policy as generic.

Conclusion: stronger than submodules for vendored libraries, but not naturally matched to scattered root `.github`, `AGENTS.md`, `.agents`, and autonomic paths.

Reference:

- https://github.com/git/git/blob/master/contrib/subtree/git-subtree.adoc

## Plain upstream Git merge / remote tracking

A generated repository from a GitHub template has unrelated single-commit history, so it is not naturally an upstream branch.

One could manually add the template as a remote and merge with `--allow-unrelated-histories`, or construct shared ancestry later, but this treats the entire repository as baseline-owned and causes project implementation/history to share the same merge topology as infrastructure updates.

That is a bad ownership match and should not be the default synchronization model.

## Ordered patch/migration system

A custom baseline updater could model updates as ordered migrations:

- consumer declares baseline version N;
- baseline release N+1 contains migrations;
- updater applies migrations N→N+1→...→target;
- each migration knows exactly which schema/policy change it owns;
- local data lives in separate extension/config surfaces where possible;
- migration produces a normal diff/PR.

Strengths:

- explicit intent and compatibility behavior;
- easy to make destructive operations opt-in;
- migrations can alter repository-side settings as well as files if authorized;
- excellent for structural changes that naive text merges cannot understand.

Weaknesses:

- bespoke migration code must be maintained forever or across supported upgrade ranges;
- requires baseline version/schema discipline;
- arbitrary human edits to baseline-controlled files still need merge/conflict strategy;
- skipping versions and adopting legacy repos need careful bootstrap logic.

Conclusion: likely valuable **in addition to** three-way file reconciliation for schema transitions, not as the only update mechanism.

## Manifest-driven generated/reconciled files

A minimal consumer manifest could record concepts such as:

- baseline source identity;
- applied baseline version/commit;
- profile/features enabled;
- answers/parameters;
- files/components managed by the baseline;
- files/components intentionally detached/local;
- schema version for the manifest itself.

This solves discovery and diagnostics but not merging by itself.

The manifest should record facts, not falsely claim ownership over every byte of a file. `AGENTS.md` may simultaneously contain baseline-derived and repository-specific content unless A-050 finds a cleaner layering boundary.

## Pull-request-based update delivery

Regardless of update engine, a strong safety model is:

1. updater computes candidate change;
2. updater works on a branch;
3. updater creates a pull request with old→new baseline version and migration notes;
4. ordinary repository CI/agent-policy validation runs;
5. conflicts or local-policy changes are reviewed;
6. merge records adoption.

This preserves:

- reviewability;
- ordinary Git rollback/revert;
- repository-local history;
- CI proof;
- human veto;
- auditable baseline-version transition.

Direct unattended writes to `main` are difficult to justify for policy/instruction changes.

## Where update PRs can originate

### Manual local command

Maintainer runs an updater against a repository and reviews/pushes the result.

Pros:

- simplest trust model;
- human starts every update;
- local token/credentials already exist;
- excellent first implementation.

Cons:

- does not automatically tell every repo that an update exists;
- repeated manual fleet work.

### Consumer scheduled/check workflow

Each repository periodically invokes a shared update-check mechanism.

It can:

- compare manifest/current baseline to latest supported version;
- report status/fail a check;
- potentially create a PR if granted write/pull-request permissions.

Important GitHub constraints:

- personal-account repositories default to restricted `GITHUB_TOKEN` permissions;
- Actions is not allowed to create/approve PRs by default for a newly created personal-account repository unless enabled;
- `GITHUB_TOKEN` is repository-scoped;
- events generated using `GITHUB_TOKEN` generally do not recursively trigger new workflow runs, so updater-created PR validation can require deliberate token/event design.

References:

- https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository
- https://docs.github.com/en/actions/concepts/security/github_token

### Central GitHub App/bot/controller

A GitHub App installed on selected repositories could:

- enumerate consumers;
- read baseline manifests;
- create branches/PRs;
- configure repository-side settings within granted permissions;
- trigger/observe normal CI.

Pros:

- centralized fleet visibility;
- least-privilege installation model possible;
- can work across existing repositories independent of consumer scheduled workflows.

Cons:

- significantly more infrastructure/auth complexity;
- app lifecycle/credentials/permissions become part of the baseline system;
- overkill until the number of repositories or automation demand justifies it.

Conclusion: credible later scale-up path, not required for first implementation.

## Dependabot as a version-ref updater

GitHub Dependabot version updates natively understand GitHub Actions references.

GitHub documents that Dependabot can open PRs to update:

- actions referenced in workflow files;
- **reusable workflows** referenced from workflow files.

This is highly relevant if consumers pin central reusable workflow/action code to a SHA/tag:

- arbitrary baseline files still need another updater;
- shared executable refs can get a mature PR-based update mechanism almost for free.

References:

- https://docs.github.com/en/code-security/concepts/supply-chain-security/dependabot-version-updates
- https://docs.github.com/en/code-security/how-tos/secure-your-supply-chain/secure-your-dependencies/auto-update-actions

## Existing repositories that never came from the template

A future adoption process should not pretend provenance exists.

Safe conceptual adoption:

1. inventory current repo agent infrastructure;
2. choose a baseline version/profile that most closely matches intended policy;
3. render that baseline separately;
4. compare it with current repo;
5. classify differences as baseline-compatible local override, repo-specific content, or conflicting policy;
6. reconcile through an explicit adoption PR;
7. only after review record the baseline manifest/version as adopted.

A tool such as Cruft's `link` demonstrates that attaching provenance after creation is possible, but for this project the adoption step should prove the asserted baseline relationship rather than simply recording a commit.

## Conflict semantics

A baseline update system should distinguish at least:

- **clean baseline-only change** — consumer did not modify affected baseline region/file;
- **local-only change** — baseline unchanged; preserve consumer;
- **compatible independent change** — normal three-way merge succeeds;
- **semantic conflict** — both changed same policy/region; require review;
- **detached/local-owned component** — updater must not touch;
- **new mandatory migration** — baseline schema requires an explicit structural transition;
- **removed baseline component** — removal must not delete local data blindly.

Unknown state should stop or produce conflict, never silently choose the baseline.

## Version discovery versus update application

These should be separate operations.

Useful commands/concepts:

- `status` / `check-update` — read-only; report current baseline and available target;
- `diff` / `plan-update` — generate proposed changes without applying/committing;
- `update` — apply to working tree/branch;
- `migrate` — explicit ordered structural changes;
- `adopt` / `link` — establish baseline provenance for pre-existing repo after review.

This separation enables scheduled automation to report drift without giving every scheduled job write authority.

## Candidate ranking after A-040

### Strong

1. **Baseline manifest + update-aware three-way reconciliation + migration hooks + PR review.**
2. Existing tool model (especially Copier) as implementation/reference candidate rather than reinventing merge semantics blindly.
3. Dependabot for pinned Actions/reusable-workflow reference updates.

### Plausible supplemental

- Cruft/Cookiecutter lifecycle tooling;
- manual CLI first, GitHub App later;
- scheduled read-only update detection;
- explicit migration scripts for schema changes.

### Weak as primary baseline synchronization

- raw GitHub template regeneration/overwrite;
- submodules;
- subtree as the whole system;
- merging template repository history into consumer history;
- silent scheduled direct-to-main mutation.

## A-040 conclusion

Template provenance/version must become explicit consumer state if copied files are expected to evolve.

The architecture should favor **reviewable convergence**, not enforced byte identity:

- know what baseline produced the repo;
- know what local changes were made since;
- know what the new baseline proposes;
- merge those facts;
- make ambiguity visible;
- adopt through ordinary repository history.

A-050 now needs to reduce how much merging is necessary at all by finding clean generic/local ownership boundaries.
