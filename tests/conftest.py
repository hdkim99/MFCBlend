from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def _run_from_repository_root(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(Path(__file__).resolve().parents[1])
