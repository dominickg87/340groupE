"""Run the solo mining calculator with simple user interaction."""

from __future__ import annotations

from pathlib import Path
from typing import List

import pandas as pd

from config import APP_VERSION
from lib.module import LOGGER, write_csv
from mining_models import SoloMiningModel
from viz_base import VizBase

PROJECT_ROOT = Path(__file__).resolve().parent
OUTPUT_TABLES = PROJECT_ROOT / "Output" / "tables"


def prompt_float(prompt: str) -> float:
    """Keep asking the user for a number until they provide a valid value."""
    while True:
        raw = input(prompt)
        try:
            return float(raw)
        except ValueError:
            print("Please enter a numeric value.")


def build_scenarios(hashrate: float, days: float) -> pd.DataFrame:
    """Generate simple hashrate test cases so users can see how odds change."""
    sample_hashrates: List[float] = [
        max(0.1, hashrate * 0.5),
        hashrate,
        hashrate * 2,
        50.0,
        100.0,
        200.0,
    ]

    rows = []
    for h in sorted(set(round(val, 4) for val in sample_hashrates)):
        model = SoloMiningModel(h, days)
        lam = model.compute_lambda()
        probability = model.mining_probability()
        expected = model.expected_value()
        rows.append(
            {
                "hashrate_ths": h,
                "lambda": lam,
                "probability_at_least_one": probability,
                "expected_value_usd": expected,
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    """Entry point used by the CLI."""
    print("===================================")
    print(" Bitcoin Solo Mining Calculator")
    print(f" Version {APP_VERSION}")
    print("===================================")

    miner_hashrate = prompt_float("Enter your miner hashrate (TH/s): ")
    days = prompt_float("Enter the number of days to model: ")

    model = SoloMiningModel(miner_hashrate, days)
    model.print_summary()

    scenario_df = build_scenarios(miner_hashrate, days)

    viz = VizBase()
    plot_path = viz.plot_line(
        scenario_df["hashrate_ths"],
        scenario_df["probability_at_least_one"],
        title="Probability vs Hashrate",
        xlabel="Miner Hashrate (TH/s)",
        ylabel="Probability of Finding ≥1 Block",
        filename="probability_vs_hashrate.png",
    )
    print(f"Saved probability plot to: {plot_path}")

    csv_path = OUTPUT_TABLES / "probability_vs_hashrate.csv"
    if write_csv(scenario_df, csv_path):
        print(f"Saved scenario table to: {csv_path}")
    else:
        print("Failed to save the scenario table. See logs for details.")

    LOGGER.info(
        "Session complete for hashrate=%.2f TH/s, days=%.2f", miner_hashrate, days
    )


if __name__ == "__main__":
    main()
