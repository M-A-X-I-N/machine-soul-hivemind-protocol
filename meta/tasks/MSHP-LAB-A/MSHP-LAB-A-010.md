# MSHP-LAB-A-010 — Investigate Cloudflare-tunneled workhorse MCP access

## Description

Research replacing Remote Desktop Commander for normal workhorse access with an authenticated MCP endpoint reachable through Cloudflare Tunnel or equivalent narrow remote transport.

## Requirements

- Document server placement, HTTPS/TLS, Cloudflare Access/service tokens, host binding, agent authentication, least privilege, command/filesystem control, revocation and security risks; compare to RDC and SSH.

## Constraints / non-goals

- Research only; do not expose shell/MCP ports or deploy public unauthenticated endpoints.

## Acceptance criteria

- A secure feasible architecture or explicit blocker/alternative is documented.

## Validation

- Inspect relevant source, documentation and supported-platform evidence.
- Preserve findings, counterexamples and proposed validation commands in the task workspace.
