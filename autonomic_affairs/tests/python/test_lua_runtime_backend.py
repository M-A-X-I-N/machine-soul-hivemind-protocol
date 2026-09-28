from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from annexation_procedures.lua_runtime import (
    LuaPrefixBackend,
    luajit_runtime_spec,
    puc_lua_runtime_spec,
)
from annexation_procedures.model import (
    NativeToolchainRequirement,
    OperationContext,
    OperationResult,
    Platform,
    RuntimeDesiredState,
    RuntimeSpec,
    TargetAccount,
)
from annexation_procedures.process import ProcessResult
from annexation_procedures.runtime import reconcile_runtime


class LuaFixture:
    def runner(self, argv: list[str]) -> ProcessResult:
        executable = argv[0]
        expression = argv[-1]
        normalized = str(executable).replace("\\", "/")
        if "io.write(_VERSION)" in expression:
            match = __import__("re").search(r"puc_(5\.[1-5]\.\d+)_", normalized)
            if match is None:
                return ProcessResult(91, "", "unknown PUC runtime")
            line = match.group(1).rsplit(".", 1)[0]
            return ProcessResult(0, f"Lua {line}", "")
        if "io.write(jit.version)" in expression:
            if "luajit_" not in normalized:
                return ProcessResult(92, "", "unknown LuaJIT runtime")
            return ProcessResult(0, "LuaJIT 2.1", "")
        return ProcessResult(93, "", "unexpected runtime probe")

    def architecture(self, executable: Path) -> str:
        marker = executable.parent / "arch.txt"
        return marker.read_text(encoding="utf-8").strip()

    def builder(
        self,
        _context: OperationContext,
        spec: RuntimeSpec,
        _source_root: Path,
        staging: Path,
        _prerequisite: dict[str, object],
    ) -> OperationResult:
        executable = staging / str(spec.metadata["executable_name"])
        executable.write_bytes(b"MZfake")
        (staging / "arch.txt").write_text(str(spec.architecture), encoding="utf-8")
        if spec.flavor == "puc":
            compiler = spec.metadata.get("compiler_name")
            if isinstance(compiler, str):
                (staging / compiler).write_bytes(b"MZfake")
        return OperationResult.success("fixture_built", "fixture built", changed=True)


