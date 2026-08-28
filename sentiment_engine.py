import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
"""
Exit Clock — Sentiment Engine
Scores retail FOMO signals. High score = institutional distribution underway.
This is the behavioral finance core of the model.
"""

SIGNALS = [
    {
        "id": "zerodha_list",
        "label": "Asset appears on Zerodha / Groww top-bought lists consistently",
        "weight": 1,
        "explanation": "When a stock dominates retail broker top-buy lists, it means late-stage retail entry. Institutions use this liquidity to exit."
    },
    {
        "id": "delivery_drop",
        "label": "Delivery % dropped sharply — intraday / momentum buyers dominating",
        "weight": 1,
        "explanation": "Low delivery = speculative buying, not conviction. Institutions typically have high delivery %. When delivery falls, smart money is stepping back."
    },
    {
        "id": "options_spike",
        "label": "Call OI spiking at round numbers above current price",
        "weight": 1,
        "explanation": "Retail traders buy OTM calls dreaming of big moves. Concentrated OI at round numbers = retail gambling, not hedging. Classic euphoria signal."
    },
    {
        "id": "social_trend",
        "label": "Trending on Twitter/X finance community or YouTube thumbnails",
        "weight": 1,
        "explanation": "Financial YouTube thumbnails with big ₹ numbers = the story has reached the last layer of retail. By the time it's viral, distribution is nearly complete."
    },
    {
        "id": "shareholding_jump",
        "label": "Retail shareholding % jumped 2%+ in latest quarterly BSE data",
        "weight": 1,
        "explanation": "The BSE shareholding pattern is gold. If retail % is rising while price is near highs, institutions are handing their shares to retailers. Check this every quarter."
    },
    {
        "id": "news_channels",
        "label": "Business news channels running daily segments on this asset",
        "weight": 1,
        "explanation": "CNBC, ET Now daily coverage = the story is fully in the public domain. No information edge remains. Institutions front-ran this months ago."
    },
    {
        "id": "friends_family",
        "label": "Non-finance friends / family asking about this stock or coin",
        "weight": 1,
        "explanation": "The classic Buffett barber indicator. When your relatives start asking about a stock, the distribution phase is in its final stages."
    },
    {
        "id": "whatsapp_buzz",
        "label": "WhatsApp group tips / grey market premium buzz at peak levels",
        "weight": 1,
        "explanation": "GMP data is often manipulated to create urgency. Widespread WhatsApp forwarding = the narrative has saturated. Exit liquidity is maximum right now."
    },
]


def score_sentiment(active_signals: list) -> dict:
    """
    active_signals: list of signal IDs that are currently true
    Returns score, interpretation, and recommended action
    """
    total_weight = sum(s["weight"] for s in SIGNALS)
    active_weight = sum(
        s["weight"] for s in SIGNALS if s["id"] in active_signals
    )
    score = active_weight
    score_pct = active_weight / total_weight * 100

    if score <= 2:
        interpretation = "Low retail FOMO"
        detail = "Accumulation or early markup phase likely. Big money is still building. You are not in the exit window yet."
        action = "Hold comfortably"
        color = "green"
        phase = "Accumulation / Early markup"
    elif score <= 4:
        interpretation = "Moderate retail interest"
        detail = "Retail is entering but not at peak FOMO. Institutions may be trimming but not fully exiting. Monitor closely."
        action = "Prepare exit ladder — no urgency yet"
        color = "yellow"
        phase = "Mid markup / Early distribution"
    elif score <= 6:
        interpretation = "High retail FOMO detected"
        detail = "Smart money is almost certainly distributing. You are providing exit liquidity if you buy here. If holding, begin trimming NOW."
        action = "Begin trimming per the exit ladder"
        color = "orange"
        phase = "Distribution"
    else:
        interpretation = "Peak euphoria — maximum exit signal"
        detail = "This is a textbook distribution top. Every signal is firing. The story is fully priced in and then some. This is your exit window. Use it."
        action = "Sell aggressively into this strength"
        color = "red"
        phase = "Late distribution / Top"

    return {
        "score": score,
        "score_pct": round(score_pct, 1),
        "interpretation": interpretation,
        "detail": detail,
        "action": action,
        "color": color,
        "phase": phase,
        "active_count": len(active_signals),
        "total_signals": len(SIGNALS),
    }


def get_all_signals():
    return SIGNALS
