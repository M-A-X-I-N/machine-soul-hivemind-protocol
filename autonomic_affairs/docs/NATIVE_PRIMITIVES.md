# Native primitive process protocol

Native primitives are narrow platform-native helpers used only when portable Python is materially worse, unsafe, or unable to express the operation cleanly.

Python owns policy. A primitive performs one requested native action and reports structured facts.

## When a primitive is justified

Prefer Python first.

A native `.ps1`/`.sh` helper is justified only when the native platform interface is materially clearer/safer or Python would require brittle emulation.

Do not create a primitive merely because Windows and Linux use different APIs.

A primitive must not contain:

- application-specific policy;
- backup/restore policy;
- account-target selection policy;
- orchestration/workflow selection;
- human UI/progress output on stdout.

## Protocol version

Current protocol version:

```text
1
```

Breaking response-schema changes require a new `protocol_version`. Python rejects versions it does not explicitly understand.

## Response transport

A successful **protocol exchange** writes exactly one UTF-8 JSON object to stdout, optionally followed by normal trailing whitespace/newline.

No banners, progress text, warnings, or debug messages may appear on stdout.

Diagnostics belong on stderr.

Protocol-v1 response:

```json
{
  "protocol_version": 1,
  "primitive": "create_symlink",
  "result": {
    "status": "success",
    "changed": true,
    "code": "symlink_created",
    "message": "Symbolic link was created.",
    "data": {
      "destination": "..."
    }
  }
}
```

Top-level fields are exactly:

- `protocol_version`;
- `primitive`;
- `result`.

`primitive` is lower_snake_case and must match the primitive Python intended to invoke.

`result` is exactly the canonical `OperationResult` dictionary defined in `OPERATION_RESULTS.md`.

## Process exit semantics

The native process exit code describes **process/protocol success**, not the semantic operation status.

### Exit 0

Exit 0 means:

> the primitive process completed normally and stdout is intended to contain one trustworthy protocol envelope.

The nested semantic result may still be:

- `FAILURE`;
- `UNSUPPORTED`;
- `NOT_IMPLEMENTED`;
- `ERROR`;
- `changed=true` after a partial mutation.

Python parses/normalizes that result normally.

Example: permission denied may be a valid protocol exchange:

```text
process exit: 0
result.status: error
result.code: permission_denied
changed: false
```

### Nonzero exit

A nonzero primitive process exit means the process/protocol itself failed.

Python raises `PrimitiveProcessError` and does **not** trust stdout as a semantic `OperationResult` even if stdout happens to look like JSON.

stderr is retained as diagnostic context but is not merged into the semantic result automatically.

## Protocol failure

Exit 0 combined with any of the following raises `PrimitiveProtocolError`:

- missing/empty stdout;
- malformed JSON;
- multiple values or extra human text on stdout;
- non-object response;
- missing or unknown top-level fields;
- unsupported protocol version;
- primitive-name mismatch;
- malformed `OperationResult` shape/status/code/data.

A protocol failure is not converted to `OperationResult(ERROR, ...)` because Machine-Soul cannot trust that the primitive produced a valid semantic response.

## Partial changes

If a native action partially mutates state before failing, the primitive should still complete the protocol normally when it can truthfully describe the outcome:

```json
{
  "status": "error",
  "changed": true,
  "code": "partial_change",
  "message": "Mutation partially completed.",
  "data": {}
}
```

This keeps the danger visible to rollback/orchestration logic.

If the primitive cannot reliably determine what happened, it should fail the process/protocol rather than fabricate a semantic result.

## Verification

A primitive reports the facts it observed.

For safety-critical mutations, the Python operation engine may independently verify resulting state after receiving a successful semantic result.

Native success therefore does not remove the higher-level Apply/Unapply verification rules.

## Input transport

Protocol v1 standardizes the **response** transport.

Primitive input should normally use explicit argv elements supplied directly by `subprocess` without shell-string interpolation.

Do not force JSON stdin merely for symmetry when doing so would require extra parsers such as `jq` in an otherwise tiny Bash helper.

A specific primitive may use structured stdin when its native environment handles it cleanly, but its input format is part of that primitive's contract and does not change the response envelope.

## Invocation safety

Python invocation code must:

- construct argv as a sequence, not a shell command string;
- avoid `shell=True` unless a separately justified primitive specifically requires a shell;
- capture stdout/stderr separately;
- decode text predictably;
- treat timeouts/spawn failures/nonzero exits as process failures;
- parse stdout only after process exit 0.

PowerShell primitives should normally run without loading user profiles so startup text cannot corrupt stdout.

## Python normalization API

The initial shared protocol implementation exposes:

- `build_primitive_envelope(...)` for the canonical v1 shape;
- `parse_primitive_response(...)` for strict stdout validation;
- `normalize_primitive_process(...)` for process-exit + protocol normalization;
- `PrimitiveProcessError` for nonzero/untrusted process outcomes;
- `PrimitiveProtocolError` for invalid protocol data.

The actual subprocess invocation helpers land with the shared core implementation.

## Boundary examples

Valid semantic failure:

```text
exit 0
stdout valid v1 envelope
nested result = FAILURE conflict
=> return OperationResult
```

Valid semantic partial error:

```text
exit 0
stdout valid v1 envelope
nested result = ERROR partial_change, changed=true
=> return OperationResult
```

Primitive malfunction:

```text
exit 7
stderr contains diagnostic
=> raise PrimitiveProcessError
```

Protocol corruption:

```text
exit 0
stdout = "Starting operation...\n{...}"
=> raise PrimitiveProtocolError
```
