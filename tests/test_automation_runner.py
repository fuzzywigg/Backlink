"""Unit tests for LIVE automation.runner.AutonomousRunner.

Covers manifest load/save, stop-hook, logging, and execute_next tick
behavior — no network, secrets, or production deploy paths. All FS I/O
is confined to tmp_path.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

from automation.runner import AutonomousRunner


def _write_manifest(path: Path, tasks: list[dict[str, Any]]) -> Path:
    path.write_text(json.dumps(tasks), encoding="utf-8")
    return path


@pytest.fixture
def runner_env(tmp_path: Path) -> tuple[AutonomousRunner, Path]:
    """Isolated runner with temp manifest, stop signal, and session log."""
    manifest_path = tmp_path / "manifest.json"
    _write_manifest(
        manifest_path,
        [
            {
                "id": "task_a",
                "description": "First pending task",
                "status": "pending",
                "priority": "high",
            },
            {
                "id": "task_b",
                "description": "Already done",
                "status": "completed",
                "priority": "low",
            },
        ],
    )
    runner = AutonomousRunner(manifest_path=str(manifest_path))
    runner.stop_signal_file = str(tmp_path / "STOP.signal")
    runner.log_file = str(tmp_path / "session.log")
    return runner, manifest_path


@pytest.mark.unit
class TestLoadManifest:
    """_load_manifest() reads task list from JSON."""

    def test_loads_tasks_from_manifest_path(self, tmp_path: Path) -> None:
        path = _write_manifest(
            tmp_path / "m.json",
            [{"id": "x", "description": "d", "status": "pending"}],
        )
        runner = AutonomousRunner(manifest_path=str(path))
        assert len(runner.manifest) == 1
        assert runner.manifest[0]["id"] == "x"

    def test_missing_manifest_raises(self, tmp_path: Path) -> None:
        missing = tmp_path / "absent.json"
        with pytest.raises(FileNotFoundError):
            AutonomousRunner(manifest_path=str(missing))


@pytest.mark.unit
class TestSaveManifest:
    """_save_manifest() persists in-memory task list."""

    def test_writes_updated_status(self, runner_env: tuple[AutonomousRunner, Path]) -> None:
        runner, manifest_path = runner_env
        runner.manifest[0]["status"] = "in_progress"
        runner._save_manifest()
        saved = json.loads(manifest_path.read_text(encoding="utf-8"))
        assert saved[0]["status"] == "in_progress"
        assert saved[1]["status"] == "completed"


@pytest.mark.unit
class TestLog:
    """log() prints and appends timestamped lines."""

    def test_appends_to_log_file(
        self, runner_env: tuple[AutonomousRunner, Path], capsys: pytest.CaptureFixture[str]
    ) -> None:
        runner, _ = runner_env
        runner.log("hello hive")
        log_text = Path(runner.log_file).read_text(encoding="utf-8")
        assert "hello hive" in log_text
        assert log_text.startswith("[")
        captured = capsys.readouterr()
        assert "hello hive" in captured.out

    def test_appends_multiple_entries(self, runner_env: tuple[AutonomousRunner, Path]) -> None:
        runner, _ = runner_env
        runner.log("one")
        runner.log("two")
        lines = Path(runner.log_file).read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 2
        assert "one" in lines[0]
        assert "two" in lines[1]


@pytest.mark.unit
class TestCheckStopHook:
    """check_stop_hook() halt when STOP.signal is present."""

    def test_returns_false_when_absent(self, runner_env: tuple[AutonomousRunner, Path]) -> None:
        runner, _ = runner_env
        assert runner.check_stop_hook() is False

    def test_returns_true_when_present(
        self, runner_env: tuple[AutonomousRunner, Path], capsys: pytest.CaptureFixture[str]
    ) -> None:
        runner, _ = runner_env
        Path(runner.stop_signal_file).write_text("stop", encoding="utf-8")
        assert runner.check_stop_hook() is True
        assert "STOP SIGNAL" in Path(runner.log_file).read_text(encoding="utf-8")
        assert "STOP SIGNAL" in capsys.readouterr().out


@pytest.mark.unit
class TestExecuteNext:
    """execute_next() single-tick pending → in_progress transition."""

    def test_marks_first_pending_in_progress(
        self, runner_env: tuple[AutonomousRunner, Path]
    ) -> None:
        runner, manifest_path = runner_env
        assert runner.execute_next() is True
        assert runner.manifest[0]["status"] == "in_progress"
        assert runner.manifest[1]["status"] == "completed"
        saved = json.loads(manifest_path.read_text(encoding="utf-8"))
        assert saved[0]["status"] == "in_progress"
        log_text = Path(runner.log_file).read_text(encoding="utf-8")
        assert "Starting Task: task_a" in log_text
        assert "IN_PROGRESS" in log_text

    def test_skips_non_pending_tasks(self, tmp_path: Path) -> None:
        path = _write_manifest(
            tmp_path / "m.json",
            [
                {"id": "done", "description": "d", "status": "completed"},
                {"id": "next", "description": "n", "status": "pending"},
            ],
        )
        runner = AutonomousRunner(manifest_path=str(path))
        runner.stop_signal_file = str(tmp_path / "STOP.signal")
        runner.log_file = str(tmp_path / "session.log")
        assert runner.execute_next() is True
        assert runner.manifest[0]["status"] == "completed"
        assert runner.manifest[1]["status"] == "in_progress"

    def test_returns_false_when_all_completed(self, tmp_path: Path) -> None:
        path = _write_manifest(
            tmp_path / "m.json",
            [
                {"id": "a", "description": "d", "status": "completed"},
                {"id": "b", "description": "d", "status": "failed"},
            ],
        )
        runner = AutonomousRunner(manifest_path=str(path))
        runner.stop_signal_file = str(tmp_path / "STOP.signal")
        runner.log_file = str(tmp_path / "session.log")
        assert runner.execute_next() is False
        log_text = Path(runner.log_file).read_text(encoding="utf-8")
        assert "All tasks in manifest completed" in log_text

    def test_halts_on_stop_signal_before_enact(
        self, runner_env: tuple[AutonomousRunner, Path]
    ) -> None:
        runner, manifest_path = runner_env
        Path(runner.stop_signal_file).write_text("stop", encoding="utf-8")
        assert runner.execute_next() is False
        saved = json.loads(manifest_path.read_text(encoding="utf-8"))
        assert saved[0]["status"] == "pending"

    def test_marks_failed_when_save_raises(self, runner_env: tuple[AutonomousRunner, Path]) -> None:
        runner, _ = runner_env
        # First save (in_progress) fails; second save (failed) succeeds.
        with patch.object(
            runner,
            "_save_manifest",
            side_effect=[OSError("disk full"), None],
        ):
            assert runner.execute_next() is False
        assert runner.manifest[0]["status"] == "failed"
        log_text = Path(runner.log_file).read_text(encoding="utf-8")
        assert "Error in Task task_a" in log_text
        assert "disk full" in log_text

    def test_empty_manifest_returns_false(self, tmp_path: Path) -> None:
        path = _write_manifest(tmp_path / "empty.json", [])
        runner = AutonomousRunner(manifest_path=str(path))
        runner.stop_signal_file = str(tmp_path / "STOP.signal")
        runner.log_file = str(tmp_path / "session.log")
        assert runner.execute_next() is False
