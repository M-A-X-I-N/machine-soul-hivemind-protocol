# MSHP-AGENT-BASELINE-A-010 — GitHub template repository mechanics

Research date: 2026-10-04.

## Scope and repository observation

`M-A-X-I-N/template` was inspected read-only. GitHub reports:

- `is_template: true`;
- public visibility;
- default branch `main`;
- no fork parent/source;
- `template_repository: null` because it is itself the source template rather than a generated consumer;
- repository size 0 / currently empty.

No write was made to that repository.

## What GitHub templates actually copy

GitHub documents repository templates as a mechanism for generating a new repository with the same directory structure and files as the template. By default generation uses the template's default branch; the user may instead choose to include all branches.

A repository generated from a template is a new project, not a fork. GitHub explicitly documents that:

- a fork includes the parent's full commit history;
- a repository generated from a template starts with a single commit;
- template-created branches have unrelated histories.

Therefore the template is a snapshot/bootstrap source, not a Git-history upstream. Ordinary pull requests/merges do not provide an update channel back to the template.

Official references:

- https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-repository-from-a-template
- https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-template-repository

## Branch behavior

Generation choices:

- default: copy the default branch's directory structure/files;
- optional: include all branches;
- when all branches are included, generated branches are still unrelated histories rather than preserving the template's branch DAG.

This makes multiple template branches usable as independent starter snapshots, not as a future merge/synchronization topology.

## Git LFS limitation

GitHub documents that a template repository cannot include files stored using Git LFS.

For this agent-infrastructure use case that is unlikely to matter unless future template content grows beyond ordinary text/scripts/assets, but it is a hard platform constraint worth retaining.

## Creation surfaces

GitHub currently exposes template generation through:

- the web UI (`Use this template` / new repository flow);
- GitHub CLI: `gh repo create --template <repository>` with optional `--include-all-branches`;
- REST: `POST /repos/{template_owner}/{template_repo}/generate`.

The REST generation endpoint exposes owner, repository name, description, include-all-branches, and public/private creation choice. It does not expose a generic 'clone all repository settings' option.

Official references:

- https://docs.github.com/en/rest/repos/repos#create-a-repository-using-a-template
- https://cli.github.com/manual/gh_repo_create

## Access and visibility

Anyone with read access to a template repository can generate a repository from it.

For the REST generation endpoint, if the template is non-public, GitHub documents that the authenticated user must own the template or be a member of the organization that owns it. Creating into an organization requires membership/appropriate repository-creation authority.

The generated repository's visibility is selected at creation rather than documented as inherited from the source template. The web flow explicitly asks for visibility; the REST endpoint accepts `private` independently of source visibility.

For the current public personal-account `M-A-X-I-N/template`, read access is therefore not a distribution obstacle for the maintainer's own repositories.

## Repository content versus repository-side configuration

The documented template contract is deliberately narrow: directory structure, files, and optionally branches.

File-backed GitHub configuration therefore travels because it is repository content. Examples include, when present:

- `.github/workflows/*.yml`;
- issue/PR template files;
- `CODEOWNERS`;
- Dependabot configuration;
- repository-local scripts/configuration;
- `AGENTS.md` and `.agents/` content.

That does **not** mean repository-side state/settings are part of the template-copy contract.

The template creation UI and REST generation API do not document copying repository-side resources such as:

- Actions secrets;
- Actions repository/environment variables;
- branch protection rules;
- repository rulesets;
- existing issues or pull requests;
- labels/milestones;
- repository environments;
- collaborators/permissions;
- webhooks;
- Pages configuration;
- security/analysis settings;
- merge strategy settings;
- discussions/settings;
- deployment keys.

GitHub exposes many of those as separate repository/API resources. The repository-template documentation promises files/branches, not a repository-settings clone.

Research conclusion for architecture: **treat repository-side settings as not inherited by the template mechanism unless a specific current GitHub document/API explicitly establishes otherwise.** This is intentionally conservative wording: the research did not create a consumer repository to experimentally enumerate every setting because this block forbids external mutation.

Supporting official references:

- Template copy contract: https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-repository-from-a-template
- Actions variables are repository/org/environment resources: https://docs.github.com/en/actions/concepts/workflows-and-actions/variables
- Actions secrets are separate repository resources: https://docs.github.com/en/rest/actions/secrets
- Repository rulesets are separate repository resources: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets

## Template provenance metadata

The REST repository representation includes both:

- `is_template` — whether the repository acts as a template source;
- `template_repository` — a repository-valued field in the repository schema.

The current `M-A-X-I-N/template` source returns `template_repository: null`.

This means GitHub has a machine-readable concept for template provenance in repository metadata. However, the public documentation reviewed here does not define that field as a synchronization/update contract, nor does the create-from-template documentation expose any 'sync from template' operation.

Therefore later architecture may use template provenance as discovery/hint metadata if it proves reliably populated for generated consumers, but **must not treat it as an upstream relationship equivalent to a fork** without further evidence.

REST reference:

- https://docs.github.com/en/rest/repos/repos

## Ongoing synchronization: explicit negative finding

No GitHub-native template-update/synchronization operation was found in the current repository-template documentation, CLI creation command, or REST create-from-template endpoint.

This is consistent with GitHub's documented model: generation starts a new single-commit project with unrelated history.

Consequently:

- a template is suitable for initial bootstrap;
- changes made later to the source template are not documented as automatically propagating to already-generated repositories;
- ongoing baseline evolution must be solved by another mechanism or a higher-level synchronization/migration process.

This is the most important architectural limitation discovered in A-010.

## Contrast with migration/forking mechanisms

GitHub's migration documentation explicitly distinguishes templates from mechanisms that preserve/migrate broader repository state. GitHub Enterprise Importer, for example, is documented as migrating source/version-control history plus issues, pull requests, settings, and more. Forks preserve upstream history and have native upstream synchronization concepts.

That contrast reinforces that templates are deliberately lightweight starter-content generation, not repository cloning/migration or long-lived upstream topology.

Reference:

- https://docs.github.com/en/migrations/overview/programmatically-importing-repositories

## Unknown / intentionally unproven details

Because the research boundary forbids creating a generated consumer repository, these details remain intentionally unverified experimentally:

- exactly which `template_repository` fields GitHub returns for a newly generated consumer in the current API;
- whether any undocumented repository settings happen to be copied by a particular UI path;
- edge behavior of an entirely empty template when generating a repository;
- exact commit authorship/message metadata used for generated repositories.

None is required to establish the main architectural facts above. Later implementation work may experimentally verify them if they materially affect the chosen design.

## A-010 conclusion

`M-A-X-I-N/template` is a strong candidate for **bootstrap distribution of generic file-based agent infrastructure**. It is not, by itself, an ongoing shared-infrastructure or synchronization system.

Research should therefore continue by separating:

1. what generic infrastructure is worth bootstrapping;
2. what should remain live/shared rather than copied;
3. how already-existing repositories receive future baseline evolution.

No final architecture is selected by this task.
