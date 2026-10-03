#!/usr/bin/env python3
"""Resolve Machine-Soul CI check selection and runner coalescing."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import re
import subprocess
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
_APPROVED_KINDS = (
    "Feature", "Fix", "Research", "Documentation", "Test", "CI",
    "Build", "Refactor", "Chore", "CBA",
)
_COMMIT_SUMMARY = re.compile(
    r"^\\[(?:" + "|".join(_APPROVED_KINDS) + r")\\]"
    r"(?:\\[[^]\\r\\n]+\\])? [^\\r\\n]+$"
)
_CONTROL_PATHS = frozenset({
    ".github/workflows/machine_soul_validation.yml",
    ".github/workflows/machine_soul_validation_linux.yml",
    ".github/workflows/machine_soul_validation_windows.yml",
    ".github/workflows/machine_soul_validation_fresh_linux.yml",
    ".github/workflows/machine_soul_validation_fresh_windows.yml",
    ".github/workflows/codeql.yml",
    "autonomic_affairs/ci_validation_selector.py",
    "autonomic_affairs/ci_validation_history.py",
    "autonomic_affairs/tests/python/test_ci_validation_selector.py",
    "autonomic_affairs/tests/python/test_ci_validation_history.py",
})
_BLOCKING_CHECKS = REGISTERED_CHECKS[:-2]
_INSTALL_MARKERS = (
    "/install.py",
    "installation_",
    "/tests/install/",
    "bootstrap",
)
_INERT_TEXT_PREFIXES = (
    ".agents/",
    "autonomic_affairs/tasks/",
    "autonomic_affairs/docs/",
    "autonomic_affairs/initiatives/",
    "acquired_intelligence/",
    "abandoned_artifacts/",
)
_INERT_TEXT_FILES = frozenset({
    "AGENTS.md",
    "README.md",
    "autonomic_affairs/tasks.md",
    "autonomic_affairs/reminders.md",
})


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



class PolicyEvidenceError(RuntimeError):
    """Raised when automatic policy evidence cannot be established safely."""


def validate_commit_summary(summary: str) -> str | None:
    """Return an error for a commit summary that violates repository grammar."""

    value = (summary or "").splitlines()[0] if summary else ""
    if _COMMIT_SUMMARY.fullmatch(value):
        return None
    return "commit summary must match [Kind][Scope?] Imperative summary"


def _ordered_checks(checks: Iterable[str]) -> tuple[str, ...]:
    requested = set(checks)
    return tuple(check for check in REGISTERED_CHECKS if check in requested)


def _is_inert_text(path: str) -> bool:
    if not path.endswith((".md", ".txt", ".rst")):
        return False
    return path in _INERT_TEXT_FILES or path.startswith(_INERT_TEXT_PREFIXES)


def _checks_for_path(path: str) -> tuple[str, ...] | None:
    normalized = path.replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]

    if normalized in _CONTROL_PATHS:
        return REGISTERED_CHECKS

    if (
        normalized.startswith(".github/workflows/")
        and normalized.endswith((".yml", ".yaml"))
    ):
        return ("codeql-actions",)

    if _is_inert_text(normalized):
        return ()

    exact_test_checks = {
        "autonomic_affairs/tests/applications/test_linux_operations.sh": (
            "linux-applications",
            "fresh-linux",
        ),
        "autonomic_affairs/tests/applications/test_windows_operations.ps1": (
            "windows-applications",
            "fresh-windows",
        ),
        "autonomic_affairs/tests/applications/test_windows_posix_operations.sh": (
            "windows-posix",
        ),
        "autonomic_affairs/tests/install/test_linux_install_dry_run.sh": (
            "linux-install",
        ),
        "autonomic_affairs/tests/install/test_windows_install_dry_run.ps1": (
            "windows-install",
        ),
        "autonomic_affairs/tests/session/test_linux_account_boundaries.sh": (
            "linux-session",
        ),
        "autonomic_affairs/tests/matrix/test_linux_host_matrix.sh": (
            "linux-matrix",
        ),
    }
    if normalized in exact_test_checks:
        return exact_test_checks[normalized]

    if normalized.startswith("assimilation_directives/"):
        return (
            "linux-applications",
            "linux-session",
            "linux-matrix",
            "windows-applications",
            "windows-posix",
            "fresh-linux",
            "fresh-windows",
        )

    if normalized.endswith(".py"):
        if normalized.startswith("annexation_procedures/"):
            if any(marker in normalized for marker in _INSTALL_MARKERS):
                return (*_BLOCKING_CHECKS, "codeql-python")
            return ("linux-python", "windows-python", "codeql-python")
        if normalized.startswith("autonomic_affairs/tests/python/"):
            return ("linux-python", "windows-python")
        return ("codeql-python",)

    return None


def checks_for_paths(paths: Iterable[str]) -> PolicySelection:
    """Classify changed paths into a conservative union of relevant checks."""

    selected: set[str] = set()
    for path in paths:
        path_checks = _checks_for_path(path)
        if path_checks is None:
            return PolicySelection(
                REGISTERED_CHECKS,
                True,
                "path-classifier-fallback",
                error=f"unclassified path: {path}",
            )
        selected.update(path_checks)
    return PolicySelection(_ordered_checks(selected), True, "path-classifier")


def _run_git(args: list[str], *, cwd: Path | str | None = None) -> str:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=cwd,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        detail = getattr(exc, "stderr", None) or str(exc)
        raise PolicyEvidenceError(detail.strip()) from exc
    return result.stdout


def git_changed_paths(
    base: str,
    head: str,
    *,
    three_dot: bool = False,
    cwd: Path | str | None = None,
) -> tuple[str, ...]:
    """Return changed paths for a Git two-dot or three-dot event range."""

    if not base or not head:
        raise PolicyEvidenceError("missing Git range endpoint")
    _run_git(["rev-parse", "--verify", f"{base}^{{commit}}"], cwd=cwd)
    _run_git(["rev-parse", "--verify", f"{head}^{{commit}}"], cwd=cwd)
    if three_dot:
        _run_git(["merge-base", base, head], cwd=cwd)
    separator = "..." if three_dot else ".."
    raw = _run_git(
        ["diff", "--name-status", "-M", f"{base}{separator}{head}"],
        cwd=cwd,
    )

    paths: list[str] = []
    seen: set[str] = set()
    for line in raw.splitlines():
        fields = line.split("\t")
        if not fields:
            continue
        status = fields[0]
        candidates = (
            fields[1:3] if status.startswith(("R", "C")) else fields[1:2]
        )
        for candidate in candidates:
            if candidate and candidate not in seen:
                seen.add(candidate)
                paths.append(candidate)
    return tuple(paths)


def selector_from_commit_message(
    message: str,
    *,
    default_auto: bool = False,
) -> PolicySelection:
    """Resolve a selector from exact CI: message lines."""

    matches = _CI_TRAILER.findall(message or "")
    if not matches:
        return parse_selector(
            None,
            source="main-default",
            default_auto=default_auto,
        )
    if len(matches) != 1:
        return _all_invalid(
            "commit-trailer",
            "multiple CI: selectors found in the pushed tip commit",
        )
    return parse_selector(matches[0], source="commit-trailer")



def resolve_automatic_event(
    event_name: str,
    *,
    commit_message: str = "",
    manual_selector: str = "",
    before: str = "",
    after: str = "",
    base: str = "",
    head: str = "",
    forced: bool = False,
    cwd: Path | str | None = None,
) -> PolicySelection:
    """Resolve explicit intent or conservative automatic event evidence."""

    if event_name == "workflow_dispatch":
        return parse_selector(manual_selector, source="manual-dispatch")
    if event_name == "schedule":
        return PolicySelection(
            REGISTERED_CHECKS,
            True,
            "schedule-placeholder",
        )
    if event_name not in {"push", "pull_request"}:
        return PolicySelection(
            REGISTERED_CHECKS,
            True,
            "unknown-event-fallback",
        )

    if commit_message:
        summary_error = validate_commit_summary(commit_message)
        if summary_error:
            return _all_invalid("commit-metadata", summary_error)

    selector = selector_from_commit_message(
        commit_message,
        default_auto=True,
    )
    if not selector.valid or not selector.automatic:
        return selector

    if event_name == "push":
        if forced or not before or not after or set(before) == {"0"}:
            return PolicySelection(
                REGISTERED_CHECKS,
                True,
                "push-range-fallback",
            )
        try:
            paths = git_changed_paths(before, after, cwd=cwd)
        except PolicyEvidenceError as exc:
            return PolicySelection(
                REGISTERED_CHECKS,
                True,
                "push-range-fallback",
                error=str(exc),
            )
        classified = checks_for_paths(paths)
        return PolicySelection(
            classified.selected,
            classified.valid,
            classified.source,
            classified.error,
        )

    if not base or not head:
        return PolicySelection(
            REGISTERED_CHECKS,
            True,
            "pr-range-fallback",
        )
    try:
        paths = git_changed_paths(
            base,
            head,
            three_dot=True,
            cwd=cwd,
        )
    except PolicyEvidenceError as exc:
        return PolicySelection(
            REGISTERED_CHECKS,
            True,
            "pr-range-fallback",
            error=str(exc),
        )
    classified = checks_for_paths(paths)
    return PolicySelection(
        classified.selected,
        classified.valid,
        classified.source,
        classified.error,
    )

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
