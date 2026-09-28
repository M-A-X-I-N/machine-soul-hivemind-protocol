"""Mutation-side installation scope policy.

Observed installation scope remains in model.discovery.InstallationScope.
This module defines what a mutating strategy intends/requires.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

from .discovery import InstallationScope

if TYPE_CHECKING:
    from .context import TargetAccount


class InstallationScopePolicyMode(str, Enum):
    """How a mutating strategy determines installation scope."""

    FIXED = "fixed"
    REQUIRED = "required"
    DELEGATED = "delegated"


@dataclass(frozen=True)
class InstallationScopePolicy:
    """Mutation-side installation scope contract."""

    mode: InstallationScopePolicyMode
    scope: InstallationScope | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.mode, InstallationScopePolicyMode):
            raise TypeError("mode must be an InstallationScopePolicyMode.")
        if self.mode is InstallationScopePolicyMode.DELEGATED:
            if self.scope is not None:
                raise ValueError("Delegated scope policy cannot declare a concrete scope.")
            return
        if self.scope not in {InstallationScope.USER, InstallationScope.MACHINE}:
            raise ValueError(
                "Fixed/required installation scope must be USER or MACHINE."
            )

    @classmethod
    def fixed(cls, scope: InstallationScope) -> "InstallationScopePolicy":
        return cls(InstallationScopePolicyMode.FIXED, scope)

    @classmethod
    def required(cls, scope: InstallationScope) -> "InstallationScopePolicy":
        return cls(InstallationScopePolicyMode.REQUIRED, scope)

    @classmethod
    def delegated(cls) -> "InstallationScopePolicy":
        return cls(InstallationScopePolicyMode.DELEGATED)


def installation_scope_compatible(
    policy: InstallationScopePolicy,
    actual: InstallationScope,
    *,
    target_is_current: bool,
) -> bool:
    """Return whether observed scope satisfies a mutation policy."""
    if not isinstance(policy, InstallationScopePolicy):
        raise TypeError("policy must be an InstallationScopePolicy.")
    if not isinstance(actual, InstallationScope):
        raise TypeError("actual must be an InstallationScope.")

    if actual is InstallationScope.UNKNOWN:
        return False

    if policy.mode is InstallationScopePolicyMode.DELEGATED:
        if actual is InstallationScope.PACKAGE_USER:
            return target_is_current
        return actual in {InstallationScope.USER, InstallationScope.MACHINE}

    if policy.scope is InstallationScope.USER:
        if actual is InstallationScope.USER:
            return True
        return actual is InstallationScope.PACKAGE_USER and target_is_current

    return policy.scope is InstallationScope.MACHINE and actual is InstallationScope.MACHINE


def installation_scope_target_error(
    policy: InstallationScopePolicy,
    target: "TargetAccount",
) -> str | None:
    """Return a safety error before mutation for unsupported target/scope pairs."""
    if not isinstance(policy, InstallationScopePolicy):
        raise TypeError("policy must be an InstallationScopePolicy.")
    from .context import TargetAccount

    if not isinstance(target, TargetAccount):
        raise TypeError("target must be a TargetAccount.")

    if target.is_current:
        return None

    if policy.mode is InstallationScopePolicyMode.DELEGATED:
        return (
            "Delegated installation scope is unsafe for a non-current target account "
            "without a proven backend target-user mechanism."
        )

    if policy.scope is InstallationScope.USER:
        return (
            "User-scoped installation for a non-current target account is unsupported "
            "without a proven backend target-user mechanism."
        )

    return None
