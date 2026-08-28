import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

st.set_page_config(
    page_title="Exit Clock — Smart Profit Booking Model",
    page_icon="⏰",
    layout="wide",
    initial_sidebar_state="expanded"
)

import importlib
asset_input  = importlib.import_module("pages.asset_input")
valuation    = importlib.import_module("pages.valuation")
exit_ladder  = importlib.import_module("pages.exit_ladder")
sentiment    = importlib.import_module("pages.sentiment")
verdict      = importlib.import_module("pages.verdict")

st.sidebar.title("⏰ Exit Clock")
st.sidebar.caption("Smart profit booking model for any asset")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate",
    ["1. Asset Inputs", "2. Valuation Engine", "3. Exit Ladder", "4. Sentiment Check", "5. Final Verdict"],
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    **Works for:**
    - 🇮🇳 Indian Stocks
    - ₿ Crypto
    - 🥇 Gold / Commodity
    - 🏢 Startups / Unlisted
    - 📄 Bonds
    """
)
st.sidebar.markdown("---")
st.sidebar.caption("Built by a 2nd year EE student with 2 years trading experience. Behavioral finance meets quant.")

if page == "1. Asset Inputs":
    asset_input.render()
elif page == "2. Valuation Engine":
    valuation.render()
elif page == "3. Exit Ladder":
    exit_ladder.render()
elif page == "4. Sentiment Check":
    sentiment.render()
elif page == "5. Final Verdict":
    verdict.render()
