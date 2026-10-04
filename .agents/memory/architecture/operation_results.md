# Common operation results

Canonical contract: [`../../../autonomic_affairs/docs/OPERATION_RESULTS.md`](../../../autonomic_affairs/docs/OPERATION_RESULTS.md).

V2-54 established real Python `OperationResult` / `ResultStatus` types and shared renderers.

Key rules:

- broad statuses: success, failure, unsupported, not_implemented, error;
- exit mapping: 0 / 1 / 2 / 2 / 3;
- `code` is stable lower_snake_case semantic identity;
- `message` is human detail and may evolve;
- `data` must be JSON-compatible;
- `changed` is independent of status and may be true on partial-change errors;
- expected safe non-success outcomes are normal results;
- programmer errors and malformed native protocols remain exceptional;
- wrappers/orchestrators/native normalization all converge on this one model;
- human output is `<STATUS> <code>: <message>`;
- machine output comes from the fixed result dictionary/JSON shape.
