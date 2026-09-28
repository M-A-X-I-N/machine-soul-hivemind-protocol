# Agent authorship provenance

This file is the canonical policy for agent provenance commit trailers in this repository.

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

`Agent-authored-by:` is required when the agent wholly authors the substantive commit regardless of the Git Author identity used to create the commit.

The Git Author field and the provenance trailer answer different questions:

- Git Author identifies the account/identity recorded by Git.
- `Agent-authored-by:` identifies the agent variant substantively responsible for producing the change.

An agent, bot, automation, or service Git author therefore does not replace or weaken the normal `Agent-authored-by:` requirement.

Human-authored or genuinely mixed-authorship work may require different provenance treatment when such a convention is later defined; do not falsely label a human-authored substantive change as wholly agent-authored.

## Human operator provenance

When the Git Author identity does not itself identify the accountable human operator, a wholly agent-authored substantive commit must additionally include:

```text
Agent-operated-by: <accountable human operator identity>
```

This trailer records human operational accountability. It does not claim code review, approval, or technical authorship.

It means the named human directed or operated the agent run and is accountable for allowing the agent-authored commit to enter this repository.

Do not rename this concept to `Reviewed-by:`, `Approved-by:`, or similar unless a separate real review/approval convention is later defined. Ordinary prompting, supervision, skimming, or saying "go next" is not formal review.

### When the trailer is required

Require `Agent-operated-by:` when all of these are true:

1. the substantive commit is agent-authored and therefore already requires `Agent-authored-by:`;
2. the Git Author identity is non-human or otherwise fails to identify the accountable human operator;
3. an accountable human operator is truthfully known.

Do not add the trailer redundantly when the Git Author identity already identifies the accountable human.

If the Git Author is non-human and the accountable human operator cannot be truthfully determined, do not invent one. Resolve that provenance ambiguity before creating the substantive commit when practical.

The Git Committer field, hosting-service actor, or automation account does not substitute for this accountable-human information when the Author identity is non-human.

### Grammar

Use:

```text
Agent-operated-by: <human identity>
```

The value may include harmless project-local humor, but the human identity must remain unambiguous.

Example with non-human Git Author:

```text
Author: agent-service-account

Agent-authored-by: Gippity, Keeper of the Build (OpenAI ChatGPT Chat, GPT-5.6 Sol)
Agent-operated-by: Human Maintainer
```

Example when Git Author already identifies the human:

```text
Author: Human Maintainer

Agent-authored-by: Gippity, Keeper of the Build (OpenAI ChatGPT Chat, GPT-5.6 Sol)
```

No `Agent-operated-by:` trailer is required in the second case merely because an agent produced the substantive change.

Commit summary format remains:

```text
[Kind][Scope] Imperative summary
```

with the kinds defined in `AGENTS.md`.
