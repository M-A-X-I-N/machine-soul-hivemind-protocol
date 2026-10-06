"""Portable repository/platform/host/account discovery."""

from __future__ import annotations

import getpass
import os
from pathlib import Path
import socket
import sys
from typing import Mapping

from .model import ConflictPolicy, OperationContext, Platform, TargetAccount


ROOT_MARKER = ".machine_soul_root"


class DiscoveryError(RuntimeError):
    """Runtime environment cannot be resolved safely."""


class UnsupportedTargetAccount(DiscoveryError):
    """Requested cross-account target is not supported on this platform."""


def detect_platform() -> Platform:
    """Return the Machine-Soul platform for the current Python process."""
    if os.name == "nt":
        return Platform.WINDOWS
    if sys.platform.startswith(("linux", "darwin", "freebsd")) or os.name == "posix":
        return Platform.LINUX
    raise DiscoveryError(f"Unsupported Python platform: os.name={os.name!r}, sys.platform={sys.platform!r}.")


def resolve_repository_root(
    start: str | os.PathLike[str] | None = None,
    *,
    environ: Mapping[str, str] | None = None,
) -> Path:
    """Resolve the checkout root using MACHINE_SOUL or the stable root marker."""
    env = os.environ if environ is None else environ
    configured = env.get("MACHINE_SOUL")
    if configured:
        candidate = Path(configured).expanduser().absolute()
        if (candidate / ROOT_MARKER).is_file():
            return candidate
        raise DiscoveryError(
            f"MACHINE_SOUL points to {candidate!s}, but {ROOT_MARKER} was not found there."
        )

    cursor = Path(start or __file__).expanduser().absolute()
    if cursor.is_file():
        cursor = cursor.parent

    for candidate in (cursor, *cursor.parents):
        if (candidate / ROOT_MARKER).is_file():
            return candidate

    raise DiscoveryError("Unable to resolve Machine-Soul repository root from ancestry.")


def discover_host(*, environ: Mapping[str, str] | None = None) -> str:
    """Discover host identity with an explicit test/override escape hatch."""
    env = os.environ if environ is None else environ
    override = env.get("MACHINE_SOUL_HOST")
    if override:
        return override.strip().lower()

    name = socket.gethostname().split(".", 1)[0].strip().lower()
    if not name:
        raise DiscoveryError("Unable to discover a non-empty host identity.")
    return name


def _current_account_name(env: Mapping[str, str]) -> str:
    if os.name == "nt" and env.get("USERNAME"):
        return env["USERNAME"]
    return getpass.getuser()


def resolve_target_account(
    name: str | None = None,
    *,
    platform: Platform | None = None,
    environ: Mapping[str, str] | None = None,
) -> TargetAccount:
    """Resolve one logical target account without changing process identity."""
    env = os.environ if environ is None else environ
    active_platform = platform or detect_platform()
    current_name = _current_account_name(env)
    requested = name or current_name
    is_current = requested.casefold() == current_name.casefold()

    if active_platform is Platform.WINDOWS:
        if not is_current:
            raise UnsupportedTargetAccount(
                f"Explicit non-current Windows account {requested!r} is not implemented."
            )

        home_raw = env.get("USERPROFILE") or env.get("HOME")
        if not home_raw:
            home_raw = str(Path.home())
        local_raw = env.get("LOCALAPPDATA")
        return TargetAccount(
            requested,
            Path(home_raw),
            True,
            Path(local_raw) if local_raw else None,
        )

    if is_current:
        home_raw = env.get("HOME")
        if home_raw:
            home = Path(home_raw)
        else:
            try:
                import pwd

                home = Path(pwd.getpwnam(current_name).pw_dir)
            except (ImportError, KeyError) as exc:
                raise DiscoveryError(
                    f"Unable to resolve home directory for current account {current_name!r}."
                ) from exc
        return TargetAccount(requested, home, True)

    try:
        import pwd
    except ImportError as exc:
        raise UnsupportedTargetAccount(
            "Explicit non-current account lookup requires a POSIX account database."
        ) from exc

    try:
        record = pwd.getpwnam(requested)
    except KeyError as exc:
        raise DiscoveryError(f"Account {requested!r} does not exist in the local account database.") from exc

    return TargetAccount(record.pw_name, Path(record.pw_dir), False)


def build_operation_context(
    *,
    repository_root: str | os.PathLike[str] | None = None,
    platform: Platform | None = None,
    host: str | None = None,
    target_account: str | None = None,
    dry_run: bool = False,
    conflict_policy: ConflictPolicy = ConflictPolicy.ABORT,
    environ: Mapping[str, str] | None = None,
) -> OperationContext:
    """Resolve all common operation inputs exactly once."""
    env = os.environ if environ is None else environ
    active_platform = platform or detect_platform()
    root = (
        Path(repository_root).expanduser().absolute()
        if repository_root is not None
        else resolve_repository_root(environ=env)
    )
    if not (root / ROOT_MARKER).is_file():
        raise DiscoveryError(f"Repository root {root!s} does not contain {ROOT_MARKER}.")

    resolved_account_name = target_account
    if resolved_account_name is None and env.get("MACHINE_SOUL_ACCOUNT"):
        # Transitional compatibility for legacy tests/invocations. Public account
        # selection is the explicit operation-context input.
        resolved_account_name = env["MACHINE_SOUL_ACCOUNT"]

    account = resolve_target_account(
        resolved_account_name,
        platform=active_platform,
        environ=env,
    )
    return OperationContext(
        repository_root=root,
        platform=active_platform,
        host=(host or discover_host(environ=env)).lower(),
        target_account=account,
        dry_run=dry_run,
        conflict_policy=conflict_policy,
        environment=dict(env),
    )
