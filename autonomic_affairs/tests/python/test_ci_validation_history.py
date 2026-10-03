from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import subprocess
import tempfile
import unittest

from autonomic_affairs.ci_validation_history import (
    GitHubActionsHistory,
    reconcile_scheduled_checks,
    successful_check_executions,
)

UTC = timezone.utc


def ts(hours: int) -> str:
    return (
        datetime(2026, 10, 1, tzinfo=UTC) + timedelta(hours=hours)
    ).isoformat().replace("+00:00", "Z")


class FakeHistory:
    def __init__(self, runs, jobs):
        self._runs = tuple(runs)
        self._jobs = jobs

    def recent_runs(self):
        return self._runs

    def jobs_for_run(self, run_id):
        return tuple(self._jobs.get(run_id, ()))


def run(
    run_id,
    sha,
    *,
    branch="main",
    conclusion="success",
    updated_at=None,
):
    return {
        "id": run_id,
        "head_sha": sha,
        "head_branch": branch,
        "conclusion": conclusion,
        "updated_at": updated_at or ts(run_id),
    }


def job(
    sha,
    *steps,
    conclusion="success",
    name="linux / linux_validation",
    completed_at=None,
):
    return {
        "head_sha": sha,
        "name": name,
        "conclusion": conclusion,
        "completed_at": completed_at or ts(10),
        "steps": list(steps),
    }


def step(check_id, conclusion="success", completed_at=None):
    return {
        "name": f"Check {check_id}",
        "conclusion": conclusion,
        "completed_at": completed_at or ts(10),
    }


class HistoryParsingTests(unittest.TestCase):
    def test_successful_stable_step_is_recorded(self):
        history = FakeHistory(
            [run(2, "b"), run(1, "a")],
            {
                2: [
                    job(
                        "b",
                        step("linux-python", completed_at=ts(20)),
                    )
                ],
                1: [],
            },
        )
        found = successful_check_executions(
            history,
            current_run_id=99,
            default_branch="main",
        )
        self.assertEqual("b", found["linux-python"][0])
        self.assertEqual(
            datetime.fromisoformat(ts(20).replace("Z", "+00:00")),
            found["linux-python"][1],
        )

    def test_skipped_step_does_not_count_as_coverage(self):
        history = FakeHistory(
            [run(2, "b")],
            {
                2: [
                    job(
                        "b",
                        step("linux-python", conclusion="skipped"),
                    )
                ]
            },
        )
        found = successful_check_executions(
            history,
            current_run_id=99,
            default_branch="main",
        )
        self.assertNotIn("linux-python", found)

    def test_current_run_and_non_main_runs_are_ignored(self):
        history = FakeHistory(
            [
                run(9, "current"),
                run(8, "agent", branch="agent/x"),
                run(7, "main"),
            ],
            {
                9: [job("current", step("linux-python"))],
                8: [job("agent", step("linux-python"))],
                7: [
                    job(
                        "main",
                        step("linux-python", completed_at=ts(7)),
                    )
                ],
            },
        )
        found = successful_check_executions(
            history,
            current_run_id=9,
            default_branch="main",
        )
        self.assertEqual("main", found["linux-python"][0])

    def test_latest_success_wins_and_failed_step_does_not_replace_it(self):
        history = FakeHistory(
            [run(3, "c"), run(2, "b"), run(1, "a")],
            {
                3: [
                    job(
                        "c",
                        step("linux-python", conclusion="failure"),
                    )
                ],
                2: [
                    job(
                        "b",
                        step("linux-python", completed_at=ts(20)),
                    )
                ],
                1: [
                    job(
                        "a",
                        step("linux-python", completed_at=ts(10)),
                    )
                ],
            },
        )
        found = successful_check_executions(
            history,
            current_run_id=99,
            default_branch="main",
        )
        self.assertEqual("b", found["linux-python"][0])

    def test_successful_codeql_job_identity_counts(self):
        history = FakeHistory(
            [run(4, "d")],
            {
                4: [
                    job(
                        "d",
                        name="codeql-python / Check codeql-python",
                        completed_at=ts(30),
                    )
                ]
            },
        )
        found = successful_check_executions(
            history,
            current_run_id=99,
            default_branch="main",
        )
        self.assertEqual("d", found["codeql-python"][0])


