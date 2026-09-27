# MSHP-META-A-010 — Rename the repository-meta namespace to `autonomic_affairs`

## Description

Rename the repository/project self-management namespace from `collective_affairs/` to `autonomic_affairs/` and make the repository's accidental all-A thematic top-level naming convention explicit.

## Requirements

- Move the complete repository-meta tree to `autonomic_affairs/`.
- Update live paths in runtime-adjacent tooling, CI, tests, documentation, `.agents/`, navigation, and task references.
- Codify that repository-controlled thematic top-level directories begin with `a`.
- Preserve tool/convention-defined roots and externally dictated identifiers unchanged.
- Preserve executable modes, links, fresh-clone behavior, and CI behavior.

## Constraints / non-goals

- Do not rename external/application identifiers to satisfy the theme.
- Historical references to the former namespace may remain when they are explicitly historical.
- Do not rewrite Git history.

## Acceptance criteria

- No live repository path remains under `collective_affairs/`.
- `autonomic_affairs/` owns the repository-meta namespace.
- Live references point to `autonomic_affairs/`.
- The top-level thematic naming convention is documented.

## Validation

- Inspect the recursive Git tree for stale `collective_affairs/` paths.
- Scan live navigation/CI/documentation references.
- Run the full existing Linux/Windows/fresh-clone CI matrix.
