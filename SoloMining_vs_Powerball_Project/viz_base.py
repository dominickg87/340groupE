"""Basic visualization helpers for the solo mining calculator."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Sequence

import matplotlib.pyplot as plt

# Resolve directories relative to project root.
PROJECT_ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = PROJECT_ROOT / "Output"
FIG_DIR = OUTPUT_DIR / "figs"


class VizBase:
    """Common plotting utilities built on top of matplotlib."""

    def __init__(self) -> None:
        # Create the folder once so individual plots can save without errors.
        FIG_DIR.mkdir(parents=True, exist_ok=True)

    def plot_line(
        self,
        x: Sequence[float],
        y: Sequence[float],
        title: str,
        xlabel: str,
        ylabel: str,
        filename: str = "line_plot.png",
    ) -> Path:
        """Create a simple line plot and save it to disk."""
        plt.figure(figsize=(6, 4))
        plt.plot(x, y, marker="o")
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.grid(True)
        save_path = FIG_DIR / filename
        plt.tight_layout()
        plt.savefig(save_path)
        plt.close()
        return save_path

    def plot_hist(
        self,
        data: Iterable[float],
        title: str,
        filename: str = "hist_plot.png",
        bins: int = 10,
    ) -> Path:
        """Create a histogram and save it to disk."""
        plt.figure(figsize=(6, 4))
        plt.hist(list(data), bins=bins, edgecolor="black")
        plt.title(title)
        plt.xlabel("Value")
        plt.ylabel("Frequency")
        plt.grid(True)
        save_path = FIG_DIR / filename
        plt.tight_layout()
        plt.savefig(save_path)
        plt.close()
        return save_path
