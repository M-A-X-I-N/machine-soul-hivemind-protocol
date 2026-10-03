# MSHP-DEV-A-060 — Survey additional runtime candidates

## Description

Survey other commonly useful developer runtimes/toolchains so Machine-Soul does not accidentally treat Lua, Python, and Node as an exhaustive list. This is a prioritization survey, not a deep implementation investigation.

## Requirements

- Identify commonly useful additional Windows developer runtimes/toolchains that plausibly belong in annexation procedures.
- Consider candidates such as Ruby, Perl, PHP, Java/JDKs, .NET SDK/runtime, Go, Rust toolchains, or others only where current relevance justifies mention; interpreted-only status is not a requirement.
- For each candidate, note whether multiversion coexistence/version-manager choice is likely material.
- Classify candidates as worth near-term deep investigation, worth initiative tracking only, or not useful for the maintainer's likely environment.
- Do not create executable tasks for every candidate solely because it exists.
- Update MSHP-DEV-ENV with structured gaps/priorities.

## Constraints / non-goals

- Do not perform deep research equivalent to the Lua/Python/Node tasks.
- Do not implement/install anything.
- Do not turn a generic developer-tool catalog into an obligation to support everything.

## Acceptance criteria

- A bounded candidate survey exists.
- Likely future priorities and intentionally deferred runtimes are distinguishable.
- No zombie tasks are created merely to remember candidates.

## Validation

- Use current ecosystem reality rather than historical popularity alone.
- Keep rationale concise and relevant to Machine-Soul annexation.
