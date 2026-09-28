from __future__ import annotations

from dataclasses import FrozenInstanceError
import json
import math
import unittest

from annexation_procedures.model import (
    DiscoveryObservation,
    EvidenceStrength,
    InstallationAssessment,
    InstallationCandidate,
    InstallationOwnership,
    InstallationPresence,
    InstallationScope,
    ObservationAuthority,
    TriState,
    VerificationAssessment,
    VerificationConclusion,
    VerificationObservation,
)


class DiscoveryModelTests(unittest.TestCase):
    def test_observation_is_deeply_immutable_and_round_trips(self) -> None:
        source = {"nested": {"values": [1, 2]}}
        item = DiscoveryObservation(
            "package_registration",
            "dpkg",
            ObservationAuthority.DIRECT,
            source,
        )
        source["nested"]["values"].append(3)

        self.assertEqual([1, 2], item.to_dict()["data"]["nested"]["values"])
        with self.assertRaises(TypeError):
            item.data["new"] = True  # type: ignore[index]

        payload = item.to_dict()
        self.assertEqual(item, DiscoveryObservation.from_dict(payload))
        json.dumps(payload, sort_keys=True, allow_nan=False)

    def test_observation_rejects_non_json_data(self) -> None:
        with self.assertRaises(TypeError):
            DiscoveryObservation("x", "test", ObservationAuthority.DIRECT, {"value": object()})
        with self.assertRaises(ValueError):
            DiscoveryObservation("x", "test", ObservationAuthority.DIRECT, {"value": math.nan})

    def test_installation_candidate_dimensions_are_independent(self) -> None:
        candidate = InstallationCandidate(
            native_identity="JanDeDobbeleer.OhMyPosh",
            display_identity="Oh My Posh",
            version="27.0.0",
            paths=(r"C:\Program Files\oh-my-posh\bin\oh-my-posh.exe",),
            scope=InstallationScope.MACHINE,
            scope_subject=None,
            registration_kind="arp",
            acquisition_channel="unknown",
            acquisition_authority=ObservationAuthority.HINT,
            preferred_match=TriState.YES,
            manageable_by_preferred_strategy=TriState.YES,
            ownership=InstallationOwnership.UNMANAGED,
            uninstall_identity="{EXAMPLE}",
        )

        self.assertEqual(TriState.YES, candidate.preferred_match)
        self.assertEqual(InstallationOwnership.UNMANAGED, candidate.ownership)
        self.assertEqual(candidate, InstallationCandidate.from_dict(candidate.to_dict()))

    def test_installation_candidate_scope_subject_round_trips(self) -> None:
        candidate = InstallationCandidate(
            native_identity="example",
            scope=InstallationScope.PACKAGE_USER,
            scope_subject="fixture_user",
        )
        self.assertEqual(candidate, InstallationCandidate.from_dict(candidate.to_dict()))

    def test_present_assessment_requires_candidate_and_round_trips(self) -> None:
        candidate = InstallationCandidate(
            native_identity="fish",
            preferred_match=TriState.YES,
            ownership=InstallationOwnership.MANAGED,
        )
        assessment = InstallationAssessment(
            InstallationPresence.PRESENT,
            (candidate,),
            preferred_candidate_index=0,
            machine_soul_state=InstallationOwnership.MANAGED,
        )

        self.assertIs(candidate, assessment.preferred_candidate)
        payload = assessment.to_dict()
        self.assertEqual(assessment, InstallationAssessment.from_dict(payload))
        json.dumps(payload, sort_keys=True, allow_nan=False)

        with self.assertRaises(ValueError):
            InstallationAssessment(InstallationPresence.PRESENT)
        with self.assertRaises(ValueError):
            InstallationAssessment(InstallationPresence.ABSENT, (candidate,))

    def test_unknown_and_ambiguous_preserve_partial_candidates(self) -> None:
        partial = InstallationCandidate(native_identity="pwsh.exe")
        unknown = InstallationAssessment(
            InstallationPresence.UNKNOWN,
            (partial,),
            errors=("WinGet backend unavailable.",),
        )
        ambiguous = InstallationAssessment(
            InstallationPresence.AMBIGUOUS,
            (
                partial,
                InstallationCandidate(native_identity="Microsoft.PowerShell_7.6"),
            ),
        )

        self.assertEqual(1, len(unknown.candidates))
        self.assertEqual(2, len(ambiguous.candidates))

    def test_preferred_candidate_must_explicitly_match(self) -> None:
        candidate = InstallationCandidate(native_identity="manual", preferred_match=TriState.NO)
        with self.assertRaises(ValueError):
            InstallationAssessment(
                InstallationPresence.PRESENT,
                (candidate,),
                preferred_candidate_index=0,
            )

    def test_verification_assessment_orders_evidence_and_round_trips(self) -> None:
        resolution = VerificationObservation(
            "resolved_path",
            "windows_terminal",
            EvidenceStrength.RESOLUTION,
            VerificationConclusion.EFFECTIVE,
            {"path": "settings.json"},
        )
        runtime = VerificationObservation(
            "startup_trace",
            "bash",
            EvidenceStrength.RUNTIME,
            VerificationConclusion.EFFECTIVE,
            {"source": ".bashrc"},
        )
        assessment = VerificationAssessment(
            VerificationConclusion.EFFECTIVE,
            EvidenceStrength.RUNTIME,
            (resolution, runtime),
        )

        self.assertGreater(EvidenceStrength.RUNTIME.rank, EvidenceStrength.APPLICATION.rank)
        self.assertGreater(EvidenceStrength.APPLICATION.rank, EvidenceStrength.RESOLUTION.rank)
        self.assertEqual(assessment, VerificationAssessment.from_dict(assessment.to_dict()))
        json.dumps(assessment.to_dict(), sort_keys=True, allow_nan=False)

    def test_verification_rejects_impossible_strength_or_conclusion(self) -> None:
        with self.assertRaises(ValueError):
            VerificationAssessment(
                VerificationConclusion.EFFECTIVE,
                EvidenceStrength.NONE,
            )

        observation = VerificationObservation(
            "resolved_path",
            "terminal",
            EvidenceStrength.RESOLUTION,
            VerificationConclusion.NOT_EFFECTIVE,
        )
        with self.assertRaises(ValueError):
            VerificationAssessment(
                VerificationConclusion.EFFECTIVE,
                EvidenceStrength.RESOLUTION,
                (observation,),
            )

        with self.assertRaises(ValueError):
            VerificationAssessment(
                VerificationConclusion.INDETERMINATE,
                EvidenceStrength.APPLICATION,
                (observation,),
            )

    def test_dataclasses_are_frozen(self) -> None:
        candidate = InstallationCandidate(native_identity="example")
        with self.assertRaises(FrozenInstanceError):
            candidate.version = "1"  # type: ignore[misc]


if __name__ == "__main__":
    unittest.main()
