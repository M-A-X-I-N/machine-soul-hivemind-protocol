# Paired configuration / operation taxonomy

## Decision

Machine-Soul intentionally separates application configuration content from the machinery that applies or installs it.

The paired trees are:

```text
assimilation_directives/<application>/...
    canonical tracked configuration content

annexation_procedures/<application>/...
    Apply / Unapply / Check / Install / Uninstall entry points
```

The matching application name is the relationship between the two trees.

Do not reintroduce per-application `config/` or `operations/` wrapper directories beneath these roots. The root names already provide those semantics.

## Shared operation machinery

Cross-application discovery, configuration resolution, symlink/backup/state policy, operation dispatch, installation strategies, native-protocol support, and orchestration live in the shared Python package:

```text
annexation_procedures/
```

`accumulated_instruments/` is the general-purpose tracked toolbox for useful programs/scripts that are not intrinsically part of the assimilation/annexation system. The Machine-Soul runtime itself does not live there.

The former `accumulated_instruments/configuration_deployment/` Bash/PowerShell runtime was transitional and was retired after Python parity.

## Historical note

The first v2 baseline temporarily used:

```text
assimilation_directives/<application>/config/
assimilation_directives/<application>/operations/
accumulated_instruments/framework/
```

Those paths are obsolete after post-baseline tasks V2-41/V2-42. They should appear only in historical discussion or migration context, not in active runtime paths.
