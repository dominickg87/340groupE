
"""Project-wide configuration values for the solo mining calculator."""

# Bitcoin mining defaults (all values can be customized later).
BLOCK_REWARD_BTC = 3.125
POOL_FEE = 0.0
BTC_PRICE_USD = 65000
ELECTRICITY_RATE = 0.12  # Electricity cost per kWh in USD.
NETWORK_HASHRATE_EHs = 600  # Total network hashrate in exa-hash per second.

# Application metadata.
APP_VERSION = "1.0"

# Shared configuration dictionary for quick imports.
CONFIG = {
    "block_reward_btc": BLOCK_REWARD_BTC,
    "pool_fee": POOL_FEE,
    "btc_price_usd": BTC_PRICE_USD,
    "electricity_rate": ELECTRICITY_RATE,
    "network_hashrate_ehs": NETWORK_HASHRATE_EHs,
    "app_version": APP_VERSION,
}
