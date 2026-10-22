"""Static validity checks for GitHub Actions workflow definitions (TODO-089).

Covers the PR #30 regression "workflow expressions must be valid": every
workflow parses as YAML, `needs:` targets exist, steps that use `${{ }}` keep
balanced delimiters, every `uses:` action is pinned to a ref, and referenced
repository scripts exist.
"""

from __future__ import annotations

import os
import re

import pytest
import yaml

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
WORKFLOW_DIR = os.path.join(REPO_ROOT, ".github", "workflows")

WORKFLOW_FILES = sorted(
    os.path.join(WORKFLOW_DIR, name)
    for name in os.listdir(WORKFLOW_DIR)
    if name.endswith((".yml", ".yaml"))
)

EXPRESSION = re.compile(r"\$\{\{(.*?)\}\}", re.S)


def _load(path):
    with open(path, encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def test_workflow_directory_is_not_empty():
    assert WORKFLOW_FILES, "no workflow files found"


@pytest.mark.parametrize("path", WORKFLOW_FILES, ids=lambda p: os.path.basename(p))
def test_workflow_yaml_parses(path):
    data = _load(path)
    assert isinstance(data, dict), f"{path} is not a mapping"
    assert "jobs" in data and data["jobs"], f"{path} declares no jobs"


@pytest.mark.parametrize("path", WORKFLOW_FILES, ids=lambda p: os.path.basename(p))
def test_workflow_expressions_are_balanced(path):
    with open(path, encoding="utf-8") as handle:
        text = handle.read()
    assert text.count("${{") == text.count("}}"), f"{path}: unbalanced expression delimiters"
    for match in EXPRESSION.finditer(text):
        body = match.group(1).strip()
        assert body, f"{path}: empty expression"
        assert body.count("'") % 2 == 0, f"{path}: unbalanced single quotes in {body!r}"


@pytest.mark.parametrize("path", WORKFLOW_FILES, ids=lambda p: os.path.basename(p))
def test_workflow_jobs_have_runner_and_valid_needs(path):
    data = _load(path)
    jobs = data["jobs"]
    for job_id, job in jobs.items():
        assert isinstance(job, dict), f"{path}: job {job_id} is not a mapping"
        assert "uses" in job or "runs-on" in job, f"{path}: job {job_id} has no runner or reusable call"
        for dependency in job.get("needs", []) if isinstance(job.get("needs", []), list) else [job.get("needs")]:
            assert dependency in jobs, f"{path}: job {job_id} needs unknown job {dependency}"


@pytest.mark.parametrize("path", WORKFLOW_FILES, ids=lambda p: os.path.basename(p))
def test_uses_steps_are_pinned(path):
    data = _load(path)
    for job_id, job in data["jobs"].items():
        for step in job.get("steps", []) or []:
            ref = step.get("uses")
            if not ref or ref.startswith("./"):
                continue
            assert "@" in ref, f"{path}: {job_id} uses unpinned action {ref}"
            _, version = ref.rsplit("@", 1)
            assert version, f"{path}: {job_id} uses {ref} without a ref"


@pytest.mark.parametrize("path", WORKFLOW_FILES, ids=lambda p: os.path.basename(p))
def test_referenced_repo_scripts_exist(path):
    data = _load(path)
    for job in data["jobs"].values():
        job_defaults = job.get("defaults") or {}
        default_dir = (job_defaults.get("run") or {}).get("working-directory") or ""
        for step in job.get("steps", []) or []:
            run = step.get("run") or ""
            step_dir = step.get("working-directory") or default_dir
            for script in re.findall(r"(?:python|node)\s+([\w./-]+\.(?:py|mjs|js))", run):
                candidate = os.path.normpath(
                    os.path.join(REPO_ROOT, step_dir, script.replace("/", os.sep))
                )
                assert candidate.startswith(REPO_ROOT), (
                    f"{path}: script {script} escapes the repository"
                )
                assert os.path.exists(candidate), f"{path}: missing script {step_dir}/{script}"
