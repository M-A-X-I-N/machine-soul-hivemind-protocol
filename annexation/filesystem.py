"""Portable filesystem/symlink facts used by configuration engines."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import os
from pathlib import Path


class LinkStatus(str, Enum):
    APPLIED = "applied"
    NOT_APPLIED = "not_applied"
    CONFLICT = "conflict"
    WRONG_TARGET = "wrong_target"
    BROKEN = "broken"


@dataclass(frozen=True)
class LinkInfo:
    status: LinkStatus
    expected_target: Path
    destination: Path
    actual_target: Path | None = None
    raw_target: str | None = None


def absolute_no_follow(path: str | Path) -> Path:
    """Canonicalize a path's parent without dereferencing the final object."""
    raw = Path(os.path.abspath(os.fspath(path)))
    parent = Path(os.path.realpath(os.fspath(raw.parent)))
    return parent / raw.name


def canonical_target(path: str | Path) -> Path:
    return Path(os.path.realpath(os.fspath(path)))


def _comparison_path(path: str | Path) -> str:
    value = os.path.normpath(os.path.abspath(os.fspath(path)))
    if os.name == "nt":
        # Python's os.readlink() intentionally exposes Windows substitution
        # paths, commonly as \\?\C:\\... or \\?\UNC\\..., while ordinary
        # filesystem APIs usually produce DOS/UNC form. They name the same
        # object and must compare equal.
        if value.startswith("\\\\?\\UNC\\"):
            value = "\\\\" + value[8:]
        elif value.startswith("\\\\?\\"):
            value = value[4:]
    return os.path.normcase(value)


def paths_equal(left: str | Path, right: str | Path) -> bool:
    return _comparison_path(left) == _comparison_path(right)


def resolve_raw_link_target(destination: str | Path, raw_target: str) -> Path:
    dest = absolute_no_follow(destination)
    raw = Path(raw_target)
    candidate = raw if raw.is_absolute() else dest.parent / raw
    return canonical_target(candidate)


def classify_link(source: str | Path, destination: str | Path) -> LinkInfo:
    """Classify destination relative to the expected canonical source file."""
    expected = canonical_target(source)
    dest = absolute_no_follow(destination)

    if dest.is_symlink():
        raw = os.readlink(dest)
        actual = resolve_raw_link_target(dest, raw)
        if paths_equal(actual, expected) and actual.is_file():
            status = LinkStatus.APPLIED
        elif not actual.exists():
            status = LinkStatus.BROKEN
        else:
            status = LinkStatus.WRONG_TARGET
        return LinkInfo(status, expected, dest, actual, raw)

    if os.path.lexists(dest):
        return LinkInfo(LinkStatus.CONFLICT, expected, dest)

    return LinkInfo(LinkStatus.NOT_APPLIED, expected, dest)


def create_file_symlink(source: str | Path, destination: str | Path) -> None:
    """Create one file symlink without shell interpolation."""
    os.symlink(os.fspath(source), os.fspath(destination), target_is_directory=False)
