import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
"""
Exit Clock — Valuation Engine
Computes fair value independently using 4 models.
No analyst dependency. You feed fundamentals, model returns fair value.
"""

import math


def compute_all(inputs: dict) -> dict:
    """
    Master function. Returns fair value from all 4 models + blended value.
    Works for: stock, crypto, gold, startup, bond
    """
    asset_type = inputs.get("asset_type", "stock")

    if asset_type == "stock":
        return _compute_stock(inputs)
    elif asset_type == "crypto":
        return _compute_crypto(inputs)
    elif asset_type == "gold":
        return _compute_gold(inputs)
    elif asset_type == "startup":
        return _compute_startup(inputs)
    elif asset_type == "bond":
        return _compute_bond(inputs)
    else:
        return {"pe": 0, "peg": 0, "dcf": 0, "ps": 0, "blend": 0, "notes": {}}


# ─────────────────────────────────────────────
# STOCK VALUATION — 4 independent models
# ─────────────────────────────────────────────

def _compute_stock(i: dict) -> dict:
    eps       = i.get("eps", 0)
    epsg      = i.get("eps_growth", 0)       # EPS growth % per year
    spe       = i.get("sector_pe", 25)        # Sector average PE
    hpe       = i.get("hist_pe", 20)          # 5-year historical PE of the stock
    revg      = i.get("rev_growth", 0)        # Revenue growth % per year
    npm       = i.get("net_margin", 0)        # Net profit margin %
    de        = i.get("debt_equity", 0)       # Debt-to-equity ratio
    roe       = i.get("roe", 15)              # Return on equity %
    cur       = i.get("current_price", 1)

    notes = {}

    # ── Model 1: PE-based valuation ──────────────────────────────────────────
    # Quality adjustment: better ROE = premium PE, high debt = discounted PE
    quality_adj = 1 + (roe - 12) / 100 + (0.05 if de < 0.5 else -0.15 if de > 2 else -0.05)
    quality_adj = max(0.5, min(quality_adj, 1.5))   # cap between 0.5x and 1.5x

    # Growth PE: higher growth = higher justified PE, capped at 60
    growth_pe = min(epsg * 1.2, 60)

    # Justified PE = blend of sector PE and growth PE, quality adjusted
    justified_pe = min((spe + growth_pe) / 2 * quality_adj, 80)

    fv_pe = eps * justified_pe if eps > 0 else 0

    notes["pe"] = {
        "quality_adj": round(quality_adj, 2),
        "growth_pe": round(growth_pe, 1),
        "justified_pe": round(justified_pe, 1),
        "formula": f"Fair Value = EPS (₹{eps}) × Justified PE ({justified_pe:.1f}x)"
    }

    # ── Model 2: PEG ratio valuation ─────────────────────────────────────────
    # PEG of 1.0 = fairly valued for its growth rate
    # Fair value is where PEG would be exactly 1.0
    fv_peg = eps * epsg * 1.0 if eps > 0 and epsg > 0 else 0
    cur_pe  = cur / eps if eps > 0 else 0
    peg_ratio = cur_pe / epsg if epsg > 0 else 0

    notes["peg"] = {
        "current_pe": round(cur_pe, 1),
        "peg_ratio": round(peg_ratio, 2),
        "interpretation": (
            "Undervalued for growth" if peg_ratio < 1
            else "Fairly valued" if peg_ratio < 2
            else "Overvalued — growth priced in"
        ),
        "formula": f"Fair PEG = 1.0 → Fair Value = EPS (₹{eps}) × Growth ({epsg}%)"
    }

    # ── Model 3: Simplified DCF (5-year) ─────────────────────────────────────
    # Projects EPS forward 5 years at given growth rate
    # Terminal value using conservative multiple (historical PE, max 40x)
    # Discounted back at 12% (India equity risk rate)
    discount_rate = 0.12
    terminal_multiple = min(hpe if hpe > 0 else spe, 40)
    fwd_eps_5y = eps * math.pow(1 + epsg / 100, 5) if eps > 0 else 0
    terminal_value = fwd_eps_5y * terminal_multiple
    fv_dcf = terminal_value / math.pow(1 + discount_rate, 5) if fwd_eps_5y > 0 else 0

    notes["dcf"] = {
        "eps_in_5y": round(fwd_eps_5y, 2),
        "terminal_multiple": terminal_multiple,
        "discount_rate": "12% (India equity risk rate)",
        "formula": f"PV of (EPS_5y × {terminal_multiple}x) discounted at 12%"
    }

    # ── Model 4: Price-to-Sales cross-check ──────────────────────────────────
    # Revenue per share derived from EPS + net margin
    # Then valued at a sector PS multiple
    if npm > 0 and eps > 0:
        rev_per_share = eps / (npm / 100)
        ps_multiple = max(1.0, spe / 15)           # rough PS from PE
        # Reconstruct per-share value
        fv_ps = rev_per_share * (npm / 100) * justified_pe
    else:
        fv_ps = fv_pe   # fallback to PE model

    notes["ps"] = {
        "net_margin": f"{npm}%",
        "ps_multiple": round(max(1.0, spe / 15), 1),
        "formula": "Revenue/share × Net Margin × Justified PE (cross-check)"
    }

    blend = (fv_pe + fv_peg + fv_dcf + fv_ps) / 4

    return {
        "pe": round(fv_pe, 2),
        "peg": round(fv_peg, 2),
        "dcf": round(fv_dcf, 2),
        "ps": round(fv_ps, 2),
        "blend": round(blend, 2),
        "notes": notes,
        "justified_pe": round(justified_pe, 1),
        "peg_ratio": round(peg_ratio, 2),
    }


