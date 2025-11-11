from __future__ import annotations
module_name_gl = 'lottery_models'

'''
Version: v1.0
Description:
    Powerball probability + EV model.
    - Computes per-ticket probabilities for all standard tiers from combinatorics.
    - Supports scenarios: num_tickets, drawings_per_week, weeks, jackpot, ticket_cost.
    - Exports CSV/PKL and logs steps.
Authors: Group E
Date Created     : 2025-11-10
Date Last Updated: 2025-11-10
Doc: see project PDF & group doc
'''

#%% IMPORTS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os
import math
import json
import pickle
import logging
from dataclasses import dataclass, asdict
from typing import Dict, Tuple, List

import pandas as pd

from probability_base import ProbabilityBase
import config

#%% USER INTERFACE ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# None

#%% CONSTANTS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
WB = config.POWERBALL["white_ball_count"]
DW = config.POWERBALL["draw_white"]
PB = config.POWERBALL["power_ball_count"]
DEFAULT_PAYOUTS = config.POWERBALL["default_payouts"]
TICKET_COST = float(config.POWERBALL["ticket_cost"])

#%% CONFIGURATION / LOGGING ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
os.makedirs(config.OUTPUT_DIR_LOG, exist_ok=True)
LOG_PATH = os.path.join(config.OUTPUT_DIR_LOG, "lottery.log")
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

#%% DECLARATIONS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@dataclass
class PowerballScenario:
    num_tickets: int
    drawings_per_week: int
    weeks: int
    jackpot: float
    ticket_cost: float = TICKET_COST
    # Optional override of tier payouts
    payouts: Dict[Tuple[int, bool], float] = None

    @property
    def total_drawings(self) -> int:
        return self.drawings_per_week * self.weeks

    @property
    def total_tickets(self) -> int:
        return self.num_tickets * self.total_drawings


