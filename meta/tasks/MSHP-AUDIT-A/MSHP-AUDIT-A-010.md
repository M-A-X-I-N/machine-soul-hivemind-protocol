# MSHP-AUDIT-A-010 — Add Linux audit command collection

## Description

Add a Linux-only Machine-Soul capability for long-lived command archaeology using the Linux Audit subsystem (`auditd`).

The purpose is durable reconstruction of **which external processes a human login session executed, with their argv**, so future operators can answer questions such as “what did I do yesterday that broke this?” or “what commands did I use years ago to configure this machine?”

The task owns the complete first collection implementation. It does **not** own a human-friendly history/query UI.

## Requirements

- Integrate the capability into the existing MSHP annexation/assimilation model rather than adding a standalone ad-hoc setup script.
- Use distro/platform-native audit tooling and existing MSHP installation/discovery/ownership mechanisms where practical.
- Keep software installation ownership separate from configuration ownership:
  - pre-existing `auditd`/audit userspace installation must not be silently claimed as Machine-Soul-owned;
  - configuration Apply/Unapply must work independently of whether MSHP installed the package;
  - package Uninstall must obey existing installation-ownership semantics.
- Add persistent audit rules for process execution:
  - capture `execve`;
  - capture `execveat` where supported;
  - handle relevant supported syscall architectures correctly rather than assuming one syscall table;
  - tag Machine-Soul command-history events with a stable audit key.
- Scope collection to attributable human login sessions using audit login UID (`auid`) semantics:
  - derive the normal-user threshold from the target machine's actual `UID_MIN` (for example from `/etc/login.defs`) rather than hard-coding 1000;
  - exclude unset loginuid values;
  - preserve the original login identity through privilege escalation.
- Support the intended privilege-escalation case:
  - commands run through ordinary `sudo` must remain attributable to the original login user;
  - commands run after `sudo -i` / an equivalent root shell must remain attributable to the original login user through `auid`, while normal effective/root identity fields still reflect root execution;
  - do not configure `pam_loginuid` on `sudo` or `su` in a way that rewrites the original loginuid.
- Preserve full process argv in the raw audit record. Do not perform collection-time secret redaction.
- Treat audit logs as sensitive root-controlled system data.
- Configure retention/rotation suitable for the stated archaeology goal:
  - avoid a tiny/default retention window that defeats multi-year reconstruction;
  - avoid unbounded active-log growth that can fill the system volume;
  - prefer native audit/log-rotation mechanisms over bespoke archival machinery where they are sufficient.
- Keep Machine-Soul-owned audit configuration narrow and reversible:
  - preserve unrelated existing audit rules/configuration;
  - Unapply must remove only Machine-Soul-managed command-collection configuration and restore/preserve displaced state according to normal MSHP safety rules;
  - reloading/reapplying rules must be deterministic and idempotent where practical.
- Add meaningful Check/Verify behavior that can distinguish at least:
  - audit tooling unavailable/not installed;
  - tooling installed but Machine-Soul collection not applied;
  - collection applied and effective;
  - conflicting or partially effective state.

## Constraints / non-goals

- Linux only for this task.
- Do not build the future pretty viewer / `wtfidid`-style query tool.
- Do not add shell-history integration.
- Do not add TTY/session recording or `tlog`.
- Do not attempt to capture shell builtins that do not result in process execution.
- Do not record editor/file contents, diffs, keystrokes, or command output merely for archaeology.
- Do not add collection-time argv redaction; the operator already treats visible command-line arguments as loggable/sensitive.
- Do not broaden this into a complete host security-auditing policy, remote SIEM pipeline, or generic audit-rule framework.
- Do not filter away subprocess/build noise in the collection layer merely to make future viewing prettier; raw collection should favor completeness, with presentation filtering deferred to a later feature.

## Acceptance criteria

- A supported Linux host can install/detect the required audit tooling through MSHP's normal lifecycle mechanisms.
- Applying the capability installs persistent Machine-Soul-owned audit configuration without destroying unrelated audit policy.
- After rule reload/reboot, an external command run by a normal human login session produces an audit event containing its executable/argv and the expected stable Machine-Soul audit key.
- A command run via `sudo` is recorded with the original human login's `auid` while reflecting privileged execution in the normal UID/effective-UID fields.
- A command run from a `sudo -i` root shell is likewise recorded with the original human login's `auid`.
- The normal-user filter is derived from the target system's configured UID boundary rather than a hard-coded numeric assumption.
- Rotation/retention is explicitly configured for long-term archaeology without intentionally allowing uncontrolled active-log growth.
- Apply/Check/Verify/Unapply are repeatable and preserve unrelated audit configuration.
- No pretty-query UI, shell recorder, or redaction subsystem is introduced by this task.

## Validation

- Validate on at least one supported Linux host with a real login session whose `auid` is set.
- Run a controlled normal-user command with a recognizable harmless argv and verify it appears under the Machine-Soul audit key.
- Run a controlled `sudo <command>` and verify:
  - the event is captured;
  - `auid` remains the original login user;
  - privileged identity fields reflect root/elevated execution.
- Enter a controlled `sudo -i` shell, run a harmless external command, and verify the same original-`auid` behavior.
- Verify rules survive the intended persistent rule reload/reboot path.
- Verify Unapply removes only Machine-Soul-owned audit collection configuration and leaves unrelated audit state intact.
- Verify Check/Verify reports meaningful effective-state distinctions before and after Apply/Unapply.
- Inspect retention/rotation configuration and demonstrate that it is materially longer-lived than a short default window while remaining bounded/managed.
