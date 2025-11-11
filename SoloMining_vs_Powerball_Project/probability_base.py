"""Simple probability utilities shared by mining models."""

import math
from typing import Any

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
