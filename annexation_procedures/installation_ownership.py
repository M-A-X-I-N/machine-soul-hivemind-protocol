"""Shared matching between installation candidates, scope policy, and provenance."""

from __future__ import annotations

from .model import (
    InstallationCandidate,
    InstallationScope,
    InstallationScopePolicy,
    TargetAccount,
    installation_scope_compatible,
)
from .state import InstallState


_USER_SCOPES = {InstallationScope.USER, InstallationScope.PACKAGE_USER}


def candidate_satisfies_scope_policy(
    candidate: InstallationCandidate,
    policy: InstallationScopePolicy,
    target: TargetAccount,
) -> bool:
    """Return whether one observed candidate can satisfy the mutation contract."""
    if not installation_scope_compatible(
        policy,
        candidate.scope,
        target_is_current=target.is_current,
    ):
        return False
    if candidate.scope in _USER_SCOPES:
        return (
            target.is_current
            and candidate.scope_subject is not None
            and candidate.scope_subject == target.name
        )
    return True


def state_satisfies_scope_policy(
    state: InstallState,
    policy: InstallationScopePolicy,
    target: TargetAccount,
) -> bool:
    """Return whether one ownership record belongs to the intended mutation scope."""
    if not installation_scope_compatible(
        policy,
        state.actual_scope,
        target_is_current=target.is_current,
    ):
        return False
    if state.actual_scope in _USER_SCOPES:
        return (
            target.is_current
            and state.scope_subject is not None
            and state.scope_subject == target.name
        )
    return True


def installation_candidate_matches_state(
    state: InstallState,
    candidate: InstallationCandidate,
) -> bool:
    """Match one canonical scoped ownership record to one discovered candidate."""
    if state.actual_scope is InstallationScope.UNKNOWN:
        return False
    if state.actual_scope is not candidate.scope:
        return False
    if state.actual_scope in _USER_SCOPES:
        if (
            state.scope_subject is None
            or candidate.scope_subject is None
            or state.scope_subject != candidate.scope_subject
        ):
            return False

    if state.manager == "apt":
        if candidate.registration_kind != "dpkg":
            return False
        if state.identity.casefold() != candidate.native_identity.casefold():
            return False
    elif state.manager == "winget":
        if candidate.registration_kind != "winget_correlation":
            return False
        if state.identity.casefold() != candidate.native_identity.casefold():
            return False
    elif state.native_identity is not None:
        if state.native_identity.casefold() != candidate.native_identity.casefold():
            return False
    else:
        return False

    if (
        state.native_identity is not None
        and state.native_identity.casefold() != candidate.native_identity.casefold()
    ):
        return False
    if (
        state.uninstall_identity is not None
        and candidate.uninstall_identity is not None
        and state.uninstall_identity.casefold() != candidate.uninstall_identity.casefold()
    ):
        return False
    return True
