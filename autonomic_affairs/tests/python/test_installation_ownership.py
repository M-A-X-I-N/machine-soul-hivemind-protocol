from __future__ import annotations

from pathlib import Path
import unittest

from annexation_procedures.installation_ownership import (
    candidate_satisfies_scope_policy,
    installation_candidate_matches_state,
    state_satisfies_scope_policy,
)
from annexation_procedures.model import (
    InstallationCandidate,
    InstallationScope,
    InstallationScopePolicy,
    InstallationScopePolicyMode,
    TargetAccount,
)
from annexation_procedures.state import InstallState


class InstallationOwnershipTests(unittest.TestCase):
    def setUp(self) -> None:
        self.target = TargetAccount("fixture_user", Path("/home/fixture"), True)

    def test_scope_policy_requires_current_user_subject(self) -> None:
        policy = InstallationScopePolicy.required(InstallationScope.USER)
        matching = InstallationCandidate(
            "Vendor.Example",
            scope=InstallationScope.PACKAGE_USER,
            scope_subject="fixture_user",
            registration_kind="winget_correlation",
        )
        wrong_subject = InstallationCandidate(
            "Vendor.Example",
            scope=InstallationScope.USER,
            scope_subject="other_user",
            registration_kind="winget_correlation",
        )
        self.assertTrue(candidate_satisfies_scope_policy(matching, policy, self.target))
        self.assertFalse(candidate_satisfies_scope_policy(wrong_subject, policy, self.target))

    def test_machine_state_matches_exact_dpkg_candidate(self) -> None:
        state = InstallState(
            application="fish",
            host="fixture_host",
            account="fixture_user",
            manager="apt",
            identity="fish",
            requested_scope_mode=InstallationScopePolicyMode.FIXED,
            requested_scope=InstallationScope.MACHINE,
            actual_scope=InstallationScope.MACHINE,
            native_identity="fish",
        )
        candidate = InstallationCandidate(
            "fish",
            scope=InstallationScope.MACHINE,
            registration_kind="dpkg",
        )
        self.assertTrue(installation_candidate_matches_state(state, candidate))
        self.assertTrue(
            state_satisfies_scope_policy(
                state,
                InstallationScopePolicy.fixed(InstallationScope.MACHINE),
                self.target,
            )
        )

    def test_scope_or_subject_mismatch_never_matches_state(self) -> None:
        state = InstallState(
            application="example",
            host="fixture_host",
            account="fixture_user",
            manager="winget",
            identity="Vendor.Example",
            requested_scope_mode=InstallationScopePolicyMode.REQUIRED,
            requested_scope=InstallationScope.USER,
            actual_scope=InstallationScope.USER,
            scope_subject="fixture_user",
            native_identity="Vendor.Example",
        )
        machine = InstallationCandidate(
            "Vendor.Example",
            scope=InstallationScope.MACHINE,
            registration_kind="winget_correlation",
        )
        wrong_user = InstallationCandidate(
            "Vendor.Example",
            scope=InstallationScope.USER,
            scope_subject="other_user",
            registration_kind="winget_correlation",
        )
        self.assertFalse(installation_candidate_matches_state(state, machine))
        self.assertFalse(installation_candidate_matches_state(state, wrong_user))


if __name__ == "__main__":
    unittest.main()
