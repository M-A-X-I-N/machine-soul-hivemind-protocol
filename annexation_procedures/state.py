"""Versioned Machine-Soul configuration/install state persistence."""

from __future__ import annotations

import base64
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Mapping

from .model import OperationContext, Platform


CONFIG_STATE_SCHEMA = 3
INSTALL_STATE_SCHEMA = 2


class StateError(RuntimeError):
    """Persisted Machine-Soul state is malformed or cannot be used safely."""


def _absolute_no_follow(path: str | Path) -> Path:
    raw = os.path.abspath(os.fspath(path))
    return Path(raw)


def destination_hash(path: str | Path) -> str:
    normalized = os.path.normcase(os.fspath(_absolute_no_follow(path)))
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _scratch(context: OperationContext) -> Path:
    return context.repository_root / "scratch"


def application_state_path(
    context: OperationContext,
    application: str,
    name: str,
) -> Path:
    """Return a generic per-application auxiliary state path."""
    if not name or "/" in name or "\\" in name:
        raise ValueError("Application state name must be one filename component.")
    return (
        _scratch(context)
        / "state"
        / "application"
        / context.host
        / context.target_account.name
        / application
        / f"{name}.json"
    )


def write_json_state(path: Path, payload: Mapping[str, object]) -> None:
    """Atomically persist generic JSON state."""
    _write_json_atomic(path, payload)


def read_json_state(path: Path) -> dict[str, object] | None:
    """Read one generic JSON state object."""
    if not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise StateError(f"Malformed JSON state: {path!s}") from exc
    if not isinstance(payload, dict):
        raise StateError(f"JSON state must be an object: {path!s}")
    return payload


def config_state_path(
    context: OperationContext,
    application: str,
    destination: str | Path,
    *,
    extension: str = ".json",
) -> Path:
    return (
        _scratch(context)
        / "state"
        / "config"
        / context.host
        / context.target_account.name
        / application
        / f"{destination_hash(destination)}{extension}"
    )


def _legacy_destination_hash(context: OperationContext, path: str | Path) -> str:
    """Reproduce the legacy platform runtime's destination-hash input."""
    raw = Path(os.path.abspath(os.fspath(path)))
    if context.platform is Platform.WINDOWS:
        text = os.path.normpath(os.fspath(raw))
        if text.startswith("\\\\?\\UNC\\"):
            text = "\\\\" + text[8:]
        elif text.startswith("\\\\?\\"):
            text = text[4:]
    else:
        parent = os.path.realpath(os.fspath(raw.parent))
        text = os.fspath(Path(parent) / raw.name)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _legacy_config_state_path(
    context: OperationContext,
    application: str,
    destination: str | Path,
    extension: str,
) -> Path:
    return (
        _scratch(context)
        / "state"
        / "config"
        / context.host
        / context.target_account.name
        / application
        / f"{_legacy_destination_hash(context, destination)}{extension}"
    )


def install_state_path(
    context: OperationContext,
    application: str,
    *,
    extension: str = ".json",
) -> Path:
    return (
        _scratch(context)
        / "state"
        / "install"
        / context.host
        / context.target_account.name
        / f"{application}{extension}"
    )


def backup_root(
    context: OperationContext,
    application: str,
    destination: str | Path,
) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    return (
        _scratch(context)
        / "backups"
        / context.host
        / context.target_account.name
        / application
        / f"{stamp}-{destination_hash(destination)}"
    )


