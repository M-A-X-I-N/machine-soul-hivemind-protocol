#!/usr/bin/env python3
"""Resolve Machine-Soul CI check selection and runner coalescing."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import re
from typing import Iterable

REGISTERED_CHECKS: tuple[str, ...] = (
    "linux-python",
    "linux-applications",
    "linux-install",
    "linux-session",
    "linux-matrix",
    "windows-python",
    "windows-applications",
    "windows-posix",
    "windows-install",
    "fresh-linux",
    "fresh-windows",
    "codeql-python",
    "codeql-actions",
)

GROUP_ALIASES: dict[str, tuple[str, ...]] = {
    "linux": REGISTERED_CHECKS[0:5],
    "windows": REGISTERED_CHECKS[5:9],
}

RUNNER_GROUP_CHECKS: dict[str, tuple[str, ...]] = {
    "linux": REGISTERED_CHECKS[0:5],
    "windows": REGISTERED_CHECKS[5:9],
    "fresh-linux": ("fresh-linux",),
    "fresh-windows": ("fresh-windows",),
    "codeql-python": ("codeql-python",),
    "codeql-actions": ("codeql-actions",),
}

_CI_TRAILER = re.compile(r"^CI:\s*(.*)\s*$", re.MULTILINE)
_STANDALONE_SELECTORS = frozenset({"all", "none", "auto"})


@dataclass(frozen=True)
class PolicySelection:
    """Normalized check selection and whether the request was valid."""

    selected: tuple[str, ...]
    valid: bool
    source: str
    error: str | None = None
    automatic: bool = False


def _all_invalid(source: str, error: str) -> PolicySelection:
    return PolicySelection(
        selected=REGISTERED_CHECKS,
        valid=False,
        source=source,
        error=error,
    )


def parse_selector(
    selector: str | None,
    *,
    source: str,
    default_auto: bool = False,
) -> PolicySelection:
    """Parse one selector, failing safe to all registered checks."""

    if selector is None or not selector.strip():
        if default_auto:
            return PolicySelection((), True, source, automatic=True)
        return PolicySelection(REGISTERED_CHECKS, True, source)

    value = selector.strip()
    if value == "all":
        return PolicySelection(REGISTERED_CHECKS, True, source)
    if value == "none":
        return PolicySelection((), True, source)
    if value == "auto":
        return PolicySelection((), True, source, automatic=True)

    tokens = [token.strip() for token in value.split(",")]
    if any(not token for token in tokens):
        return _all_invalid(source, f"empty check token in {value!r}")

    mixed_standalone = sorted(_STANDALONE_SELECTORS.intersection(tokens))
    if mixed_standalone:
        return _all_invalid(
            source,
            "'all', 'none', and 'auto' must be used alone rather than mixed "
            "with check or group names",
        )

    expanded: set[str] = set()
    unknown: set[str] = set()
    for token in tokens:
        if token in REGISTERED_CHECKS:
            expanded.add(token)
        elif token in GROUP_ALIASES:
            expanded.update(GROUP_ALIASES[token])
        else:
            unknown.add(token)

    if unknown:
        return _all_invalid(
            source,
            "unknown check/group(s): " + ", ".join(sorted(unknown)),
        )

    normalized = tuple(name for name in REGISTERED_CHECKS if name in expanded)
    return PolicySelection(normalized, True, source)


def runner_groups_for_checks(checks: Iterable[str]) -> dict[str, tuple[str, ...]]:
    """Coalesce selected checks into the minimum compatible runner groups."""

    requested = set(checks)
    return {
        group: tuple(check for check in members if check in requested)
        for group, members in RUNNER_GROUP_CHECKS.items()
        if any(check in requested for check in members)
    }


def selector_from_commit_message(message: str) -> PolicySelection:
    """Resolve a selector from exact CI: message lines."""

    matches = _CI_TRAILER.findall(message or "")
    if not matches:
        return parse_selector(None, source="main-default")
    if len(matches) != 1:
        return _all_invalid(
            "commit-trailer",
            "multiple CI: selectors found in the pushed tip commit",
        )
    return parse_selector(matches[0], source="commit-trailer")


def resolve_event_selection(
    event_name: str,
    *,
    commit_message: str = "",
    manual_selector: str = "",
) -> PolicySelection:
    """Resolve current explicit intent while automatic routing is added later."""

    if event_name == "push":
        return selector_from_commit_message(commit_message)
    if event_name == "workflow_dispatch":
        return parse_selector(manual_selector, source="manual-dispatch")
    return PolicySelection(
        REGISTERED_CHECKS,
        True,
        f"{event_name or 'unknown'}-default",
    )


def _write_github_output(path: Path, selection: PolicySelection) -> None:
    groups = runner_groups_for_checks(selection.selected)
    lines = [
        *(
            f"{name}={'true' if name in groups else 'false'}"
            for name in ("linux", "windows", "fresh-linux", "fresh-windows")
        ),
        f"valid={'true' if selection.valid else 'false'}",
        "selection=" + (
            ",".join(selection.selected) if selection.selected else "none"
        ),
        f"source={selection.source}",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--event", required=True)
    parser.add_argument("--commit-message", default="")
    parser.add_argument("--manual-selector", default="")
    parser.add_argument("--github-output", type=Path)
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    selection = resolve_event_selection(
        args.event,
        commit_message=args.commit_message,
        manual_selector=args.manual_selector,
    )

    print(
        "validation selection:",
        ",".join(selection.selected) if selection.selected else "none",
        (
            f"(source={selection.source}, valid={selection.valid}, "
            f"automatic={selection.automatic})"
        ),
    )
    if selection.error:
        print("selector error:", selection.error)

    if args.github_output:
        _write_github_output(args.github_output, selection)

    return 0 if selection.valid else 2


if __name__ == "__main__":
    raise SystemExit(main())
