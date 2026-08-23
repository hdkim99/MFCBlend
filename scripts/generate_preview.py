"""Regenerate the social preview from the documented exact inverse example."""

from pathlib import Path

from mfcblend.application import RunRequest, execute
from mfcblend.io import load_system
from mfcblend.plotting import save_feed_diagram

ROOT = Path(__file__).resolve().parents[1]
system_path = ROOT / "examples" / "co2_hydrogen_system.json"
result = execute(
    RunRequest(
        system_path=system_path,
        values_path=ROOT / "examples" / "target_5co2_20h2.json",
        mode="inverse",
    )
)
save_feed_diagram(load_system(system_path), result, ROOT / "docs" / "assets" / "social-preview.png")
