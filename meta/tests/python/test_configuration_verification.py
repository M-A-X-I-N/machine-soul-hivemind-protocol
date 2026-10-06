from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from annexation_procedures.configuration_verification import (
    assess_verification,
    verify_config,
)
from annexation_procedures.model import (
    Application,
    ConfigurationVerificationPlan,
    CustomVerification,
    EvidenceStrength,
    Operation,
    OperationContext,
    Platform,
    PlatformDeclaration,
    Support,
    TargetAccount,
    VerificationConclusion,
    VerificationObservation,
)
from annexation_procedures.operations import perform_operation


class ConfigurationVerificationTests(unittest.TestCase):
    def _context(self, root: Path) -> OperationContext:
        return OperationContext(
            repository_root=root,
            platform=Platform.LINUX,
            host="fixture_host",
            target_account=TargetAccount("fixture_user", root / "home", True),
        )

    def _observation(
        self,
        *,
        evidence: EvidenceStrength = EvidenceStrength.RESOLUTION,
        supports: VerificationConclusion = VerificationConclusion.EFFECTIVE,
        kind: str = "fixture",
    ) -> VerificationObservation:
        return VerificationObservation(
            kind,
            "fixture_probe",
            evidence,
            supports,
            {"fixture": True},
        )

    def _application(self, handler, *, support: Support = Support.SUPPORTED) -> Application:
        declaration = PlatformDeclaration(
            platform=Platform.LINUX,
            capabilities={Operation.VERIFY_CONFIG: support},
            configuration_verification=(
                ConfigurationVerificationPlan((CustomVerification(handler),))
                if support is Support.SUPPORTED
                else None
            ),
        )
        return Application(id="example", display_name="Example", platforms=(declaration,))

    def test_assessment_uses_strongest_evidence(self) -> None:
        assessment = assess_verification(
            (
                self._observation(
                    evidence=EvidenceStrength.RESOLUTION,
                    supports=VerificationConclusion.NOT_EFFECTIVE,
                    kind="weak",
                ),
                self._observation(
                    evidence=EvidenceStrength.RUNTIME,
                    supports=VerificationConclusion.EFFECTIVE,
                    kind="strong",
                ),
            )
        )
        self.assertEqual(VerificationConclusion.EFFECTIVE, assessment.conclusion)
        self.assertEqual(EvidenceStrength.RUNTIME, assessment.strongest_evidence)

    def test_conflicting_strongest_evidence_is_indeterminate(self) -> None:
        assessment = assess_verification(
            (
                self._observation(
                    evidence=EvidenceStrength.RUNTIME,
                    supports=VerificationConclusion.EFFECTIVE,
                    kind="one",
                ),
                self._observation(
                    evidence=EvidenceStrength.RUNTIME,
                    supports=VerificationConclusion.NOT_EFFECTIVE,
                    kind="two",
                ),
            )
        )
        self.assertEqual(VerificationConclusion.INDETERMINATE, assessment.conclusion)
        self.assertEqual(EvidenceStrength.RUNTIME, assessment.strongest_evidence)

    def test_supported_effective_result_serializes_assessment(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            app = self._application(lambda *_: self._observation())
            declaration = app.platforms[0]

            result = verify_config(app, declaration, self._context(root))

            self.assertEqual("config_effective", result.code)
            self.assertEqual("effective", result.data["assessment"]["conclusion"])
            self.assertEqual("resolution", result.data["assessment"]["strongest_evidence"])
            json.dumps(result.to_dict(), sort_keys=True, allow_nan=False)

    def test_supported_not_effective_and_indeterminate_are_distinct(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            not_effective = self._application(
                lambda *_: self._observation(
                    supports=VerificationConclusion.NOT_EFFECTIVE,
                )
            )
            indeterminate = self._application(lambda *_: None)

            negative = perform_operation(
                not_effective,
                Operation.VERIFY_CONFIG,
                self._context(root),
            )
            unknown = perform_operation(
                indeterminate,
                Operation.VERIFY_CONFIG,
                self._context(root),
            )

            self.assertEqual("config_not_effective", negative.code)
            self.assertEqual("verification_indeterminate", unknown.code)
            self.assertEqual("none", unknown.data["assessment"]["strongest_evidence"])

    def test_capability_not_implemented_short_circuits_missing_plan(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            app = self._application(lambda *_: None, support=Support.NOT_IMPLEMENTED)

            result = perform_operation(
                app,
                Operation.VERIFY_CONFIG,
                self._context(root),
            )

            self.assertEqual("operation_not_implemented", result.code)
            self.assertEqual(2, result.exit_code)

    def test_direct_engine_without_plan_is_not_implemented(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            declaration = PlatformDeclaration(platform=Platform.LINUX, capabilities={})
            app = Application(id="example", display_name="Example", platforms=(declaration,))

            result = verify_config(app, declaration, self._context(root))

            self.assertEqual("verification_plan_missing", result.code)
            self.assertEqual(2, result.exit_code)

    def test_probe_exception_is_operational_error(self) -> None:
        def fail(*_):
            raise RuntimeError("fixture boom")

        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            app = self._application(fail)
            result = perform_operation(app, Operation.VERIFY_CONFIG, self._context(root))

        self.assertEqual("verification_probe_failed", result.code)
        self.assertEqual(3, result.exit_code)


if __name__ == "__main__":
    unittest.main()
