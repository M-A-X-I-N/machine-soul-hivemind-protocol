"""Machine-Soul-owned Windows Lua/LuaJIT multiversion runtime backend."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import ntpath
import os
from pathlib import Path
import re
import shutil
import tarfile
import tempfile
from typing import Callable, Mapping
from urllib.request import urlopen
import zipfile

from .model import (
    NativeToolchainRequirement,
    OperationContext,
    OperationResult,
    Platform,
    ResultStatus,
    RuntimeInstance,
    RuntimeSpec,
)
from .native_toolchain import check_native_toolchain_requirement
from .process import ProcessResult, run_process
from .state import read_json_state, write_json_state


Runner = Callable[[list[str]], ProcessResult]
ArchitectureProbe = Callable[[Path], str]
PrerequisiteChecker = Callable[
    [OperationContext, NativeToolchainRequirement],
    OperationResult,
]
SourceBuilder = Callable[
    [OperationContext, RuntimeSpec, Path, Path, Mapping[str, object]],
    OperationResult,
]
FetchBytes = Callable[[str], bytes]

_MANIFEST_SCHEMA = 1
_BACKEND = "machine-soul-lua-prefix"
_SUBJECT = "lua"
_SUPPORTED_PUC_LINES = {"5.1", "5.2", "5.3", "5.4", "5.5"}


@dataclass(frozen=True)
class LuaBinaryArtifact:
    """One exact downloadable LuaBinaries archive."""

    url: str
    digest: str

    def to_dict(self) -> dict[str, str]:
        return {"url": self.url, "digest": self.digest}


def _artifacts(version: str, arch: str, hashes: tuple[str, str]) -> tuple[LuaBinaryArtifact, ...]:
    label = "Win64" if arch == "x64" else "Win32"
    return (
        LuaBinaryArtifact(
            f"https://downloads.sourceforge.net/project/luabinaries/{version}/"
            f"Tools%20Executables/lua-{version}_{label}_bin.zip",
            hashes[0],
        ),
        LuaBinaryArtifact(
            f"https://downloads.sourceforge.net/project/luabinaries/{version}/"
            f"Windows%20Libraries/Dynamic/lua-{version}_{label}_dllw6_lib.zip",
            hashes[1],
        ),
    )


# Exact published LuaBinaries artifacts currently used by Scoop manifests.
# No fallback to a different patch version is allowed.
_LUABINARIES: dict[tuple[str, str], tuple[tuple[LuaBinaryArtifact, ...], str, str]] = {
    ("5.1.5", "x64"): (_artifacts("5.1.5", "x64", (
        "sha256:5f34cf7d40a20a587ea351482a4207d93b92ef6f1983e910a13338253819fe93",
        "sha256:353564351aee748dca5d2ef98376cb93305679a3e94170b12936d7526afe8a6c",
    )), "lua5.1.exe", "luac5.1.exe"),
    ("5.1.5", "x86"): (_artifacts("5.1.5", "x86", (
        "sha256:c831a26d9c2280adf594a33690324de5de3cf6fb75f26b3753bae00812bcf162",
        "sha256:c889c2dc06a7cba2b7a254dfe2f7bfb44c472ce7dbb366ea4598d9ee62a391c2",
    )), "lua5.1.exe", "luac5.1.exe"),
    ("5.2.4", "x64"): (_artifacts("5.2.4", "x64", (
        "sha256:6cc8153640b5c1fc4632f18dadaa8696c5b7aef85e885245280d7e31011549d9",
        "sha256:1f301605fd304754e179c37803af78d930175f7ca7301be62d97ff2228dee3dd",
    )), "lua52.exe", "luac52.exe"),
    ("5.2.4", "x86"): (_artifacts("5.2.4", "x86", (
        "sha256:2ab5a24ac1a78bb88bde0bb75ad09c7fabc2c9f886fbf4e9f72e5b7745a9f76a",
        "sha256:95240e52d0d10c5b4575d11ee35428f171b0819b6a9d543685cafe16610f6607",
    )), "lua52.exe", "luac52.exe"),
    ("5.3.6", "x64"): (_artifacts("5.3.6", "x64", (
        "sha1:5e9311aae6cf48b2603ea3cfea28d250b0c38484",
        "sha1:47f4f6f80c299d8f3b29d6d703ced46aee50d01d",
    )), "lua53.exe", "luac53.exe"),
    ("5.3.6", "x86"): (_artifacts("5.3.6", "x86", (
        "sha1:afcb8bdc066036e264d1f3872a8835415f8f1528",
        "sha1:541f923d9548d502ca581a51bf14a99b005076ee",
    )), "lua53.exe", "luac53.exe"),
    ("5.4.8", "x64"): (_artifacts("5.4.8", "x64", (
        "sha1:bfa45b037d3e21efe4a0b197f89a3a2735733959",
        "sha1:cf0a41a96f54e41639907cd2cf7b0ce9b003cc74",
    )), "lua54.exe", "luac54.exe"),
    ("5.4.8", "x86"): (_artifacts("5.4.8", "x86", (
        "sha1:497fb1df6f44f8080b7e9f01efed217e8c56bf98",
        "sha1:50964884ae5ecddfdef9d09cca6be3607baf0261",
    )), "lua54.exe", "luac54.exe"),
    ("5.5.0", "x64"): (_artifacts("5.5.0", "x64", (
        "sha1:c795954a3953848b9aa30b2320748766569a16cc",
        "sha1:3ec78fc8fd0df65cf5823e9b91df0518ca8fe215",
    )), "lua55.exe", "luac55.exe"),
    ("5.5.0", "x86"): (_artifacts("5.5.0", "x86", (
        "sha1:9fce32b2a4fe7dfd463fff757e7af22d9a6780c1",
        "sha1:28984422cbcf4937d71388254b2b1090b481183c",
    )), "lua55.exe", "luac55.exe"),
}


class LuaRuntimeError(RuntimeError):
    """Lua runtime state/acquisition could not be addressed safely."""


def _exact_puc_line(version: str) -> str:
    match = re.fullmatch(r"(5\.[1-5])\.\d+", version)
    if match is None:
        raise ValueError("PUC Lua version must be an exact 5.1-5.5 patch release.")
    return match.group(1)


def puc_lua_runtime_spec(
    version: str,
    architecture: str,
    *,
    source_sha256: str | None = None,
) -> RuntimeSpec:
    """Create an exact PUC Lua runtime spec without patch substitution."""
    line = _exact_puc_line(version)
    if architecture not in {"x86", "x64"}:
        raise ValueError("PUC Lua Windows backend currently supports x86 or x64.")
    prebuilt = _LUABINARIES.get((version, architecture))
    if prebuilt is not None:
        artifacts, executable, compiler = prebuilt
        metadata: dict[str, object] = {
            "acquisition": "luabinaries",
            "artifacts": [item.to_dict() for item in artifacts],
            "executable_name": executable,
            "compiler_name": compiler,
            "lua_line": line,
        }
    else:
        if source_sha256 is None or not re.fullmatch(r"[0-9a-fA-F]{64}", source_sha256):
            raise ValueError(
                "Exact LuaBinaries artifact is unavailable; an exact official-source "
                "SHA-256 is required instead of silently substituting another patch."
            )
        digits = line.replace(".", "")
        metadata = {
            "acquisition": "source",
            "source_url": f"https://www.lua.org/ftp/lua-{version}.tar.gz",
            "source_sha256": source_sha256.casefold(),
            "executable_name": f"lua{digits}.exe",
            "compiler_name": f"luac{digits}.exe",
            "lua_line": line,
        }
    return RuntimeSpec(
        subject=_SUBJECT,
        version=version,
        backend=_BACKEND,
        backend_key=f"puc:{version}:{architecture}",
        architecture=architecture,
        flavor="puc",
        distribution="lua.org",
        metadata=metadata,
    )


def luajit_runtime_spec(
    version: str,
    architecture: str,
    *,
    source_url: str,
    source_sha256: str,
) -> RuntimeSpec:
    """Create an exact LuaJIT source-build runtime specification."""
    if architecture not in {"x64", "arm64"}:
        raise ValueError("LuaJIT Windows source backend supports x64 or arm64.")
    if not version.strip() or not source_url.strip():
        raise ValueError("LuaJIT version and source URL cannot be empty.")
    if not re.fullmatch(r"[0-9a-fA-F]{64}", source_sha256):
        raise ValueError("LuaJIT source_sha256 must be an exact SHA-256 digest.")
    return RuntimeSpec(
        subject=_SUBJECT,
        version=version,
        backend=_BACKEND,
        backend_key=f"luajit:{version}:{architecture}",
        architecture=architecture,
        flavor="luajit",
        distribution="luajit.org",
        metadata={
            "acquisition": "source",
            "source_url": source_url,
            "source_sha256": source_sha256.casefold(),
            "executable_name": "luajit.exe",
            "compiler_name": None,
        },
    )


def _default_fetch(url: str) -> bytes:
    with urlopen(url, timeout=60) as response:
        return response.read()


def _digest_matches(payload: bytes, expected: str) -> bool:
    if ":" in expected:
        algorithm, wanted = expected.split(":", 1)
    else:
        algorithm, wanted = "sha256", expected
    try:
        actual = hashlib.new(algorithm, payload).hexdigest()
    except ValueError as exc:
        raise LuaRuntimeError(f"Unsupported digest algorithm {algorithm!r}.") from exc
    return actual.casefold() == wanted.casefold()


def _safe_zip_extract(payload: bytes, destination: Path) -> None:
    archive = destination / "_archive.zip"
    archive.write_bytes(payload)
    try:
        with zipfile.ZipFile(archive) as zf:
            root = destination.resolve()
            for member in zf.infolist():
                target = (destination / member.filename).resolve()
                if root not in target.parents and target != root:
                    raise LuaRuntimeError("Lua archive contains an unsafe path.")
            zf.extractall(destination)
    finally:
        archive.unlink(missing_ok=True)


def _safe_tar_extract(payload: bytes, destination: Path) -> Path:
    archive = destination / "_source.tar.gz"
    archive.write_bytes(payload)
    try:
        with tarfile.open(archive, "r:gz") as tf:
            root = destination.resolve()
            members = tf.getmembers()
            for member in members:
                target = (destination / member.name).resolve()
                if root not in target.parents and target != root:
                    raise LuaRuntimeError("Lua source archive contains an unsafe path.")
            try:
                tf.extractall(destination, members=members, filter="data")
            except TypeError:
                # Python versions predating tarfile's filter parameter still
                # use the explicit path traversal checks above.
                tf.extractall(destination, members=members)
    finally:
        archive.unlink(missing_ok=True)
    directories = [
        item for item in destination.iterdir()
        if item.is_dir() and not item.name.startswith(".")
    ]
    if len(directories) != 1:
        raise LuaRuntimeError("Lua source archive must contain one source root.")
    return directories[0]


def _default_architecture_probe(executable: Path) -> str:
    data = executable.read_bytes()
    if len(data) < 0x40 or data[:2] != b"MZ":
        raise LuaRuntimeError(f"{executable!s} is not a PE executable.")
    pe_offset = int.from_bytes(data[0x3C:0x40], "little")
    if len(data) < pe_offset + 6 or data[pe_offset:pe_offset + 4] != b"PE\0\0":
        raise LuaRuntimeError(f"{executable!s} has no valid PE header.")
    machine = int.from_bytes(data[pe_offset + 4:pe_offset + 6], "little")
    return {
        0x014C: "x86",
        0x8664: "x64",
        0xAA64: "arm64",
    }.get(machine, f"pe-machine-{machine:04x}")


def _default_prerequisite_checker(
    context: OperationContext,
    requirement: NativeToolchainRequirement,
) -> OperationResult:
    return check_native_toolchain_requirement(context, requirement)


class LuaPrefixBackend:
    """Per-user exact-prefix backend for PUC Lua and LuaJIT."""

    subject = _SUBJECT
    name = _BACKEND

    def __init__(
        self,
        *,
        runner: Runner = run_process,
        architecture_probe: ArchitectureProbe = _default_architecture_probe,
        fetch_bytes: FetchBytes = _default_fetch,
        prerequisite_checker: PrerequisiteChecker = _default_prerequisite_checker,
        source_builder: SourceBuilder | None = None,
    ) -> None:
        self._runner = runner
        self._architecture_probe = architecture_probe
        self._fetch = fetch_bytes
        self._prerequisite_checker = prerequisite_checker
        self._source_builder = source_builder or self._default_source_builder

    def ownership_scope(self, context: OperationContext) -> str | None:
        self._guard_context(context)
        return f"user:{context.target_account.name.casefold()}"

    def _guard_context(self, context: OperationContext) -> None:
        if context.platform is not Platform.WINDOWS:
            raise LuaRuntimeError("Lua prefix lifecycle is only supported on Windows.")
        if not context.target_account.is_current:
            raise LuaRuntimeError(
                "Lua prefix lifecycle cannot safely mutate a non-current target account."
            )

    def runtime_root(self, context: OperationContext) -> Path:
        self._guard_context(context)
        local = context.target_account.local_app_data
        if local is None:
            configured = context.environment.get("LOCALAPPDATA")
            local = Path(configured) if configured else (
                context.target_account.home / "AppData" / "Local"
            )
        return Path(local) / "Machine-Soul" / "runtimes" / "lua"

    def launcher_root(self, context: OperationContext) -> Path:
        return self.runtime_root(context) / "bin"

    def _prefix(self, context: OperationContext, backend_key: str) -> Path:
        safe = re.sub(r"[^A-Za-z0-9._-]+", "_", backend_key)
        return self.runtime_root(context) / "instances" / safe

    def _manifest(self, prefix: Path) -> Path:
        return prefix / "runtime.json"

    def _selection_path(self, context: OperationContext) -> Path:
        return self.runtime_root(context) / "selected.json"

    def _manifest_payload(self, spec: RuntimeSpec) -> dict[str, object]:
        return {
            "schema": _MANIFEST_SCHEMA,
            "subject": spec.subject,
            "version": spec.version,
            "backend": spec.backend,
            "backend_key": spec.backend_key,
            "architecture": spec.architecture,
            "flavor": spec.flavor,
            "distribution": spec.distribution,
            "metadata": dict(spec.metadata),
        }

    def _runtime_probe(self, spec: RuntimeSpec, executable: Path) -> None:
        expression = (
            "io.write(jit.version)"
            if spec.flavor == "luajit"
            else "io.write(_VERSION)"
        )
        result = self._runner([str(executable), "-e", expression])
        if result.returncode != 0:
            raise LuaRuntimeError(
                f"Runtime probe failed for {executable!s}: {result.stderr[-1000:]}"
            )
        observed = result.stdout.strip()
        if spec.flavor == "puc":
            line = str(spec.metadata.get("lua_line", ""))
            if observed != f"Lua {line}":
                raise LuaRuntimeError(
                    f"PUC Lua probe returned {observed!r}, expected line {line!r}."
                )
        elif not observed.startswith("LuaJIT "):
            raise LuaRuntimeError(
                f"LuaJIT probe returned unexpected identity {observed!r}."
            )

    def _instance_from_manifest(self, prefix: Path) -> RuntimeInstance:
        payload = read_json_state(self._manifest(prefix))
        if payload is None:
            raise LuaRuntimeError(f"Missing runtime manifest in {prefix!s}.")
        if payload.get("schema") != _MANIFEST_SCHEMA:
            raise LuaRuntimeError("Unsupported Lua runtime manifest schema.")
        metadata = payload.get("metadata")
        if not isinstance(metadata, dict):
            raise LuaRuntimeError("Lua runtime manifest metadata must be an object.")
        executable_name = metadata.get("executable_name")
        if not isinstance(executable_name, str) or not executable_name:
            raise LuaRuntimeError("Lua runtime manifest lacks executable_name.")
        executable = prefix / executable_name
        if not executable.is_file():
            raise LuaRuntimeError(f"Lua runtime executable is missing: {executable!s}.")

        spec = RuntimeSpec(
            subject=str(payload["subject"]),
            version=str(payload["version"]),
            backend=str(payload["backend"]),
            backend_key=str(payload["backend_key"]),
            architecture=(
                str(payload["architecture"])
                if payload.get("architecture") not in (None, "")
                else None
            ),
            flavor=(
                str(payload["flavor"])
                if payload.get("flavor") not in (None, "")
                else None
            ),
            distribution=(
                str(payload["distribution"])
                if payload.get("distribution") not in (None, "")
                else None
            ),
            metadata=metadata,
        )
        observed_arch = self._architecture_probe(executable)
        if spec.architecture is not None and observed_arch != spec.architecture:
            raise LuaRuntimeError(
                f"Lua runtime architecture drift: manifest={spec.architecture}, "
                f"executable={observed_arch}."
            )
        self._runtime_probe(spec, executable)
        return RuntimeInstance(
            subject=spec.subject,
            version=spec.version,
            backend=spec.backend,
            backend_key=spec.backend_key,
            architecture=observed_arch,
            flavor=spec.flavor,
            distribution=spec.distribution,
            executable=executable,
            prefix=prefix,
            metadata=dict(metadata),
        )

    def discover(self, context: OperationContext) -> tuple[RuntimeInstance, ...]:
        root = self.runtime_root(context) / "instances"
        if not root.is_dir():
            return ()
        instances: list[RuntimeInstance] = []
        for prefix in sorted((item for item in root.iterdir() if item.is_dir()), key=lambda p: p.name):
            instances.append(self._instance_from_manifest(prefix))
        return tuple(instances)

    def selected_key(self, context: OperationContext) -> str | None:
        state = read_json_state(self._selection_path(context))
        if state is None:
            return None
        key = state.get("backend_key")
        executable = state.get("executable")
        if not isinstance(key, str) or not isinstance(executable, str):
            return None
        launcher = self.launcher_root(context) / "lua.cmd"
        if not launcher.is_file() or not Path(executable).is_file():
            return None
        return key

    def _download_prebuilt(self, spec: RuntimeSpec, staging: Path) -> OperationResult:
        raw_artifacts = spec.metadata.get("artifacts")
        if not isinstance(raw_artifacts, list) or not raw_artifacts:
            return OperationResult.error(
                "lua_artifacts_missing",
                "LuaBinaries acquisition metadata is missing exact archives.",
            )
        try:
            for raw in raw_artifacts:
                if not isinstance(raw, dict):
                    raise LuaRuntimeError("Lua artifact metadata must be an object.")
                url = raw.get("url")
                digest = raw.get("digest")
                if not isinstance(url, str) or not isinstance(digest, str):
                    raise LuaRuntimeError("Lua artifact metadata lacks URL/digest.")
                payload = self._fetch(url)
                if not _digest_matches(payload, digest):
                    raise LuaRuntimeError(f"Lua artifact checksum mismatch for {url}.")
                _safe_zip_extract(payload, staging)
        except Exception as exc:
            return OperationResult.error(
                "lua_prebuilt_acquisition_failed",
                f"LuaBinaries acquisition failed: {exc}",
            )
        return OperationResult.success(
            "lua_prebuilt_acquired",
            "Exact LuaBinaries archives were verified and extracted.",
            changed=True,
        )

    def _source_requirement(self, spec: RuntimeSpec) -> NativeToolchainRequirement:
        target = {
            "x64": "amd64",
            "x86": "x86",
            "arm64": "arm64",
        }.get(spec.architecture or "")
        if target is None:
            raise LuaRuntimeError(
                f"Unsupported source-build architecture {spec.architecture!r}."
            )
        return NativeToolchainRequirement(target_architecture=target)

    def _download_source(self, spec: RuntimeSpec, staging: Path) -> tuple[Path, OperationResult | None]:
        url = spec.metadata.get("source_url")
        digest = spec.metadata.get("source_sha256")
        if not isinstance(url, str) or not isinstance(digest, str):
            return staging, OperationResult.error(
                "lua_source_identity_missing",
                "Source-build runtime lacks exact source URL/SHA-256 identity.",
            )
        try:
            payload = self._fetch(url)
            if not _digest_matches(payload, f"sha256:{digest}"):
                raise LuaRuntimeError("Source archive checksum mismatch.")
            source_parent = staging / "_source"
            source_parent.mkdir(parents=True, exist_ok=True)
            return _safe_tar_extract(payload, source_parent), None
        except Exception as exc:
            return staging, OperationResult.error(
                "lua_source_acquisition_failed",
                f"Exact Lua source acquisition failed: {exc}",
            )

    def _default_source_builder(
        self,
        _context: OperationContext,
        spec: RuntimeSpec,
        source_root: Path,
        staging: Path,
        prerequisite: Mapping[str, object],
    ) -> OperationResult:
        candidates = prerequisite.get("candidates")
        if not isinstance(candidates, list) or not candidates:
            return OperationResult.error(
                "lua_native_toolchain_candidate_missing",
                "Native-toolchain prerequisite succeeded without an exact candidate.",
            )
        candidate = candidates[0]
        if not isinstance(candidate, dict):
            return OperationResult.error(
                "lua_native_toolchain_candidate_invalid",
                "Native-toolchain candidate metadata is malformed.",
            )
        installation_path = candidate.get("installation_path")
        if not isinstance(installation_path, str) or not installation_path:
            return OperationResult.error(
                "lua_native_toolchain_candidate_invalid",
                "Native-toolchain candidate lacks installation_path.",
            )

        vsdev = (
            Path(installation_path)
            / "Common7"
            / "Tools"
            / "VsDevCmd.bat"
        )
        if not vsdev.is_file():
            return OperationResult.error(
                "lua_vsdevcmd_missing",
                "Selected Visual Studio/Build Tools instance lacks VsDevCmd.bat.",
                data={"path": str(vsdev)},
            )

        target = {
            "x64": "amd64",
            "x86": "x86",
            "arm64": "arm64",
        }.get(spec.architecture or "")
        if target is None:
            return OperationResult.error(
                "lua_source_architecture_unsupported",
                f"Unsupported source-build architecture {spec.architecture!r}.",
            )
        host = "arm64" if target == "arm64" else "amd64"

        src = source_root / "src"
        if not src.is_dir():
            return OperationResult.error(
                "lua_source_layout_invalid",
                "Lua source archive does not contain the expected src directory.",
            )

        script = source_root / "_machine_soul_build.cmd"
        lines = [
            "@echo off",
            "setlocal",
            f'call "{vsdev}" -no_logo -arch={target} -host_arch={host}',
            "if errorlevel 1 exit /b %errorlevel%",
            f'pushd "{src}"',
            "if errorlevel 1 exit /b %errorlevel%",
        ]

        if spec.flavor == "puc":
            line = str(spec.metadata.get("lua_line", "")).replace(".", "")
            library_name = f"lua{line}"
            all_library_sources = sorted(
                item.name
                for item in src.glob("l*.c")
                if item.name not in {"lua.c", "luac.c"}
            )
            if not all_library_sources:
                return OperationResult.error(
                    "lua_source_layout_invalid",
                    "PUC Lua source tree has no library C sources.",
                )
            runtime_library_sources = {
                "lauxlib.c",
                "lbaselib.c",
                "lcorolib.c",
                "ldblib.c",
                "liolib.c",
                "lmathlib.c",
                "loadlib.c",
                "loslib.c",
                "lstrlib.c",
                "ltablib.c",
                "lutf8lib.c",
                "linit.c",
            }
            core_sources = [
                name for name in all_library_sources
                if name not in runtime_library_sources
            ]
            all_objects = [Path(name).with_suffix(".obj").name for name in all_library_sources]
            core_objects = [Path(name).with_suffix(".obj").name for name in core_sources]
            quoted_sources = " ".join(f'"{name}"' for name in all_library_sources)
            quoted_objects = " ".join(f'"{name}"' for name in all_objects)
            quoted_core_objects = " ".join(f'"{name}"' for name in core_objects)

            lines.extend([
                (
                    "cl /nologo /O2 /MD /DLUA_USE_WINDOWS /DLUA_BUILD_AS_DLL "
                    f"/c {quoted_sources}"
                ),
                "if errorlevel 1 exit /b %errorlevel%",
                (
                    f"link /nologo /dll /out:{library_name}.dll "
                    f"/implib:{library_name}.lib {quoted_objects}"
                ),
                "if errorlevel 1 exit /b %errorlevel%",
                (
                    "cl /nologo /O2 /MD /DLUA_USE_WINDOWS /DLUA_USE_DLL "
                    f"/Fe:{spec.metadata['executable_name']} lua.c {library_name}.lib"
                ),
                "if errorlevel 1 exit /b %errorlevel%",
                (
                    "cl /nologo /O2 /MD /DLUA_USE_WINDOWS "
                    f"/Fe:{spec.metadata['compiler_name']} luac.c {quoted_core_objects}"
                ),
                "if errorlevel 1 exit /b %errorlevel%",
            ])
        elif spec.flavor == "luajit":
            lines.extend([
                "call msvcbuild.bat",
                "if errorlevel 1 exit /b %errorlevel%",
            ])
        else:
            return OperationResult.error(
                "lua_runtime_flavor_unsupported",
                f"Unsupported Lua source flavor {spec.flavor!r}.",
            )

        lines.extend(["popd", "exit /b 0"])
        script.write_text("\r\n".join(lines) + "\r\n", encoding="utf-8", newline="")

        result = self._runner(["cmd.exe", "/d", "/c", str(script)])
        if result.returncode != 0:
            return OperationResult.error(
                "lua_source_build_failed",
                f"Lua source build failed with exit code {result.returncode}.",
                data={"stderr": result.stderr[-2000:], "toolchain": candidate},
            )

        try:
            if spec.flavor == "puc":
                line = str(spec.metadata["lua_line"]).replace(".", "")
                names = [
                    str(spec.metadata["executable_name"]),
                    str(spec.metadata["compiler_name"]),
                    f"lua{line}.dll",
                    f"lua{line}.lib",
                ]
                headers = ["lua.h", "luaconf.h", "lauxlib.h", "lualib.h"]
            else:
                names = ["luajit.exe", "lua51.dll", "lua51.lib"]
                headers = ["lua.h", "luaconf.h", "lauxlib.h", "lualib.h", "luajit.h"]

            for name in names:
                source = src / name
                if not source.is_file():
                    raise LuaRuntimeError(f"Expected source-build output is missing: {source!s}")
                shutil.copy2(source, staging / name)

            include = staging / "include"
            include.mkdir(parents=True, exist_ok=True)
            for name in headers:
                source = src / name
                if source.is_file():
                    shutil.copy2(source, include / name)
        except Exception as exc:
            return OperationResult.error(
                "lua_source_build_output_missing",
                f"Lua source build output could not be staged: {exc}",
            )

        return OperationResult.success(
            "lua_source_built",
            "Exact Lua source was built with the selected native toolchain instance.",
            changed=True,
            data={"toolchain": candidate},
        )

    def _build_source(
        self,
        context: OperationContext,
        spec: RuntimeSpec,
        staging: Path,
    ) -> OperationResult:
        requirement = self._source_requirement(spec)
        prerequisite = self._prerequisite_checker(context, requirement)
        if prerequisite.status is not ResultStatus.SUCCESS:
            return OperationResult.failure(
                "lua_native_toolchain_missing",
                "Exact Lua source build requires a satisfying native toolchain.",
                data={"prerequisite": prerequisite.to_dict()},
            )
        source_root, error = self._download_source(spec, staging)
        if error is not None:
            return error
        result = self._source_builder(
            context,
            spec,
            source_root,
            staging,
            prerequisite.data,
        )
        if result.status is ResultStatus.SUCCESS:
            shutil.rmtree(staging / "_source", ignore_errors=True)
        return result

    def install(self, context: OperationContext, spec: RuntimeSpec) -> OperationResult:
        if spec.subject != self.subject or spec.backend != self.name:
            return OperationResult.error(
                "lua_runtime_spec_mismatch",
                "Lua runtime specification does not target this prefix backend.",
                data={"spec": spec.to_dict()},
            )
        prefix = self._prefix(context, spec.backend_key)
        if prefix.exists():
            return OperationResult.failure(
                "lua_prefix_already_exists",
                "Exact Lua runtime prefix already exists and must be discovered/adopted.",
                data={"prefix": str(prefix), "backend_key": spec.backend_key},
            )
        if context.dry_run:
            return OperationResult.success(
                "would_install_lua_runtime",
                "Exact Lua runtime would be acquired into a private versioned prefix.",
                data={
                    "prefix": str(prefix),
                    "backend_key": spec.backend_key,
                    "acquisition": spec.metadata.get("acquisition"),
                },
            )

        root = self.runtime_root(context)
        instances_root = root / "instances"
        instances_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix=".lua-stage-", dir=instances_root) as raw:
            staging = Path(raw)
            acquisition = spec.metadata.get("acquisition")
            if acquisition == "luabinaries":
                result = self._download_prebuilt(spec, staging)
            elif acquisition == "source":
                result = self._build_source(context, spec, staging)
            else:
                return OperationResult.error(
                    "lua_acquisition_unknown",
                    f"Unsupported Lua acquisition kind {acquisition!r}.",
                )
            if result.status is not ResultStatus.SUCCESS:
                return result

            executable_name = spec.metadata.get("executable_name")
            if not isinstance(executable_name, str) or not (staging / executable_name).is_file():
                return OperationResult.error(
                    "lua_acquisition_incomplete",
                    "Lua acquisition completed without the expected executable.",
                    data={"expected": str(staging / str(executable_name))},
                )
            write_json_state(staging / "runtime.json", self._manifest_payload(spec))
            # TemporaryDirectory owns staging, so move its content through a
            # separate sibling before the context cleans up the original name.
            finalized = instances_root / (prefix.name + ".new")
            if finalized.exists():
                shutil.rmtree(finalized)
            os.replace(staging, finalized)
            os.replace(finalized, prefix)

        return OperationResult.success(
            "lua_runtime_installed",
            "Exact Lua runtime was installed into its private versioned prefix.",
            changed=True,
            data={"prefix": str(prefix), "backend_key": spec.backend_key},
        )

    def _write_launcher(self, path: Path, executable: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            '@echo off\r\n"' + str(executable) + '" %*\r\n',
            encoding="utf-8",
            newline="",
        )

    def select(
        self,
        context: OperationContext,
        instance: RuntimeInstance,
    ) -> OperationResult:
        if instance.backend != self.name or instance.executable is None:
            return OperationResult.error(
                "lua_runtime_instance_mismatch",
                "Refusing to select a runtime not owned by the Lua prefix backend.",
            )
        launcher = self.launcher_root(context)
        if context.dry_run:
            return OperationResult.success(
                "would_select_lua_runtime",
                "Generic Machine-Soul Lua launcher would target the exact runtime.",
                data={
                    "backend_key": instance.backend_key,
                    "launcher": str(launcher / "lua.cmd"),
                    "target": str(instance.executable),
                },
            )
        self._write_launcher(launcher / "lua.cmd", instance.executable)
        compiler_name = instance.metadata.get("compiler_name")
        compiler = (
            instance.prefix / compiler_name
            if instance.prefix is not None and isinstance(compiler_name, str)
            else None
        )
        if compiler is not None and compiler.is_file():
            self._write_launcher(launcher / "luac.cmd", compiler)
        else:
            (launcher / "luac.cmd").unlink(missing_ok=True)
        write_json_state(
            self._selection_path(context),
            {
                "schema": 1,
                "backend_key": instance.backend_key,
                "executable": str(instance.executable),
                "launcher_root": str(launcher),
            },
        )
        return OperationResult.success(
            "lua_runtime_selected",
            "Generic Machine-Soul Lua launcher now targets the exact runtime.",
            changed=True,
            data={"backend_key": instance.backend_key, "launcher_root": str(launcher)},
        )

    def uninstall(
        self,
        context: OperationContext,
        instance: RuntimeInstance,
    ) -> OperationResult:
        if instance.backend != self.name or instance.prefix is None:
            return OperationResult.error(
                "lua_runtime_instance_mismatch",
                "Refusing to uninstall a runtime not owned by the Lua prefix backend.",
            )
        expected = self._prefix(context, instance.backend_key)
        if instance.prefix != expected:
            return OperationResult.error(
                "lua_runtime_prefix_mismatch",
                "Runtime prefix is outside the exact Machine-Soul-owned location.",
                data={"expected": str(expected), "observed": str(instance.prefix)},
            )
        if self.selected_key(context) == instance.backend_key:
            return OperationResult.failure(
                "lua_runtime_still_selected",
                "Refusing to remove the runtime while it is still selected.",
            )
        if context.dry_run:
            return OperationResult.success(
                "would_uninstall_lua_runtime",
                "Exact Lua runtime prefix would be removed.",
                data={"prefix": str(expected), "backend_key": instance.backend_key},
            )
        shutil.rmtree(expected)
        return OperationResult.success(
            "lua_runtime_uninstalled",
            "Exact Lua runtime prefix was removed.",
            changed=True,
            data={"prefix": str(expected), "backend_key": instance.backend_key},
        )