class PowerballModel(ProbabilityBase):
    """
    Child class implementing Powerball math:
    - exact per-ticket probabilities per prize tier via combinations
    - aggregate 'at least one win' across tickets/drawings
    - expected value and CSV/PKL export
    """

    def __init__(self, scenario: PowerballScenario):
        self.sc = scenario
        self._payouts = (scenario.payouts or DEFAULT_PAYOUTS).copy()
        # Ensure jackpot is set from scenario
        self._payouts[(5, True)] = float(scenario.jackpot)

        logging.info("Initialized PowerballModel with %s", json.dumps(asdict(self.sc)))

        self._total_white = self.nCk(WB, DW)
        self._total_tickets_universe = self._total_white * PB

    # ---------- exact tier probabilities for ONE ticket ----------
    def _count_config(self, k_white: int, powerball_match: bool) -> int:
        """Number of favorable outcomes for a tier."""
        # Choose k matching whites from the 5 drawn, and (5-k) non-matching from remaining
        white_match = self.nCk(DW, k_white) * self.nCk(WB - DW, DW - k_white)
        pb_match = 1 if powerball_match else (PB - 1)
        return white_match * pb_match

    def per_ticket_probs(self) -> Dict[Tuple[int, bool], float]:
        """Probabilities for each prize tier for a single ticket."""
        tiers = [(5, True), (5, False), (4, True), (4, False),
                 (3, True), (3, False), (2, True), (1, True), (0, True)]
        probs = {}
        for t in tiers:
            cnt = self._count_config(*t)
            probs[t] = cnt / self._total_tickets_universe
        return probs

    def per_ticket_any_prize(self) -> float:
        pmap = self.per_ticket_probs()
        return sum(pmap.values())

    def per_ticket_jackpot(self) -> float:
        return self.per_ticket_probs()[(5, True)]

    # ---------- aggregation across many tickets ----------
    def prob_at_least_one_jackpot(self) -> float:
        trials = self.sc.total_tickets
        p = self.per_ticket_jackpot()
        return self.at_least_one(trials, p)

    def prob_at_least_one_any_prize(self) -> float:
        trials = self.sc.total_tickets
        p_any = self.per_ticket_any_prize()
        return self.at_least_one(trials, p_any)

    # ---------- expected value ----------
    def expected_value_per_ticket(self) -> float:
        pmap = self.per_ticket_probs()
        payouts = []
        probs = []
        for tier, p in pmap.items():
            payouts.append(self._payouts.get(tier, 0.0))
            probs.append(p)
        return self.expected_value(payouts, probs) - self.sc.ticket_cost

    def expected_value_total(self) -> float:
        return self.expected_value_per_ticket() * self.sc.total_tickets

    # ---------- tabular outputs ----------
    def to_dataframe(self) -> pd.DataFrame:
        pmap = self.per_ticket_probs()
        rows = []
        for (k, pbm), p in pmap.items():
            rows.append({
                "tier": f"{k}W + {'PB' if pbm else 'noPB'}",
                "k_white": k,
                "powerball_match": pbm,
                "prob_per_ticket": p,
                "payout": float(self._payouts.get((k, pbm), 0.0))
            })
        df = pd.DataFrame(rows).sort_values(
            by=["k_white", "powerball_match"], ascending=[False, False]
        )
        #Setting as nullable types mostly
        df["k_white"] = df["k_white"].astype("Int64")        # nullable integer
        df["powerball_match"] = df["powerball_match"].astype("boolean")  # nullable bool
        df["prob_per_ticket"] = df["prob_per_ticket"].astype(float)
        df["payout"] = df["payout"].astype("Float64")        # nullable float

        summary = pd.DataFrame([
            {
                "tier": "ANY PRIZE",
                "k_white": pd.NA,
                "powerball_match": pd.NA,
                "prob_per_ticket": self.per_ticket_any_prize(),
                "payout": pd.NA
            },
            {
                "tier": "JACKPOT",
                "k_white": 5,
                "powerball_match": True,
                "prob_per_ticket": self.per_ticket_jackpot(),
                "payout": float(self._payouts[(5, True)])
            }
        ])

        df = pd.concat([df.reset_index(drop=True), summary], ignore_index=True)
        return df

    # ---------- export ----------
    def export_csv(self, fname: str = "powerball_tiers.csv") -> str:
        path = os.path.join(config.OUTPUT_DIR, fname)
        self.to_dataframe().to_csv(path, index=False)
        logging.info("Exported CSV to %s", path)
        return path

    def export_pickle(self, fname: str = "powerball_scenario.pkl") -> str:
        path = os.path.join(config.OUTPUT_DIR, fname)
        with open(path, "wb") as f:
            pickle.dump(self.sc, f)
        logging.info("Exported PKL to %s", path)
        return path

    # ---------- simple query helpers ----------
    def query_tier(self, k_white: int, powerball_match: bool) -> Dict[str, float]:
        p = self.per_ticket_probs().get((k_white, powerball_match), 0.0)
        return {
            "tier": f"{k_white}W + {'PB' if powerball_match else 'noPB'}",
            "prob_per_ticket": p,
            "payout": float(self._payouts.get((k_white, powerball_match), 0.0))
        }


#%% SELF-RUN ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def main():
    # Example scenario for testing purposes
    sc = PowerballScenario(
        num_tickets=10,
        drawings_per_week=3,
        weeks=4,
        jackpot=80_000_000.0,  # set the live jackpot here
    )
    model = PowerballModel(sc)
    df = model.to_dataframe()
    print(df.head(12))

    print("Per-ticket EV ($):", round(model.expected_value_per_ticket(), 4))
    print("Total EV for scenario ($):", round(model.expected_value_total(), 2))
    print("P(at least one JACKPOT):", model.prob_at_least_one_jackpot())
    print("P(at least one ANY PRIZE):", model.prob_at_least_one_any_prize())

    csv_path = model.export_csv()
    pkl_path = model.export_pickle()
    print("Wrote:", csv_path, "and", pkl_path)

if __name__ == "__main__":
    print(f"\"{module_name_gl}\" module begins.")
    main()