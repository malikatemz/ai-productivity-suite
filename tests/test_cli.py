import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent


def run(*args):
    return subprocess.run(
        [sys.executable, *args], cwd=ROOT, capture_output=True, text=True
    )


def test_meeting_cli():
    result = run("meeting_notes.py", "--file", "samples/meeting_notes.txt", "--offline")
    assert result.returncode == 0, result.stderr
    assert "## Summary" in result.stdout


def test_task_cli():
    result = run("task_prioritiser.py", "--file", "samples/tasks.txt", "--offline")
    assert result.returncode == 0, result.stderr
    assert "| Priority | Task |" in result.stdout


def test_planner_cli():
    result = run(
        "daily_planner.py", "--file", "samples/tasks.txt", "--hours", "4", "--offline"
    )
    assert result.returncode == 0, result.stderr
    assert "| Time | Task | Notes |" in result.stdout
