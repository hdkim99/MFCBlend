"""Optional result plotting; imported nowhere by the scientific core."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mfcblend.core import FeedResult, FeedSystem


def save_feed_diagram(
    system: FeedSystem,
    result: FeedResult,
    destination: str | Path,
    *,
    width_px: int = 1280,
    height_px: int = 640,
) -> Path:
    """Render an actual cylinder/MFC/result diagram using a non-interactive backend."""

    import matplotlib

    matplotlib.use("Agg", force=True)
    from matplotlib import pyplot as plt
    from matplotlib.patches import FancyBboxPatch

    dpi = 100
    figure, axis = plt.subplots(figsize=(width_px / dpi, height_px / dpi), dpi=dpi)
    figure.patch.set_facecolor("#08111f")
    axis.set_facecolor("#08111f")
    axis.set_xlim(0, 12.8)
    axis.set_ylim(0, 6.4)
    axis.axis("off")

    axis.text(0.6, 5.75, "MFCBlend", color="#e8f0ff", fontsize=27, fontweight="bold")
    axis.text(
        0.6,
        5.35,
        "Constrained catalytic-reactor gas-feed planning",
        color="#8ea7c9",
        fontsize=14,
    )
    active = [(cylinder, result.setpoints.get(cylinder.name, 0.0)) for cylinder in system.cylinders]
    spacing = 4.3 / max(1, len(active))
    for index, (cylinder, flow) in enumerate(active):
        y = 4.65 - index * spacing
        patch = FancyBboxPatch(
            (0.7, y - 0.5),
            3.25,
            0.78,
            boxstyle="round,pad=0.05,rounding_size=0.08",
            facecolor="#132640",
            edgecolor="#2dd4bf",
            linewidth=1.2,
        )
        axis.add_patch(patch)
        composition = " / ".join(
            f"{100 * fraction:g}% {species}" for species, fraction in cylinder.composition.items()
        )
        axis.text(0.95, y - 0.02, cylinder.name, color="white", fontsize=12, fontweight="bold")
        axis.text(0.95, y - 0.31, composition, color="#9fb2cc", fontsize=9)
        axis.text(
            3.72,
            y - 0.16,
            f"{flow:.3g}\n{result.flow_unit}",
            color="#5eead4",
            fontsize=10,
            ha="right",
        )
        axis.annotate(
            "",
            xy=(6.25, 3.2),
            xytext=(4.05, y - 0.12),
            arrowprops={"arrowstyle": "->", "color": "#58718f", "linewidth": 1.4},
        )

    mixer = FancyBboxPatch(
        (5.8, 2.6),
        1.45,
        1.2,
        boxstyle="round,pad=0.08,rounding_size=0.18",
        facecolor="#0f766e",
        edgecolor="#5eead4",
        linewidth=1.6,
    )
    axis.add_patch(mixer)
    axis.text(6.53, 3.35, "MIX", color="white", fontsize=18, fontweight="bold", ha="center")
    axis.text(6.53, 2.95, result.status.value.upper(), color="#ccfbf1", fontsize=10, ha="center")
    axis.annotate(
        "",
        xy=(8.25, 3.2),
        xytext=(7.3, 3.2),
        arrowprops={"arrowstyle": "->", "color": "#5eead4", "linewidth": 2.0},
    )

    target = FancyBboxPatch(
        (8.25, 1.35),
        3.85,
        3.7,
        boxstyle="round,pad=0.09,rounding_size=0.1",
        facecolor="#132640",
        edgecolor="#60a5fa",
        linewidth=1.5,
    )
    axis.add_patch(target)
    axis.text(8.65, 4.58, "REACTOR FEED", color="white", fontsize=15, fontweight="bold")
    axis.text(
        8.65,
        4.15,
        f"Total  {result.total_flow:.4g} {result.flow_unit}",
        color="#93c5fd",
        fontsize=12,
    )
    for index, (species, fraction) in enumerate(result.composition.items()):
        axis.text(
            8.65,
            3.65 - index * 0.42,
            f"{species:<8} {100 * fraction:8.3f} mol%",
            color="#dbeafe",
            fontsize=11,
            family="monospace",
        )
    axis.text(
        0.7,
        0.42,
        (
            f"Reference: {result.standard_conditions.temperature_k:g} K, "
            f"{result.standard_conditions.pressure_pa:g} Pa absolute  •  "
            "ideal linear material balance  •  not a safety assessment"
        ),
        color="#7890ad",
        fontsize=9,
    )
    destination_path = Path(destination)
    destination_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(destination_path, dpi=dpi, facecolor=figure.get_facecolor(), bbox_inches=None)
    plt.close(figure)
    return destination_path