class LuaPrefixBackendTests(unittest.TestCase):
    def _context(self, root: Path) -> OperationContext:
        home = root / "fixture"
        return OperationContext(
            repository_root=root,
            platform=Platform.WINDOWS,
            host="fixture-host",
            target_account=TargetAccount(
                "fixture",
                home,
                True,
                local_app_data=home / "AppData" / "Local",
            ),
        )

    def _source_spec(
        self,
        version: str,
        line: str,
        architecture: str = "x64",
    ) -> RuntimeSpec:
        payload = self._source_archive_bytes()
        spec = puc_lua_runtime_spec(
            version,
            architecture,
            source_sha256=hashlib.sha256(payload).hexdigest(),
        )
        return spec

    def _backend(self, fixture: LuaFixture) -> LuaPrefixBackend:
        source_payload = self._source_archive_bytes()
        return LuaPrefixBackend(
            runner=fixture.runner,
            architecture_probe=fixture.architecture,
            fetch_bytes=lambda _url: source_payload,
            prerequisite_checker=lambda _context, requirement: OperationResult.success(
                "native_toolchain_requirement_satisfied",
                "fixture toolchain",
                data={
                    "requirement": requirement.to_dict(),
                    "candidates": [{"installation_path": r"C:\VS"}],
                },
            ),
            source_builder=fixture.builder,
        )

    def _source_archive_bytes(self) -> bytes:
        import gzip
        import io
        import tarfile

        buffer = io.BytesIO()
        with gzip.GzipFile(fileobj=buffer, mode="wb", mtime=0) as gz:
            with tarfile.open(fileobj=gz, mode="w") as tf:
                payload = b"fixture"
                info = tarfile.TarInfo("source/README")
                info.size = len(payload)
                info.mtime = 0
                tf.addfile(info, io.BytesIO(payload))
        return buffer.getvalue()

    def test_prebuilt_catalog_never_substitutes_patch_versions(self) -> None:
        prebuilt = puc_lua_runtime_spec("5.4.8", "x64")
        self.assertEqual("luabinaries", prebuilt.metadata["acquisition"])

        with self.assertRaises(ValueError):
            puc_lua_runtime_spec("5.4.9", "x64")

        source = puc_lua_runtime_spec(
            "5.4.9",
            "x64",
            source_sha256="b" * 64,
        )
        self.assertEqual("source", source.metadata["acquisition"])
        self.assertIn("lua-5.4.9.tar.gz", source.metadata["source_url"])

    def test_puc_lines_51_through_55_are_representable(self) -> None:
        versions = ("5.1.5", "5.2.4", "5.3.6", "5.4.9", "5.5.1")
        for version in versions:
            kwargs = {} if (version, "x64") in {
                ("5.1.5", "x64"),
                ("5.2.4", "x64"),
                ("5.3.6", "x64"),
            } else {"source_sha256": "c" * 64}
            spec = puc_lua_runtime_spec(version, "x64", **kwargs)
            self.assertEqual(version, spec.version)
            self.assertEqual("puc", spec.flavor)

    def test_luajit_is_a_distinct_flavor(self) -> None:
        spec = luajit_runtime_spec(
            "2.1.rolling-2026-09",
            "x64",
            source_url="https://example.invalid/luajit.tar.gz",
            source_sha256="d" * 64,
        )
        self.assertEqual("luajit", spec.flavor)
        self.assertTrue(spec.backend_key.startswith("luajit:"))

    def test_source_multiversion_reconcile_and_default_routing(self) -> None:
        fixture = LuaFixture()
        with tempfile.TemporaryDirectory() as raw:
            context = self._context(Path(raw))
            backend = self._backend(fixture)
            specs = (
                self._source_spec("5.4.9", "5.4"),
                self._source_spec("5.5.1", "5.5"),
            )
            desired = RuntimeDesiredState(
                subject="lua",
                backend=backend.name,
                instances=specs,
                selected_key=specs[0].backend_key,
            )
            result = reconcile_runtime(context, backend, desired)
            instances = backend.discover(context)
            launcher = backend.launcher_root(context) / "lua.cmd"
            selected = json.loads(
                (backend.runtime_root(context) / "selected.json").read_text(encoding="utf-8")
            )
            launcher_text = launcher.read_text(encoding="utf-8")

        self.assertEqual("runtime_reconciled", result.code, result.to_dict())
        self.assertEqual({"5.4.9", "5.5.1"}, {item.version for item in instances})
        self.assertEqual({"x64"}, {item.architecture for item in instances})
        self.assertTrue(launcher_text.startswith("@echo off"))
        self.assertEqual(specs[0].backend_key, selected["backend_key"])

    def test_selected_change_does_not_reinstall(self) -> None:
        fixture = LuaFixture()
        with tempfile.TemporaryDirectory() as raw:
            context = self._context(Path(raw))
            backend = self._backend(fixture)
            first = self._source_spec("5.4.9", "5.4")
            second = self._source_spec("5.5.1", "5.5")
            reconcile_runtime(
                context,
                backend,
                RuntimeDesiredState(
                    subject="lua",
                    backend=backend.name,
                    instances=(first, second),
                    selected_key=first.backend_key,
                ),
            )
            before = {item.backend_key: item.prefix for item in backend.discover(context)}
            result = reconcile_runtime(
                context,
                backend,
                RuntimeDesiredState(
                    subject="lua",
                    backend=backend.name,
                    instances=(first, second),
                    selected_key=second.backend_key,
                ),
            )
            after = {item.backend_key: item.prefix for item in backend.discover(context)}

        self.assertEqual("runtime_reconciled", result.code, result.to_dict())
        self.assertEqual(before, after)

    def test_exact_prefix_removal_preserves_other_version(self) -> None:
        fixture = LuaFixture()
        with tempfile.TemporaryDirectory() as raw:
            context = self._context(Path(raw))
            backend = self._backend(fixture)
            first = self._source_spec("5.4.9", "5.4")
            second = self._source_spec("5.5.1", "5.5")
            reconcile_runtime(
                context,
                backend,
                RuntimeDesiredState(
                    subject="lua",
                    backend=backend.name,
                    instances=(first, second),
                    selected_key=second.backend_key,
                ),
            )
            first_prefix = backend._prefix(context, first.backend_key)
            second_prefix = backend._prefix(context, second.backend_key)

            result = reconcile_runtime(
                context,
                backend,
                RuntimeDesiredState(
                    subject="lua",
                    backend=backend.name,
                    instances=(second,),
                    selected_key=second.backend_key,
                ),
            )
            first_exists = first_prefix.exists()
            second_exists = second_prefix.exists()

        self.assertEqual("runtime_reconciled", result.code, result.to_dict())
        self.assertFalse(first_exists)
        self.assertTrue(second_exists)

    def test_source_build_requires_native_prerequisite(self) -> None:
        fixture = LuaFixture()
        with tempfile.TemporaryDirectory() as raw:
            context = self._context(Path(raw))
            backend = LuaPrefixBackend(
                runner=fixture.runner,
                architecture_probe=fixture.architecture,
                fetch_bytes=lambda _url: self._source_archive_bytes(),
                prerequisite_checker=lambda _context, _requirement: OperationResult.failure(
                    "native_toolchain_requirement_missing",
                    "missing",
                ),
                source_builder=fixture.builder,
            )
            spec = self._source_spec("5.4.9", "5.4")
            result = backend.install(context, spec)

        self.assertEqual("lua_native_toolchain_missing", result.code)
        self.assertFalse(result.changed)

    def test_luajit_source_builder_uses_separate_identity(self) -> None:
        fixture = LuaFixture()
        with tempfile.TemporaryDirectory() as raw:
            context = self._context(Path(raw))
            backend = self._backend(fixture)
            spec = luajit_runtime_spec(
                "2.1.rolling-fixture",
                "x64",
                source_url="https://example.invalid/luajit.tar.gz",
                source_sha256="e" * 64,
            )
            result = reconcile_runtime(
                context,
                backend,
                RuntimeDesiredState(
                    subject="lua",
                    backend=backend.name,
                    instances=(spec,),
                    selected_key=spec.backend_key,
                ),
            )
            instances = backend.discover(context)

        self.assertEqual("runtime_reconciled", result.code, result.to_dict())
        self.assertEqual("luajit", instances[0].flavor)
        self.assertEqual("2.1.rolling-fixture", instances[0].version)


if __name__ == "__main__":
    unittest.main()
