# Reminders

This file holds ideas that are intentionally **not yet executable agent tasks**.

A reminder:

- is not part of Dispatch;
- carries no authorization to act;
- must not be silently executed or promoted by an agent;
- becomes executable work only after discussion/refinement makes it sufficiently specified for `tasks`.

Keep this register simple. When an idea becomes a recognized structured multi-phase concern with known gaps/boundaries but is still not itself executable, promote it deliberately into [`initiatives/`](initiatives/) rather than turning this file into a second backlog.

## Cross-repository provenance normalization / gloriously unnecessary rebases

After the new agent-provenance policy has stabilized, audit the maintainer's other repositories for legacy `Agent-authored-by:` conventions and stable-designation references.

The long-term temptation is to normalize historical commit messages with fat, completely unnecessary rebases/history rewrites.

Before this reminder can become executable work:

- enumerate every affected repository;
- enumerate the exact branches/refs and history ranges;
- identify collaboration/clone/PR/link implications;
- determine the rewrite procedure and recovery plan;
- obtain explicit human authorization for each affected history/ref and destructive rewrite.

Merely recording this reminder does **not** authorize any rebase, force-push, ref rewrite, or history destruction.

## Extend agent baseline beyond manual instruction v1

**Status:** Parked follow-up beyond active block `MSHP-AGENT-BASELINE-B`.

The active B block deliberately implements only the manually maintained **agent-instruction baseline**: generic/local/memory separation, ChatGPT-Chat-oriented routing, MSHP reference-consumer refactor, template population, and a human-plus-agent update/adoption procedure.

After that v1 has real usage experience, revisit the broader research in `autonomic_affairs/docs/CROSS_REPOSITORY_AGENT_BASELINE.md` if manual maintenance becomes painful or shared runtime provides clear value.

Deferred possibilities include:

- centrally shared reusable workflows/actions;
- automatic or semi-automatic baseline synchronization;
- baseline manifests/schema/version machinery;
- update bots or GitHub Apps;
- repository-setting reconciliation;
- broader fleet migration/automation.

Do not implement these merely because the research exists. Let actual v1 maintenance experience justify the complexity.

## Investigate OpenAI Skills for reusable repository workflows

Investigate whether repeatable Machine-Soul workflows are worth expressing as OpenAI Skills or related reusable agent workflows.

Candidate workflows include:

- interrupted-session recovery;
- claiming/executing an agent task;
- adding a new application integration;
- validating a checkpoint.

The investigation should distinguish:

- repository-local Skill discovery, especially Codex-oriented workflows;
- installed/shared Skills available through supported ChatGPT surfaces such as Chat and Work;
- actual portability of one Skill definition across those surfaces;
- what state/context a Skill can reliably discover from a repository;
- whether Skills materially improve this repository over concise `AGENTS.md` plus `.agents/` procedures.

Do not implement Skills merely because the mechanism exists.

Revisit this after the canonical task schema is established so any task-execution Skill can target the real `tasks.md` contract rather than a transitional format.

## Agent-facing repository memory hygiene

Design a lightweight process that periodically prompts agents to inventory the repository's agent-facing memory, task/context infrastructure, and related contents for issues that are difficult for the human maintainer to notice directly.

Candidate problems include:

- stale, contradictory, superseded, or duplicated agent memory;
- important discoveries that exist only in transient locations and should be promoted;
- permanent memory that has outlived its usefulness;
- navigation/discoverability problems visible mainly from an agent's reading path;
- task/workspace structures that cause unnecessary context or token load;
- instructions whose practical effect differs from their apparent intent;
- obsolete assumptions, dead links, or misleading source-of-truth claims;
- repository conventions that repeatedly cost agents investigation effort;
- other agent-specific friction that a human reviewing files normally would not be positioned to detect.

The eventual process should encourage agents to surface findings proactively at appropriate checkpoints even when the maintainer did not know to ask about them.

Before promotion to executable work, decide:

- appropriate triggers/cadence (for example lifecycle boundaries, occasional explicit audits, or both);
- what should be reported immediately versus silently corrected when safe;
- when findings should become tasks, reminders, documentation changes, or `.agents/` updates;
- how to avoid turning the audit itself into routine context/token bloat.

This reminder authorizes no recurring audit or unrelated cleanup by itself.

## Installation takeover

Investigate and eventually design an explicit mechanism for Machine-Soul to take over or normalize pre-existing application installations without conflating discovery with ownership.

Potential cases range from simple adoption of an installation already using the preferred package mechanism to migration between mechanisms, for example replacing an MSI-installed application with the preferred WinGet package while preserving user/application data.

Any future takeover design must treat destructive migration as a separate safety-sensitive operation. Before promotion to executable work, determine at least:

- how installation identity/equivalence is proven across mechanisms;
- what application data/configuration must survive removal/reinstallation;
- how uninstall behavior, install scope, services, associations, plugins, and other machine state are discovered;
- when an existing installation may be adopted without reinstalling;
- when migration is safe, unsafe, ambiguous, or unsupported;
- rollback/recovery behavior for partial takeover;
- how Machine-Soul ownership changes are recorded.

The installation-discovery workstream should preserve enough provenance/identity information to keep this future feature possible, but must not implement takeover merely because this reminder exists.


## Windhawk configuration / mod-state management

Investigate whether Windhawk should become a Machine-Soul-managed application/state domain.

Windhawk is intentionally outside the current "standard Windows applications" investigation because its interesting state is broader and more security-sensitive than one ordinary config file: installed mods, each mod's settings/configuration, global application settings, enablement state, process inclusion/exclusion rules, and potentially embedded mod source.

