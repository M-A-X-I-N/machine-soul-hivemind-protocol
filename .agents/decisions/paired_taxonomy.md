# Assimilation / annexation taxonomy

## Decision

Machine-Soul intentionally separates **desired behavioral content** from the **operational machinery that changes a machine**.

The names are intentionally asymmetric:

- **assimilation** = instructions describing how the machine should behave as part of the collective;
- **annexation** = procedures that take over / prepare / manage the machine so those desired capabilities exist.

The trees are:

```text
assimilation_directives/<subject>/...
    canonical tracked desired configuration / behavioral content

annexation_procedures/<subject>/...
    executable lifecycle/discovery/configuration/installation machinery
```

When the same subject exists in both trees, the matching subject name relates its behavioral content to its operational machinery.

**The trees are not required to be one-to-one.** Annexation support does not require assimilation directives. An install-only/runtime/version-management subject may live entirely under `annexation_procedures/`. Conversely, tracked assimilation directives do not imply that Machine-Soul owns or performs installation.

Do not create fake configuration content merely to make an annexation subject appear "complete".

Do not reintroduce per-subject `config/` or `operations/` wrapper directories beneath these roots. The root names already provide those semantics.

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
