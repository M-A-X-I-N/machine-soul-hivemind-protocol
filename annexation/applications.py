"""Side-effect-free loading/discovery of declarative applications."""

from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path
from types import ModuleType

from .model import Application


class ApplicationLoadError(RuntimeError):
    """A declaration module cannot be loaded or does not expose APPLICATION."""


def _module_name(path: Path) -> str:
    digest = hashlib.sha256(str(path.absolute()).encode("utf-8")).hexdigest()[:16]
    return f"_machine_soul_application_{digest}"


def load_application(path: str | Path) -> Application:
    """Load one _application.py module and return its APPLICATION declaration."""
    declaration_path = Path(path).absolute()
    if not declaration_path.is_file():
        raise ApplicationLoadError(f"Application declaration does not exist: {declaration_path!s}")

    spec = importlib.util.spec_from_file_location(_module_name(declaration_path), declaration_path)
    if spec is None or spec.loader is None:
        raise ApplicationLoadError(f"Unable to create import specification for {declaration_path!s}")

    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as exc:
        raise ApplicationLoadError(
            f"Application declaration raised while importing: {declaration_path!s}"
        ) from exc

    application = getattr(module, "APPLICATION", None)
    if not isinstance(application, Application):
        raise ApplicationLoadError(
            f"{declaration_path!s} must expose APPLICATION as an Application instance."
        )
    return application


def discover_applications(repository_root: str | Path) -> tuple[Application, ...]:
    """Discover application declarations in deterministic directory-name order."""
    root = Path(repository_root)
    annexation = root / "annexation"
    if not annexation.is_dir():
        return ()

    found: list[Application] = []
    ids: set[str] = set()
    for directory in sorted((item for item in annexation.iterdir() if item.is_dir()), key=lambda p: p.name):
        declaration = directory / "_application.py"
        if not declaration.is_file():
            continue
        app = load_application(declaration)
        if app.id in ids:
            raise ApplicationLoadError(f"Duplicate discovered application id: {app.id!r}")
        ids.add(app.id)
        found.append(app)
    return tuple(found)
