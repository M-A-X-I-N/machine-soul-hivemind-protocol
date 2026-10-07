# Repository meta

`meta/` is the exact lowercase repository-control namespace shared with the generic agent baseline.

In MSHP it contains project/repository state rather than machine-targeted configuration or annexation machinery.

Current contents:

- `docs/` — human-facing architecture, contracts, support notes, and extension guidance.
- `tests/` — repository validation and behavioral test suites.
- `tasks.md` — compact scheduling/state/Dispatch index.
- `tasks/` — active task specifications, temporary tracked task workspaces, task-system navigation, and structured archive under `tasks/archive/`.
- `reminders.md` — non-executable lightweight future intent.
- `initiatives/` — structured non-executable unfinished work/debt.
- `ci_validation_selector.py` and related helpers — repository CI-control policy implementation.

`tasks.md` is the authoritative ledger for sufficiently specified executable agent work. Reminders and initiatives are deliberately not Dispatch authority.

The exact path `meta/` is reserved by the baseline integration contract. Do not rename or recase it to match repository-specific source naming conventions.

Root artifacts whose placement is conventional or tool-defined remain at repository root, including `AGENTS.md`, `README.md`, `.machine_soul_root`, other dotfiles, and `.github/`.
