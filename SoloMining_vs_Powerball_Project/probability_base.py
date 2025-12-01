from __future__ import annotations

#Version: v1.0
#Date Last Updated: 1-12-2025

#%% MODULE BEGINS
module_name_gl = "probability_base"

"""
Version: v1.0

Description:
    Shared probability helpers for Poisson, binomial, and tabular operations.

Authors:
    Group E

Date Created     :  2025-11-10
Date Last Updated:  2025-01-12

Doc:
    Refer to DomNotes.md for dependency details.

Notes:
    
"""

#%% IMPORTS                    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import math
from typing import Any, Iterable, Sequence

import numpy as np
import pandas as pd


#%% CLASS DEFINITIONS          ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class ProbabilityBase:
    """Probability helper shared by mining and lottery models."""

    # --- Poisson helpers -------------------------------------------------
    def poisson_probability(self, lam: float, k: int) -> float:
        """Return P(k; lambda) = e^-lambda * lambda^k / k! for integer k."""
        lam = float(lam)
        k = int(k)
        return math.exp(-lam) * (lam**k) / math.factorial(k)

    def prob_at_least_one(self, lam: float) -> float:
        """Return the chance of at least one success in a Poisson process."""
        lam = float(lam)
        return 1.0 - math.exp(-lam)

    # --- DataFrame helper ------------------------------------------------
    def query_column(self, df: pd.DataFrame, column: str, value: Any) -> pd.DataFrame:
        """Filter a DataFrame by a column value and return the matching rows."""
        if column not in df.columns:
            raise KeyError(f"Column '{column}' not found in DataFrame.")

        data = df[column].to_numpy()
        mask = np.asarray(data == value)
        return df.loc[mask].copy()

    # --- Combinatorics + EV helpers --------------------------------------
    @staticmethod
    def nCk(n: int, k: int) -> int:
        """Return combinations of n choose k."""
        return math.comb(int(n), int(k))

    @staticmethod
    def binom_pmf(n: int, p: float, k: int) -> float:
        """Binomial probability mass function."""
        return math.comb(n, k) * (p**k) * ((1 - p) ** (n - k))

    @staticmethod
    def at_least_one(trials: int, p_single: float) -> float:
        """Return P(>=1) for repeated independent trials."""
        return 1.0 - (1.0 - p_single) ** trials

    @staticmethod
    def expected_value(payouts: Iterable[float], probs: Iterable[float]) -> float:
        """Return sum(payout_i * prob_i)."""
        return sum(x * p for x, p in zip(payouts, probs))


#%% FUNCTION DEFINITIONS        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def _demo() -> Sequence[float]:
    helper = ProbabilityBase()
    lam = 0.5
    return [
        helper.poisson_probability(lam, 0),
        helper.poisson_probability(lam, 1),
        helper.poisson_probability(lam, 2),
        helper.prob_at_least_one(lam),
    ]


def main() -> None:
    """Simple test"""
    print(f'"{module_name_gl}" demo probabilities: {list(_demo())}')


#%% SELF-RUN                    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
if __name__ == "__main__":
    print(f'"{module_name_gl}" module begins.')
    main()
