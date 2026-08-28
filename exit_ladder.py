import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
import plotly.graph_objects as go
from utils.exit_engine import generate_exit_ladder, compute_summary
from utils.valuation_engine import compute_all


def render():
    st.title("🪜 Exit Ladder")
    st.caption("Your tranche-by-tranche exit plan. Never sell all at once — exit systematically into retail FOMO.")

    if "inputs" not in st.session_state:
        st.warning("⬅ Please complete Asset Inputs first.")
        return

    inputs    = st.session_state["inputs"]
    buy       = inputs.get("buy_price", 1)
    cur       = inputs.get("current_price", buy)
    qty       = int(st.session_state.get("quantity", 100))
    fv_res    = st.session_state.get("fv_results") or compute_all(inputs)
    fair_val  = fv_res["blend"]

    st.markdown("---")

    # ── Summary metrics ──────────────────────────────────────────────────────
    summary = compute_summary(buy, fair_val, qty, cur)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total invested",       f"₹{summary['total_invested']:,.0f}")
    c2.metric("Current value",        f"₹{summary['current_value']:,.0f}",
              delta=f"₹{summary['unrealised_pnl']:+,.0f} ({summary['unrealised_pct']:+.1f}%)")
    c3.metric("Max upside (at FV)",   f"₹{summary['max_upside']:,.0f}")
    c4.metric("Upside to fair value", f"{summary['upside_to_fv_pct']:+.1f}%")

    st.markdown("---")

    # ── Exit ladder table ────────────────────────────────────────────────────
    df = generate_exit_ladder(buy, fair_val, qty, cur)

    st.markdown("#### Your exit ladder")

    def color_action(val):
        if val == "PANIC EXIT":
            return "background-color: #f8d7da; color: #721c24; font-weight: bold"
        elif val == "Sell":
            return "background-color: #fde8d8; color: #6c2b0e"
        elif val == "Trim":
            return "background-color: #fff3cd; color: #856404"
        return ""

    styled = df.style.applymap(color_action, subset=["Action"])
    st.dataframe(styled, use_container_width=True, hide_index=True)

    # ── Profit locking visual ────────────────────────────────────────────────
    st.markdown("#### Profit locked at each tranche")

    normal_rows = df[df["Action"] != "PANIC EXIT"]
    fig = go.Figure()

    cumulative_proceeds = 0
    prices = []
    proceeds_list = []
    cumulative_list = []

    for _, row in normal_rows.iterrows():
        prices.append(f"₹{row['Trigger Price (₹)']:,.0f}\n({row['Action']})")
        proceeds_list.append(row["Est. Proceeds (₹)"])
        cumulative_proceeds += row["Est. Proceeds (₹)"]
        cumulative_list.append(cumulative_proceeds)

    fig.add_trace(go.Bar(
        x=prices, y=proceeds_list,
        name="Proceeds per tranche",
        marker_color="#4C8BF5",
        opacity=0.8
    ))
    fig.add_trace(go.Scatter(
        x=prices, y=cumulative_list,
        name="Cumulative proceeds",
        mode="lines+markers",
        line=dict(color="#E24B4A", width=2),
        marker=dict(size=8)
    ))
    fig.add_hline(
        y=inputs.get("buy_price", 1) * qty,
        line_dash="dash", line_color="gray",
        annotation_text="Total invested",
        annotation_position="bottom right"
    )
    fig.update_layout(
        xaxis_title="Exit trigger",
        yaxis_title="₹ proceeds",
        height=350,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(t=40, b=20, l=20, r=20)
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── Key numbers ──────────────────────────────────────────────────────────
    st.markdown("#### Key numbers to remember")
    c1, c2, c3 = st.columns(3)
    c1.metric("Profit locked by 2x",    f"₹{summary['locked_at_2x']:,.0f}",
              help="After selling 25% at 2x your buy price, this much profit is secured regardless of what happens next.")
    c2.metric("Panic exit floor",       f"₹{summary['panic_floor']:,.0f}",
              help="If growth misses badly, exiting at 1.05x buy price still lets you leave with a small gain. Never let a winner become a loser.")
    c3.metric("Full fair value exit",   f"₹{fair_val * qty:,.0f}",
              help="Total proceeds if you sell everything at computed fair value. Your ideal scenario.")

    st.markdown("---")
    st.info(
        "**The golden rule of this model:** By the time you reach fair value, you should have already sold 50–65% "
        "of your position. The remaining 35% is your runner — it can go higher if the story gets even better. "
        "But your base profit is already locked in."
    )
