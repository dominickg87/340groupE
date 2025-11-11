
POWERBALL = {
    "white_ball_count": 69,     # current rules
    "draw_white": 5,
    "power_ball_count": 26,
    "ticket_cost": 2.0,
    # Payouts can be overridden per run; these are defaults
    # Keys are (k_white_matches, powerball_match_bool)
    "default_payouts": {
        (5, True): 10_000_000.0,   # Jackpot placeholder; set at runtime via kwargs if so deseried
        (5, False): 1_000_000.0,
        (4, True): 50_000.0,
        (4, False): 100.0,
        (3, True): 100.0,
        (3, False): 7.0,
        (2, True): 7.0,
        (1, True): 4.0,
        (0, True): 4.0,
    }
}

OUTPUT_DIR = "SoloMining_vs_Powerball_Project\Output"
OUTPUT_DIR_LOG = "SoloMining_vs_Powerball_Project\Output\logs"
INPUT_DIR = "SoloMining_vs_Powerball_Project\Input"