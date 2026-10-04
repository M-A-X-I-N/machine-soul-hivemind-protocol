# Machine-Soul CI policy

Read this file when changing CI/control-plane behavior, selecting/overriding CI, validating task completion that depends on repository CI, or diagnosing deferred validation.

This is MSHP-specific policy. Generic task-state meanings remain defined by the baseline workflow.

## Entry point

`.github/workflows/machine_soul_validation.yml` is the sole checked-in CI event entry point for:

- pushes to `main`;
- pull requests targeting `main`;
- manual dispatch;
- the daily schedule.

Ordinary non-main pushes, including `agent/**`, stay quiet unless validated explicitly.

## Automatic selection

Push/PR selection uses changed paths as **conservative evidence**, not unquestioned authority.

- known relevance selects logical checks;
- unknown paths, missing/ambiguous Git evidence, or control-plane uncertainty fail safe to the complete registered check set;
- check selection happens before compatible checks are coalesced onto shared runner jobs.

Do not run an unrelated check merely because another selected check needs the same OS.

## Explicit CI control

A pushed/PR head may use one `CI:` line:

- `auto`;
- `all`;
- `none`;
- exact registered check IDs;
- documented groups such as `linux` / `windows`.

Valid explicit intent overrides automatic path classification.

Malformed/unknown selectors fail visibly while selecting every registered check.

`CI:` covers both blocking checks and deferred CodeQL checks.

Manual validation uses explicit selection rather than inventing an automatic diff.

## Native hard bypass

`skip-checks: true` is the GitHub-level bypass when no checked-in workflow should instantiate.

GitHub requires:

- two empty lines before the trailer section;
- `skip-checks` as the final trailer.

Preserve that spacing exactly.

## Scheduled reconciliation

The daily schedule is:

```text
9 6 * * *
```

That is 06:09 UTC.

It reconciles missing coverage on default-branch HEAD.

Ordinary checks may carry successful coverage across unrelated commits.

CodeQL requires exact-HEAD success and runs:

- every 24 hours while HEAD is younger than 168 hours;
- every 168 hours afterward.

The selector validates repository commit/control metadata across the introduced push/PR range when evidence is available.

## Registered checks

- `linux-python`
- `linux-applications`
- `linux-install`
- `linux-session`
- `linux-matrix`
- `windows-python`
- `windows-applications`
- `windows-posix`
- `windows-install`
- `fresh-linux`
- `fresh-windows`
- `codeql-python`
- `codeql-actions`

## Deferred validation

`AWAITING_DEFERRED_CI` lifecycle semantics come from the baseline workflow.

For MSHP specifically, CodeQL is deferred but centrally routed by the selector.

Substantive deferred-analysis failures reopen/block originating work; infrastructure-only failures are retried/investigated separately.
