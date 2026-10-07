# Declarative application model

## Purpose

An application definition describes **what Machine-Soul knows about an application**. It does not perform operations.

Every application will eventually have:

```text
annexation/<application>/_application.py
```

That module exposes one declaration constant:

```python
APPLICATION = Application(...)
```

Importing the module is meaningful. Executing it directly performs no action and has no side effects.

## Core value objects

The shared model lives under `annexation.model`.

The initial schema provides:

- `Application` — repository identity, display name, and platform declarations;
- `PlatformDeclaration` — capabilities/config/install strategy for one platform;
- `ConfigurationFile` — one canonical source leaf plus a destination strategy;
- `Platform` — current platform identities;
- `Operation` — atomic operation names;
- `Support` — supported / unsupported / not implemented;
- strategy value objects such as `AptPackage`, `WingetPackage`, `RemoteInstallScript`, and `HomeRelativeDestination`.

These are declarations/value objects only. Engines that interpret them land in later tasks.

## Capability declarations

Missing capability entries mean `UNSUPPORTED`; desired-but-unfinished behavior is explicitly `NOT_IMPLEMENTED`.

A declaration cannot claim installation is supported without selecting an installation strategy.

This keeps the capability contract inspectable without looking for wrapper-file existence.

## Configuration declarations

A `ConfigurationFile` names one canonical leaf such as `config.fish`.

Host/account precedence remains shared configuration-resolution policy. An application declaration does not encode a particular host path such as `hosts/<hostname>/...`.

Destination selection is represented by reusable destination strategies. The first generic strategy is `HomeRelativeDestination`, which resolves relative to the **logical target account** established by the account-targeting contract.

Applications with genuinely unusual native state may later select specialized reusable configuration strategies or a documented custom hook.

## Installation strategies

Declarations select high-level reusable strategies.

Initial value types intentionally include examples required by the architecture:

- `WingetPackage`;
- `AptPackage`;
- `RemoteInstallScript`;
- `StandaloneBinary`;
- `CustomInstaller` escape hatch.

A strategy object is not an imperative sequence of steps.

Do **not** grow this into a DSL containing arbitrary `Download`, `If`, `Copy`, `Execute`, etc. If a workflow is genuinely procedural and non-reusable, use normal Python through the custom escape hatch.

## Extension rule

When an application seems to require custom code:

1. check whether an existing generic strategy already represents the behavior;
2. if the behavior is reusable, add a shared strategy;
3. only then add application-specific custom Python.

Shared engines must not accumulate `if application.id == ...` branches as a substitute for proper strategy types.

## Repository naming

Application declaration IDs are repository-owned identifiers and therefore use `lower_snake_case`, for example `oh_my_posh` and `windows_terminal`.

External identifiers stay external: the executable can still be `oh-my-posh` and a WinGet package ID remains unchanged.

## Immutability and side effects

Declarations are immutable dataclasses from the caller's perspective and must be safe to import during discovery/testing.

No declaration module may:

- install packages;
- create files/directories;
- inspect or mutate deployment state;
- prompt;
- elevate;
- execute native tools merely because it was imported.
