from __future__ import annotations

import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from annexation.configuration_verification import verify_config
from annexation.model import (
    Application,
    ConfigurationFile,
    ConfigurationVerificationPlan,
    HomeRelativeDestination,
    LocalAppDataRelativeDestination,
    OhMyPoshVerification,
    Operation,
    OperationContext,
    Platform,
    PlatformDeclaration,
    Support,
    TargetAccount,
)
from annexation.process import ProcessResult


class OhMyPoshVerificationTests(unittest.TestCase):
    def _fixture(
        self,
        root: Path,
        *,
        platform: Platform = Platform.LINUX,
        consumers: tuple[str, ...] = ("bash",),
    ):
        home = root / "home"
        local = root / "local"
        home.mkdir(parents=True, exist_ok=True)
        local.mkdir(parents=True, exist_ok=True)
        source = (
            root
            / "assimilation"
            / "oh_my_posh"
            / "default"
            / "common"
            / "theme.omp.json"
        )
        source.parent.mkdir(parents=True)
        source.write_text('{"version": 4}\n', encoding="utf-8")
        destination = (
            HomeRelativeDestination(".config/oh-my-posh/theme.omp.json")
            if platform is Platform.LINUX
            else LocalAppDataRelativeDestination("oh-my-posh/theme.omp.json")
        )
        executable = "oh-my-posh" if platform is Platform.LINUX else "oh-my-posh.exe"
        declaration = PlatformDeclaration(
            platform=platform,
            capabilities={Operation.VERIFY_CONFIG: Support.SUPPORTED},
            configurations=(
                ConfigurationFile("theme", "theme.omp.json", destination),
            ),
            configuration_verification=ConfigurationVerificationPlan(
                (OhMyPoshVerification(executable, consumers),)
            ),
        )
        app = Application(
            id="oh_my_posh",
            display_name="Oh My Posh",
            platforms=(declaration,),
        )
        env = dict(os.environ)
        env["PATH"] = "fixture"
        env["HOME"] = str(home)
        context = OperationContext(
            repository_root=root,
            platform=platform,
            host="fixture_host",
            target_account=TargetAccount(
                "fixture_user",
                home,
                True,
                local if platform is Platform.WINDOWS else None,
            ),
            environment=env,
        )
        return app, declaration, context, source

    def test_valid_theme_without_consumer_keeps_application_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            app, declaration, context, source = self._fixture(root)

            def fake_which(command, **kwargs):
                return "/opt/omp/oh-my-posh" if command == "oh-my-posh" else None

            with patch(
                "annexation.oh_my_posh_verification.shutil.which",
                side_effect=fake_which,
            ), patch(
                "annexation.oh_my_posh_verification.run_process",
                return_value=ProcessResult(0, "rendered prompt", ""),
            ):
                result = verify_config(app, declaration, context)

        self.assertEqual("config_effective", result.code)
        assessment = result.data["assessment"]
        self.assertEqual("application", assessment["strongest_evidence"])
        self.assertEqual(1, len(assessment["observations"]))
        self.assertEqual(str(source), assessment["observations"][0]["data"]["theme"])

    def test_invalid_theme_is_not_effective_at_application_strength(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            app, declaration, context, _ = self._fixture(root, consumers=())

            with patch(
                "annexation.oh_my_posh_verification.shutil.which",
                return_value="/opt/omp/oh-my-posh",
            ), patch(
                "annexation.oh_my_posh_verification.run_process",
                return_value=ProcessResult(1, "", "invalid json config: parse failed"),
            ):
                result = verify_config(app, declaration, context)

        self.assertEqual("config_not_effective", result.code)
        self.assertEqual("application", result.data["assessment"]["strongest_evidence"])

    def test_expected_bash_selected_theme_is_runtime_effective(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            app, declaration, context, source = self._fixture(root, consumers=("bash",))

            def fake_which(command, **kwargs):
                return {
                    "oh-my-posh": "/opt/omp/oh-my-posh",
                    "bash": "/bin/bash",
                }.get(command)

            def fake_run(argv, **kwargs):
                if argv[0] == "/opt/omp/oh-my-posh":
                    return ProcessResult(0, "rendered", "")
                return ProcessResult(0, "__MSHP_POSH_THEME__=" + str(source) + "\n", "")

            with patch(
                "annexation.oh_my_posh_verification.shutil.which",
                side_effect=fake_which,
            ), patch(
                "annexation.oh_my_posh_verification.run_process",
                side_effect=fake_run,
            ):
                result = verify_config(app, declaration, context)

        self.assertEqual("config_effective", result.code)
        assessment = result.data["assessment"]
        self.assertEqual("runtime", assessment["strongest_evidence"])
        self.assertTrue(assessment["observations"][1]["data"]["matches"])

    def test_wrong_selected_theme_overrides_valid_render(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            app, declaration, context, _ = self._fixture(root, consumers=("bash",))
            wrong = root / "wrong-theme.omp.json"

            def fake_which(command, **kwargs):
                return {
                    "oh-my-posh": "/opt/omp/oh-my-posh",
                    "bash": "/bin/bash",
                }.get(command)

            def fake_run(argv, **kwargs):
                if argv[0] == "/opt/omp/oh-my-posh":
                    return ProcessResult(0, "rendered", "")
                return ProcessResult(0, "__MSHP_POSH_THEME__=" + str(wrong) + "\n", "")

            with patch(
                "annexation.oh_my_posh_verification.shutil.which",
                side_effect=fake_which,
            ), patch(
                "annexation.oh_my_posh_verification.run_process",
                side_effect=fake_run,
            ):
                result = verify_config(app, declaration, context)

        self.assertEqual("config_not_effective", result.code)
        self.assertEqual("runtime", result.data["assessment"]["strongest_evidence"])

    def test_conflicting_consumers_are_runtime_indeterminate(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            app, declaration, context, source = self._fixture(
                root,
                consumers=("bash", "zsh"),
            )
            wrong = root / "wrong-theme.omp.json"

            def fake_which(command, **kwargs):
                return {
                    "oh-my-posh": "/opt/omp/oh-my-posh",
                    "bash": "/bin/bash",
                    "zsh": "/bin/zsh",
                }.get(command)

            def fake_run(argv, **kwargs):
                if argv[0] == "/opt/omp/oh-my-posh":
                    return ProcessResult(0, "rendered", "")
                selected = source if argv[0] == "/bin/bash" else wrong
                return ProcessResult(0, "__MSHP_POSH_THEME__=" + str(selected) + "\n", "")

            with patch(
                "annexation.oh_my_posh_verification.shutil.which",
                side_effect=fake_which,
            ), patch(
                "annexation.oh_my_posh_verification.run_process",
                side_effect=fake_run,
            ):
                result = verify_config(app, declaration, context)

        self.assertEqual("verification_indeterminate", result.code)
        self.assertEqual("runtime", result.data["assessment"]["strongest_evidence"])

    def test_powershell_consumer_runtime_selection_on_windows(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            app, declaration, context, source = self._fixture(
                root,
                platform=Platform.WINDOWS,
                consumers=("powershell",),
            )

            def fake_which(command, **kwargs):
                return {
                    "oh-my-posh.exe": "C:/Tools/oh-my-posh.exe",
                    "powershell.exe": "C:/Windows/System32/WindowsPowerShell/v1.0/powershell.exe",
                }.get(command)

            def fake_run(argv, **kwargs):
                if argv[0].endswith("oh-my-posh.exe"):
                    return ProcessResult(0, "rendered", "")
                return ProcessResult(0, "__MSHP_POSH_THEME__=" + str(source), "")

            with patch(
                "annexation.oh_my_posh_verification.shutil.which",
                side_effect=fake_which,
            ), patch(
                "annexation.oh_my_posh_verification.run_process",
                side_effect=fake_run,
            ):
                result = verify_config(app, declaration, context)

        self.assertEqual("config_effective", result.code)
        self.assertEqual("runtime", result.data["assessment"]["strongest_evidence"])
        self.assertEqual(
            "powershell",
            result.data["assessment"]["observations"][1]["data"]["consumer"],
        )


if __name__ == "__main__":
    unittest.main()
