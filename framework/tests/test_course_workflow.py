"""Release-gate regressions for the reusable course workflow."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess

import yaml


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "course.yml"


def _regeneration_script() -> str:
    workflow = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    steps = workflow["jobs"]["validate"]["steps"]
    step = next(
        item for item in steps
        if item.get("name") == "Regenerar y comprobar que nada se editó a mano"
    )
    return step["run"]


def _run_gate(
    script: str, repository: Path, runner_temp: Path
) -> subprocess.CompletedProcess[str]:
    gate = script[script.index('status_file="$RUNNER_TEMP/') :]
    environment = {**os.environ, "RUNNER_TEMP": str(runner_temp)}
    return subprocess.run(
        ["bash", "-e", "-o", "pipefail", "-c", gate],
        cwd=repository,
        env=environment,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )


def test_regeneration_gate_rejects_untracked_outputs(tmp_path: Path) -> None:
    script = _regeneration_script()
    assert 'status_file="$RUNNER_TEMP/course-regeneration-status.txt"' in script
    assert 'git status --porcelain=v1 --untracked-files=all > "$status_file"' in script
    assert 'if [ -s "$status_file" ]; then' in script
    assert 'sed -n \'1,200p\' "$status_file"' in script

    repository = tmp_path / "repository"
    runner_temp = tmp_path / "runner-temp"
    repository.mkdir()
    runner_temp.mkdir()
    for command in (
        ["git", "init", "-q"],
        ["git", "config", "user.name", "Audit Fixture"],
        ["git", "config", "user.email", "audit@example.invalid"],
    ):
        subprocess.run(command, cwd=repository, check=True)
    tracked = repository / "tracked.txt"
    tracked.write_text("committed\n", encoding="utf-8")
    subprocess.run(["git", "add", "tracked.txt"], cwd=repository, check=True)
    subprocess.run(["git", "commit", "-qm", "fixture"], cwd=repository, check=True)

    clean = _run_gate(script, repository, runner_temp)
    assert clean.returncode == 0, clean.stdout

    generated = repository / "generated-output.txt"
    generated.write_text("not committed\n", encoding="utf-8")
    dirty = _run_gate(script, repository, runner_temp)
    assert dirty.returncode == 1
    assert "?? generated-output.txt" in dirty.stdout
    status_file = runner_temp / "course-regeneration-status.txt"
    assert status_file.read_text(encoding="utf-8") == "?? generated-output.txt\n"

    generated.unlink()
    tracked.write_text("changed\n", encoding="utf-8")
    modified = _run_gate(script, repository, runner_temp)
    assert modified.returncode == 1
    assert " M tracked.txt" in modified.stdout
