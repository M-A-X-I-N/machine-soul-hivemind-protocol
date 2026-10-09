# MSHP-CI-RUNNER-A-020 — Research layered VM images and clone-on-write job disks

## Description

Investigate parent images/snapshots, differencing disks, QCOW2/overlay/reflinks and related mechanisms for both specialized Windows images and multiple ephemeral worker instances.

## Requirements

- Compare VirtualBox/KVM/Hyper-V realities under nested virtualization, Windows licensing/activation, capacity planning, cache lifecycle, backup, guest rollback and performance.

## Constraints / non-goals

- Research and storage design only; do not assume zero-copy or preallocated disk behavior by default.

## Acceptance criteria

- A reproducible image/worker disk strategy meets low-duplication and safety goals.

## Validation

- Inspect relevant source, documentation and supported-platform evidence.
- Preserve findings, counterexamples and proposed validation commands in the task workspace.
