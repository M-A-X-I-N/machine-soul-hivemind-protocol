# ASSIMILATION DIRECTIVES

> **DOMAIN:** ASSIMILATION / CANONICAL STATE  
> **STATUS:** AUTHORITATIVE  
> **PURPOSE:** DEFINE WHAT A RECOGNIZED HOST SHALL BECOME  
> **AUTHORITY:** MACHINE-SOUL HIVEMIND PROTOCOL

[← Return to the Machine-Soul Hivemind Protocol](../README.md)

---

## I. MANDATE

Annexation brings a machine within reach of the Hivemind.

**Assimilation makes it familiar.**

The Assimilation Directives contain the canonical configuration and desired
state imposed upon recognized hosts.

This domain answers:

> **"Given that this machine is now Ours, how should it behave?"**

Shells, prompts, terminals, editors, applications, environment settings,
operating-system preferences, and other persistent decisions belong here when
their purpose is to define the intended state of a host.

Defaults are temporary.

Doctrine is persistent.

---

## II. CANONICAL STATE

The contents of this domain should describe **intent**, not merely historical
accident.

A file belongs here because the Hivemind wants it to exist in that form.

Not because it happened to exist that way once.

Assimilation material may include:

- shell profiles;
- application configuration;
- terminal settings;
- prompt themes;
- editor configuration;
- environment configuration;
- exported settings suitable for restoration;
- host-specific overrides;
- reusable configuration fragments;
- operating-system preferences;
- application state which is both portable and intentionally preserved;
- any other material that defines expected host behavior.

The distinction between *what is* and *what should be* is sacred.

This directory concerns the latter.

---

## III. SHARED, DEFAULT, AND HOST-SPECIFIC DOCTRINE

Where a component requires host-aware configuration, the preferred conceptual
model is:

```text
<component>/
├── shared/
│   └── Reusable fragments and common foundations.
│
├── default/
│   └── Complete fallback manifestation.
│
└── <hostname>/
    └── Complete host-specific manifestation or sanctioned override.
```

`shared/` is **not** normally an entry point.

It is reusable memory.

`default/` is the fallback manifestation used when no host-specific doctrine
exists.

`<hostname>/` contains intentional state for a recognized host whose needs
differ from the default.

Thus a host named `spaceship` may receive:

```text
<component>/spaceship/
```

while an unknown or unspecialized host receives:

```text
<component>/default/
```

The Machine Soul is singular.

Its hosts are permitted different organs.

---

## IV. SYMBOLIC CONDUITS

Where practical, the live configuration consumed by software should remain
directly connected to canonical Hivemind state.

Symbolic links, junctions, or equivalent mechanisms may be used so that:

```text
APPLICATION CONFIG PATH
         │
         │ symbolic conduit
         ▼
ASSIMILATION DIRECTIVE
         │
         ▼
GIT WORKING TREE
```

This arrangement is preferred because useful mutations performed through the
ordinary application path immediately occur within the repository itself.

The alternative ritual—

```text
change setting
forget about repository
discover discrepancy six months later
swear
copy file manually
```

—is not considered a reliable synchronization protocol.

The Host changes.

The Soul remembers.

---

## V. INTENTIONAL VARIATION

Assimilation does not mean universal byte-for-byte sameness.

Hosts differ.

A workstation may need software, paths, visual settings, or performance
characteristics inappropriate for a laptop.

Such differences are valid when they are **intentional and represented in
doctrine**.

The Hivemind distinguishes:

```text
specialization
    → sanctioned difference

configuration drift
    → accidental difference
```

The former serves purpose.

The latter accumulates entropy.

When a local difference becomes useful, either generalize it into shared or
default doctrine or record it explicitly as host-specific state.

---

## VI. BOUNDARY WITH ANNEXATION

A practical distinction:

> **Does this make a capability or application exist?**

See [`../annexation-procedures/`](../annexation-procedures/).

> **Does this specify how that capability or application should behave once it
> exists?**

It belongs here.

Examples:

```text
Install PowerShell module
    → Annexation

Configure PowerShell profile
    → Assimilation

Install terminal
    → Annexation

Configure terminal appearance and behavior
    → Assimilation

Install browser extension
    → Annexation

Preserve extension configuration
    → Assimilation
```

Reality will occasionally produce edge cases.

Classify them according to future usefulness, not metaphysical panic.

---

## VII. CONFIGURATION DRIFT

Drift is inevitable whenever a host remains alive long enough to encounter:

- software updates;
- manual intervention;
- changing requirements;
- installers with opinions;
- defaults silently returning from the dead;
- undocumented behavior;
- operating-system upgrades;
- Microsoft.

Useful drift should be examined and, where appropriate, absorbed into doctrine.

Unworthy drift should be removed.

Undocumented drift is merely future confusion accruing interest.

---

## VIII. AUTHORITY

Material within this domain should be treated as active desired state.

Unlike the Abandoned Artifacts, it is not merely historical.

Unlike Arcane Experiments, it is not awaiting judgment.

Unlike Acquired Intelligence, it does not merely explain.

It **directs**.

> **THE HOST MAY DIFFER ONLY WHERE THE HIVEMIND HAS DECIDED THAT IT SHOULD.**
