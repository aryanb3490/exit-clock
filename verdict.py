import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
import plotly.graph_objects as go
from utils.valuation_engine import compute_all, interpret_valuation
from utils.sentiment_engine import score_sentiment, get_all_signals
from utils.exit_engine import generate_exit_ladder


def render():
    st.title("⚖️ Final Verdict")
    st.caption("Valuation + Sentiment + Position — combined into one clear signal.")

    if "inputs" not in st.session_state:
        st.warning("⬅ Please complete Asset Inputs first.")
        return

    inputs   = st.session_state["inputs"]
    buy      = inputs.get("buy_price", 1)
    cur      = inputs.get("current_price", buy)
    qty      = int(st.session_state.get("quantity", 100))
    fv_res   = st.session_state.get("fv_results") or compute_all(inputs)
    fv       = fv_res["blend"]
    interp   = interpret_valuation(cur, fv)
    name     = st.session_state.get("asset_name", "Asset")

    # Collect active sentiment signals
    signals = get_all_signals()
    active  = [s["id"] for s in signals if st.session_state.get(f"sent_{s['id']}", False)]
    sent    = score_sentiment(active)

    st.markdown("---")

    # ── Scoring model ────────────────────────────────────────────────────────
    ratio = cur / fv if fv > 0 else 1.0
    pts   = 0

    # Valuation points
    if ratio > 1.25:   pts += 4
    elif ratio > 1.10: pts += 3
    elif ratio > 1.00: pts += 2
    elif ratio > 0.85: pts += 1

    # Sentiment points
    ss = sent["score"]
    if ss >= 6:   pts += 3
    elif ss >= 4: pts += 2
    elif ss >= 2: pts += 1

    # Gain points — if already 2x+, distribution risk increases
    gain = (cur - buy) / buy * 100
    if gain > 150: pts += 2
    elif gain > 75: pts += 1

    # Verdict
    if ratio < 0.80 and ss < 3:
        label   = "💎 Strong hold — deep value"
        detail  = (f"{name} is significantly below computed fair value (₹{fv:,.0f}) "
                   f"and retail FOMO is low. You are likely in accumulation or early markup. "
                   f"This is the right time to hold — or even add if conviction is high.")
        color   = "success"
        actions = ["Hold full position", "Consider adding on dips", "Review again after next results"]
    elif pts <= 2:
        label   = "✅ Hold — thesis intact"
        detail  = (f"No strong exit signals. Price (₹{cur:,.0f}) is at {ratio*100:.0f}% of fair value "
                   f"and sentiment is moderate. Maintain position and review after quarterly results.")
        color   = "success"
        actions = ["Hold current position", "Set a price alert at ₹" + str(round(fv * 0.95)), "Monitor quarterly growth delivery"]
    elif pts <= 4:
        label   = "🟡 Start trimming"
        detail  = (f"You are entering the exit zone. Price is at {ratio*100:.0f}% of computed fair value "
                   f"and {ss}/8 retail signals are active. Begin the exit ladder — "
                   f"sell 10–15% at current levels and follow the tranche plan.")
        color   = "warning"
        actions = ["Sell 10% now at market", "Set limit orders at each tranche level", "Do NOT add more — exit mode only"]
    elif pts <= 6:
        label   = "🟠 Strong exit signal"
        detail  = (f"Price is {(ratio-1)*100:.0f}% above fair value. {ss}/8 retail FOMO signals are active. "
                   f"Institutions are likely distributing into your buying. "
                   f"Sell 40–50% immediately. Keep a small runner only if you have a specific catalyst.")
        color   = "warning"
        actions = ["Sell 40–50% at market immediately", "Set stop-loss on remainder at ₹" + str(round(buy * 1.1)), "Do not add under any circumstances"]
    else:
        label   = "🔴 Exit urgently"
        detail  = (f"Maximum warning. Price is {(ratio-1)*100:.0f}% above fair value with {ss}/8 retail signals "
                   f"firing simultaneously. This is a textbook distribution top. "
                   f"The market is giving you an exit at peak optimism. Use it now.")
        color   = "error"
        actions = ["Exit 75–80% position today", "Set hard stop-loss for remainder", "Do not let emotions override this signal"]

    getattr(st, color)(f"### {label}")
    st.markdown(f"**Analysis:** {detail}")

    st.markdown("#### Immediate action steps")
    for i, action in enumerate(actions, 1):
        st.markdown(f"**{i}.** {action}")

    st.markdown("---")

    # ── Score breakdown ──────────────────────────────────────────────────────
    st.markdown("#### Signal score breakdown")
    c1, c2 = st.columns(2)

    with c1:
        breakdown_data = {
            "Valuation vs fair value": (
                4 if ratio > 1.25 else 3 if ratio > 1.10 else 2 if ratio > 1.00 else 1 if ratio > 0.85 else 0
            ),
            "Retail FOMO score": (3 if ss >= 6 else 2 if ss >= 4 else 1 if ss >= 2 else 0),
            "Position gain level": (2 if gain > 150 else 1 if gain > 75 else 0),
        }

        for signal_name, signal_pts in breakdown_data.items():
            st.markdown(f"**{signal_name}:** {signal_pts} pts")

        st.markdown(f"**Total score: {pts} / 9**")
        st.progress(pts / 9)

    with c2:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=pts,
            title={"text": "Exit urgency score"},
            gauge={
                "axis": {"range": [0, 9]},
                "bar": {"color": "#E24B4A" if pts >= 7 else "#D85A30" if pts >= 5 else "#BA7517" if pts >= 3 else "#1D9E75"},
                "steps": [
                    {"range": [0, 2], "color": "#d4edda"},
                    {"range": [2, 4], "color": "#fff3cd"},
                    {"range": [4, 6], "color": "#fde8d8"},
                    {"range": [6, 9], "color": "#f8d7da"},
                ],
            }
        ))
        fig.update_layout(height=200, margin=dict(t=30, b=10, l=10, r=10))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ── Wyckoff phase ────────────────────────────────────────────────────────
    st.markdown("#### Wyckoff market cycle phase")
    phases = ["Accumulation", "Early markup", "Mid markup", "Distribution", "Markdown"]
    phase_idx = 0 if pts <= 1 else 1 if pts <= 2 else 2 if pts <= 4 else 3 if pts <= 6 else 4
    phase_tips = [
        "Quiet accumulation. Big money is building positions silently. Low volume, boring price action. Best time to buy.",
        "Early markup. Price starting to move. Smart money still buying. Retail has not noticed yet. Hold.",
        "Mid markup. Momentum strong. First retail entrants appearing. Monitor fundamentals each quarter.",
        "Distribution. Institutions quietly selling into retail enthusiasm. Exit ladder is now active.",
        "Markdown. Story is broken. Only exit into bounces — do not hold hoping for a recovery."
    ]

    cols = st.columns(5)
    for i, (phase, col) in enumerate(zip(phases, cols)):
        if i == phase_idx:
            col.error(f"**→ {phase}**")
        else:
            col.markdown(f"<div style='text-align:center;color:gray;font-size:12px'>{phase}</div>", unsafe_allow_html=True)

    st.info(phase_tips[phase_idx])

    st.markdown("---")

    # ── Risk flags ───────────────────────────────────────────────────────────
    st.markdown("#### Risk flags")
    risks = []
    if ratio > 1.10:
        risks.append(f"⚠️ Price is {(ratio-1)*100:.0f}% above computed fair value. You are holding speculative premium.")
    if ss >= 5:
        risks.append(f"⚠️ Retail FOMO at {ss}/8. Late entrants are your exit liquidity — don't confuse enthusiasm for validation.")
    de = inputs.get("debt_equity", 0)
    if de > 1.5:
        risks.append(f"⚠️ High debt (D/E: {de}). Earnings collapse faster than price in a downturn.")
    eps = inputs.get("eps", 0)
    epsg = inputs.get("eps_growth", 0)
    spe  = inputs.get("sector_pe", 25)
    if eps > 0 and epsg > 0 and (cur / eps) > epsg * 2:
        risks.append(f"⚠️ PE ({cur/eps:.0f}x) is more than 2x the growth rate ({epsg}%). Any earnings miss will be punished hard.")

    if not risks:
        st.success("✅ No major red flags currently. Maintain exit discipline regardless — conditions reverse fast.")
    else:
        for r in risks:
            st.warning(r)

    st.markdown("---")

    # ── Export summary ───────────────────────────────────────────────────────
    st.markdown("#### Export your analysis")
    df = generate_exit_ladder(buy, fv, qty, cur)
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Download exit ladder as CSV",
        data=csv,
        file_name=f"exit_clock_{name.replace(' ', '_')}.csv",
        mime="text/csv"
    )

    st.caption(
        f"Analysis for **{name}** | Buy: ₹{buy:,.0f} | Current: ₹{cur:,.0f} | "
        f"Fair value: ₹{fv:,.0f} | Sentiment: {ss}/8 | Score: {pts}/9"
    )
