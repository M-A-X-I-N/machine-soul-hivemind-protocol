# MSHP-AGENT-BASELINE-B-050 — Validate ChatGPT Chat instruction ergonomics and context routing

## Description

Evaluate the v1 architecture from the perspective of the actual primary consumer: ChatGPT Chat performing repository work with repository access and explicit Markdown navigation.

## Requirements

- Simulate fresh-session handling of representative work classes: trivial edit, substantial multi-step task, taskification, interrupted recovery, Git/provenance operation, CI change, architecture research, and memory lookup.
- For each scenario, record the minimal instruction files that must be read and whether routing is obvious from `AGENTS.md`/`.agents/README.md`.
- Identify files that are always co-read and should be merged, or files that are frequently irrelevant and should be split.
- Identify repeated rules that create context waste versus useful concise reinforcement.
- Check that local overrides are noticed reliably and not hidden behind optional memory.
- Check that agent memory is demand-loaded rather than accidentally normative.
- Tune file sizes/structure when there is a concrete expected comprehension/context benefit.
- Prefer platform-neutral Markdown patterns; document any deliberate OpenAI/ChatGPT-specific optimization and why the expected gain justifies it.

## Constraints / non-goals

- Do not optimize for theoretical token minimum at the cost of discoverability.
- Do not add platform-specific mechanisms without a clear expected performance/reliability gain.
- Do not touch the template repository yet.
- Do not redesign unrelated MSHP workflow policy merely because wording could be different.

## Acceptance criteria

- Representative ChatGPT Chat read paths are documented and satisfactory.
- No common scenario requires indiscriminate loading of all agent files.
- File boundaries reflect access patterns rather than arbitrary taxonomy.
- Any retained platform-specific behavior is explicitly justified.

## Validation

- Perform a fresh-session-style navigation pass using only tracked repository instructions.
- Compare expected read sets across scenarios and revise obvious over-reading/fragmentation.
- Run final contradiction/link checks across baseline and local instruction surfaces.
