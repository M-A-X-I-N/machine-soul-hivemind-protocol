# MSHP-APPS-A-010 — Investigate Windows config candidates

## Description

Investigate additional Windows applications and Windows-integrated tools whose configuration plausibly belongs in Machine-Soul.

The goal is not to maximize the number of managed applications. Identify configuration surfaces that are stable, meaningful to the maintainer's preferred machine state, and compatible with Machine-Soul's canonical-config / Apply / Check / Verify architecture.

Windows Terminal is already managed and should be used as a reference/baseline rather than proposed as a new application.

## Requirements

- Keep the investigation Windows-only.
- Define practical inclusion criteria for a "standard" Machine-Soul configuration candidate. Prefer Windows-integrated, Microsoft first-party, or sufficiently baseline/common machine tools over arbitrary third-party applications.
- Inventory plausible candidates and identify, for each:
  - application/tool identity and how presence can be discovered;
  - documented or otherwise trustworthy configuration storage;
  - user versus machine scope;
  - config format/schema and whether the surface is intended for user editing;
  - whether configuration is a canonical singleton, a collection of profiles/assets, registry/policy state, or an export/import model;
  - whether secrets, credentials, machine-generated IDs, caches, or other unsuitable mutable state are mixed into the same storage;
  - whether file-level symlink deployment is appropriate, or whether a different reusable Machine-Soul strategy would be safer;
  - read-only structural Check feasibility;
  - effective/runtime Verify feasibility and the strongest honest evidence level;
  - reload/restart requirements;
  - expected portability across Windows machines/accounts;
  - any version/package/distribution caveats.
- Investigate at least these seeded candidates:
  - **WinGet / Windows Package Manager client settings** — distinguish the editable client `settings.json`, administrator settings, sources, and the separate WinGet Configuration/DSC feature. Investigate whether direct file deployment or a native export/import/settings interface is the best Machine-Soul boundary.
  - **WSL global configuration** — `%UserProfile%\.wslconfig`; distinguish it from per-distribution `/etc/wsl.conf`.
  - **Windows OpenSSH client** — `%UserProfile%\.ssh\config`; explicitly consider separation from private keys, known_hosts, and other sensitive/machine-derived SSH material.
  - **PowerToys** — investigate the documented backup/restore and Microsoft DSC configuration surfaces instead of blindly symlinking internal settings files.
  - **Windows Sandbox** — determine whether tracked `.wsb` launch profiles belong as an application configuration entry, a reusable asset/tool collection, or outside the normal Apply model.
- Consider other Windows built-in/first-party surfaces discovered during research, including Notepad, Explorer/Shell, or similar tools, but reject undocumented/private/binary state when no stable configuration contract exists.
- Use current official Microsoft documentation and authoritative upstream repositories where practical; record version-sensitive facts with dates/versions where relevant.
- Produce a candidate matrix that classifies each investigated item as:
  - already managed;
  - strong implementation candidate;
  - conditional/special-model candidate;
  - not suitable for Machine-Soul configuration management at present.
- For promising candidates, outline the likely Machine-Soul application/deployment/verification shape and any reusable strategies that would need to exist.
- Preserve expensive-to-rediscover conclusions in durable docs or `.agents/` as appropriate.
- End by proposing bounded implementation tasks only where the investigation supports them; do not implement the candidates during this task.

## Constraints / non-goals

- Do not modify application configurations or add new application integrations in this investigation.
- Do not duplicate the existing Windows Terminal integration.
- Do not broaden into Linux/macOS application discovery.
- Do not treat every registry value or AppData file as a configuration contract.
- Do not track credentials, private keys, tokens, secrets, machine-generated caches, or opaque binary state merely because it can technically be copied.
- Do not assume a file-level symlink is always the right deployment mechanism.
- Do not implement Windhawk under this task; Windhawk is tracked separately as a reminder.
- Do not implement installation takeover.

## Acceptance criteria

- A sourced Windows candidate inventory exists with explicit storage/scope/stability/security/deployment/check/verification analysis.
- WinGet, WSL, OpenSSH client, PowerToys, and Windows Sandbox are each investigated explicitly.
- Existing Windows Terminal management is recognized as baseline/current state rather than duplicated.
- The result clearly distinguishes stable user configuration from policy, secrets, generated state, and launch-profile assets.
- Each candidate receives an implementation-suitability classification with rationale.
- Any proposed follow-up implementation tasks are small enough to execute independently and identify their required reusable strategy work.
- No application configuration is mutated as part of the investigation.

## Validation

- Cross-check current repository application inventory so already-managed applications are not proposed as new.
- Verify key configuration locations/interfaces against current official/upstream documentation.
- Review candidate storage for sensitive/generated state before recommending repository tracking.
- Validate that proposed Apply/Check/Verify approaches respect the existing Machine-Soul safety and evidence contracts.
- Confirm the final task ledger/workspace/durable-memory updates are internally consistent.


## Notes

Scheduling note from `MSHP-INST-A-040`: this task remains structurally independent. The scoped installation implementation is now complete enough for this investigation to resume: Machine-Soul-controlled WinGet mutations use explicit scope, so managing WinGet client scope preferences cannot silently change managed installation scope. The investigation must still distinguish WinGet client settings from administrator settings, sources, and WinGet Configuration/DSC.