Current Windhawk 2.0 prerelease work includes an official Backup & Restore flow and CLI commands such as `data export`, `data inspect`, and `data import`, making a native export/import integration potentially much cleaner than copying ProgramData and registry internals.

Before promotion to executable work, investigate at least:

- stable versus prerelease Windhawk capabilities and the version boundary for official export/import;
- what the backup archive contains and whether it is deterministic/reviewable enough for Git;
- whether Machine-Soul should track a Windhawk export artifact, a declarative mod manifest/settings model, or both;
- global app settings versus per-mod settings/configuration and enablement;
- local mods and whether source should be embedded/tracked separately;
- trust/security implications of restoring archives that install and execute mods;
- installation scope, service/engine state, elevation requirements, and restart/reload behavior;
- how Install/Check/Verify semantics would work without treating arbitrary registry/ProgramData copies as the primary contract;
- whether official CLI export/import makes a reusable Machine-Soul export/import deployment strategy worthwhile.

Do not implement Windhawk or import a backup merely because this reminder exists.


## Human review of agent instruction Markdown

At an appropriate future checkpoint, have the human maintainer actually read the repository's agent-facing instruction Markdown as a human document rather than relying only on agents to validate it.

The concern is epistemic rather than merely stylistic: an agent evaluating the instructions that define its own behavior is constrained by those same instructions and may systematically fail to notice misleading wording, unintended authority, circular assumptions, or requirements whose practical effect differs from the maintainer's intent.

The review should cover at least:

- root `AGENTS.md`;
- `.agents/README.md`;
- `.agents/baseline/WORKFLOW.md`;
- `.agents/baseline/GIT.md`;
- `.agents/baseline/PROVENANCE.md`;
- `.agents/baseline/KNOWLEDGE.md`;
- applicable files under `.agents/local/`;
- task/initiative/reminder lifecycle instructions;
- source-of-truth and authority ordering;
- any other Markdown that materially governs agent behavior.

The purpose is not to make the human verify every implementation detail. It is to sanity-check whether the written instructions actually mean what the maintainer thinks they mean when read without the agent's own interpretive machinery.

Do not treat agent self-review as a substitute for this reminder.


## Git history attitude and commit-history cleanup

Revisit the repository's long-term attitude toward Git history and whether any commit-history cleanup, normalization, consolidation, or related maintenance is desirable.

This reminder is intentionally underspecified and is not prompted by a current defect or by work completed so far.

Before promotion to executable work, decide what problem—if any—is actually being solved, what history/ref ranges would be affected, and whether the value justifies any disruption.

This reminder authorizes no rebase, squash, reset, force-push, history rewrite, commit-message rewrite, or ref movement.
## Non-symlink configuration deployment strategy

Investigate and eventually design a configuration deployment mode for cases where Machine-Soul should track canonical configuration in the repository but **must not symlink the application's native config path**.

This is deliberately only a reminder. The current configuration safety law remains file-level symlinks until a replacement/extension is explicitly designed.

Potential questions for later:

- which applications/files genuinely require materialized/copied/rendered deployment rather than links;
- how drift is detected when repository edits no longer become live instantly;
- whether apply is copy/materialize, render, import/export, or another native mechanism;
- how ownership/provenance distinguishes a Machine-Soul materialized file from an unmanaged lookalike;
- conflict, backup, rollback, Check, and Unapply semantics;
- whether deployment strategy belongs in the shared application/config declaration model.

Do not create one-off copy hacks merely because this reminder exists.

## Implement nuanced Git/commit-history cleanup policy

Replace the current intentionally conservative additive-history rule with a more precise policy that distinguishes **meaningful Git history** from incidental commit boundaries.

Maintainer direction already established:

- preserving meaningful historical repository states is the primary concern;
- commit count/order is not sacred merely because events happened that way;
- task claim / implementation / completion bookkeeping may often be representable more cleanly as fewer commits;
- fixup/admin commits may be squash candidates when no meaningful repository state is lost;
- large deletes, large squashes, and destructive rebases are **very strong warning signs**, but are not automatically disqualifying solely because they are large or destructive;
- rewriting away a substantive intermediate repository state is normally unacceptable even when the final tree is unchanged;
- published/ref topology and external references are a separate safety dimension and must be considered explicitly.
- when designing cleanup heuristics, investigate whether richer semantic commit metadata would make squash/rebase candidates easier to identify safely. Do **not** manually duplicate touched file paths merely for this purpose: Git already owns physical path facts. If metadata is useful, prefer information Git cannot infer, such as task/workstream or semantic area; evaluate whether that also justifies simplifying the current `[Kind][Scope]` title grammar.
Before promotion to executable work, define objective-ish review questions for squash/rebase candidates, published-ref authorization rules, recovery/backups, and how cleanup interacts with concurrent agent branches.

Until that policy is deliberately implemented, existing additive/no-rewrite repository rules remain authoritative.

## GitHub social preview artwork

Design and set a proper GitHub social-preview image for Machine-Soul Hivemind Protocol.

This deserves a dedicated visual-design chat rather than opportunistic generation during repository implementation work.

Direction:

- use the visual language of the maintainer's existing profile-picture **background** as the stylistic anchor;
- make the preview feel like it belongs to the same visual universe rather than stretching/cropping the avatar itself;
- design specifically for GitHub social-preview composition/readability;
- iterate on concept/composition before committing the final asset or changing repository settings.

When starting the dedicated image chat, use the exact current profile image as reference if available; if the image-generation surface cannot directly consume the Library artifact, have the maintainer attach that exact image rather than approximating it from memory.
