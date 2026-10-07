# Assimilation / annexation taxonomy

## Decision

Machine-Soul intentionally separates **desired behavioral content** from the **operational machinery that changes a machine**.

The names are intentionally asymmetric:

- **assimilation** = instructions describing how the machine should behave as part of the collective;
- **annexation** = procedures that take over / prepare / manage the machine so those desired capabilities exist.

The trees are:

```text
assimilation/<subject>/...
    canonical tracked desired configuration / behavioral content

annexation/<subject>/...
    executable lifecycle/discovery/configuration/installation machinery
```

When the same subject exists in both trees, the matching subject name relates its behavioral content to its operational machinery.

**The trees are not required to be one-to-one.** Annexation support does not require assimilation directives. An install-only/runtime/version-management subject may live entirely under `annexation/`. Conversely, tracked assimilation directives do not imply that Machine-Soul owns or performs installation.

Do not create fake configuration content merely to make an annexation subject appear "complete".

## Runtime/version-management investigation default

When investigating runtimes, interpreted languages, engines, or version managers, treat **multi-version coexistence as a desirable capability to preserve when reasonably possible**, even if the maintainer may ultimately use only one version.

Do not assume the answer is to implement multi-version machinery inside Machine-Soul. The investigation should first determine the sane current ecosystem solution:

- native side-by-side installations;
- an upstream/reputable version manager;
- package-manager-managed versions;
- explicit executable/path selection;
- or, only when justified, new reusable Machine-Soul version-management machinery.

Lua on Windows is an intentionally useful adversarial example, but the same investigation mindset applies to Python, Node.js, and future runtime/version-manager subjects.

The purpose is to avoid prematurely choosing a convenient single-version installation path that makes later coexistence unnecessarily difficult.

Do not reintroduce per-subject `config/` or `operations/` wrapper directories beneath these roots. The root names already provide those semantics.

## Shared operation machinery

Cross-application discovery, configuration resolution, symlink/backup/state policy, operation dispatch, installation strategies, native-protocol support, and orchestration live in the shared Python package:

```text
annexation/
```

`tools/` is the general-purpose tracked toolbox for useful programs/scripts that are not intrinsically part of the assimilation/annexation system. The Machine-Soul runtime itself does not live there.

The former `tools/configuration_deployment/` Bash/PowerShell runtime was transitional and was retired after Python parity.

## Historical note

The first v2 baseline temporarily used:

```text
assimilation/<application>/config/
assimilation/<application>/operations/
tools/framework/
```

Those paths are obsolete after post-baseline tasks V2-41/V2-42. They should appear only in historical discussion or migration context, not in active runtime paths.