class ScheduledReconciliationTests(unittest.TestCase):
    def _git(self, root: Path, *args: str) -> str:
        result = subprocess.run(
            ["git", *args],
            cwd=root,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return result.stdout.strip()

    def _commit(self, root: Path, message: str) -> str:
        self._git(root, "add", "-A")
        self._git(root, "commit", "-m", message)
        return self._git(root, "rev-parse", "HEAD")

    def _repo(self):
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        self._git(root, "init")
        self._git(root, "config", "user.email", "tests@example.invalid")
        self._git(root, "config", "user.name", "Tests")
        return temp, root

    def _coverage(self, check_id, sha, completed_at):
        return FakeHistory(
            [run(1, sha)],
            {
                1: [
                    job(
                        sha,
                        step(check_id, completed_at=completed_at),
                        completed_at=completed_at,
                    )
                ]
            },
        )

    def test_unrelated_docs_change_preserves_python_check_coverage(self):
        temp, root = self._repo()
        with temp:
            (root / "annexation_procedures").mkdir()
            (root / "annexation_procedures/runtime.py").write_text(
                "x=1",
                encoding="utf-8",
            )
            old = self._commit(root, "[Test] Base")
            (root / "autonomic_affairs/tasks").mkdir(parents=True)
            (root / "autonomic_affairs/tasks/note.md").write_text(
                "docs",
                encoding="utf-8",
            )
            head = self._commit(root, "[Documentation] Docs")
            selection = reconcile_scheduled_checks(
                self._coverage("linux-python", old, ts(20)),
                current_run_id=99,
                default_branch="main",
                current_head_sha=head,
                current_head_committed_at=datetime(
                    2026, 10, 1, tzinfo=UTC
                ),
                now=datetime(2026, 10, 2, tzinfo=UTC),
                cwd=root,
                checks=("linux-python",),
            )
            self.assertEqual((), selection.selected)

    def test_relevant_python_change_invalidates_old_python_coverage(self):
        temp, root = self._repo()
        with temp:
            (root / "annexation_procedures").mkdir()
            runtime = root / "annexation_procedures/runtime.py"
            runtime.write_text("x=1", encoding="utf-8")
            old = self._commit(root, "[Test] Base")
            runtime.write_text("x=2", encoding="utf-8")
            head = self._commit(root, "[Fix] Runtime")
            selection = reconcile_scheduled_checks(
                self._coverage("linux-python", old, ts(20)),
                current_run_id=99,
                default_branch="main",
                current_head_sha=head,
                current_head_committed_at=datetime(
                    2026, 10, 1, tzinfo=UTC
                ),
                now=datetime(2026, 10, 2, tzinfo=UTC),
                cwd=root,
                checks=("linux-python",),
            )
            self.assertEqual(("linux-python",), selection.selected)

    def test_unreachable_old_sha_fails_safe_due(self):
        temp, root = self._repo()
        with temp:
            (root / "a").write_text("a", encoding="utf-8")
            head = self._commit(root, "[Test] Head")
            selection = reconcile_scheduled_checks(
                self._coverage("linux-python", "f" * 40, ts(20)),
                current_run_id=99,
                default_branch="main",
                current_head_sha=head,
                current_head_committed_at=datetime(
                    2026, 10, 1, tzinfo=UTC
                ),
                now=datetime(2026, 10, 2, tzinfo=UTC),
                cwd=root,
                checks=("linux-python",),
            )
            self.assertEqual(("linux-python",), selection.selected)

    def test_codeql_requires_exact_head_success(self):
        selection = reconcile_scheduled_checks(
            self._coverage("codeql-python", "old", ts(20)),
            current_run_id=99,
            default_branch="main",
            current_head_sha="head",
            current_head_committed_at=datetime(
                2026, 10, 1, tzinfo=UTC
            ),
            now=datetime(2026, 10, 2, tzinfo=UTC),
            checks=("codeql-python",),
        )
        self.assertEqual(("codeql-python",), selection.selected)

    def test_recent_head_codeql_uses_24_hour_cadence(self):
        now = datetime(2026, 10, 3, tzinfo=UTC)
        head_time = now - timedelta(days=2)
        not_due = reconcile_scheduled_checks(
            self._coverage(
                "codeql-python",
                "head",
                (now - timedelta(hours=23)).isoformat(),
            ),
            current_run_id=99,
            default_branch="main",
            current_head_sha="head",
            current_head_committed_at=head_time,
            now=now,
            checks=("codeql-python",),
        )
        self.assertEqual((), not_due.selected)
        due = reconcile_scheduled_checks(
            self._coverage(
                "codeql-python",
                "head",
                (now - timedelta(hours=24)).isoformat(),
            ),
            current_run_id=99,
            default_branch="main",
            current_head_sha="head",
            current_head_committed_at=head_time,
            now=now,
            checks=("codeql-python",),
        )
        self.assertEqual(("codeql-python",), due.selected)

    def test_old_head_codeql_uses_168_hour_cadence(self):
        now = datetime(2026, 10, 10, tzinfo=UTC)
        head_time = now - timedelta(days=8)
        not_due = reconcile_scheduled_checks(
            self._coverage(
                "codeql-actions",
                "head",
                (now - timedelta(days=6)).isoformat(),
            ),
            current_run_id=99,
            default_branch="main",
            current_head_sha="head",
            current_head_committed_at=head_time,
            now=now,
            checks=("codeql-actions",),
        )
        self.assertEqual((), not_due.selected)
        due = reconcile_scheduled_checks(
            self._coverage(
                "codeql-actions",
                "head",
                (now - timedelta(days=7)).isoformat(),
            ),
            current_run_id=99,
            default_branch="main",
            current_head_sha="head",
            current_head_committed_at=head_time,
            now=now,
            checks=("codeql-actions",),
        )
        self.assertEqual(("codeql-actions",), due.selected)

    def test_codeql_languages_reconcile_independently(self):
        now = datetime(2026, 10, 3, tzinfo=UTC)
        history = FakeHistory(
            [run(2, "head"), run(1, "head")],
            {
                2: [
                    job(
                        "head",
                        name="codeql-python / Check codeql-python",
                        completed_at=(
                            now - timedelta(hours=2)
                        ).isoformat(),
                    )
                ],
                1: [],
            },
        )
        selection = reconcile_scheduled_checks(
            history,
            current_run_id=99,
            default_branch="main",
            current_head_sha="head",
            current_head_committed_at=now - timedelta(days=2),
            now=now,
            checks=("codeql-python", "codeql-actions"),
        )
        self.assertEqual(("codeql-actions",), selection.selected)


class ClientShapeTests(unittest.TestCase):
    def test_client_builds_authenticated_actions_requests(self):
        seen = []

        class Response:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                return None

            def read(self):
                return b'{"workflow_runs": []}'

        def opener(request):
            seen.append(request)
            return Response()

        client = GitHubActionsHistory(
            "owner/repo",
            "secret",
            123,
            opener=opener,
        )
        self.assertEqual((), client.recent_runs())
        self.assertIn(
            "/repos/owner/repo/actions/runs?",
            seen[0].full_url,
        )
        self.assertEqual(
            "Bearer secret",
            seen[0].get_header("Authorization"),
        )


if __name__ == "__main__":
    unittest.main()