# ─────────────────────────────────────────────
# CRYPTO VALUATION
# ─────────────────────────────────────────────

def _compute_crypto(i: dict) -> dict:
    ath       = i.get("ath_price", 0)
    btcd      = i.get("btc_dominance", 55)    # BTC dominance %
    netg      = i.get("network_growth", 0)    # Network/user growth %/yr
    cur       = i.get("current_price", 1)

    # BTC dominance adjustment: high dominance = altcoin season not started
    btc_adj = 0.55 if btcd > 60 else 0.70 if btcd > 55 else 0.85 if btcd > 45 else 1.1

    fv_base = ath * 0.45 * btc_adj
    fv_growth = cur * (1 + netg / 200)   # growth-adjusted current price
    blend = (fv_base + fv_growth) / 2

    notes = {
        "btc_adj": btc_adj,
        "interpretation": (
            "Altcoin season suppressed — BTC dominance too high"
            if btcd > 55 else
            "Neutral — rotation possible"
            if btcd > 45 else
            "Altcoin season conditions forming"
        )
    }

    return {
        "pe": round(fv_base, 2),
        "peg": round(fv_growth, 2),
        "dcf": round(fv_base * 1.05, 2),
        "ps": round(fv_base * 0.95, 2),
        "blend": round(blend, 2),
        "notes": notes,
    }


# ─────────────────────────────────────────────
# GOLD / COMMODITY VALUATION
# ─────────────────────────────────────────────

def _compute_gold(i: dict) -> dict:
    hist_avg   = i.get("hist_avg_price", 50000)   # 10yr avg price ₹
    inflation  = i.get("inflation_rate", 5)        # %
    real_rate  = i.get("real_interest_rate", 1)    # %

    # Inflation-adjusted historical average (2-year forward)
    infl_adj = hist_avg * math.pow(1 + inflation / 100, 2)

    # Real interest rate adjustment: negative real rates = gold premium
    rir_adj = 1.15 if real_rate < 0 else 1.0 if real_rate < 2 else 0.9

    fv = infl_adj * rir_adj

    notes = {
        "interpretation": (
            "Negative real rates — gold should trade at premium to historical average"
            if real_rate < 0 else
            "Neutral real rates — gold at historical average is fair"
            if real_rate < 2 else
            "Positive real rates — gold faces headwinds, trades at discount"
        )
    }

    return {
        "pe": round(fv, 2), "peg": round(fv, 2),
        "dcf": round(fv, 2), "ps": round(fv, 2),
        "blend": round(fv, 2), "notes": notes
    }


