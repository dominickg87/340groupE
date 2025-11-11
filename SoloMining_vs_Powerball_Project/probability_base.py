from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Dict, Iterable, Tuple, List

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