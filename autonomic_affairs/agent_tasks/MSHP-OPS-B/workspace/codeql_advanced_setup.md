# MSHP-OPS-B — CodeQL advanced-setup investigation

## Starting point

The maintainer switched the repository from GitHub-managed CodeQL default setup to the stock advanced-mode workflow at commit `910dc99bb481f2940c98a19c6688a855374e8086` in `.github/workflows/codeql.yml`.

The generated workflow currently:

- runs on pushes to `main`;
- runs on pull requests targeting `main`;
- runs weekly at `30 0 * * 0`;
- analyzes `actions` and `python`;
- uses `build-mode: none` for both;
- runs one Ubuntu job per language;
- uses the built-in default query suite;
- uploads one stable category per language;
- has no manual dispatch, concurrency policy, custom config file, custom queries, path analysis filters, or resource tuning.

The first advanced-mode run succeeded. Python reported full extraction coverage of **183/183 Python files** and **6/6 GitHub Actions files**; Actions reported **6/6 GitHub Actions files**.

A correctly formatted `skip-checks: true` trailer was also empirically verified after advanced setup was enabled: commit `2f26538d527333a258386490e1b9ac5b66d179ac` produced zero workflow runs, suppressing both normal validation and CodeQL.

## Authoritative references

- [Workflow configuration options for code scanning](https://docs.github.com/en/code-security/reference/code-scanning/workflow-configuration-options)
- [Configuring advanced setup for code scanning](https://docs.github.com/en/code-security/how-tos/find-and-fix-code-vulnerabilities/configure-code-scanning/configuring-advanced-setup-for-code-scanning)
- [CodeQL query suites](https://docs.github.com/en/enterprise-cloud@latest/code-security/concepts/code-scanning/codeql/codeql-query-suites)
- [Manually running a workflow](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow)
- [Workflow syntax / concurrency](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax)
- [Skipping workflow runs](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/skip-workflow-runs)
- [Code scanning analysis takes too long](https://docs.github.com/en/code-security/reference/code-scanning/troubleshoot-analysis-errors/analysis-takes-too-long)
- [github/codeql-action init inputs](https://github.com/github/codeql-action/blob/main/init/action.yml)
- [github/codeql-action analyze inputs](https://github.com/github/codeql-action/blob/main/analyze/action.yml)

## Configuration surface

### Workflow routing

Advanced setup is an ordinary GitHub Actions workflow. It supports standard `push`, `pull_request`, `schedule`, and `workflow_dispatch` routing, matrices, permissions, runner choice, conditions, and concurrency.

`workflow_dispatch` must be registered on the default branch, but a manual run can target another branch/ref. Native commit-message skip instructions apply to `push` and `pull_request`; scheduled/manual runs are separate event types.

### Languages and build modes

The explicit `actions` + `python` matrix is appropriate. Both current languages support `build-mode: none`, and the stock run proved complete extraction. `autobuild` and `manual` exist for compiled-language use but are not currently relevant.

### Query suites, packs, filters, and models

Built-in suites are:

- `default`: high-precision security queries and comparatively few false positives;
- `security-extended`: default plus lower-precision/lower-severity security queries, with greater false-positive potential;
- `security-and-quality`: security-extended plus maintainability/reliability queries.

Advanced setup also supports published query packs, custom queries/suites, query include/exclude filters, and model packs. MSHP currently has no demonstrated need for any of them.

### Config file versus inline policy

`codeql-action/init` accepts `config-file` or an inline `config` YAML string. A CodeQL config can own query/pack policy, query filters, threat-model settings, and analysis `paths` / `paths-ignore`.

For current MSHP, a separate config file would contain no justified persistent policy beyond defaults. Creating one now would add an abstraction with no payload. Add `.github/codeql/...` configuration only when a real stable setting needs ownership.

### Analysis paths versus trigger paths

CodeQL config `paths` / `paths-ignore` control what source is analyzed. They are explicitly distinct from Actions `on.push.paths` / `on.pull_request.paths`, which decide whether the workflow launches. Therefore analysis-path filtering would not violate MSHP's ban on changed-path CI routing.

It is still unjustified today: stock analysis has full coverage, the repo is small, no generated/vendor subtree has been identified, and whole-repository context benefits data-flow analysis.

### Categories and multiple analysis origins

The `analyze` action's `category` identifies/matches analysis results. GitHub supports multiple code-scanning configurations, but the same issue may then have multiple analysis origins and stale configurations can retain stale alert state.

Therefore event-specific automatic query profiles are unattractive here. Prefer one stable automatic CodeQL policy unless a concrete need justifies another analysis origin.

### Permissions

The generated template grants `security-events: write`, `contents: read`, `packages: read`, and `actions: read`. For this public repo with no private/custom packs, current needs justify only:

- `contents: read`
- `security-events: write`

Add package/action permissions later only if a feature actually needs them.

### Runners, databases, and resources

The action exposes runner choice, `ram`, `threads`, `source-root`, `db-location`, debug artifacts, caches, and alternate CodeQL tool versions. None solves a current MSHP problem: Ubuntu succeeds, coverage is complete, the repo is small, defaults complete quickly, and GitHub-hosted runners provide clean temporary storage.

### Scheduling

Scheduled analysis is useful because updated CodeQL queries/models can find newly understood vulnerabilities even without source changes. Keep the generated weekly full-default-branch scan. There is no evidence supporting a different cadence.

### Concurrency

CodeQL is deferred analysis, so finishing an obsolete same-ref run after a newer run exists is usually waste. Recommended workflow concurrency:

```yaml
concurrency:
  group: codeql-${{ github.workflow }}-${{ github.event_name }}-${{ github.ref }}
  cancel-in-progress: true
```

Including `github.event_name` prevents a scheduled main scan and a normal main-push scan from accidentally cancelling one another.

### Other controls investigated but not recommended now

Current CodeQL actions also expose alternate/nightly tools, private registries/tokens, database location, RAM/thread caps, debug mode, source-root override, cache switches, skip-queries, SARIF upload modes, database upload, explicit upload ref/SHA, and post-processed SARIF output. These are valid mechanisms but none addresses a current repository need.

## Recommended MSHP architecture

### Lifecycle

**Keep CodeQL separate from registered blocking validation sets.** Normal Machine-Soul validation gates implementation advancement; CodeQL is security analysis and already has a deferred lifecycle in repository policy.

| Event | CodeQL behavior |
|---|---|
| Push to `main` | automatic full CodeQL analysis |
| Pull request targeting `main` | automatic full CodeQL analysis |
| Ordinary push to `agent/**` / other non-main branch | no automatic CodeQL |
| `workflow_dispatch` targeting a chosen ref | deliberate CodeQL analysis of that ref |
| Weekly schedule | automatic full analysis of default branch |

This mirrors normal-CI branch philosophy without coupling the workflows.

### Query policy

Use **one stable automatic query policy: the built-in default suite**.

Reasons:

1. It is GitHub's high-precision security-focused suite.
2. Current coverage is already complete.
3. No alert/noise evidence justifies lower precision.
4. `security-and-quality` changes the workflow's purpose into general maintainability/reliability analysis.
5. Event-specific uploaded profiles complicate analysis-origin/category semantics.

Do not automatically add `security-extended` or `security-and-quality` yet. If broader coverage is desired later, evaluate it deliberately against actual findings/noise, then decide whether to replace the stable policy globally.

### Configuration ownership

Keep current policy in `.github/workflows/codeql.yml` for now. Add a dedicated CodeQL config file only after it has real persistent analysis-policy content.

### Workflow cleanup

The implementation should:

- preserve `push: main`, `pull_request: main`, and the weekly schedule;
- add `workflow_dispatch` without unnecessary profile inputs;
- add event/ref-scoped cancellation;
- retain explicit `actions` + `python`, `build-mode: none`, `fail-fast: false`, Ubuntu, and stable language categories;
- retain the default query suite;
- reduce permissions to `contents: read` + `security-events: write`;
- replace generic generated-template comments with concise repository rationale;
- document CodeQL explicitly as deferred analysis.

### Non-goals

Do not currently add trigger path routing, analysis exclusions, custom queries/packs/models, event-specific query suites, a second persistent analysis origin, Windows runners, blocking-gate semantics, resource tuning, alternate CodeQL tool versions, or reusable-workflow abstraction.

## Evidence-backed follow-up taskification

The investigation justifies **one implementation/validation task**, not separate implementation and validation tasks. The change is one small coherent workflow-policy checkpoint, and validation is inseparable from proving it.

No additional query-profile/config-file task is justified until real scan results create a need.

## B-020 implementation validation

Implemented at `f586ca133132b41d9006192e7bdbe12e24174ac6`.

Verified behavior:

- ordinary push to `agent/lyra_260928-230718/main` produced zero workflow runs;
- integration to `main` used `CI: none`, so Machine-Soul validation ran only its selector job and skipped all four blocking validation sets;
- CodeQL still ran independently on the same main push;
- `Analyze (actions)` succeeded with reduced permissions, scanned 6/6 GitHub Actions files, and uploaded SARIF successfully;
- `Analyze (python)` succeeded with reduced permissions, scanned 183/183 Python files plus 6/6 GitHub Actions files, and uploaded SARIF successfully;
- the default-branch workflow contains `workflow_dispatch`, event/ref-scoped concurrency, the same explicit `actions` + `python` matrix, `build-mode: none`, and stable `/language:${{ matrix.language }}` categories;
- no CodeQL config sidecar or additional checked-in category/profile was introduced.

### Manual-dispatch verification limitation

The GitHub connector available to this agent can inspect workflow runs/jobs/logs and rerun existing jobs, but does not expose an action for creating a `workflow_dispatch` event. The connector also does not expose the workflow-metadata dispatch endpoint directly.

The workflow is on the default branch and contains `workflow_dispatch`, satisfying GitHub's registration prerequisite. Manual selected-ref behavior is therefore left to GitHub's documented semantics rather than a manufactured substitute test.

Exact manual verification paths:

- GitHub UI: **Actions → CodeQL Advanced → Run workflow → choose the target branch/ref → Run workflow**.
- GitHub CLI: `gh workflow run codeql.yml --ref agent/lyra_260928-230718/main` (replace the ref as desired).
