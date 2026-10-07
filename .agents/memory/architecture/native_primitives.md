# Native primitive protocol

Canonical contract: [`../../../meta/docs/NATIVE_PRIMITIVES.md`](../../../meta/docs/NATIVE_PRIMITIVES.md).

V2-55 rules:

- Python owns policy; native scripts perform one narrow native action;
- prefer portable Python before creating a primitive;
- protocol v1 response is exactly one JSON object on stdout: `protocol_version`, `primitive`, `result`;
- stderr is diagnostics only;
- exit 0 means protocol/process success, **not** semantic success;
- semantic failure/error/partial-change with a valid envelope still exits 0 and normalizes to `OperationResult`;
- nonzero exit raises `PrimitiveProcessError` and stdout is untrusted;
- malformed/missing/version-mismatched/name-mismatched output raises `PrimitiveProtocolError`;
- protocol failures are never laundered into normal `OperationResult(ERROR)` values;
- input defaults to explicit argv; do not impose JSON stdin on Bash if it requires extra parsing dependencies;
- safety-critical state may be independently verified by Python after native success.
