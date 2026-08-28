import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
import plotly.graph_objects as go
from utils.sentiment_engine import score_sentiment, get_all_signals


def render():
    st.title("📡 Sentiment Check")
    st.caption("Retail FOMO detector. When all 8 signals fire — that is your exit liquidity. Use it.")

    st.markdown("---")
    st.markdown("#### Check which signals are active right now for your asset")

    signals = get_all_signals()
    active_signals = []

    for sig in signals:
        col1, col2 = st.columns([5, 1])
        with col1:
            st.markdown(f"**{sig['label']}**")
            st.caption(sig["explanation"])
        with col2:
            checked = st.checkbox("Active", key=sig["id"],
                                  value=st.session_state.get(f"sent_{sig['id']}", False))
            st.session_state[f"sent_{sig['id']}"] = checked
            if checked:
                active_signals.append(sig["id"])
        st.markdown("---")

    result = score_sentiment(active_signals)
    st.session_state["sentiment_result"] = result
    st.session_state["active_signals"]   = active_signals

    # ── Score display ────────────────────────────────────────────────────────
    st.markdown("#### Your retail trap score")
    c1, c2 = st.columns([1, 2])

    with c1:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=result["score"],
            title={"text": "FOMO Score"},
            gauge={
                "axis": {"range": [0, 8], "tickvals": [0, 2, 4, 6, 8]},
                "bar": {"color": "#E24B4A" if result["score"] >= 6 else "#BA7517" if result["score"] >= 4 else "#1D9E75"},
                "steps": [
                    {"range": [0, 2], "color": "#d4edda"},
                    {"range": [2, 4], "color": "#fff3cd"},
                    {"range": [4, 6], "color": "#fde8d8"},
                    {"range": [6, 8], "color": "#f8d7da"},
                ],
            }
        ))
        fig.update_layout(height=220, margin=dict(t=30, b=10, l=10, r=10))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        color_func = {"green": st.success, "yellow": st.warning, "orange": st.warning, "red": st.error}
        getattr(color_func.get(result["color"], st.info), "__call__", st.info)(
            f"**{result['interpretation']}** — {result['active_count']}/{result['total_signals']} signals active"
        )
        st.markdown(f"**What this means:** {result['detail']}")
        st.markdown(f"**Recommended action:** `{result['action']}`")
        st.markdown(f"**Wyckoff phase:** {result['phase']}")

    st.markdown("---")
    st.markdown("→ Navigate to **Final Verdict** in the sidebar for the combined signal.")
