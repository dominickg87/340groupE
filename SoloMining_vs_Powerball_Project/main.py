#Version: v1.0
#Date Last Updated: 1-12-2025

#%% MODULE BEGINS
module_name_gl = "main"

"""
Version: v1.0

Description:
    command line workflow for the Solo Mining vs Powerball project. Prompts the user for
    mining inputs, prints summaries, and generates supporting tables/plots.

Authors:
    Group E

Date Created     :  2025-11-10
Date Last Updated:  2025-01-12

Doc:
    Refer to DomNotes.md for detailed usage instructions.
"""

#%% IMPORTS                    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
from __future__ import annotations

from pathlib import Path
from typing import List

import pandas as pd

from config import APP_VERSION
from lib.module import LOGGER, write_csv
from lottery_models import PowerballModel, PowerballScenario
from mining_models import SoloMiningModel
from viz_base import VizBase


#%% CONSTANTS                   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
PROJECT_ROOT = Path(__file__).resolve().parent
OUTPUT_TABLES = PROJECT_ROOT / "Output" / "tables"


#%% FUNCTION DEFINITIONS        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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


def run_powerball_demo() -> None:
    """Helper for manually running the Powerball scenario demo."""
    run_powerball()


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
        ylabel="Probability of Finding >=1 Block",
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


#%% PARTNER POWERBALL LOGIC    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def run_powerball():
    """Original Powerball demo contributed by partner code."""
    sc = PowerballScenario(
        num_tickets=10,
        drawings_per_week=3,
        weeks=2,
        jackpot=120_000_000.0,  # override per run
        # Optional: payouts=your_custom_dict
    )
    model = PowerballModel(sc)
    df = model.to_dataframe()
    print(df)
    print(f"EV per ticket: {round(model.expected_value_per_ticket(), 2)}$")
    print(f"Total EV for scenario: {round(model.expected_value_total(), 2)}$")
    print("P(>=1 jackpot):", model.prob_at_least_one_jackpot())
    print("P(>=1 any):", model.prob_at_least_one_any_prize())
    model.export_csv("powerball_example.csv")
    model.export_pickle("powerball_example.pkl")


#%% SELF-RUN                    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
if __name__ == "__main__":
    print(f'"{module_name_gl}" module begins.')
    main()
