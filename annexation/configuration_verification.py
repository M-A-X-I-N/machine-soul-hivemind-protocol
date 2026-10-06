"""Read-only effective configuration verification engine."""

from __future__ import annotations

from collections.abc import Iterable

from .model import (
    Application,
    ApplicationConfigProbe,
    CmdAutoRunVerification,
    ConfigurationVerificationPlan,
    CustomVerification,
    EvidenceStrength,
    OhMyPoshVerification,
    OperationContext,
    OperationResult,
    PlatformDeclaration,
    ResolvedPathVerification,
    ShellStartupVerification,
    VerificationAssessment,
    VerificationConclusion,
    VerificationObservation,
)
from .oh_my_posh_verification import verify_oh_my_posh
from .native_configuration_verification import (
    verify_application_config_probe,
    verify_cmd_autorun,
    verify_resolved_path,
)
from .shell_verification import verify_shell_startup


def _normalize_observations(value: object) -> tuple[VerificationObservation, ...]:
    if value is None:
        return ()
    if isinstance(value, VerificationObservation):
        return (value,)
    if isinstance(value, tuple) and all(isinstance(item, VerificationObservation) for item in value):
        return value
    if isinstance(value, list) and all(isinstance(item, VerificationObservation) for item in value):
        return tuple(value)
    raise TypeError(
        "Verification strategy handlers must return VerificationObservation, "
        "a list/tuple of VerificationObservation, or None."
    )


def assess_verification(
    observations: Iterable[VerificationObservation],
    *,
    errors: Iterable[str] = (),
) -> VerificationAssessment:
    """Combine observations without confusing truth with evidence strength."""
    values = tuple(observations)
    error_values = tuple(str(error) for error in errors if str(error).strip())
    if not values:
        return VerificationAssessment(
            VerificationConclusion.INDETERMINATE,
            EvidenceStrength.NONE,
            (),
            error_values,
        )

    strongest_rank = max(item.evidence.rank for item in values)
    strongest = tuple(item for item in values if item.evidence.rank == strongest_rank)
    supports = {item.supports for item in strongest}

    if len(supports) == 1:
        conclusion = next(iter(supports))
    else:
        conclusion = VerificationConclusion.INDETERMINATE

    return VerificationAssessment(
        conclusion,
        strongest[0].evidence,
        values,
        error_values,
    )


def verify_config(
    application: Application,
    declaration: PlatformDeclaration,
    context: OperationContext,
) -> OperationResult:
    """Execute the declared verification plan and return the shared result contract."""
    plan: ConfigurationVerificationPlan | None = declaration.configuration_verification
    if plan is None:
        return OperationResult.not_implemented(
            "verification_plan_missing",
            "No effective-configuration verification plan is declared.",
            data={"application": application.id},
        )

    observations: list[VerificationObservation] = []
    errors: list[str] = []
    for strategy in plan.strategies:
        if isinstance(strategy, OhMyPoshVerification):
            observations.extend(
                verify_oh_my_posh(
                    application,
                    declaration,
                    context,
                    strategy,
                )
            )
            continue
        if isinstance(strategy, ResolvedPathVerification):
            observations.append(
                verify_resolved_path(application, declaration, context, strategy)
            )
            continue
        if isinstance(strategy, ApplicationConfigProbe):
            observations.append(
                verify_application_config_probe(
                    application,
                    declaration,
                    context,
                    strategy,
                )
            )
            continue
        if isinstance(strategy, CmdAutoRunVerification):
            observations.append(
                verify_cmd_autorun(application, declaration, context, strategy)
            )
            continue
        if isinstance(strategy, ShellStartupVerification):
            try:
                observations.append(
                    verify_shell_startup(
                        application,
                        declaration,
                        context,
                        strategy,
                    )
                )
            except Exception as exc:
                return OperationResult.error(
                    "verification_probe_failed",
                    f"Shell startup verification failed: {exc}",
                    data={"application": application.id},
                )
            continue
        if isinstance(strategy, CustomVerification):
            try:
                observations.extend(
                    _normalize_observations(
                        strategy.handler(application, declaration, context)
                    )
                )
            except Exception as exc:
                return OperationResult.error(
                    "verification_probe_failed",
                    f"Configuration verification probe failed: {exc}",
                    data={"application": application.id},
                )
            continue
        return OperationResult.not_implemented(
            "verification_strategy_not_implemented",
            f"No shared verification handler exists for {type(strategy).__name__}.",
            data={"application": application.id},
        )

    assessment = assess_verification(observations, errors=errors)
    data = {
        "application": application.id,
        "assessment": assessment.to_dict(),
    }

    if assessment.conclusion is VerificationConclusion.EFFECTIVE:
        return OperationResult.success(
            "config_effective",
            "Configuration is effective at the reported evidence strength.",
            data=data,
        )
    if assessment.conclusion is VerificationConclusion.NOT_EFFECTIVE:
        return OperationResult.failure(
            "config_not_effective",
            "Configuration is not effective at the reported evidence strength.",
            data=data,
        )
    return OperationResult.failure(
        "verification_indeterminate",
        "Configuration effectiveness could not be determined conclusively.",
        data=data,
    )
