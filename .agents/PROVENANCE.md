# Agent authorship provenance

This file is the canonical policy for `Agent-authored-by:` commit trailers in this repository.

The purpose is durable authorship provenance across agent products, surfaces, and model revisions without pretending that a product name and a stable project-local identity are the same thing.

## Concepts

### Agent variant

An **agent variant** is the product/surface identity to which a stable designation belongs. A model upgrade does not by itself create a new stable designation.

Current registry:

| Agent variant | Stable designation |
|---|---|
| OpenAI ChatGPT Chat | `Gippity` |
| OpenAI ChatGPT Work | `UNNAMED` |
| OpenAI Codex | `UNNAMED` |

Assigned stable designations must be unique across agent variants.

`UNNAMED` is a visible sentinel, not a real assigned designation.

### Stable designation

The stable designation is the short project-local identity that remains recognizable across model revisions of the same agent variant.

For example, ChatGPT Chat is currently `Gippity`.

### Official identity

The **official identity** is written fresh by the authoring agent for each commit and appears last in parentheses.

It should be as accurate and specific as the agent can truthfully determine, at roughly this level:

```text
<organization> <product/surface>, <model when meaningfully known>
```

For the ChatGPT Chat agent authoring this policy, an accurate identity is:

```text
OpenAI ChatGPT Chat, GPT-5.6 Sol
```

Official identity is deliberately **not** frozen in the registry. Models and runtime details change.

Never invent model, product, organization, or runtime details that the agent cannot actually know. Omit unknown details rather than guessing.

## Trailer grammar

Every wholly agent-authored substantive commit uses one `Agent-authored-by:` trailer.

For a named agent:

```text
Agent-authored-by: <optional prefix honorific><stable designation><optional suffix honorific> (<official identity>)
```

Punctuation and natural-language spacing around optional honorifics may vary as long as the stable designation and final parenthesized official identity remain unambiguous.

Examples:

```text
Agent-authored-by: Gippity (OpenAI ChatGPT Chat, GPT-5.6 Sol)
Agent-authored-by: Minister Gippity (OpenAI ChatGPT Chat, GPT-5.6 Sol)
Agent-authored-by: Gippity, Keeper of the Boring Interpreter (OpenAI ChatGPT Chat, GPT-5.6 Sol)
Agent-authored-by: His Excellency Gippity, Destroyer of Kebab Case (OpenAI ChatGPT Chat, GPT-5.6 Sol)
```

Honorific material is:

- optional but encouraged;
- allowed before and/or after the stable designation;
- allowed to be funny, serious, grandiose, mundane, or otherwise arbitrary;
- not required to be a literal title;
- forbidden from containing a slur unless the human explicitly authorizes that use.

Normally keep the provenance trailer on one physical line. The complete trailer may use at most two physical lines when genuinely necessary for readability.

## Unnamed or unregistered agents

An agent variant is treated as unnamed when it is absent from the registry or its registry entry is `UNNAMED`.

An unnamed agent:

1. uses exactly the visible stable-designation sentinel `UNNAMED`;
2. does **not** invent its own stable designation;
3. does **not** use any honorific prefix or suffix;
4. supplies the most accurate official identity it can truthfully determine;
5. writes exactly this semantic form:

   ```text
   Agent-authored-by: UNNAMED (<official identity>)
   ```

6. promptly notifies the human that its agent variant has no stable designation;
7. if it can ask for input without losing/restarting active work, asks the human to assign a designation;
8. once a designation is assigned, updates this registry for future commits.

Already-created commits are not rewritten merely to retrofit a subsequently assigned designation. Any such history rewrite requires separate explicit authorization.

The `UNNAMED` restriction intentionally forbids honorifics so unnamed provenance remains visually conspicuous.

## Scope

This trailer is required when the agent wholly authors the substantive commit.

Human-authored or genuinely mixed-authorship work may require different provenance treatment when such a convention is later defined; do not falsely label a human-authored substantive change as wholly agent-authored.

Commit summary format remains:

```text
[Kind][Scope] Imperative summary
```

with the kinds defined in `AGENTS.md`.
