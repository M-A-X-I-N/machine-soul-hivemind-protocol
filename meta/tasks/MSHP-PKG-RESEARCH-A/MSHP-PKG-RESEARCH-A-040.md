# MSHP-PKG-RESEARCH-A-040 — Investigate unmanaged Windows EXE/MSI installer lifecycle

## Description

Research how arbitrary Windows installers outside package-manager control can be discovered, verified, installed, upgraded and removed safely; use Visual Studio only as one illustrative case.

## Requirements

- Compare ARP registry, MSI product/upgrade codes, uninstall strings, signed installer metadata, vendor APIs, silent installer switches, custom bootstrappers, Visual Studio Installer and unknown executables; flag unknowable/unsafe cases.

## Constraints / non-goals

- Research only; do not claim all EXE installs can have reliable generic automation; preserve already completed VS instance/component research.

## Acceptance criteria

- Produce capability categories, identity limits and conservative candidate implementation tasks.

## Validation

- Inspect current source/architecture and authoritative references relevant to the task.
- Record reproducible findings or targeted validation evidence; explicitly flag untestable claims.
