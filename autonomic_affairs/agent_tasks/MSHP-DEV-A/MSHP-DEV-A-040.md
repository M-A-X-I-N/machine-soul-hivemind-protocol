# MSHP-DEV-A-040 — Investigate Python multiversion annexation

## Description

Investigate Python on Windows with the same multiversion-first mindset as Lua: preserve sane side-by-side operation, discovery, default selection, and safe lifecycle management without assuming one installer/manager in advance.

## Requirements

- Research current official Python Windows installation/distribution mechanisms and side-by-side version behavior.
- Investigate the current Python launcher/manager story plus credible maintained third-party version managers where useful.
- Map version-specific executables, launcher selectors, PATH/app-execution-alias behavior, architecture, and install scope.
- Investigate deterministic discovery of multiple installed versions and default-selection semantics.
- Investigate uninstalling one version without damaging others.
- Separate Python runtime installation from pip, virtual environments, and package-environment state.
- Compare version-manager delegation with direct runtime management.
- Produce conceptual outputs comparable with the Lua and Node investigations.

## Constraints / non-goals

- Do not install/uninstall Python.
- Do not manage pip inventories here.
- Do not conflate venvs with installed runtime versions.
- Do not preselect a version manager.
- Do not require assimilation directives where no useful Python config is desired.

## Acceptance criteria

- Windows multiversion Python lifecycle options are mapped.
- Discovery/default-selection/uninstall semantics are explicit.
- Runtime state is separated cleanly from pip/venv state.
- Findings are comparable with Lua and Node.

## Validation

- Use current official Python docs and maintained manager sources.
- Verify Windows behavior rather than extrapolating Unix conventions.
- Date volatile launcher/version-manager findings.
