# MSHP-HOUSEKEEPING-A-050 — Audit agent memory and instruction hygiene

## Description

Perform a cautious one-time audit of agent-facing memory, instructions, and context surfaces for stale/duplicated/contradictory content and unnecessary context burden, even though a formal recurring memory-hygiene workflow has not yet been designed.

## Requirements

- Audit root AGENTS.md, all tracked files under .agents/, lifecycle instructions governing tasks/initiatives/reminders, agent-facing navigation/read-order guidance, authority statements, recovery/lineage/CI/provenance instructions, and durable agent memories whose continued context cost may exceed their value.
- Look for stale assumptions, superseded instructions, duplicated authority, contradictions, circular/misleading source-of-truth claims, dead links, stranded temporary knowledge, clearly obsolete permanent memory, unnecessary mandatory-reading load, and poor discoverability.
- Merge, update, or prune only when the conclusion is high confidence.
- When relevance or historical value is uncertain, retain the material and record the concern rather than deleting it.
- Preserve expensive-to-rediscover knowledge.
- Record audit findings and deferred uncertain items in the HOUSEKEEPING-A workspace.
- Keep the Agent-facing repository memory hygiene reminder unless this task actually designs and establishes the recurring process described by that reminder.

## Constraints / non-goals

- This is a one-time best-effort audit, not authorization to invent the future recurring audit process.
- Do not delete uncertain memory merely to reduce file count or token load.
- Do not treat shorter context as inherently better than useful context.
- Do not remove historically useful scar tissue without a clear surviving home.
- Do not override human-authored policy intent based only on agent preference.

## Acceptance criteria

- All current agent instruction/memory surfaces have been deliberately reviewed.
- High-confidence stale/duplicated/contradictory content is corrected.
- Context/read-order burden is reduced where safely justified.
- Uncertain cleanup candidates are retained and documented.
- No important durable knowledge is knowingly discarded.

## Validation

- Re-read fresh-session reading order from scratch and follow it as a simulated new agent.
- Cross-check authority statements across AGENTS.md, .agents/, and autonomic governance docs.
- Search for references to files/paths removed or archived during HOUSEKEEPING-A.
