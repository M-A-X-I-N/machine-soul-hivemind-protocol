"""Deterministic presentation and standalone wrapper adaptation."""

from __future__ import annotations

import argparse
from dataclasses import replace
import json
from typing import Callable, Sequence

from .discovery import DiscoveryError, UnsupportedTargetAccount, build_operation_context
from .model import ConflictPolicy, OperationContext, OperationResult


RunOperation = Callable[[OperationContext | None], OperationResult]


def render_human(result: OperationResult) -> str:
    """Render the canonical concise human-facing one-line result."""
    return f"{result.status.value.upper()} {result.code}: {result.message}"


def render_json(result: OperationResult) -> str:
    """Render deterministic compact JSON for automation/process consumers."""
    return json.dumps(
        result.to_dict(),
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--account",
        dest="target_account",
        help="Logical target account; defaults to the current account.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Plan the operation without persistent mutation.",
    )
    parser.add_argument(
        "--conflict-policy",
        choices=[policy.value for policy in ConflictPolicy],
        default=ConflictPolicy.PROMPT.value,
        help="How mutating config operations handle existing unmanaged state.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Render the common result as deterministic JSON.",
    )
    return parser


def _render(result: OperationResult, *, json_output: bool) -> str:
    return render_json(result) if json_output else render_human(result)


def wrapper_main(run: RunOperation, argv: Sequence[str] | None = None) -> int:
    """Adapt one importable atomic operation to the common standalone CLI."""
    args = _parser().parse_args(list(argv) if argv is not None else None)
    policy = ConflictPolicy(args.conflict_policy)

    try:
        context = build_operation_context(
            target_account=args.target_account,
            dry_run=args.dry_run,
            conflict_policy=policy,
        )
    except UnsupportedTargetAccount as exc:
        result = OperationResult.unsupported("target_account_unsupported", str(exc))
        print(_render(result, json_output=args.json_output))
        return result.exit_code
    except DiscoveryError as exc:
        result = OperationResult.error("context_discovery_failed", str(exc))
        print(_render(result, json_output=args.json_output))
        return result.exit_code

    result = run(context)

    if result.code == "confirmation_required" and policy is ConflictPolicy.PROMPT:
        answer = input("Replace and preserve existing unmanaged configuration? [y/N] ")
        if answer.strip().casefold() in {"y", "yes"}:
            result = run(
                replace(
                    context,
                    conflict_policy=ConflictPolicy.BACKUP_AND_REPLACE,
                )
            )
        else:
            result = OperationResult.failure(
                "declined",
                "Operation was declined by the maintainer.",
            )

    print(_render(result, json_output=args.json_output))
    return result.exit_code
