from __future__ import annotations

import unittest

from annexation_procedures.model import (
    AptPackage,
    InstallationScope,
    InstallationScopePolicy,
    InstallationScopePolicyMode,
    TargetAccount,
    WingetPackage,
    installation_scope_compatible,
    installation_scope_target_error,
)


class InstallationScopePolicyTests(unittest.TestCase):
    def test_fixed_required_and_delegated_policies(self) -> None:
        fixed = InstallationScopePolicy.fixed(InstallationScope.MACHINE)
        required = InstallationScopePolicy.required(InstallationScope.USER)
        delegated = InstallationScopePolicy.delegated()

        self.assertEqual(InstallationScopePolicyMode.FIXED, fixed.mode)
        self.assertEqual(InstallationScope.MACHINE, fixed.scope)
        self.assertEqual(InstallationScopePolicyMode.REQUIRED, required.mode)
        self.assertEqual(InstallationScope.USER, required.scope)
        self.assertEqual(InstallationScopePolicyMode.DELEGATED, delegated.mode)
        self.assertIsNone(delegated.scope)

    def test_invalid_policy_combinations_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            InstallationScopePolicy(
                InstallationScopePolicyMode.REQUIRED,
                InstallationScope.UNKNOWN,
            )
        with self.assertRaises(ValueError):
            InstallationScopePolicy(
                InstallationScopePolicyMode.DELEGATED,
                InstallationScope.USER,
            )

    def test_scope_compatibility(self) -> None:
        user = InstallationScopePolicy.required(InstallationScope.USER)
        machine = InstallationScopePolicy.fixed(InstallationScope.MACHINE)
        delegated = InstallationScopePolicy.delegated()

        self.assertTrue(
            installation_scope_compatible(
                user,
                InstallationScope.USER,
                target_is_current=True,
            )
        )
        self.assertTrue(
            installation_scope_compatible(
                user,
                InstallationScope.PACKAGE_USER,
                target_is_current=True,
            )
        )
        self.assertFalse(
            installation_scope_compatible(
                user,
                InstallationScope.PACKAGE_USER,
                target_is_current=False,
            )
        )
        self.assertFalse(
            installation_scope_compatible(
                user,
                InstallationScope.MACHINE,
                target_is_current=True,
            )
        )
        self.assertTrue(
            installation_scope_compatible(
                machine,
                InstallationScope.MACHINE,
                target_is_current=False,
            )
        )
        self.assertFalse(
            installation_scope_compatible(
                machine,
                InstallationScope.USER,
                target_is_current=True,
            )
        )
        self.assertFalse(
            installation_scope_compatible(
                delegated,
                InstallationScope.UNKNOWN,
                target_is_current=True,
            )
        )

    def test_target_guard_refuses_noncurrent_user_or_delegated_scope(self) -> None:
        current = TargetAccount("current", "/home/current", True)
        other = TargetAccount("other", "/home/other", False)

        self.assertIsNone(
            installation_scope_target_error(
                InstallationScopePolicy.required(InstallationScope.USER),
                current,
            )
        )
        self.assertIsNotNone(
            installation_scope_target_error(
                InstallationScopePolicy.required(InstallationScope.USER),
                other,
            )
        )
        self.assertIsNotNone(
            installation_scope_target_error(
                InstallationScopePolicy.delegated(),
                other,
            )
        )
        self.assertIsNone(
            installation_scope_target_error(
                InstallationScopePolicy.fixed(InstallationScope.MACHINE),
                other,
            )
        )

    def test_winget_requires_explicit_required_scope(self) -> None:
        with self.assertRaises(ValueError):
            WingetPackage(
                "Vendor.Example",
                InstallationScopePolicy.delegated(),
            )
        with self.assertRaises(ValueError):
            WingetPackage(
                "Vendor.Example",
                InstallationScopePolicy.fixed(InstallationScope.MACHINE),
            )

    def test_current_strategy_declarations_are_explicit(self) -> None:
        apt = AptPackage("fish")
        winget = WingetPackage(
            "Vendor.Example",
            InstallationScopePolicy.required(InstallationScope.USER),
        )

        self.assertEqual(InstallationScopePolicyMode.FIXED, apt.scope_policy.mode)
        self.assertEqual(InstallationScope.MACHINE, apt.scope_policy.scope)
        self.assertEqual(InstallationScopePolicyMode.REQUIRED, winget.scope_policy.mode)
        self.assertEqual(InstallationScope.USER, winget.scope_policy.scope)


if __name__ == "__main__":
    unittest.main()
