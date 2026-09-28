# Common operation-result model

`OperationResult` is the semantic boundary shared by operation engines, wrappers, orchestration, tests, and normalized native/spawned operations.

## Fixed shape

Every normal operation outcome contains:

```text
status   broad semantic category
changed  whether persistent state changed, including partial-change failures
code     stable lower_snake_case machine identifier
message  human-readable detail
data     optional JSON-compatible structured mapping
```

Python type:

```python
OperationResult(
    status=ResultStatus.SUCCESS,
    changed=True,
    code="installed",
    message="Application was installed.",
    data={"application": "example", "version": "1.2.3"},
)
```

`data` keys are strings and the mapping must be JSON-serializable. The result stores its own read-only mapping copy so caller mutation of the original mapping cannot silently alter the result.

## Broad statuses

| Status | Meaning | Process exit |
|---|---|---:|
| `SUCCESS` | requested operation/state succeeded | 0 |
| `FAILURE` | expected safe non-success state such as conflict/not-applied/decline | 1 |
| `UNSUPPORTED` | operation/platform is intentionally not applicable | 2 |
| `NOT_IMPLEMENTED` | desired capability is explicitly unfinished | 2 |
| `ERROR` | environmental/operational error was caught and can be represented safely | 3 |

The broad status is deliberately **not** the detailed state token.

Stable codes carry operation-specific semantics such as:

```text
applied
not_applied
conflict
installed
not_installed
permission_denied
rollback_failed
```

Consumers branch on `status` for broad process behavior and on `code` when they need a specific semantic state.

## `changed` is independent from success

Do not assume non-success means nothing changed.

For example, a failed mutation followed by an incomplete rollback may validly produce:

```python
OperationResult.error(
    "rollback_failed",
    "Rollback was incomplete.",
    changed=True,
)
```

This allows orchestration to surface partial-change risk rather than losing it behind a boolean success value.

## Semantic result versus malfunction

Expected operation outcomes are `OperationResult` values.

Examples:

- destination conflict;
- configuration not currently applied;
- user declined a replacement;
- package already present but unmanaged;
- unsupported platform;
- not-yet-implemented capability;
- caught filesystem/subprocess failure for which the operation can still report a truthful semantic result.

Programming errors, broken wrapper contracts, malformed/missing native protocol payloads, and other situations where Machine-Soul cannot trust the semantic response are **not** converted into fake normal results merely to avoid exceptions.

Those remain exceptional/protocol failures. The native boundary is defined in [`NATIVE_PRIMITIVES.md`](NATIVE_PRIMITIVES.md).

## Stable code rules

`code` is a public machine-facing identifier and must use lower_snake_case:

```text
^[a-z][a-z0-9_]*$
```

Messages may improve over time without breaking consumers. Codes should not be renamed casually once callers/tests depend on them.

## Canonical machine representation

`OperationResult.to_dict()` returns exactly:

```json
{
  "status": "success",
  "changed": true,
  "code": "installed",
  "message": "Application was installed.",
  "data": {
    "application": "example"
  }
}
```

This dictionary is the semantic JSON representation used above process/primitive transport layers.

A transport may wrap it with protocol metadata such as `protocol_version`; it must not reinterpret the semantic fields.

## Deterministic JSON rendering

`render_json(result)` serializes the canonical dictionary using deterministic sorted keys and compact separators.

Callers needing structured data consume JSON/result objects rather than parsing human text.

## Deterministic human rendering

The baseline concise human renderer is:

```text
<STATUS> <code>: <message>
```

Example:

```text
SUCCESS installed: Application was installed.
FAILURE conflict: Destination contains unmanaged configuration.
```

Structured `data` is intentionally not dumped into the default one-line human renderer. Richer interfaces/orchestration may present it separately.

## Wrapper relationship

Imported wrapper `run(...)` returns `OperationResult` directly.

Standalone wrapper `main(...)`:

1. receives the result from `run(...)`;
2. renders it through the shared presentation layer;
3. exits using `result.exit_code`.

Wrappers do not invent operation-specific exit-code tables or parse their own status text.

## Orchestrator relationship

The orchestrator receives the same result objects as direct wrappers.

It may aggregate/display them differently, but does not translate bespoke application output into common meaning.

## Native/spawned relationship

A valid native/spawned semantic payload is normalized immediately into `OperationResult`.

A malformed protocol response is not an `OperationResult(ERROR, ...)`; it is a protocol malfunction handled by [`NATIVE_PRIMITIVES.md`](NATIVE_PRIMITIVES.md).

This distinction prevents corrupt/untrusted transport output from masquerading as a trustworthy operation result.


## Discovery assessment data

Installation discovery and effective-configuration verification may require richer typed assessments below the operation layer.

Do not expand `ResultStatus` into a combinatorial discovery-state enum. Raw observations and semantic assessments belong in discovery/verification value objects; an atomic operation then maps the assessment to a stable `OperationResult.code` and serializable `data`.

Evidence strength (runtime/application-native/resolution/convention/none) is structured data describing why an effective-config conclusion is credible. It is independent from `ResultStatus`.

See [`DISCOVERY_SEMANTICS.md`](DISCOVERY_SEMANTICS.md).
