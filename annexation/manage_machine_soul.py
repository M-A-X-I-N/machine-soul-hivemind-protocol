#!/usr/bin/env python3
"""Broad interactive/CLI manager composed entirely from atomic wrappers."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT))

from annexation_procedures.discovery import (  # noqa: E402
    DiscoveryError,
    UnsupportedTargetAccount,
    build_operation_context,
)
from annexation_procedures.model import ConflictPolicy, Operation  # noqa: E402
from annexation_procedures.orchestration import (  # noqa: E402
    WrapperBinding,
    apply_installed_configurations,
    apply_selected_configurations,
    bindings_for_operation,
    check_all_configurations,
    discovery_status,
    discover_wrappers,
)
from annexation_procedures.presentation import render_human  # noqa: E402
from annexation_procedures.status_presentation import (  # noqa: E402
    render_discovery_status_human,
    render_discovery_status_json,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Machine-Soul operation manager")
    parser.add_argument(
        "--workflow",
        choices=("list", "status", "check-config-all", "apply-config", "apply-installed"),
        help="Run a workflow non-interactively; omit for the interactive menu.",
    )
    parser.add_argument(
        "--application",
        action="append",
        default=[],
        help="Application ID for apply-config; repeat to select multiple.",
    )
    parser.add_argument("--account", help="Logical target account.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--conflict-policy",
        choices=[policy.value for policy in ConflictPolicy],
        default=ConflictPolicy.PROMPT.value,
    )
    parser.add_argument("--json", action="store_true", dest="json_output")
    return parser


def _application_ids(bindings: tuple[WrapperBinding, ...], operation: Operation) -> list[str]:
    return sorted({binding.application_id for binding in bindings_for_operation(bindings, operation)})


def _render_list(bindings: tuple[WrapperBinding, ...]) -> str:
    grouped: dict[str, set[str]] = {}
    names: dict[str, str] = {}
    for binding in bindings:
        grouped.setdefault(binding.application_id, set()).add(binding.operation.value)
        names[binding.application_id] = binding.display_name

    lines = []
    for application_id in sorted(grouped):
        operations = ", ".join(sorted(grouped[application_id]))
        lines.append(f"{application_id} ({names[application_id]}): {operations}")
    return "\n".join(lines)


def _render_report(report, *, json_output: bool) -> str:
    if json_output:
        return json.dumps(
            report.to_dict(),
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    if not report.attempts:
        return "No operations were performed."
    return "\n".join(
        f"{attempt.application_id} {attempt.operation.value}: {render_human(attempt.result)}"
        for attempt in report.attempts
    )


def _confirm_replacement(binding: WrapperBinding, _result) -> bool:
    answer = input(
        f"{binding.application_id}: replace and preserve existing unmanaged configuration? [y/N] "
    )
    return answer.strip().casefold() in {"y", "yes"}


def _interactive_choice(bindings: tuple[WrapperBinding, ...]) -> tuple[str | None, list[str]]:
    print("Machine-Soul manager")
    print("1) Check configuration for all discovered applications")
    print("2) Apply configuration to selected applications")
    print("3) Apply configuration to detected installed applications")
    print("4) Show installation / configuration / effective status")
    print("5) Exit without performing operations")
    choice = input("Choice [5]: ").strip() or "5"

    if choice == "1":
        return "check-config-all", []
    if choice == "2":
        available = _application_ids(bindings, Operation.APPLY_CONFIG)
        print("Available:", ", ".join(available))
        raw = input("Application IDs (comma-separated, or 'all'): ").strip()
        if not raw:
            return None, []
        if raw.casefold() == "all":
            return "apply-config", available
        return "apply-config", [part.strip() for part in raw.split(",") if part.strip()]
    if choice == "3":
        return "apply-installed", []
    if choice == "4":
        return "status", []
    if choice == "5":
        return None, []
    raise ValueError(f"Unknown interactive choice: {choice!r}.")


def main(argv=None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    bindings = discover_wrappers(REPOSITORY_ROOT)

    workflow = args.workflow
    selected = list(args.application)

    if workflow == "list":
        print(_render_list(bindings))
        return 0

    if workflow is None:
        try:
            workflow, selected = _interactive_choice(bindings)
        except ValueError as exc:
            parser.error(str(exc))
        if workflow is None:
            print("No operations were performed.")
            return 0

    if workflow == "apply-config":
        available = set(_application_ids(bindings, Operation.APPLY_CONFIG))
        if not selected:
            parser.error("apply-config requires at least one --application (or interactive selection).")
        unknown = sorted(set(selected) - available)
        if unknown:
            parser.error(f"Unknown/unavailable application IDs: {', '.join(unknown)}")

    try:
        context = build_operation_context(
            repository_root=REPOSITORY_ROOT,
            target_account=args.account,
            dry_run=args.dry_run,
            conflict_policy=ConflictPolicy(args.conflict_policy),
        )
    except UnsupportedTargetAccount as exc:
        print(f"UNSUPPORTED target_account_unsupported: {exc}")
        return 2
    except DiscoveryError as exc:
        print(f"ERROR context_discovery_failed: {exc}")
        return 3

    if workflow == "status":
        status_report = discovery_status(bindings, context)
        print(
            render_discovery_status_json(status_report)
            if args.json_output
            else render_discovery_status_human(status_report)
        )
        return status_report.exit_code

    if workflow == "check-config-all":
        report = check_all_configurations(bindings, context)
    elif workflow == "apply-config":
        report = apply_selected_configurations(
            bindings,
            context,
            selected,
            confirm_replacement=_confirm_replacement,
        )
    elif workflow == "apply-installed":
        report = apply_installed_configurations(
            bindings,
            context,
            confirm_replacement=_confirm_replacement,
        )
    else:
        raise AssertionError(f"Unhandled workflow: {workflow!r}")

    print(_render_report(report, json_output=args.json_output))
    return report.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