def _write_json_atomic(path: Path, payload: Mapping[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, sort_keys=True, separators=(",", ":"), allow_nan=False)
            stream.write("\n")
        os.replace(temporary, path)
    except Exception:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


@dataclass(frozen=True)
class ConfigState:
    application: str
    host: str
    account: str
    source_relative: str
    destination: str
    prior_type: str
    backup_relative: str | None
    backup_absolute: str | None
    prior_target: str | None
    applied_target: str
    applied_utc: str
    schema: int = CONFIG_STATE_SCHEMA

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class InstallState:
    application: str
    host: str
    account: str
    manager: str
    identity: str
    metadata: Mapping[str, object] = field(default_factory=dict)
    schema: int = INSTALL_STATE_SCHEMA

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["metadata"] = dict(self.metadata)
        return payload


def write_config_state(
    context: OperationContext,
    state: ConfigState,
) -> Path:
    path = config_state_path(context, state.application, state.destination)
    _write_json_atomic(path, state.to_dict())
    return path


def _decode_legacy(value: str) -> str:
    if not value:
        return ""
    try:
        return base64.b64decode(value.encode("ascii")).decode("utf-8")
    except Exception as exc:
        raise StateError("Legacy base64 state field is invalid.") from exc


def _legacy_line_state(path: Path) -> ConfigState:
    fields: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        if "=" not in raw:
            continue
        key, value = raw.split("=", 1)
        fields[key] = value

    required = {"application_b64", "host_b64", "account_b64", "source_relative_b64", "destination_b64", "prior_type", "applied_target_b64"}
    missing = required - set(fields)
    if missing:
        raise StateError(f"Legacy config state missing fields: {sorted(missing)}")

    backup_relative = _decode_legacy(fields.get("backup_relative_b64", "")) or None
    backup_absolute = _decode_legacy(fields.get("backup_b64", "")) or None
    prior_target = _decode_legacy(fields.get("prior_target_b64", "")) or None
    return ConfigState(
        application=_decode_legacy(fields["application_b64"]),
        host=_decode_legacy(fields["host_b64"]),
        account=_decode_legacy(fields["account_b64"]),
        source_relative=_decode_legacy(fields["source_relative_b64"]),
        destination=_decode_legacy(fields["destination_b64"]),
        prior_type=fields["prior_type"],
        backup_relative=backup_relative,
        backup_absolute=backup_absolute,
        prior_target=prior_target,
        applied_target=_decode_legacy(fields["applied_target_b64"]),
        applied_utc=fields.get("applied_utc", ""),
    )


def _json_config_state(payload: Mapping[str, object]) -> ConfigState:
    try:
        schema = int(payload.get("schema", 0))
        if schema not in {1, 2, CONFIG_STATE_SCHEMA}:
            raise StateError(f"Unsupported config state schema: {schema}.")
        return ConfigState(
            application=str(payload["application"]),
            host=str(payload["host"]),
            account=str(payload["account"]),
            source_relative=str(payload["source_relative"]),
            destination=str(payload["destination"]),
            prior_type=str(payload.get("prior_type", "absent")),
            backup_relative=(str(payload["backup_relative"]) if payload.get("backup_relative") else None),
            backup_absolute=(
                str(payload.get("backup_absolute") or payload.get("backup"))
                if payload.get("backup_absolute") or payload.get("backup")
                else None
            ),
            prior_target=(str(payload["prior_target"]) if payload.get("prior_target") else None),
            applied_target=str(payload["applied_target"]),
            applied_utc=str(payload.get("applied_utc", "")),
            schema=CONFIG_STATE_SCHEMA,
        )
    except KeyError as exc:
        raise StateError(f"Config state missing field: {exc.args[0]}.") from exc


def read_config_state(
    context: OperationContext,
    application: str,
    destination: str | Path,
) -> ConfigState | None:
    """Read new JSON state or the legacy Linux line/base64 format."""
    candidates = [
        config_state_path(context, application, destination),
        _legacy_config_state_path(context, application, destination, ".json"),
    ]
    seen: set[Path] = set()
    for json_path in candidates:
        if json_path in seen:
            continue
        seen.add(json_path)
        if not json_path.is_file():
            continue
        try:
            payload = json.loads(json_path.read_text(encoding="utf-8-sig"))
        except json.JSONDecodeError as exc:
            raise StateError(f"Malformed config state JSON: {json_path!s}") from exc
        if not isinstance(payload, dict):
            raise StateError("Config state JSON must be an object.")
        return _json_config_state(payload)

    line_candidates = [
        config_state_path(context, application, destination, extension=".state"),
        _legacy_config_state_path(context, application, destination, ".state"),
    ]
    for legacy_path in line_candidates:
        if legacy_path in seen:
            continue
        seen.add(legacy_path)
        if legacy_path.is_file():
            return _legacy_line_state(legacy_path)
    return None


def delete_config_state(
    context: OperationContext,
    application: str,
    destination: str | Path,
) -> None:
    paths = {
        config_state_path(context, application, destination, extension=extension)
        for extension in (".json", ".state")
    }
    paths.update(
        _legacy_config_state_path(context, application, destination, extension)
        for extension in (".json", ".state")
    )
    for path in paths:
        try:
            path.unlink()
        except FileNotFoundError:
            pass


def resolve_backup_path(context: OperationContext, state: ConfigState) -> Path | None:
    if state.backup_relative:
        return context.repository_root / state.backup_relative
    if state.backup_absolute:
        return Path(state.backup_absolute)
    return None


def write_install_state(context: OperationContext, state: InstallState) -> Path:
    path = install_state_path(context, state.application)
    _write_json_atomic(path, state.to_dict())
    return path


def _json_install_state(payload: Mapping[str, object]) -> InstallState:
    schema = int(payload.get("schema", 1))
    if schema not in {1, INSTALL_STATE_SCHEMA}:
        raise StateError(f"Unsupported install state schema: {schema}.")
    application = str(payload["application"])
    manager = str(payload.get("manager", "unknown"))
    identity = str(
        payload.get("identity")
        or payload.get("package")
        or payload.get("package_id")
        or application
    )
    known = {"schema", "application", "host", "account", "manager", "identity", "package", "package_id", "metadata"}
    nested_metadata = payload.get("metadata", {})
    if not isinstance(nested_metadata, Mapping):
        raise StateError("Install state metadata must be a mapping.")
    metadata = dict(nested_metadata)
    metadata.update({str(k): v for k, v in payload.items() if k not in known})
    return InstallState(
        application=application,
        host=str(payload.get("host", "")),
        account=str(payload.get("account", "")),
        manager=manager,
        identity=identity,
        metadata=metadata,
    )


def _legacy_install_state(path: Path) -> InstallState:
    fields: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        if "=" in raw:
            key, value = raw.split("=", 1)
            fields[key] = value
    if "application" not in fields:
        raise StateError("Legacy install state is missing application.")
    return _json_install_state(fields)


def read_install_state(context: OperationContext, application: str) -> InstallState | None:
    json_path = install_state_path(context, application)
    if json_path.is_file():
        try:
            payload = json.loads(json_path.read_text(encoding="utf-8-sig"))
        except json.JSONDecodeError as exc:
            raise StateError(f"Malformed install state JSON: {json_path!s}") from exc
        if not isinstance(payload, dict):
            raise StateError("Install state JSON must be an object.")
        return _json_install_state(payload)

    legacy = install_state_path(context, application, extension=".state")
    if legacy.is_file():
        return _legacy_install_state(legacy)
    return None


def delete_install_state(context: OperationContext, application: str) -> None:
    for extension in (".json", ".state"):
        path = install_state_path(context, application, extension=extension)
        try:
            path.unlink()
        except FileNotFoundError:
            pass
