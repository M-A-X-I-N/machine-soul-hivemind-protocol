# Documentation identity and abstraction style

Durable documentation should explain the project without unnecessarily publishing or coupling itself to the maintainer's concrete machine/account identities.

## Generic by default

In human-facing documentation and durable agent-facing guidance, describe environmental identities by role unless the concrete value is materially necessary to the fact being documented.

Prefer forms such as:

```text
<linux_host>
<windows_host>
<remote_host>
<target_account>
<normal_account>
<privileged_account>
<home>
```

or equivalent clear prose such as "the Windows host variant" or "the target account".

This applies especially to architecture explanations, examples, support descriptions, session-boundary examples, and historical task prose whose point does not depend on the real hostname/account string.

## When concrete identities belong

Concrete identities are appropriate when they are genuinely the subject or required implementation data, including:

- tracked host-specific configuration paths that must select a real machine variant;
- runtime and test fixtures exercising a concrete identity;
- persisted state formats or exact values whose correctness depends on the identity;
- investigation/decision records documenting the existence or removal of specifically named files/machines;
- exact external commands or identifiers when genericizing them would make the instruction false or unusable.

Do not contort implementation data merely to make a documentation example generic.

## Historical scope

Do not rewrite Git history merely to remove old concrete examples.

Tracked legacy task prose may be updated when machine/account names were incidental examples, but established task IDs and substantive historical meaning remain unchanged.

## Clarity

Generic wording is not an excuse for vagueness. Documentation must still make host selection, account targeting, configuration precedence, SSH/sudo process boundaries, and platform behavior precise.
