#!/usr/bin/env python3
"""Resolve explicit Machine-Soul validation-set selection.

The selector is intentionally independent from changed paths. A malformed
selector fails safe to the complete registered validation set.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import re
from typing import Iterable

REGISTERED_VALIDATION_SETS: tuple[str, ...] = (
    "linux",
    "windows",
    "fresh-linux",
    "fresh-windows",
)

_CI_TRAILER = re.compile(r"^CI:\s*(.*)\s*$", re.MULTILINE)


@dataclass(frozen=True)
class ValidationSelection:
    """Normalized validation selection and whether the request was valid."""

    selected: tuple[str, ...]
    valid: bool
    source: str
    error: str | None = None


def _all_invalid(source: str, error: str) -> ValidationSelection:
    return ValidationSelection(
        selected=REGISTERED_VALIDATION_SETS,
        valid=False,
        source=source,
        error=error,
    )


def parse_selector(selector: str | None, *, source: str) -> ValidationSelection:
    """Parse one selector, failing safe to all registered sets."""

    if selector is None or not selector.strip():
        return ValidationSelection(REGISTERED_VALIDATION_SETS, True, source)

    value = selector.strip()
    if value == "all":
        return ValidationSelection(REGISTERED_VALIDATION_SETS, True, source)
    if value == "none":
        return ValidationSelection((), True, source)

    raw_tokens = value.split(",")
    tokens = [token.strip() for token in raw_tokens]
    if any(not token for token in tokens):
        return _all_invalid(source, f"empty validation-set token in {value!r}")

    if "all" in tokens or "none" in tokens:
        return _all_invalid(
            source,
            "'all' and 'none' must be used alone rather than mixed with set names",
        )

    unknown = sorted(set(tokens).difference(REGISTERED_VALIDATION_SETS))
    if unknown:
        return _all_invalid(
            source,
            "unknown validation set(s): " + ", ".join(unknown),
        )

    requested = set(tokens)
    normalized = tuple(
        name for name in REGISTERED_VALIDATION_SETS if name in requested
    )
    return ValidationSelection(normalized, True, source)


def selector_from_commit_message(message: str) -> ValidationSelection:
    """Resolve a main-push selector from exact CI: message lines."""

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
) -> ValidationSelection:
    """Resolve validation intent for one GitHub Actions event."""

    if event_name == "push":
        return selector_from_commit_message(commit_message)
    if event_name == "workflow_dispatch":
        return parse_selector(manual_selector, source="manual-dispatch")

    return ValidationSelection(
        REGISTERED_VALIDATION_SETS,
        True,
        f"{event_name or 'unknown'}-default",
    )


def _write_github_output(path: Path, selection: ValidationSelection) -> None:
    selected = set(selection.selected)
    lines = [
        *(f"{name}={'true' if name in selected else 'false'}"
          for name in REGISTERED_VALIDATION_SETS),
        f"valid={'true' if selection.valid else 'false'}",
        "selection=" + (",".join(selection.selected) if selection.selected else "none"),
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
        f"(source={selection.source}, valid={selection.valid})",
    )
    if selection.error:
        print("selector error:", selection.error)

    if args.github_output:
        _write_github_output(args.github_output, selection)

    return 0 if selection.valid else 2


if __name__ == "__main__":
    raise SystemExit(main())
