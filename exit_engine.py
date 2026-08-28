import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
"""
Exit Clock — Exit Ladder Engine
Generates tranche-based exit plan from buy price, fair value, and quantity.
Core thesis: never sell all at once. Exit systematically into retail FOMO.
"""

import pandas as pd


def generate_exit_ladder(buy_price: float, fair_value: float, quantity: int, current_price: float) -> pd.DataFrame:
    """
    Returns a DataFrame of tranche exit points.
    Each row = one exit action with price trigger, units to sell, proceeds.
    """
    if fair_value <= 0:
        fair_value = buy_price * 2   # fallback

    tranches = [
        {
            "trigger":    buy_price * 1.5,
            "sell_pct":   10,
            "action":     "Trim",
            "rationale":  "First capital recovery — reduce risk on the table",
            "phase":      "Early markup"
        },
        {
            "trigger":    buy_price * 2.0,
            "sell_pct":   15,
            "action":     "Trim",
            "rationale":  "House money point — now playing with pure profit",
            "phase":      "Mid markup"
        },
        {
            "trigger":    fair_value * 0.85,
            "sell_pct":   15,
            "action":     "Trim",
            "rationale":  "Approaching fair value — core reduction begins",
            "phase":      "Late markup"
        },
        {
            "trigger":    fair_value,
            "sell_pct":   25,
            "action":     "Sell",
            "rationale":  "Fair value reached — thesis fully priced in",
            "phase":      "Distribution"
        },
        {
            "trigger":    fair_value * 1.10,
            "sell_pct":   20,
            "action":     "Sell",
            "rationale":  "Greed zone — sell into retail FOMO",
            "phase":      "Distribution"
        },
        {
            "trigger":    fair_value * 1.25,
            "sell_pct":   10,
            "action":     "Sell",
            "rationale":  "Final runner — extreme overvaluation",
            "phase":      "Late distribution"
        },
        {
            "trigger":    buy_price * 1.05,
            "sell_pct":   100,
            "action":     "PANIC EXIT",
            "rationale":  "Growth miss — exit on any bounce. Story is broken.",
            "phase":      "Markdown trigger"
        },
    ]

    rows = []
    remaining = quantity

    for t in tranches:
        is_panic = t["action"] == "PANIC EXIT"
        units = remaining if is_panic else int(quantity * t["sell_pct"] / 100)
        proceeds = t["trigger"] * units
        gain_from_buy = (t["trigger"] - buy_price) / buy_price * 100

        rows.append({
            "Trigger Price (₹)":    round(t["trigger"], 2),
            "Action":               t["action"],
            "Sell %":               t["sell_pct"],
            "Units to Sell":        units,
            "Est. Proceeds (₹)":    round(proceeds, 2),
            "Gain from Buy (%)":    round(gain_from_buy, 1),
            "Phase":                t["phase"],
            "Rationale":            t["rationale"],
        })

        if not is_panic:
            remaining = max(0, remaining - units)

    return pd.DataFrame(rows)


def compute_summary(buy_price: float, fair_value: float, quantity: int, current_price: float) -> dict:
    """Key portfolio summary numbers for the exit plan."""
    total_invested = buy_price * quantity
    current_value = current_price * quantity
    unrealised_pnl = current_value - total_invested
    unrealised_pct = unrealised_pnl / total_invested * 100

    # Value locked in at each milestone
    locked_at_1_5x = int(quantity * 0.10) * buy_price * 1.5
    locked_at_2x   = int(quantity * 0.25) * buy_price * 2.0
    max_upside      = fair_value * quantity
    panic_floor     = buy_price * 1.05 * quantity

    return {
        "total_invested":    round(total_invested, 2),
        "current_value":     round(current_value, 2),
        "unrealised_pnl":    round(unrealised_pnl, 2),
        "unrealised_pct":    round(unrealised_pct, 2),
        "locked_at_1_5x":    round(locked_at_1_5x, 2),
        "locked_at_2x":      round(locked_at_2x, 2),
        "max_upside":        round(max_upside, 2),
        "panic_floor":       round(panic_floor, 2),
        "upside_to_fv_pct":  round((fair_value - current_price) / current_price * 100, 1),
    }
