"""Read GitHub Actions history and reconcile scheduled CI coverage."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
from typing import Callable, Iterable
from urllib.request import Request, urlopen

from autonomic_affairs.ci_validation_selector import (
    PolicyEvidenceError,
    PolicySelection,
    REGISTERED_CHECKS,
    checks_for_paths,
    git_changed_paths,
)

_CODEQL_CHECKS = frozenset({"codeql-python", "codeql-actions"})


class HistoryEvidenceError(RuntimeError):
    """Raised when GitHub Actions history cannot be read safely."""


def _parse_timestamp(value: str | None) -> datetime:
    if not value:
        raise HistoryEvidenceError("missing completion timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise HistoryEvidenceError(f"invalid timestamp: {value!r}") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


class GitHubActionsHistory:
    """Minimal read-only GitHub Actions history client."""

    def __init__(
        self,
        repository: str,
        token: str,
        current_run_id: int,
        *,
        opener: Callable = urlopen,
    ) -> None:
        self.repository = repository
        self.token = token
        self.current_run_id = current_run_id
        self._opener = opener
        self._base = f"https://api.github.com/repos/{repository}"

    def _get_json(self, url: str) -> dict:
        request = Request(
            url,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self.token}",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "machine-soul-ci-policy",
            },
        )
        try:
            with self._opener(request) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            raise HistoryEvidenceError(str(exc)) from exc

    def recent_runs(self) -> tuple[dict, ...]:
        runs: list[dict] = []
        page = 1
        while True:
            data = self._get_json(
                f"{self._base}/actions/runs?per_page=100&page={page}"
            )
            batch = data.get("workflow_runs", [])
            if not isinstance(batch, list):
                raise HistoryEvidenceError("workflow_runs response is not a list")
            runs.extend(batch)
            if len(batch) < 100:
                return tuple(runs)
            page += 1

    def jobs_for_run(self, run_id: int) -> tuple[dict, ...]:
        jobs: list[dict] = []
        page = 1
        while True:
            data = self._get_json(
                f"{self._base}/actions/runs/{run_id}/jobs?per_page=100&page={page}"
            )
            batch = data.get("jobs", [])
            if not isinstance(batch, list):
                raise HistoryEvidenceError("jobs response is not a list")
            jobs.extend(batch)
            if len(batch) < 100:
                return tuple(jobs)
            page += 1


def successful_check_executions(
    history,
    *,
    current_run_id: int,
    default_branch: str,
) -> dict[str, tuple[str, datetime]]:
    """Return the newest successful execution of each recognized check on main."""

    found: dict[str, tuple[str, datetime]] = {}
    for run in history.recent_runs():
        if run.get("id") == current_run_id:
            continue
        if run.get("head_branch") != default_branch:
            continue
        run_sha = run.get("head_sha")
        if not run_sha:
            continue

        for job in history.jobs_for_run(int(run["id"])):
            job_sha = job.get("head_sha") or run_sha
            completed_at = job.get("completed_at") or run.get("updated_at")

            if job.get("conclusion") == "success":
                name = str(job.get("name") or "")
                for check_id in _CODEQL_CHECKS:
                    if (
                        check_id not in found
                        and name.endswith(f"Check {check_id}")
                    ):
                        found[check_id] = (
                            job_sha,
                            _parse_timestamp(completed_at),
                        )

            for step in job.get("steps") or ():
                if step.get("conclusion") != "success":
                    continue
                name = str(step.get("name") or "")
                if not name.startswith("Check "):
                    continue
                check_id = name.removeprefix("Check ")
                if check_id not in REGISTERED_CHECKS or check_id in found:
                    continue
                stamp = step.get("completed_at") or completed_at
                found[check_id] = (
                    job_sha,
                    _parse_timestamp(stamp),
                )

        if len(found) == len(REGISTERED_CHECKS):
            break

    return found


def reconcile_scheduled_checks(
    history,
    *,
    current_run_id: int,
    default_branch: str,
    current_head_sha: str,
    current_head_committed_at: datetime,
    now: datetime,
    checks: Iterable[str] = REGISTERED_CHECKS,
    cwd: Path | str | None = None,
) -> PolicySelection:
    """Select scheduled checks whose coverage is stale or cannot be proven."""

    requested_set = set(checks)
    requested = tuple(
        check for check in REGISTERED_CHECKS if check in requested_set
    )
    executions = successful_check_executions(
        history,
        current_run_id=current_run_id,
        default_branch=default_branch,
    )

    now_utc = now.astimezone(timezone.utc)
    head_time = current_head_committed_at
    if head_time.tzinfo is None:
        head_time = head_time.replace(tzinfo=timezone.utc)
    head_time = head_time.astimezone(timezone.utc)
    head_age = now_utc - head_time

    due: set[str] = set()
    for check_id in requested:
        execution = executions.get(check_id)
        if check_id in _CODEQL_CHECKS:
            if execution is None or execution[0] != current_head_sha:
                due.add(check_id)
                continue
            cadence = timedelta(
                hours=24 if head_age < timedelta(hours=168) else 168
            )
            if now_utc - execution[1] >= cadence:
                due.add(check_id)
            continue

        if execution is None:
            due.add(check_id)
            continue
        covered_sha, _ = execution
        if covered_sha == current_head_sha:
            continue
        try:
            changed = git_changed_paths(
                covered_sha,
                current_head_sha,
                cwd=cwd,
            )
            relevance = checks_for_paths(changed)
        except PolicyEvidenceError:
            due.add(check_id)
            continue
        if check_id in relevance.selected:
            due.add(check_id)

    selected = tuple(
        check for check in REGISTERED_CHECKS if check in due
    )
    return PolicySelection(
        selected,
        True,
        "schedule-reconciliation",
    )
