"""Basic visualization helpers for the solo mining calculator."""

from __future__ import annotations

import numbers
from pathlib import Path
from typing import Iterable, Optional, Sequence

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

    @staticmethod
    def _normalize_series(
        data: Iterable[Iterable[float]] | Iterable[float],
        labels: Optional[Sequence[str]] = None,
    ) -> tuple[list[list[float]], list[str]]:
        values = list(data)
        if not values:
            raise ValueError("No data supplied for plotting.")

        if isinstance(values[0], numbers.Number):
            series = [values]
        else:
            series = [list(seq) for seq in values]

        resolved_labels = list(labels) if labels else [f"Series {idx + 1}" for idx in range(len(series))]
        if len(resolved_labels) != len(series):
            raise ValueError("Label count does not match data series count.")
        return series, resolved_labels

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

    def plot_scatter(
        self,
        x: Sequence[float],
        y: Sequence[float],
        title: str,
        xlabel: str,
        ylabel: str,
        filename: str = "scatter_plot.png",
    ) -> Path:
        """Create a scatter plot of paired observations."""
        plt.figure(figsize=(6, 4))
        plt.scatter(x, y, edgecolor="black")
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.grid(True, linestyle="--", alpha=0.5)
        save_path = FIG_DIR / filename
        plt.tight_layout()
        plt.savefig(save_path)
        plt.close()
        return save_path

    def plot_box(
        self,
        data: Iterable[Iterable[float]] | Iterable[float],
        title: str,
        ylabel: str,
        filename: str = "box_plot.png",
        labels: Optional[Sequence[str]] = None,
    ) -> Path:
        """Create a box-and-whisker plot for one or more series."""
        series, resolved_labels = self._normalize_series(data, labels)

        plt.figure(figsize=(6, 4))
        plt.boxplot(series, labels=resolved_labels, patch_artist=True)
        plt.title(title)
        plt.ylabel(ylabel)
        plt.grid(True, axis="y", linestyle="--", alpha=0.5)
        save_path = FIG_DIR / filename
        plt.tight_layout()
        plt.savefig(save_path)
        plt.close()
        return save_path

    def plot_violin(
        self,
        data: Iterable[Iterable[float]] | Iterable[float],
        title: str,
        ylabel: str,
        filename: str = "violin_plot.png",
        labels: Optional[Sequence[str]] = None,
    ) -> Path:
        """Create a violin plot to display data distributions."""
        series, resolved_labels = self._normalize_series(data, labels)

        plt.figure(figsize=(6, 4))
        parts = plt.violinplot(series, showmeans=True, showmedians=True)
        for body in parts["bodies"]:
            body.set_alpha(0.7)
        plt.title(title)
        plt.ylabel(ylabel)
        plt.xticks(range(1, len(resolved_labels) + 1), resolved_labels)
        plt.grid(True, axis="y", linestyle="--", alpha=0.5)
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