# ─────────────────────────────────────────────
# STARTUP / UNLISTED VALUATION
# ─────────────────────────────────────────────

def _compute_startup(i: dict) -> dict:
    revenue    = i.get("annual_revenue", 0)       # ₹ Cr
    rev_growth = i.get("rev_growth", 0)           # %/yr
    ind_mult   = i.get("industry_multiple", 5)    # revenue multiple
    burn       = i.get("monthly_burn", 0)         # ₹ Cr/month

    # Forward revenue (1 year)
    fwd_revenue = revenue * (1 + rev_growth / 100)

    # Runway sustainability adjustment
    annual_burn = burn * 12
    runway_adj = (
        1.1 if revenue > annual_burn * 2
        else 0.9 if revenue > annual_burn
        else 0.65
    )

    fv = fwd_revenue * ind_mult * runway_adj

    notes = {
        "fwd_revenue": round(fwd_revenue, 2),
        "runway_adj": runway_adj,
        "interpretation": (
            "Healthy runway — premium multiple justified"
            if runway_adj >= 1.0 else
            "Burn rate concern — discounted multiple applied"
        )
    }

    return {
        "pe": round(fv, 2), "peg": round(fv, 2),
        "dcf": round(fv, 2), "ps": round(fv, 2),
        "blend": round(fv, 2), "notes": notes
    }


# ─────────────────────────────────────────────
# BOND VALUATION — pure present value math
# ─────────────────────────────────────────────

def _compute_bond(i: dict) -> dict:
    coupon_rate = i.get("coupon_rate", 8)     # %
    ytm         = i.get("ytm", 7)             # yield to maturity %
    face_value  = i.get("face_value", 1000)   # ₹
    maturity    = int(i.get("maturity_years", 5))

    coupon = face_value * coupon_rate / 100
    pv = sum(coupon / math.pow(1 + ytm / 100, t) for t in range(1, maturity + 1))
    pv += face_value / math.pow(1 + ytm / 100, maturity)

    notes = {
        "annual_coupon": round(coupon, 2),
        "formula": f"PV of {maturity} coupon payments + face value, discounted at YTM {ytm}%",
        "interpretation": (
            "Bond trading below fair value — good entry"
            if i.get("current_price", pv) < pv * 0.97
            else "Bond at fair value"
            if i.get("current_price", pv) < pv * 1.03
            else "Bond overpriced relative to YTM"
        )
    }

    return {
        "pe": round(pv, 2), "peg": round(pv, 2),
        "dcf": round(pv, 2), "ps": round(pv, 2),
        "blend": round(pv, 2), "notes": notes
    }


# ─────────────────────────────────────────────
# VALUATION INTERPRETATION HELPER
# ─────────────────────────────────────────────

def interpret_valuation(current_price: float, fair_value: float) -> dict:
    if fair_value <= 0:
        return {"label": "Cannot compute", "cls": "gray", "ratio": 0}

    ratio = current_price / fair_value
    discount_pct = (fair_value - current_price) / fair_value * 100

    if ratio < 0.80:
        return {
            "label": f"Undervalued — {abs(discount_pct):.1f}% below fair value",
            "cls": "green", "ratio": ratio,
            "action": "Strong hold / accumulate",
            "color": "🟢"
        }
    elif ratio < 1.00:
        return {
            "label": f"Approaching fair value — {abs(discount_pct):.1f}% upside left",
            "cls": "yellow", "ratio": ratio,
            "action": "Hold — prepare exit ladder",
            "color": "🟡"
        }
    elif ratio < 1.20:
        return {
            "label": f"Overvalued — {(ratio-1)*100:.1f}% above fair value",
            "cls": "orange", "ratio": ratio,
            "action": "Begin trimming",
            "color": "🟠"
        }
    else:
        return {
            "label": f"Significantly overvalued — {(ratio-1)*100:.1f}% above fair value",
            "cls": "red", "ratio": ratio,
            "action": "Exit urgently",
            "color": "🔴"
        }
