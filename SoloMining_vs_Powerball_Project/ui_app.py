"""Simple Tkinter UI for exploring solo mining and Powerball scenarios."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from config import (
    BLOCK_REWARD_BTC,
    BTC_PRICE_USD,
    ELECTRICITY_RATE,
    INPUT_DIR,
    POWERBALL,
)
from lottery_models import PowerballModel, PowerballScenario
from main import build_scenarios
from mining_models import SoloMiningModel

JACKPOT_HISTORY_FILE = INPUT_DIR / "powerball_jackpot_history.csv"


class ScenarioApp(tk.Tk):
    """Dashboard for entering parameters and viewing plots."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Solo Mining vs Powerball")
        self.geometry("1200x720")

        self.vars: dict[str, tk.StringVar] = {}
        self.entry_meta: dict[str, dict[str, bool]] = {}
        self.plot_type_var = tk.StringVar(value="Line")
        self.status_var = tk.StringVar(value="Enter values and run the simulation.")
        self.scenario_df = None
        self.solo_odds_var = tk.StringVar(value="Odds of ≥1 block: —")
        self.powerball_odds_var = tk.StringVar(value=self._compute_powerball_odds_text())
        self.jackpot_stats_var = tk.StringVar(value="Stats unavailable (missing file).")
        self.run_count_var = tk.StringVar(value="Runs this session: 0")
        self._next_run_count = self._make_run_counter()
        self.jackpot_history = None

        self._build_layout()
        self._load_jackpot_stats()

    def _build_layout(self) -> None:
        container = ttk.Frame(self, padding=10)
        container.pack(fill=tk.BOTH, expand=True)
        container.columnconfigure(0, weight=0)
        container.columnconfigure(1, weight=1)
        container.rowconfigure(0, weight=1)

        controls = ttk.LabelFrame(container, text="Inputs and Plot Selection", padding=10)
        controls.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        plot_frame = ttk.LabelFrame(container, text="Visualization", padding=10)
        plot_frame.grid(row=0, column=1, sticky="nsew")
        plot_frame.rowconfigure(0, weight=1)
        plot_frame.columnconfigure(0, weight=1)

        bitcoin_fields = [
            ("Hashrate (TH/s)", "hashrate", "100.0", True),
            ("Days to model", "days", "7.0", False),
            ("Block reward (BTC)", "block_reward", str(BLOCK_REWARD_BTC), False),
            ("BTC price (USD)", "btc_price", str(BTC_PRICE_USD), True),
            ("Energy cost ($/kWh)", "energy_cost", str(ELECTRICITY_RATE), False),
        ]
        powerball_fields = [
            ("Powerball ticket cost ($)", "powerball_cost", str(POWERBALL["ticket_cost"]), False),
            ("Powerball jackpot ($)", "powerball_jackpot", "120000000", True),
        ]

        row = 0
        ttk.Label(controls, text="Bitcoin", font=("Segoe UI", 10, "bold")).grid(
            row=row, column=0, columnspan=2, sticky="w", pady=(0, 4)
        )
        row += 1
        row = self._add_field_group(controls, bitcoin_fields, row)

        ttk.Label(controls, text="Powerball", font=("Segoe UI", 10, "bold")).grid(
            row=row, column=0, columnspan=2, sticky="w", pady=(12, 4)
        )
        row += 1
        row = self._add_field_group(controls, powerball_fields, row)

        ttk.Label(controls, text="Plot type").grid(row=row, column=0, sticky="w", pady=(12, 4))
        plot_options = ["Line", "Scatter", "Box", "Violin"]
        plot_combo = ttk.Combobox(
            controls,
            textvariable=self.plot_type_var,
            values=plot_options,
            state="readonly",
            width=16,
        )
        plot_combo.grid(row=row, column=1, sticky="ew", pady=(12, 4))
        plot_combo.bind("<<ComboboxSelected>>", self.update_plot)

        row += 1
        run_button = ttk.Button(controls, text="Run Simulation", command=self.run_simulation)
        run_button.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(12, 4))

        row += 1
        status = ttk.Label(controls, textvariable=self.status_var, wraplength=220, justify="left")
        status.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(8, 0))

        row += 1
        ttk.Label(controls, textvariable=self.run_count_var, foreground="#444").grid(
            row=row, column=0, columnspan=2, sticky="w", pady=(4, 0)
        )
        row += 1
        ttk.Label(controls, text="Stats for last 100 Jackpots", font=("Segoe UI", 10, "bold")).grid(
            row=row, column=0, columnspan=2, sticky="w", pady=(8, 0)
        )
        row += 1
        ttk.Label(controls, textvariable=self.jackpot_stats_var, wraplength=220, foreground="#444").grid(
            row=row, column=0, columnspan=2, sticky="w"
        )

        self.figure = Figure(figsize=(6, 5), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=plot_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=0, column=0, sticky="nsew")
        self._show_placeholder()

    def _show_placeholder(self) -> None:
        self.ax.clear()
        self.ax.text(0.5, 0.5, "Run a simulation to display plots.", ha="center", va="center")
        self.ax.axis("off")
        self.canvas.draw_idle()

    @staticmethod
    def _make_run_counter():
        count = 0

        def increment():
            nonlocal count
            count += 1
            return count

        return increment

    def _load_jackpot_stats(self) -> None:
        path = JACKPOT_HISTORY_FILE
        if not path.exists():
            self.jackpot_stats_var.set(f"Stats unavailable (missing {path.name}).")
            return

        try:
            df = pd.read_csv(path)
        except Exception as exc:  # pragma: no cover - simple UI feedback
            self.jackpot_stats_var.set(f"Stats unavailable ({exc}).")
            self.jackpot_history = None
            return

        jackpot_col = None
        for col in df.columns:
            if col.lower() in {"jackpot", "jackpot_usd", "jackpot_size", "jackpot ($)"}:
                jackpot_col = col
                break

        if not jackpot_col:
            self.jackpot_stats_var.set("Stats unavailable (jackpot column missing).")
            self.jackpot_history = None
            return

        # Keep last 100 jackpots
        stats_df = df.tail(100).copy()
        values = pd.to_numeric(stats_df[jackpot_col], errors="coerce")
        stats_df["jackpot_value"] = values
        stats_df = stats_df.dropna(subset=["jackpot_value"])

        if stats_df.empty:
            self.jackpot_stats_var.set("Stats unavailable (no numeric jackpots).")
            self.jackpot_history = None
            return

        date_col = None
        for col in stats_df.columns:
            if "date" in col.lower():
                date_col = col
                break

        if date_col:
            stats_df["date_label"] = stats_df[date_col].astype(str)
        else:
            stats_df["date_label"] = stats_df.index.to_series().astype(str)

        stats_df.reset_index(drop=True, inplace=True)
        self.jackpot_history = stats_df

        values_series = stats_df["jackpot_value"]
        mean = values_series.mean()
        median = values_series.median()
        std = values_series.std()
        self.jackpot_stats_var.set(
            f"mean ${mean:,.0f} | median ${median:,.0f} | std ${std:,.0f}"
        )
        self.update_plot()

    def _add_field_group(
        self,
        frame: ttk.Frame,
        fields: list[tuple[str, str, str, bool]],
        start_row: int,
    ) -> int:
        row = start_row
        for label_text, key, default, use_commas in fields:
            ttk.Label(frame, text=label_text).grid(row=row, column=0, sticky="w", pady=4)
            var = tk.StringVar(value=self._initial_value(default, use_commas))
            entry = ttk.Entry(frame, textvariable=var, width=18)
            entry.grid(row=row, column=1, sticky="ew", pady=4)
            self.vars[key] = var
            self.entry_meta[key] = {"format_commas": use_commas}
            entry.bind("<FocusOut>", lambda _event, k=key: self._format_entry(k))
            row += 1
            if key == "energy_cost":
                ttk.Label(frame, textvariable=self.solo_odds_var, foreground="#444").grid(
                    row=row, column=0, columnspan=2, sticky="w", pady=(0, 6)
                )
                row += 1
            if key == "powerball_jackpot":
                ttk.Label(frame, textvariable=self.powerball_odds_var, foreground="#444").grid(
                    row=row, column=0, columnspan=2, sticky="w", pady=(0, 6)
                )
                row += 1
        return row

    def _initial_value(self, default: str, use_commas: bool) -> str:
        if not use_commas:
            return default
        try:
            value = float(str(default).replace(",", ""))
        except ValueError:
            return default
        return self._format_number_for_display(value)

    def _format_entry(self, key: str) -> None:
        meta = self.entry_meta.get(key, {})
        if not meta.get("format_commas"):
            return
        raw = self.vars[key].get().replace(",", "")
        try:
            value = float(raw)
        except ValueError:
            return
        self.vars[key].set(self._format_number_for_display(value))

    @staticmethod
    def _format_number_for_display(value: float) -> str:
        if float(value).is_integer():
            return f"{int(value):,}"
        text = f"{value:,.4f}".rstrip("0").rstrip(".")
        return text or "0"

    def _format_odds(self, probability: float) -> str:
        if probability <= 0:
            return "N/A"
        inverse = 1.0 / probability
        if inverse >= 1_000:
            formatted = f"{inverse:,.0f}"
        else:
            formatted = f"{inverse:,.2f}".rstrip("0").rstrip(".")
        return f"1 in {formatted}"

    def _compute_powerball_odds_text(self) -> str:
        default_jackpot = POWERBALL.get("default_payouts", {}).get((5, True), 0.0)
        sc = PowerballScenario(
            num_tickets=1,
            drawings_per_week=1,
            weeks=1,
            jackpot=default_jackpot,
            ticket_cost=POWERBALL["ticket_cost"],
        )
        model = PowerballModel(sc)
        prob = model.per_ticket_jackpot()
        return f"Odds of jackpot: {self._format_odds(prob)}"

    def _get_float(self, key: str, label: str) -> float:
        try:
            return float(self.vars[key].get().replace(",", ""))
        except ValueError as exc:  # pragma: no cover - UI helper
            raise ValueError(f"{label} must be a numeric value.") from exc

    def run_simulation(self) -> None:
        try:
            hashrate = self._get_float("hashrate", "Hashrate")
            days = self._get_float("days", "Days to model")
            block_reward = self._get_float("block_reward", "Block reward")
            btc_price = self._get_float("btc_price", "BTC price")
            energy_cost = self._get_float("energy_cost", "Energy cost")
            powerball_cost = self._get_float("powerball_cost", "Powerball ticket cost")
            powerball_jackpot = self._get_float("powerball_jackpot", "Powerball jackpot")
        except ValueError as exc:
            messagebox.showerror("Invalid input", str(exc))
            return

        self.scenario_df = build_scenarios(
            hashrate,
            days,
            btc_price=btc_price,
            block_reward_btc=block_reward,
            electricity_rate=energy_cost,
        )

        miner_model = SoloMiningModel(
            hashrate,
            days,
            price=btc_price,
            rate=energy_cost,
            block_reward_btc=block_reward,
        )
        solo_probability = miner_model.mining_probability()
        solo_expected = miner_model.expected_value()

        pb_scenario = PowerballScenario(
            num_tickets=10,
            drawings_per_week=3,
            weeks=2,
            jackpot=powerball_jackpot,
            ticket_cost=powerball_cost,
        )
        pb_model = PowerballModel(pb_scenario)
        pb_ev = pb_model.expected_value_per_ticket()

        self.status_var.set(
            (
                f"Solo mining: P(>=1 block) = {solo_probability:.6%}, "
                f"EV = ${solo_expected:,.2f}\n"
                f"Powerball EV per ticket: ${pb_ev:,.2f}"
            )
        )
        self.solo_odds_var.set(f"Odds of ≥1 block: {self._format_odds(solo_probability)}")
        run_number = self._next_run_count()
        self.run_count_var.set(f"Runs this session: {run_number}")

        self.update_plot()

    def update_plot(self, *_args) -> None:
        if self.jackpot_history is None or self.jackpot_history.empty:
            self._show_placeholder()
            return

        data = self.jackpot_history
        values = data["jackpot_value"].tolist()
        labels = data["date_label"].tolist()
        x = list(range(len(values)))

        self.ax.clear()
        plot_type = self.plot_type_var.get()

        if plot_type == "Line":
            self.ax.plot(x, values, marker="o", color="#0072b2")
            self.ax.set_xlabel("Draw")
            self.ax.set_ylabel("Jackpot ($)")
        elif plot_type == "Scatter":
            self.ax.scatter(x, values, c="#d55e00", edgecolor="black")
            self.ax.set_xlabel("Draw")
            self.ax.set_ylabel("Jackpot ($)")
        elif plot_type == "Box":
            self.ax.boxplot([values], labels=["Jackpot ($)"], patch_artist=True)
            self.ax.set_ylabel("Jackpot ($)")
        elif plot_type == "Violin":
            parts = self.ax.violinplot(values, showmeans=True, showmedians=True)
            for body in parts["bodies"]:
                body.set_alpha(0.7)
            self.ax.set_ylabel("Jackpot ($)")
            self.ax.set_xticks([1])
            self.ax.set_xticklabels(["Jackpot ($)"])
        else:
            self.ax.text(0.5, 0.5, "Unknown plot selection.", ha="center", va="center")
            self.canvas.draw_idle()
            return

        if plot_type in {"Line", "Scatter"}:
            self._format_axes_for_dates(x, labels)

        self.ax.set_title(f"{plot_type} of last {len(values)} jackpots")
        self.ax.grid(True, linestyle="--", alpha=0.4)
        self.canvas.draw_idle()

    def _format_axes_for_dates(self, x: list[int], labels: list[str]) -> None:
        if not labels:
            return
        step = max(1, len(labels) // 10)
        tick_positions = x[::step]
        tick_labels = labels[::step]
        self.ax.set_xticks(tick_positions)
        self.ax.set_xticklabels(tick_labels, rotation=45, ha="right")


def launch_dashboard() -> None:
    app = ScenarioApp()
    app.mainloop()


if __name__ == "__main__":
    launch_dashboard()
