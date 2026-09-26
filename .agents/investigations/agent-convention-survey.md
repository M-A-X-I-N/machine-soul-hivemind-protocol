# Agent convention survey

Surveyed accessible sibling repositories:

- `M-A-X-I-N/satisfactory-wiremod-rss-integration`
- `M-A-X-I-N/Mailchemy`
- `M-A-X-I-N/FactoryLens`

## Reusable conventions found

The common pattern is strong:

- inspect current repository state before trusting remembered chat;
- keep root `AGENTS.md` concise and route detailed procedure to `.agents/`;
- preserve Git history/recoverability and prefer additive corrections;
- use small coherent checkpoints and push completed work promptly;
- run the smallest validation that genuinely proves the changed surface;
- stop for genuine architecture ambiguity rather than silently making a human decision;
- place information according to ownership instead of duplicating authority;
- use `[Kind][Scope] Imperative summary` commits;
- reserve `CBA` for explicit human selection;
- use agent-authorship provenance for wholly agent-authored substantive commits;
- distinguish ephemeral/generated/machine-local state from tracked source.

## Deliberate adaptation here

Sibling repositories mostly frame `.agents/` as procedure/context while durable technical facts live elsewhere.

Machine-Soul v2 intentionally broadens `.agents/` into a living agent knowledge base too: expensive-to-rediscover technical knowledge should be persisted proactively.

Human-relevant durable design still belongs in normal project documentation as well. The broader `.agents/` role is supplementary memory, not hidden competing architecture authority.
