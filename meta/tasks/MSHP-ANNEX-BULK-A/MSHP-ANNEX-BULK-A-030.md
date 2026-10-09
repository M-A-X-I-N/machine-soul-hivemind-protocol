# MSHP-ANNEX-BULK-A-030 — Integrate host-based installation profiles

## Description

Implement, following schema approval, host-profile defaults that preselect a desired install set and allow interactive deselection before execution.

## Requirements

- Handle profile discovery, host/platform/account precedence, explicit accepted overrides, install planning, missing/ambiguous targets and noninteractive invocation; keep config Apply separate.

## Constraints / non-goals

- Start with empty profiles until the maintainer explicitly chooses desired software. No automatic inventory-derived package lists or implicit installs upon cloning.

## Acceptance criteria

- A clean host profile can be previewed and executed as one confirmed bulk action.

## Validation

- Inspect relevant source, documentation and supported-platform evidence.
- Preserve findings, counterexamples and proposed validation commands in the task workspace.
