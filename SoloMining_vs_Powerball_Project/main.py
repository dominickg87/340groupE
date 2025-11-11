from lottery_models import PowerballScenario, PowerballModel

def run_powerball():
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
    print(f"EV per ticket: {round(model.expected_value_per_ticket(),2)}$")
    print(f"Total EV for scenario: {round(model.expected_value_total(),2)}$")
    print("P(≥1 jackpot):", model.prob_at_least_one_jackpot())
    print("P(≥1 any):", model.prob_at_least_one_any_prize())
    model.export_csv("powerball_example.csv")
    model.export_pickle("powerball_example.pkl")

if __name__ == "__main__":
    run_powerball()