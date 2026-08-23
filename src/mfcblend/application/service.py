"""Application services shared by the CLI and GUI."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from mfcblend.core import FeedResult, forward_mix, inverse_mix
from mfcblend.io import export_result, load_setpoints, load_system, load_target


@dataclass(frozen=True)
class RunRequest:
    system_path: Path
    values_path: Path
    mode: str
    allow_approximate: bool = False


def execute(request: RunRequest) -> FeedResult:
    system = load_system(request.system_path)
    if request.mode == "forward":
        return forward_mix(system, load_setpoints(request.values_path))
    if request.mode == "inverse":
        composition, total_flow = load_target(request.values_path)
        return inverse_mix(
            system,
            composition,
            total_flow,
            allow_approximate=request.allow_approximate,
        )
    raise ValueError("mode must be 'forward' or 'inverse'.")


def execute_and_export(request: RunRequest, destination: str | Path) -> FeedResult:
    result = execute(request)
    export_result(result, destination)
    return result
