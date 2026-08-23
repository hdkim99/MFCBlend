from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_dgx_routing_and_public_fork_guard() -> None:
    workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert "runs-on: [self-hosted, Linux, ARM64, dgx-spark]" in workflow
    assert "pull_request_target" not in workflow
    assert "github.event.pull_request.head.repo.full_name == github.repository" in workflow
    assert "permissions:\n  contents: read" in workflow


def test_actions_are_pinned_to_full_commit_shas() -> None:
    for path in (ROOT / ".github/workflows").glob("*.yml"):
        workflow = path.read_text(encoding="utf-8")
        for action in re.findall(r"uses:\s+([^\s#]+)", workflow):
            assert re.fullmatch(r"[^@]+@[0-9a-f]{40}", action), (path, action)


def test_package_and_cli_have_no_qt_dependencies() -> None:
    metadata = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    lowered = metadata.lower()
    assert 'name = "mfcblend"' in metadata
    assert 'mfcblend = "mfcblend.cli:main"' in metadata
    assert "pyqt" not in lowered
    assert "pyside" not in lowered
    assert "qtpy" not in lowered


def test_release_uses_trusted_publishing_environment() -> None:
    workflow = (ROOT / ".github/workflows/release.yml").read_text(encoding="utf-8")
    assert "id-token: write" in workflow
    assert "name: pypi" in workflow
    assert "gh-action-pypi-publish@" in workflow
    assert "API_TOKEN" not in workflow
