from __future__ import annotations

import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from annexation_procedures.configuration_verification import verify_config
from annexation_procedures.model import (
    Application,
    ConfigurationFile,
    ConfigurationVerificationPlan,
    EvidenceStrength,
    HomeRelativeDestination,
    OperationContext,
    Platform,
    PlatformDeclaration,
    ShellStartupVerification,
    Support,
    Operation,
    TargetAccount,
)
from annexation_procedures.process import ProcessResult
from annexation_procedures.shell_verification import verify_shell_startup


class ShellVerificationTests(unittest.TestCase):
    def _context(
        self,
        root: Path,
        *,
        platform: Platform = Platform.LINUX,
        current: bool = True,
    ) -> OperationContext:
        home = root / "home"
        home.mkdir(parents=True, exist_ok=True)
        env = dict(os.environ)
        env["HOME"] = str(home)
        return OperationContext(
            repository_root=root,
            platform=platform,
            host="fixture_host",
            target_account=TargetAccount(
                "fixture_user",
                home,
                current,
                root / "local" if platform is Platform.WINDOWS else None,
            ),
            environment=env,
        )

    def _declaration(self, shell: str, leaf: str) -> PlatformDeclaration:
        return PlatformDeclaration(
            platform=Platform.LINUX,
            capabilities={Operation.VERIFY_CONFIG: Support.SUPPORTED},
            configurations=(
                ConfigurationFile(
                    name="main",
                    source_leaf=leaf,
                    destination=HomeRelativeDestination(leaf),
                ),
            ),
            configuration_verification=ConfigurationVerificationPlan(
                (ShellStartupVerification(shell, shell, "main"),)
            ),
        )

    def test_bash_trace_requires_positive_and_negative_control(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            context = self._context(root)
            destination = context.target_account.home / ".bashrc"
            destination.write_text("true\n", encoding="utf-8")
            declaration = self._declaration("bash", ".bashrc")
            app = Application(id="bash", display_name="Bash", platforms=(declaration,))

            def fake_run(argv, **kwargs):
                if "--norc" in argv:
                    return ProcessResult(0, "", "")
                return ProcessResult(0, "", f"+{destination}:1: true\n")

            with patch(
                "annexation_procedures.shell_verification.shutil.which",
                return_value="/bin/bash",
            ), patch(
                "annexation_procedures.shell_verification.run_process",
                side_effect=fake_run,
            ):
                result = verify_config(app, declaration, context)

        self.assertEqual("config_effective", result.code)
        assessment = result.data["assessment"]
        self.assertEqual("runtime", assessment["strongest_evidence"])
        data = assessment["observations"][0]["data"]
        self.assertTrue(data["ordinary_startup_attributed"])
        self.assertFalse(data["startup_disabled_attributed"])

    def test_bash_negative_control_blocks_false_runtime_proof(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            context = self._context(root)
            destination = context.target_account.home / ".bashrc"
            destination.write_text("true\n", encoding="utf-8")
            declaration = self._declaration("bash", ".bashrc")
            strategy = declaration.configuration_verification.strategies[0]

            with patch(
                "annexation_procedures.shell_verification.shutil.which",
                return_value="/bin/bash",
            ), patch(
                "annexation_procedures.shell_verification.run_process",
                return_value=ProcessResult(0, "", f"+{destination}:1: true\n"),
            ):
                observation = verify_shell_startup(
                    Application(id="bash", display_name="Bash", platforms=(declaration,)),
                    declaration,
                    context,
                    strategy,
                )

        self.assertEqual(EvidenceStrength.RUNTIME, observation.evidence)
        self.assertEqual("not_effective", observation.supports.value)
        self.assertTrue(observation.data["startup_disabled_attributed"])

    def test_zsh_trace_uses_source_attribution(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            context = self._context(root)
            destination = context.target_account.home / ".zshrc"
            destination.write_text("true\n", encoding="utf-8")
            declaration = self._declaration("zsh", ".zshrc")
            strategy = declaration.configuration_verification.strategies[0]

            def fake_run(argv, **kwargs):
                if "-f" in argv:
                    return ProcessResult(0, "", "")
                return ProcessResult(0, "", f"+{destination}:1: true\n")

            with patch(
                "annexation_procedures.shell_verification.shutil.which",
                return_value="/bin/zsh",
            ), patch(
                "annexation_procedures.shell_verification.run_process",
                side_effect=fake_run,
            ):
                observation = verify_shell_startup(
                    Application(id="zsh", display_name="Zsh", platforms=(declaration,)),
                    declaration,
                    context,
                    strategy,
                )

        self.assertEqual(EvidenceStrength.RUNTIME, observation.evidence)
        self.assertEqual("effective", observation.supports.value)

    def test_fish_is_deliberately_resolution_strength(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            context = self._context(root)
            destination = context.target_account.home / ".config/fish/config.fish"
            destination.parent.mkdir(parents=True)
            destination.write_text("true\n", encoding="utf-8")
            declaration = PlatformDeclaration(
                platform=Platform.LINUX,
                capabilities={Operation.VERIFY_CONFIG: Support.SUPPORTED},
                configurations=(
                    ConfigurationFile(
                        "main",
                        "config.fish",
                        HomeRelativeDestination(".config/fish/config.fish"),
                    ),
                ),
                configuration_verification=ConfigurationVerificationPlan(
                    (ShellStartupVerification("fish", "fish"),)
                ),
            )
            strategy = declaration.configuration_verification.strategies[0]

            with patch(
                "annexation_procedures.shell_verification.shutil.which",
                return_value="/usr/bin/fish",
            ):
                observation = verify_shell_startup(
                    Application(id="fish", display_name="Fish", platforms=(declaration,)),
                    declaration,
                    context,
                    strategy,
                )

        self.assertEqual(EvidenceStrength.RESOLUTION, observation.evidence)
        self.assertEqual("effective", observation.supports.value)
        self.assertIn("does not provide a trustworthy source-path attribution", observation.data["reason"])

    def test_missing_shell_is_indeterminate_not_not_effective(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            context = self._context(root)
            declaration = self._declaration("bash", ".bashrc")
            strategy = declaration.configuration_verification.strategies[0]

            with patch(
                "annexation_procedures.shell_verification.shutil.which",
                return_value=None,
            ):
                observation = verify_shell_startup(
                    Application(id="bash", display_name="Bash", platforms=(declaration,)),
                    declaration,
                    context,
                    strategy,
                )

        self.assertEqual(EvidenceStrength.RESOLUTION, observation.evidence)
        self.assertEqual("indeterminate", observation.supports.value)

    def test_windows_expected_path_is_translated_before_trace_matching(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            context = self._context(root, platform=Platform.WINDOWS)
            declaration = PlatformDeclaration(
                platform=Platform.WINDOWS,
                capabilities={Operation.VERIFY_CONFIG: Support.SUPPORTED},
                configurations=(
                    ConfigurationFile(
                        "main",
                        ".bashrc",
                        HomeRelativeDestination(".bashrc"),
                    ),
                ),
                configuration_verification=ConfigurationVerificationPlan(
                    (ShellStartupVerification("bash", "bash"),)
                ),
            )
            strategy = declaration.configuration_verification.strategies[0]

            def fake_which(command, **kwargs):
                return {
                    "bash": r"C:\msys64\usr\bin\bash.exe",
                    "cygpath": r"C:\msys64\usr\bin\cygpath.exe",
                }.get(command)

            def fake_run(argv, **kwargs):
                if "cygpath.exe" in argv[0]:
                    return ProcessResult(0, "/home/fixture/.bashrc\n", "")
                if "--norc" in argv:
                    return ProcessResult(0, "", "")
                return ProcessResult(0, "", "+/home/fixture/.bashrc:1: true\n")

            with patch(
                "annexation_procedures.shell_verification.shutil.which",
                side_effect=fake_which,
            ), patch(
                "annexation_procedures.shell_verification.run_process",
                side_effect=fake_run,
            ):
                observation = verify_shell_startup(
                    Application(id="bash", display_name="Bash", platforms=(declaration,)),
                    declaration,
                    context,
                    strategy,
                )

        self.assertEqual("effective", observation.supports.value)
        self.assertEqual("/home/fixture/.bashrc", observation.data["expected_trace_path"])

    @unittest.skipUnless(os.name == "posix" and shutil.which("bash"), "Bash integration requires POSIX Bash")
    def test_real_bash_startup_attributes_bashrc_without_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            context = self._context(root)
            destination = context.target_account.home / ".bashrc"
            original = "true\n"
            destination.write_text(original, encoding="utf-8")
            declaration = self._declaration("bash", ".bashrc")
            app = Application(id="bash", display_name="Bash", platforms=(declaration,))

            result = verify_config(app, declaration, context)

            self.assertEqual("config_effective", result.code, result.to_dict())
            self.assertEqual(original, destination.read_text(encoding="utf-8"))
            self.assertFalse((context.target_account.home / ".bash_history").exists())


if __name__ == "__main__":
    unittest.main()
