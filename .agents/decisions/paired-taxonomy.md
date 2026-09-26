# Paired configuration / operation taxonomy

## Decision

Machine-Soul intentionally separates application configuration content from the machinery that applies or installs it.

The paired trees are:

```text
assimilation-directives/<application>/...
    canonical tracked configuration content

annexation-procedures/<application>/...
    Apply / Unapply / Check / Install / Uninstall entry points
```

The matching application name is the relationship between the two trees.

Do not reintroduce per-application `config/` or `operations/` wrapper directories beneath these roots. The root names already provide those semantics.

## Shared deployment machinery

Cross-application symlink, backup, state, dispatch, and path-translation code lives under:

```text
accumulated-instruments/configuration-deployment/
```

The name is deliberately specific.

`accumulated-instruments/` is a general-purpose repository area for reusable system-management tools. Future tooling unrelated to configuration deployment—such as a Windows font-registry manager—may live beside `configuration-deployment/` rather than inside it.

## Historical note

The first v2 baseline temporarily used:

```text
assimilation-directives/<application>/config/
assimilation-directives/<application>/operations/
accumulated-instruments/framework/
```

Those paths are obsolete after post-baseline tasks V2-41/V2-42. They should appear only in historical discussion or migration context, not in active runtime paths.
