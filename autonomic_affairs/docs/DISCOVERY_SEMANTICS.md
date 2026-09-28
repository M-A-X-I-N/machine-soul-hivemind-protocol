# Discovery and verification semantics

Machine-Soul distinguishes three independent questions that happen to be related to application state.

## 1. Installation discovery

Installation discovery asks:

> Does an application installation appear to exist, and what can Machine-Soul learn about each candidate installation?

It is not a boolean package-manager check.

A useful installation assessment may contain multiple candidates and facts such as:

- mechanism/provider (WinGet, apt, MSI, Store/package registration, manual/portable, upstream installer, unknown);
- package/product identity;
- executable/path evidence;
- version;
- user/system scope;
- registration/uninstall identity;
- whether a candidate matches the application's preferred declared install strategy;
- whether Machine-Soul has matching ownership/provenance state;
- confidence/evidence behind each claim.

Preferred mechanism and Machine-Soul ownership are **orthogonal**. An installation may use the preferred mechanism but predate Machine-Soul, or Machine-Soul may later support another explicitly managed mechanism.

The semantic installation-presence conclusion must permit at least:

- `present` — sufficient evidence identifies one or more installations;
- `absent` — the available authoritative mechanisms support a meaningful absence conclusion;
- `ambiguous` — evidence identifies multiple/conflicting candidates such that no single installation identity can safely be assumed;
- `unknown` — discovery could not establish presence or absence with adequate evidence.

Candidate details must remain available even when the conclusion is ambiguous.

## 2. Applied configuration

Applied-configuration checking asks only:

> Does the expected Machine-Soul deployment structurally exist at the declared native destination, and is its ownership/state relationship coherent?

For the normal file-link lifecycle this includes the tracked source, destination, actual filesystem object/link target, and relevant Machine-Soul deployment metadata.

Application-specific structural coupling may widen the structural state. CMD, for example, includes the expected AutoRun integration as part of its applied configuration.

Structural checking does **not** prove:

- that the application is installed;
- that the application will read the destination;
- that a running process has reloaded the configuration;
- that settings from the configuration are effective.

`check_config` remains the atomic operation for this question.

## 3. Effective configuration verification

Effective verification asks:

> What evidence exists that the application actually selects/consumes the intended configuration, and how strong is that evidence?

This is semantically different enough to warrant a distinct future atomic operation: **`verify_config`**.

Applications may support different evidence strengths. Verification must report the strongest evidence actually obtained rather than pretending all checks are equivalent.

### Evidence strength

Use an ordered vocabulary whose names may be refined during implementation but whose meanings remain distinct:

1. **runtime** — controlled execution/inspection demonstrates behavior caused by or traceable to the intended configuration;
2. **application** — an application-native effective/resolved-config/origin interface identifies the intended config or resulting settings without relying solely on Machine-Soul path convention;
3. **resolution** — deterministic application resolution rules plus observable environment/path facts establish that the application should select the intended file;
4. **convention** — only conventional/documented placement supports the conclusion; useful evidence but not proof of actual consumption;
5. **none** — no meaningful verification evidence is available.

Evidence strength describes *how the conclusion was established*, not whether the conclusion is positive.

An effective-config assessment therefore needs a semantic conclusion such as:

- `effective`;
- `not_effective`;
- `indeterminate`.

Operation capability remains separate: a platform/application may report the `verify_config` operation itself as unsupported or not implemented.

## 4. Facts, assessments, and operation results

Keep three layers distinct.

### Raw observations

Discovery/probe code produces factual observations: command output, package-registration records, resolved paths, link classification, application-native origin data, runtime probe results, etc.

Observations should identify their source/mechanism and avoid policy conclusions such as "preferred" or "managed" unless those facts are inherent to the source.

### Semantic assessments

Shared discovery/verification code combines observations with declarative application policy to form typed semantic assessments.

Examples include:

- installation candidates plus a presence conclusion;
- whether an installation candidate matches the preferred declared strategy;
- whether recorded Machine-Soul provenance matches that candidate;
- effective-config conclusion plus evidence strength and supporting observations.

These should be ordinary Python value objects and remain usable independently of CLI/process presentation.

### `OperationResult`

Atomic operations convert an assessment into the existing common `OperationResult` contract.

`OperationResult.status` remains a coarse operation outcome category. Stable result codes identify semantic state, while structured `data` carries serializable assessment details/evidence.

Do not encode every discovery dimension into one giant result-code enum. For example, "preferred mechanism" and "Machine-Soul managed" are separate fields, not one combinatorial status such as `preferred_managed_installed`.

## 5. Extension boundary

Prefer shared discovery strategies keyed by capability/mechanism rather than application identity.

The expected order is:

1. generic platform/mechanism discovery strategy;
2. declarative application hints/identities consumed by that strategy;
3. new reusable strategy when several applications share a need;
4. narrow application-specific probe only when behavior is genuinely unique.

Generic engines must not branch on `application.id`.

Application-specific verification hooks may use ordinary Python behind the same assessment contract. Do not create an arbitrary declarative step language.

## 6. Relationship between the three questions

No one question implies another.

Examples:

| Installation | Applied config | Effective config | Valid interpretation |
|---|---|---|---|
| preferred, unmanaged | applied | effective | Existing installation uses Machine-Soul config without installation ownership. |
| foreign | applied | effective | Installation method is non-preferred, but configuration works. |
| present | applied | not effective | Deployment exists but the application selected/loaded something else. |
| absent | applied | indeterminate | Config may be staged for a future install; there is no runtime to verify. |
| present | not applied | effective | The application may be using some non-Machine-Soul configuration. |
| unknown | applied | resolution-level effective | Deployment/path resolution may be knowable even when install provenance is not. |

The orchestrator/presentation layer may show these together as one health/status view, but they remain separate semantic operations/facts.

## 7. Future installation takeover

Discovery should preserve enough identity, mechanism, scope, version, path, registration, uninstall, and ownership information to support a future explicit installation-takeover workflow.

That future workflow is not part of discovery. Discovery gathers/assesses facts; takeover would be a separate mutating safety-sensitive operation.
