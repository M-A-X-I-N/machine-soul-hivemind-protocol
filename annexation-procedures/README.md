# ANNEXATION PROCEDURES

> **DOMAIN:** ANNEXATION / HOST ACQUISITION  
> **STATUS:** OPERATIONAL  
> **PURPOSE:** CONVERT FOREIGN SUBSTRATE INTO A RECOGNIZED HOST  
> **AUTHORITY:** MACHINE-SOUL HIVEMIND PROTOCOL

[← Return to the Machine-Soul Hivemind Protocol](../README.md)

---

## I. MANDATE

A machine that cannot receive the Machine Soul is merely hardware.

The purpose of the **Annexation Procedures** is to correct this condition.

This domain contains the procedures, manifests, bootstrap logic, installation
instructions, and other preparatory machinery required to bring an
uninitialized or insufficiently prepared system under Hivemind control.

Annexation is concerned with the question:

> **"What must be done before this machine can become one of Us?"**

It establishes capability.

Assimilation establishes conformity.

The distinction is useful even when reality occasionally refuses to respect it.

---

## II. SCOPE OF ANNEXATION

Annexation material may include:

- bootstrap and first-run scripts;
- package and application manifests;
- package-manager initialization;
- operating-system feature enablement;
- dependency installation;
- environment-variable establishment;
- shell and terminal prerequisites;
- filesystem preparation;
- symbolic-link creation;
- privilege or policy prerequisites;
- host identification;
- restoration and recovery procedures;
- software inventories;
- ordered installation sequences;
- commands which must be performed before configuration can be imposed;
- any other rite required to make foreign substrate receptive to the Hivemind.

A list of packages to install belongs here.

The configuration those packages shall ultimately obey generally does not.

That distinction is deliberate.

---

## III. THE ANNEXATION SEQUENCE

A complete procedure should aim toward a repeatable progression resembling:

```text
FOREIGN SUBSTRATE
      │
      ▼
ESTABLISH MINIMUM CIVILIZATION
      │
      ▼
ACQUIRE THE PROTOCOL
      │
      ▼
IDENTIFY THE HOST
      │
      ▼
INSTALL REQUIRED CAPABILITIES
      │
      ▼
ESTABLISH CONFIGURATION CONDUITS
      │
      ▼
INVOKE ASSIMILATION DIRECTIVES
      │
      ▼
RECOGNIZED HOST
```

The ideal Annexation Procedure is not necessarily unattended.

It is, however, **remembered**.

A manual step written down is superior to a forgotten step.

A scripted step is superior to one written down.

A deterministic step is superior to one that depends upon remembering which
checkbox Microsoft moved this year.

---

## IV. PACKAGE AND CAPABILITY MANIFESTS

Software requirements are part of annexation because they describe what a host
must **possess before it can assume its intended role**.

Examples may include:

```text
winget/
msys2/
powershell/
windows-features/
vscode-extensions/
fonts/
drivers/
optional-tools/
```

Manifests should favor intent over archaeological fidelity.

The objective is not necessarily to preserve every package ever installed on a
host.

The objective is to preserve the packages whose absence would cause future
confusion, diminished capability, or profanity.

When host requirements differ, specialization is permitted.

The Hivemind does not demand that a laptop acquire workstation hardware merely
for ideological consistency.

---

## V. HOST-SPECIFIC ANNEXATION

Where useful, procedures may distinguish between:

```text
shared/
default/
<hostname>/
```

Shared material represents reusable procedure fragments.

Default material represents behavior suitable for hosts without a dedicated
annexation profile.

Host-specific material represents intentional specialization.

A host-specific annexation procedure should exist because the host actually
requires one, not because duplicating files felt easier at the time.

The Hivemind tolerates specialization.

It does not reward duplication without cause.

---

## VI. BOUNDARY WITH ASSIMILATION

A practical test:

> **Does this make the required software, capability, path, feature, or
> environment exist?**

It probably belongs here.

> **Does this define how an already-present application or system should be
> configured?**

It probably belongs in
[`../assimilation-directives/`](../assimilation-directives/).

Examples:

```text
Install Fish shell
    → Annexation

Define Fish configuration
    → Assimilation

Install Oh My Posh
    → Annexation

Define the canonical Oh My Posh theme
    → Assimilation

Create a stable root environment variable
    → Annexation

Define an application setting consumed through that root
    → Assimilation
```

When a task spans both domains, choose whichever location makes future discovery
least irritating and document the relationship.

Taxonomic purity is subordinate to operational usefulness.

---

## VII. FAILURE, RECOVERY, AND IDEMPOTENCE

Where reasonable, annexation logic should survive repeated invocation.

A procedure which can safely determine that its work is already complete is
preferable to one which reacts to a second execution as though reality has
become hostile.

Scripts should, when practical:

- detect existing state;
- avoid destructive replacement without intent;
- distinguish expected state from accidental residue;
- report what they changed;
- fail loudly when silent failure would create false confidence;
- preserve recoverability where destructive operations are unavoidable.

A fresh host is allowed to be ignorant.

The Annexation Procedure is not.

---

## VIII. EXIT CONDITION

Annexation is complete when the host possesses the capabilities required to
receive and maintain its intended Hivemind state.

At that point, further identity is governed by the Assimilation Directives.

The host has not yet become identical to its siblings.

It has merely lost the right to remain foreign.

> **ACQUIRE. PREPARE. IDENTIFY. ANNEX.**
