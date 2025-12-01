from __future__ import annotations

#Version: v1.0
#Date Last Updated: 1-12-2025

#%% MODULE BEGINS
module_name_gl = "config"

"""
Version: v1.0

Description:
    Centralized configuration values and directory helpers for the Solo
    Mining vs Powerball project.

Authors:
    Group E

Date Created     :  2025-11-10
Date Last Updated:  2025-01-12

Doc:
    See DomNotes.md for module relationships.

Notes:
    Values here act as defaults; individual modules can override when needed.
"""

#%% IMPORTS                    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from pathlib import Path


#%% CONSTANTS                   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
PROJECT_ROOT = Path(__file__).resolve().parent
INPUT_DIR = PROJECT_ROOT / "Input"
OUTPUT_DIR = PROJECT_ROOT / "Output"
OUTPUT_DIR_LOG = OUTPUT_DIR / "logs"

# Bitcoin mining defaults (all values can be customized later).
BLOCK_REWARD_BTC = 3.125
POOL_FEE = 0.0
BTC_PRICE_USD = 65_000
ELECTRICITY_RATE = 0.12  # Electricity cost per kWh in USD.
NETWORK_HASHRATE_EHs = 600  # Total network hashrate in exa-hash per second.

# Application metadata.
APP_VERSION = "1.0"

# Powerball defaults.
POWERBALL = {
    "white_ball_count": 69,
    "draw_white": 5,
    "power_ball_count": 26,
    "ticket_cost": 2.0,
    "default_payouts": {
        (5, True): 10_000_000.0,  # Override with the live jackpot at runtime.
        (5, False): 1_000_000.0,
        (4, True): 50_000.0,
        (4, False): 100.0,
        (3, True): 100.0,
        (3, False): 7.0,
        (2, True): 7.0,
        (1, True): 4.0,
        (0, True): 4.0,
    },
}


#%% DECLARATIONS                ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
CONFIG = {
    "block_reward_btc": BLOCK_REWARD_BTC,
    "pool_fee": POOL_FEE,
    "btc_price_usd": BTC_PRICE_USD,
    "electricity_rate": ELECTRICITY_RATE,
    "network_hashrate_ehs": NETWORK_HASHRATE_EHs,
    "app_version": APP_VERSION,
}


#%% FUNCTION DEFINITIONS        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def main() -> None:
    """Simple self-test to print the current configuration."""
    print(f'"{module_name_gl}" configuration summary')
    print(f"Project root        : {PROJECT_ROOT}")
    print(f"Input directory     : {INPUT_DIR}")
    print(f"Output directory    : {OUTPUT_DIR}")
    print(f"Log directory       : {OUTPUT_DIR_LOG}")
    print(f"Bitcoin block reward: {BLOCK_REWARD_BTC} BTC")
    print(f"BTC price (USD)     : {BTC_PRICE_USD}")
    print(f"Electricity rate    : {ELECTRICITY_RATE} $/kWh")
    print(f"Network hashrate    : {NETWORK_HASHRATE_EHs} EH/s")


#%% SELF-RUN                    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
if __name__ == "__main__":
    print(f'"{module_name_gl}" module begins.')
    main()
