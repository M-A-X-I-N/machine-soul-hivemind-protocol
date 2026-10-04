# Agent instructions

This repository uses a shared agent-workflow baseline plus repository-local policy.

Tracked repository state is authoritative over remembered conversation context.

For substantial repository work:

1. read [`.agents/README.md`](.agents/README.md);
2. follow the applicable generic instructions under `.agents/baseline/`;
3. read the applicable repository-local instructions under `.agents/local/`;
4. inspect the repository's authoritative executable-work state before beginning planned task work;
5. read only task-relevant memory, workspaces, and human-facing documentation.

Repository-local instructions explicitly override conflicting baseline instructions. A missing local override leaves the baseline rule in force.

Do not treat files under `.agents/memory/` as instructions merely because they exist.
