import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
import plotly.graph_objects as go
from utils.valuation_engine import compute_all, interpret_valuation


def render():
    st.title("📊 Valuation Engine")
    st.caption("Four independent models. No analyst needed. You feed fundamentals — model returns fair value.")

    if "inputs" not in st.session_state:
        st.warning("⬅ Please complete Asset Inputs first.")
        return

    inputs  = st.session_state["inputs"]
    fv      = compute_all(inputs)
    cur     = inputs["current_price"]
    buy     = inputs.get("buy_price", cur)
    interp  = interpret_valuation(cur, fv["blend"])

    # Save updated FV to session
    st.session_state["fv_results"] = fv
    st.session_state["valuation_interp"] = interp

    st.markdown("---")

    # ── 4 model cards ────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    atype = inputs.get("asset_type", "stock")

    def model_card(col, label, value, note=""):
        col.metric(label, f"₹{value:,.0f}", help=note)

    if atype == "stock":
        notes = fv.get("notes", {})
        model_card(c1, "PE model",  fv["pe"],  notes.get("pe",  {}).get("formula", ""))
        model_card(c2, "PEG model", fv["peg"], notes.get("peg", {}).get("formula", ""))
        model_card(c3, "DCF model", fv["dcf"], notes.get("dcf", {}).get("formula", ""))
        model_card(c4, "PS model",  fv["ps"],  notes.get("ps",  {}).get("formula", ""))
    else:
        c1.metric("Computed fair value", f"₹{fv['blend']:,.0f}")
        c2.metric("Current price", f"₹{cur:,.0f}")
        c3.metric("Buy price", f"₹{buy:,.0f}")
        c4.metric("Upside / downside", f"{(fv['blend']-cur)/cur*100:+.1f}%")

    st.markdown("---")

    # ── Model detail tabs ────────────────────────────────────────────────────
    if atype == "stock":
        notes = fv.get("notes", {})
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["PE model", "PEG ratio", "DCF model", "Price-to-sales", "🎯 Blended"])

        with tab1:
            st.markdown("#### PE-based valuation")
            pe_notes = notes.get("pe", {})
            c1, c2, c3 = st.columns(3)
            c1.metric("Quality adjustment", f"{pe_notes.get('quality_adj', 1):.2f}x",
                      help="Higher ROE = premium. High debt = discount.")
            c2.metric("Justified PE", f"{pe_notes.get('justified_pe', 0):.1f}x",
                      help="Blended sector PE + growth PE, quality adjusted.")
            c3.metric("PE fair value", f"₹{fv['pe']:,.0f}")
            st.info(f"**Formula:** {pe_notes.get('formula', '')}")
            st.caption("Quality adj factors in ROE and D/E ratio. A high-ROE, low-debt business justifies trading at a premium to sector PE.")

        with tab2:
            st.markdown("#### PEG ratio valuation")
            peg_notes = notes.get("peg", {})
            peg = fv.get("peg_ratio", 0)
            c1, c2, c3 = st.columns(3)
            c1.metric("Current PE", f"{peg_notes.get('current_pe', 0):.1f}x")
            c2.metric("PEG ratio", f"{peg:.2f}",
                      delta="Undervalued" if peg < 1 else "Overvalued" if peg > 2 else "Fair",
                      delta_color="normal" if peg < 1 else "inverse")
            c3.metric("PEG fair value", f"₹{fv['peg']:,.0f}")
            st.info(f"**Interpretation:** {peg_notes.get('interpretation', '')}")
            st.caption("PEG < 1 = stock is cheap for its growth rate. PEG > 2 = the growth story is fully (over) priced in.")

        with tab3:
            st.markdown("#### DCF — 5-year projection")
            dcf_notes = notes.get("dcf", {})
            c1, c2, c3 = st.columns(3)
            c1.metric("EPS in 5 years", f"₹{dcf_notes.get('eps_in_5y', 0):.2f}")
            c2.metric("Terminal multiple", f"{dcf_notes.get('terminal_multiple', 0):.0f}x")
            c3.metric("DCF fair value", f"₹{fv['dcf']:,.0f}")
            st.info(f"**Discount rate:** {dcf_notes.get('discount_rate', '12%')}")
            st.caption("Projects EPS 5 years forward at your growth rate. Applies conservative historical PE as terminal multiple. Discounts at 12% India equity risk rate.")

        with tab4:
            st.markdown("#### Price-to-sales cross-check")
            ps_notes = notes.get("ps", {})
            c1, c2 = st.columns(2)
            c1.metric("Net margin", ps_notes.get("net_margin", "N/A"))
            c2.metric("PS fair value", f"₹{fv['ps']:,.0f}")
            st.caption("Validates earnings-based models against revenue reality. Useful when quarterly earnings are lumpy or one-time items distort EPS.")

        with tab5:
            st.markdown("#### 🎯 Blended fair value — average of all four models")
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("PE", f"₹{fv['pe']:,.0f}")
            c2.metric("PEG", f"₹{fv['peg']:,.0f}")
            c3.metric("DCF", f"₹{fv['dcf']:,.0f}")
            c4.metric("PS", f"₹{fv['ps']:,.0f}")
            c5.metric("**Blended**", f"₹{fv['blend']:,.0f}")
            st.caption("If models diverge widely, it signals uncertainty — investigate why before acting.")
    else:
        # Non-stock: single model
        notes = fv.get("notes", {})
        st.metric("Computed fair value", f"₹{fv['blend']:,.0f}")
        if "interpretation" in notes:
            st.info(notes["interpretation"])

    st.markdown("---")

    # ── Visual: price vs fair value gauge ────────────────────────────────────
    st.markdown("#### Price vs fair value")
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=cur,
        delta={"reference": fv["blend"], "valueformat": ",.0f", "prefix": "vs FV ₹"},
        title={"text": f"Current price vs ₹{fv['blend']:,.0f} fair value"},
        gauge={
            "axis": {"range": [0, max(cur, fv["blend"]) * 1.4]},
            "bar": {"color": "#1f77b4"},
            "steps": [
                {"range": [0, fv["blend"] * 0.80],              "color": "#d4edda"},
                {"range": [fv["blend"] * 0.80, fv["blend"]],    "color": "#fff3cd"},
                {"range": [fv["blend"], fv["blend"] * 1.20],    "color": "#fde8d8"},
                {"range": [fv["blend"] * 1.20, max(cur, fv["blend"]) * 1.4], "color": "#f8d7da"},
            ],
            "threshold": {
                "line": {"color": "red", "width": 3},
                "thickness": 0.75,
                "value": fv["blend"]
            }
        }
    ))
    fig.update_layout(height=280, margin=dict(t=30, b=10, l=20, r=20))
    st.plotly_chart(fig, use_container_width=True)

    # ── Verdict banner ───────────────────────────────────────────────────────
    color_map = {"green": "success", "yellow": "warning", "orange": "warning", "red": "error"}
    icon_map  = {"green": "✅", "yellow": "🟡", "orange": "🟠", "red": "🔴"}
    getattr(st, color_map.get(interp["color"], "info"))(
        f"{icon_map.get(interp['color'], '•')} **{interp['label']}** — {interp['action']}"
    )

    st.markdown("→ Navigate to **Exit Ladder** in the sidebar to see your tranche plan.")
