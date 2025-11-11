"""Simple probability utilities shared by mining models."""
from __future__ import annotations
import math
from typing import Any
from dataclasses import dataclass
from typing import Dict, Iterable, Tuple, List
import numpy as np
import pandas as pd


class ProbabilityBase:
    """Collection of probability helpers geared towards Poisson processes."""

    def poisson_probability(self, lam: float, k: int) -> float:
        """Return P(k; λ) = e^(−λ) * λ^k / k! for integer k."""
        lam = float(lam)
        k = int(k)
        return math.exp(-lam) * (lam**k) / math.factorial(k)

    def prob_at_least_one(self, lam: float) -> float:
        """Return the chance of at least one success in a Poisson process."""
        lam = float(lam)
        return 1.0 - math.exp(-lam)

    def query_column(self, df: pd.DataFrame, column: str, value: Any) -> pd.DataFrame:
        """Filter a DataFrame by a column value and return the matching rows."""
        if column not in df.columns:
            raise KeyError(f"Column '{column}' not found in DataFrame.")

        data = df[column].to_numpy()
        mask = np.asarray(data == value)
        return df.loc[mask].copy()

@dataclass
class ProbabilityBase:

    @staticmethod
    def nCk(n: int, k: int) -> int:
        return math.comb(n, k)

    @staticmethod
    #Binomial Probability Mass Function
    def binom_pmf(n: int, p: float, k: int) -> float:
        return math.comb(n, k) * (p**k) * ((1 - p)**(n - k))

    @staticmethod
    def at_least_one(trials: int, p_single: float) -> float:
        # P(≥1) = 1 - (1-p)^trials
        return 1.0 - (1.0 - p_single) ** trials

    @staticmethod
    def expected_value(payouts: Iterable[float], probs: Iterable[float]) -> float:
        return sum(x * p for x, p in zip(payouts, probs))