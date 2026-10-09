# MSHP-WORKHORSE-CI — Workhorse remote access and nested self-hosted CI infrastructure

**Status:** OPEN

## Goal

Investigate a secure alternative to RDC for shared agent access to the workhorse and build a storage-efficient, extensible, nested-virtualization CI system supporting generic and prepared Windows/Linux workers.

## Current state / coverage

The existing workhorse is an Ubuntu VirtualBox VM, while current MSHP repository CI runs through GitHub Actions. No self-hosted nested virtualization or remote MCP service is currently established by this initiative.

## Known gaps

- Cloudflare Tunnel / MCP remote access feasibility and security.
- Scheduling/resource isolation across multiple agents using one workhorse.
- Shared-object/worktree and copy-on-write workspace techniques.
- General nested self-hosted CI worker/controller topology.
- Layered/differencing Windows and SML-preinstalled worker images, concurrent worker disks.
- Self-hosted-if-available versus GitHub-hosted fallback semantics.

## Deliberate boundaries / deferred work

- Do not place runner/controller services on the physical workstation host.
- Do not expose unauthenticated MCP/shell endpoints.
- Do not assume an official GitHub-hosted image can simply be booted as an independent self-hosted VM.
- Plan a generic controller, not a dedicated SML-only deployment.
- Limit concurrent resource use; avoid unnecessary full VM clones.

## Related executable tasks

- [`MSHP-LAB-A-010`](../tasks/MSHP-LAB-A/MSHP-LAB-A-010.md)
- [`MSHP-LAB-A-020`](../tasks/MSHP-LAB-A/MSHP-LAB-A-020.md)
- [`MSHP-LAB-A-030`](../tasks/MSHP-LAB-A/MSHP-LAB-A-030.md)
- [`MSHP-CI-RUNNER-A-010`](../tasks/MSHP-CI-RUNNER-A/MSHP-CI-RUNNER-A-010.md)
- [`MSHP-CI-RUNNER-A-020`](../tasks/MSHP-CI-RUNNER-A/MSHP-CI-RUNNER-A-020.md)
- [`MSHP-CI-RUNNER-A-030`](../tasks/MSHP-CI-RUNNER-A/MSHP-CI-RUNNER-A-030.md)
- [`MSHP-CI-RUNNER-A-040`](../tasks/MSHP-CI-RUNNER-A/MSHP-CI-RUNNER-A-040.md)
- [`MSHP-CI-RUNNER-A-050`](../tasks/MSHP-CI-RUNNER-A/MSHP-CI-RUNNER-A-050.md)

Mutable task states, dependencies and Dispatch remain authoritative in [`../tasks.md`](../tasks.md).

## Promotion / closure criteria

Remote-control, resource sharing, and hybrid-runner feasibility are settled, followed by a separately approved implementation path for the supported machines.
