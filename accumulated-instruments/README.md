# ACCUMULATED INSTRUMENTS

> **DOMAIN:** INSTRUMENTS / RETAINED CAPABILITY  
> **STATUS:** OPERATIONAL  
> **PURPOSE:** PRESERVE USEFUL IMPLEMENTS TOO SMALL, STRANGE, OR PERSONAL FOR INDEPENDENT EXISTENCE  
> **AUTHORITY:** MACHINE-SOUL HIVEMIND PROTOCOL

[← Return to the Machine-Soul Hivemind Protocol](../README.md)

---

## I. MANDATE

Not every useful program deserves its own repository.

Some scripts exist because a single registry key behaved offensively.

Some utilities exist because an operating system exposed five interfaces for a
setting and honored the sixth.

Some programs were written to answer a question which should never have
required code.

They shall nevertheless be preserved.

The **Accumulated Instruments** are the retained implements of the Machine Soul:
small programs, scripts, probes, converters, repair tools, automation, and other
reusable machinery whose loss would eventually require the same problem to be
solved again.

That outcome is forbidden by good taste and prior suffering.

---

## II. ADMISSION CRITERIA

An instrument belongs here when it is primarily something that **does** rather
than something that **describes** or **configures**.

Typical examples include:

- PowerShell utilities;
- registry mutation tools;
- diagnostic probes;
- migration scripts;
- filesystem manipulation tools;
- format converters;
- tiny command-line programs;
- maintenance utilities;
- repeatable repair procedures;
- automation helpers;
- source code for one-purpose tools;
- scripts produced during an investigation which proved generally useful.

An instrument need not be elegant.

It need not be publishable.

It need not survive peer review.

It need only satisfy a simpler requirement:

> **Recreating this later would be more annoying than preserving it now.**

---

## III. INSTRUMENT VERSUS PROCEDURE

The boundary with
[`../annexation-procedures/`](../annexation-procedures/)
is defined by intent.

If a script exists specifically to acquire or initialize a host as part of the
Hivemind, it is an Annexation Procedure.

If the script is a generally reusable implement which may be invoked during
annexation, experimentation, repair, or ordinary operation, it is an
Accumulated Instrument.

For example:

```text
setup-host.ps1
    → annexation-procedures/

registry-config-tool.ps1
    → accumulated-instruments/

install-fonts.ps1
    → perhaps annexation-procedures/

inspect-caption-font.ps1
    → accumulated-instruments/
```

The same instrument may be *used by* an Annexation Procedure without becoming
one.

A hammer does not become architecture because a house depends upon it.

---

## IV. INSTRUMENT VERSUS INTELLIGENCE

If the important part is the executable capability, preserve the tool here.

If the important part is the knowledge gained, preserve that knowledge under
[`../acquired-intelligence/`](../acquired-intelligence/).

Often both are justified.

An experiment may produce:

```text
accumulated-instruments/
└── dwm-font-diagnostic/

acquired-intelligence/
└── windows/
    └── dwm-caption-font-behavior.md
```

The tool answers the question again.

The intelligence prevents the Hivemind from forgetting the answer.

---

## V. INTERNAL EXPECTATIONS

Where reasonable, an instrument should carry enough local context that its
future operator does not need to reconstruct the circumstances of its birth
from commit archaeology.

Useful additions may include:

- a local `README.md`;
- usage examples;
- assumptions and prerequisites;
- required privilege level;
- platform limitations;
- known hazards;
- source references;
- comments explaining non-obvious decisions;
- an explicit warning when the tool is intentionally cursed.

The threshold should remain proportional.

A twelve-line helper does not require a constitution.

A registry mutation framework probably deserves more than a filename.

---

## VI. ORGANIZATION

No single structure is mandated.

Reasonable organization may emerge by:

```text
platform/
purpose/
language/
tool-name/
```

or some mixture thereof.

Prefer discoverability over taxonomic perfection.

If a future version of the Hivemind can answer:

> "Didn't I already make something for this?"

and find the answer quickly, the structure is functioning.

---

## VII. LIFECYCLE

Many instruments begin life within
[`../arcane-experiments/`](../arcane-experiments/).

Once an experiment produces a stable, reusable capability, it may be promoted
here.

If an instrument becomes obsolete but remains historically or practically
interesting, it may be transferred to
[`../abandoned-artifacts/`](../abandoned-artifacts/).

If it grows into a substantial independent project with its own lifecycle,
dependencies, users, or dignity, it may eventually earn exile into a repository
of its own.

Until then, the Hivemind provides shelter.

---

## VIII. FINAL DIRECTIVE

Automation too useful to delete and too stupid to publish is still automation.

A tool need not be important.

It need only be annoying enough to recreate.

> **FORGE ONCE. PRESERVE INDEFINITELY. SWEAR LESS NEXT TIME.**
