import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
from utils.valuation_engine import compute_all, interpret_valuation


def render():
    st.title("⏰ Exit Clock")
    st.subheader("Step 1 — Asset Inputs")
    st.caption("Enter your position details and fundamentals. The model computes fair value itself — no analyst needed.")

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        asset_name = st.text_input("Asset name", value=st.session_state.get("asset_name", "Suzlon Energy"))
    with col2:
        asset_type = st.selectbox(
            "Asset type",
            options=["stock", "crypto", "gold", "startup", "bond"],
            format_func=lambda x: {
                "stock": "🇮🇳 Indian Stock",
                "crypto": "₿ Crypto",
                "gold": "🥇 Gold / Commodity",
                "startup": "🏢 Startup / Unlisted",
                "bond": "📄 Bond"
            }[x],
            index=["stock", "crypto", "gold", "startup", "bond"].index(
                st.session_state.get("asset_type", "stock")
            )
        )

    st.markdown("#### Position")
    c1, c2, c3 = st.columns(3)
    with c1:
        buy_price = st.number_input("Avg buy price (₹)", min_value=0.01, value=float(st.session_state.get("buy_price", 45.0)), step=0.5)
    with c2:
        current_price = st.number_input("Current price (₹)", min_value=0.01, value=float(st.session_state.get("current_price", 72.0)), step=0.5)
    with c3:
        quantity = st.number_input("Quantity held", min_value=1, value=int(st.session_state.get("quantity", 1000)), step=1)

    st.markdown("---")

    # ── Fundamentals by asset type ───────────────────────────────────────────
    inputs = {
        "asset_type": asset_type,
        "current_price": current_price,
        "buy_price": buy_price,
    }

    if asset_type == "stock":
        st.markdown("#### Fundamentals — Stock")
        st.caption("All data available free on Screener.in, Tickertape, or BSE website.")

        c1, c2, c3 = st.columns(3)
        with c1:
            inputs["eps"]        = st.number_input("EPS — trailing 12m (₹)", value=float(st.session_state.get("eps", 2.1)), step=0.1)
            inputs["eps_growth"] = st.number_input("EPS growth rate (%/yr)", value=float(st.session_state.get("eps_growth", 28.0)), step=1.0)
            inputs["sector_pe"]  = st.number_input("Sector avg PE", value=float(st.session_state.get("sector_pe", 30.0)), step=1.0)
        with c2:
            inputs["rev_growth"] = st.number_input("Revenue growth (%/yr)", value=float(st.session_state.get("rev_growth", 25.0)), step=1.0)
            inputs["net_margin"] = st.number_input("Net profit margin (%)", value=float(st.session_state.get("net_margin", 8.0)), step=0.5)
            inputs["debt_equity"]= st.number_input("Debt-to-equity ratio", value=float(st.session_state.get("debt_equity", 0.4)), step=0.1)
        with c3:
            inputs["roe"]        = st.number_input("ROE (%)", value=float(st.session_state.get("roe", 18.0)), step=1.0)
            inputs["hist_pe"]    = st.number_input("5yr historical avg PE", value=float(st.session_state.get("hist_pe", 22.0)), step=1.0)
            inputs["promoter"]   = st.number_input("Promoter holding (%)", value=float(st.session_state.get("promoter", 55.0)), step=1.0)

    elif asset_type == "crypto":
        st.markdown("#### Fundamentals — Crypto")
        c1, c2 = st.columns(2)
        with c1:
            inputs["ath_price"]      = st.number_input("All-time high price (₹)", value=float(st.session_state.get("ath_price", 5000.0)), step=100.0)
            inputs["btc_dominance"]  = st.number_input("BTC dominance (%)", value=float(st.session_state.get("btc_dominance", 55.0)), step=1.0)
        with c2:
            inputs["network_growth"] = st.number_input("Network / user growth (%/yr)", value=float(st.session_state.get("network_growth", 40.0)), step=5.0)
        st.info("💡 BTC dominance above 55% = altcoin season has not started. Fair value gets discounted accordingly.")

    elif asset_type == "gold":
        st.markdown("#### Fundamentals — Gold / Commodity")
        c1, c2 = st.columns(2)
        with c1:
            inputs["hist_avg_price"]      = st.number_input("10yr avg price (₹/10g)", value=float(st.session_state.get("hist_avg_price", 50000.0)), step=1000.0)
            inputs["inflation_rate"]      = st.number_input("Inflation rate (%)", value=float(st.session_state.get("inflation_rate", 5.0)), step=0.5)
        with c2:
            inputs["real_interest_rate"]  = st.number_input("Real interest rate (%)", value=float(st.session_state.get("real_interest_rate", 1.0)), step=0.5)
        st.info("💡 Negative real interest rates = gold should trade at premium. Positive real rates = headwind for gold.")

    elif asset_type == "startup":
        st.markdown("#### Fundamentals — Startup / Unlisted")
        c1, c2 = st.columns(2)
        with c1:
            inputs["annual_revenue"]     = st.number_input("Annual revenue (₹ Cr)", value=float(st.session_state.get("annual_revenue", 100.0)), step=10.0)
            inputs["rev_growth"]         = st.number_input("Revenue growth (%/yr)", value=float(st.session_state.get("rev_growth", 60.0)), step=5.0)
        with c2:
            inputs["industry_multiple"]  = st.number_input("Industry revenue multiple (x)", value=float(st.session_state.get("industry_multiple", 5.0)), step=0.5)
            inputs["monthly_burn"]       = st.number_input("Monthly burn (₹ Cr)", value=float(st.session_state.get("monthly_burn", 5.0)), step=1.0)
        st.info("💡 Runway = Revenue / (Burn × 12). Low runway = discount applied to valuation automatically.")

    elif asset_type == "bond":
        st.markdown("#### Fundamentals — Bond")
        c1, c2 = st.columns(2)
        with c1:
            inputs["coupon_rate"]    = st.number_input("Coupon rate (%)", value=float(st.session_state.get("coupon_rate", 8.0)), step=0.25)
            inputs["ytm"]            = st.number_input("Yield to maturity (%)", value=float(st.session_state.get("ytm", 7.0)), step=0.25)
        with c2:
            inputs["face_value"]     = st.number_input("Face value (₹)", value=float(st.session_state.get("face_value", 1000.0)), step=100.0)
            inputs["maturity_years"] = st.number_input("Years to maturity", value=float(st.session_state.get("maturity_years", 5.0)), step=1.0)

    st.markdown("---")

    if st.button("💡 Compute fair value →", type="primary", use_container_width=True):
        fv = compute_all(inputs)
        interp = interpret_valuation(current_price, fv["blend"])

        # Save everything to session state
        st.session_state.update({
            "asset_name": asset_name,
            "asset_type": asset_type,
            "buy_price": buy_price,
            "current_price": current_price,
            "quantity": quantity,
            "inputs": inputs,
            "fv_results": fv,
            "valuation_interp": interp,
            **{k: v for k, v in inputs.items() if k not in ["asset_type", "current_price", "buy_price"]},
        })

        # ── Quick snapshot ───────────────────────────────────────────────────
        st.markdown("#### Quick snapshot")
        m1, m2, m3, m4 = st.columns(4)
        gain = (current_price - buy_price) / buy_price * 100
        upside = (fv["blend"] - current_price) / current_price * 100

        m1.metric("Computed fair value", f"₹{fv['blend']:,.0f}")
        m2.metric("Current gain", f"{gain:+.1f}%")
        m3.metric("Upside to fair value", f"{upside:+.1f}%")
        m4.metric("Position value", f"₹{current_price * quantity:,.0f}")

        color_map = {"green": "✅", "yellow": "🟡", "orange": "🟠", "red": "🔴"}
        st.markdown(f"""
        > {color_map.get(interp['color'], '•')} **{interp['label']}**
        > Recommended action: **{interp['action']}**
        """)

        st.success("Done! Navigate to **Valuation Engine** in the sidebar to see the full breakdown →")
