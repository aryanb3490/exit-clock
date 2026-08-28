# ⏰ Exit Clock — Smart Profit Booking Model

> **The exit problem is harder than the entry problem.**
> Everyone has a buy thesis. Almost nobody has a structured sell thesis.

Exit Clock is a behavioral finance tool that tells you **when to sell, how much to sell, and at what price** — for any asset class. Built on the thesis that smart money exits systematically into retail FOMO, while retailers hold hoping for a top that has already passed.

---

## 🧠 The Core Idea

Most retail investors lose not because they buy wrong — but because they **exit wrong**.

- They sell too early when they see any profit
- They hold too long because they anchored to a higher price
- They have no plan, so they decide emotionally

This model solves that. You enter your fundamentals. The model:
1. Computes fair value independently (no analyst dependency)
2. Generates a tranche-based exit ladder
3. Scores retail FOMO signals to identify the distribution phase
4. Gives a final verdict: Hold / Trim / Exit / Panic exit

---

## 📊 Works For Any Asset

| Asset | Valuation method used |
|---|---|
| 🇮🇳 Indian stocks | PE model + PEG ratio + DCF + Price-to-sales (blended) |
| ₿ Crypto | ATH-based + BTC dominance adjustment + network growth |
| 🥇 Gold / Commodity | Inflation-adjusted historical average + real rate model |
| 🏢 Startup / Unlisted | Forward revenue × industry multiple + runway adjustment |
| 📄 Bonds | Present value of coupons + face value discounted at YTM |

---

## 🔑 Key Features

- **Self-computed fair value** — 4 independent valuation models, blended. No analyst targets.
- **Tranche exit ladder** — exact price levels for each sell tranche (10%, 15%, 25%...)
- **Retail FOMO detector** — 8-signal behavioral checklist to identify distribution phase
- **Wyckoff cycle phase** — tells you which market phase you are currently in
- **Panic exit trigger** — automatic floor if growth thesis breaks
- **CSV export** — download your exit plan

---

## 🚀 How to Run Locally

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/exit-clock.git
cd exit-clock

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
streamlit run app.py
```

App opens at `http://localhost:8501`

---

## 🗂️ Project Structure

```
exit_clock/
├── app.py                    # Main entry point
├── requirements.txt
├── README.md
├── pages/
│   ├── asset_input.py        # Step 1 — enter position + fundamentals
│   ├── valuation.py          # Step 2 — 4-model fair value engine
│   ├── exit_ladder.py        # Step 3 — tranche exit plan
│   ├── sentiment.py          # Step 4 — retail FOMO detector
│   └── verdict.py            # Step 5 — combined signal + export
└── utils/
    ├── valuation_engine.py   # Core valuation math (PE, PEG, DCF, PS, bond, crypto, gold)
    ├── exit_engine.py        # Exit ladder generation
    └── sentiment_engine.py   # Behavioral signal scoring
```

---

## 📖 The Behavioral Finance Thesis

This tool is built around one observation:

**The market cycle always follows the same psychology:**

```
Accumulation → Early markup → Mid markup → Distribution → Markdown
     ↑                                           ↑
Smart money buys here                  Smart money sells here
(boring, low volume, no news)          (FOMO, viral, news coverage)
```

By the time a stock is on CNBC daily, your auto-driver is asking about it, and retail shareholding jumped 3% — the distribution phase has already started. This model quantifies those signals so you can exit before the trap closes.

---

## 🇮🇳 Case Studies (Blog)

This model was built as part of research into retail trapping in Indian markets during the 2024 bull run:
- **Suzlon Energy** — green energy narrative, retailer entry at top
- **IRFC** — safety bias (PSU = can't fall) trap
- **IPO cycle** — Zomato, Paytm, Hyundai — same trap, different logo
- **Crypto altcoin season** — BTC dominance, whale accumulation, retailer FOMO cycle

---

## 👤 About

Built by a 2nd-year Electrical Engineering student with 2 years of trading experience, pursuing CFA.
Interest: behavioral finance, institutional market mechanics, the psychology of retail trapping.

*Data sources: Screener.in, Tickertape, BSE shareholding patterns, NSE bulk/block deals*

---

## ⚠️ Disclaimer

This tool is for **educational and research purposes only**.
It is not financial advice. Always do your own research before making investment decisions.
Past performance of any model does not guarantee future results.
