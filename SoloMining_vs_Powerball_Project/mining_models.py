#Version: v1.0
#Date Last Updated: 1-12-2025

#%% MODULE BEGINS
module_name_gl = "mining_models"

"""
Version: v1.0

Description:
    Solo mining probability and expected value models that inherit from
    ProbabilityBase for Poisson calculations.

Authors:
    Group E

Date Created     :  2025-11-10
Date Last Updated:  2025-01-12

Doc:
    See DomNotes.md for overview and usage instructions.
"""

#%% IMPORTS                    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
from __future__ import annotations

from config import (
    BLOCK_REWARD_BTC,
    BTC_PRICE_USD,
    ELECTRICITY_RATE,
    NETWORK_HASHRATE_EHs,
)
from probability_base import ProbabilityBase


#%% CLASS DEFINITIONS          ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class SoloMiningModel(ProbabilityBase):
    """Estimate solo mining outcomes using a simple Poisson approach."""

    def __init__(
        self,
        miner_hashrate_ths: float,
        days: float,
        price: float = BTC_PRICE_USD,
        rate: float = ELECTRICITY_RATE,
    ) -> None:
        # Store the miner's hashrate and other settings for later calculations.
        self.miner_hashrate_ths = float(miner_hashrate_ths)
        self.days = float(days)
        self.price = float(price)
        self.rate = float(rate)  # Placeholder for future electricity cost modeling.

    def compute_lambda(self) -> float:
        """Return the expected number of blocks the miner might find."""
        network_ths = NETWORK_HASHRATE_EHs * 1_000_000  # Convert EH/s to TH/s.
        return 144.0 * (self.miner_hashrate_ths / network_ths) * self.days

    def mining_probability(self) -> float:
        """Return the probability of finding at least one block."""
        lam = self.compute_lambda()
        return self.prob_at_least_one(lam)

    def expected_value(self) -> float:
        """Return the expected mining payout in USD."""
        probability = self.mining_probability()
        reward_value = BLOCK_REWARD_BTC * self.price
        return probability * reward_value

    def print_summary(self) -> None:
        """Display a simple summary for the console."""
        lam = self.compute_lambda()
        probability = self.prob_at_least_one(lam)
        reward_value = BLOCK_REWARD_BTC * self.price
        expected_usd = probability * reward_value

        print("\n--- Solo Mining Summary ---")
        print(f"Hashrate (TH/s): {self.miner_hashrate_ths:.2f}")
        print(f"Days modeled   : {self.days:.2f}")
        print(f"Lambda (lambda): {lam:.6f}")
        print(f"Prob >=1 block : {probability:.6%}")
        print(f"Expected Value : ${expected_usd:,.2f}\n")


#%% FUNCTION DEFINITIONS        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def main() -> None:
    """Ad-hoc smoke test when the module is run directly."""
    model = SoloMiningModel(miner_hashrate_ths=100.0, days=7.0)
    model.print_summary()


#%% SELF-RUN                    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
if __name__ == "__main__":
    print(f'"{module_name_gl}" module begins.')
    main()
