"""Human and machine presentation for grouped discovery status."""

from __future__ import annotations

from collections.abc import Mapping
import json

from .model import OperationResult
from .orchestration import DiscoveryStatusReport


def _fallback(result: OperationResult) -> str:
    return f"{result.status.value} ({result.code})"


def _assessment(result: OperationResult) -> Mapping[str, object] | None:
    value = result.data.get("assessment")
    return value if isinstance(value, Mapping) else None


def _installation(result: OperationResult) -> str:
    assessment = _assessment(result)
    if assessment is None:
        return _fallback(result)

    presence = str(assessment.get("presence", result.code))
    ownership = str(assessment.get("machine_soul_state", "unknown"))
    raw_candidates = assessment.get("candidates")
    candidates = raw_candidates if isinstance(raw_candidates, (list, tuple)) else ()

    preferred_yes = 0
    preferred_no = 0
    preferred_unknown = 0
    for candidate in candidates:
        if not isinstance(candidate, Mapping):
            continue
        match = candidate.get("preferred_match")
        if match == "yes":
            preferred_yes += 1
        elif match == "no":
            preferred_no += 1
        else:
            preferred_unknown += 1

    preferred = (
        f"yes={preferred_yes},no={preferred_no},unknown={preferred_unknown}"
        if candidates
        else "n/a"
    )
    return (
        f"{presence}; candidates={len(candidates)}; "
        f"preferred_match[{preferred}]; ownership={ownership}"
    )


def _configuration(result: OperationResult) -> str:
    ownership = result.data.get("ownership_state")
    if isinstance(ownership, str):
        return f"{result.code}; ownership={ownership}"

    nested = result.data.get("results")
    if isinstance(nested, (list, tuple)) and len(nested) == 1:
        item = nested[0]
        if isinstance(item, Mapping):
            data = item.get("data")
            if isinstance(data, Mapping) and isinstance(data.get("ownership_state"), str):
                return f"{result.code}; ownership={data['ownership_state']}"

    return _fallback(result) if result.status.value in {"unsupported", "not_implemented", "error"} else result.code


def _effective(result: OperationResult) -> str:
    assessment = _assessment(result)
    if assessment is None:
        return _fallback(result)
    conclusion = str(assessment.get("conclusion", result.code))
    evidence = str(assessment.get("strongest_evidence", "none"))
    return f"{conclusion}; evidence={evidence}"


def render_discovery_status_human(report: DiscoveryStatusReport) -> str:
    """Render all three dimensions without collapsing them into a verdict."""
    lines: list[str] = []
    for entry in report.applications:
        lines.append(f"{entry.application_id} ({entry.display_name})")
        lines.append(f"  installation: {_installation(entry.installation.result)}")
        lines.append(f"  configuration: {_configuration(entry.configuration.result)}")
        lines.append(f"  effective: {_effective(entry.effective.result)}")
    return "\n".join(lines) if lines else "No applications were discovered."


def render_discovery_status_json(report: DiscoveryStatusReport) -> str:
    """Preserve complete atomic results for machine consumers."""
    return json.dumps(
        report.to_dict(),
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
