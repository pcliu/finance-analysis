import json, os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Account snapshot
account_data = {
    "snapshot_time": "2026-05-04 18:00:07",
    "total_assets_usd": 8456.54,
    "cash_available_usd": 2048.37,
    "market_val_usd": 0.0,
    "frozen_cash": 0.0,
    "currency": "USD",
    "trading_env": "REAL",
    "positions": [],
    "orders_today": []
}

# Watchlist with real-time prices
watchlist_rt = {
    "RKLB": {"name": "Rocket Lab", "last": 78.81, "prev_close": 82.51, "change_pct": -4.48, "volume": 16378755, "type": "STOCK"},
    "AMD":  {"name": "Advanced Micro Devices", "last": 360.54, "prev_close": 354.49, "change_pct": 1.71, "volume": 34279169, "type": "STOCK"},
    "TSLA": {"name": "Tesla", "last": 390.82, "prev_close": 381.63, "change_pct": 2.41, "volume": 65338257, "type": "STOCK"},
    "SLV":  {"name": "iShares Silver Trust", "last": 68.29, "prev_close": 66.66, "change_pct": 2.44, "volume": 20237187, "type": "ETF"},
    "GOOG": {"name": "Alphabet-C", "last": 383.22, "prev_close": 381.94, "change_pct": 0.34, "volume": 28047873, "type": "STOCK"},
    "IAU":  {"name": "iShares Gold Trust", "last": 86.72, "prev_close": 86.85, "change_pct": -0.15, "volume": 9814938, "type": "ETF"},
    "TSM":  {"name": "Taiwan Semiconductor", "last": 397.67, "prev_close": 396.06, "change_pct": 0.41, "volume": 9926401, "type": "STOCK"},
    "NVDA": {"name": "NVIDIA", "last": 198.45, "prev_close": 199.57, "change_pct": -0.56, "volume": 128646996, "type": "STOCK"},
}

account_data["watchlist_realtime"] = watchlist_rt

with open(os.path.join(SCRIPT_DIR, 'us_account_data.json'), 'w') as f:
    json.dump(account_data, f, ensure_ascii=False, indent=2)

# Sentiment data
sentiment_data = {
    "snapshot_time": "2026-05-04 18:00:07",
    "macro": {
        "tariff": "Supreme Court struck down broad emergency-powers tariffs Jan 20 2026; admin responded with 15% import duty under new authority. Tariff headwinds persist.",
        "fed": "Fed expected to cut 50bps in 2026. Powell term ending in May. Next chair may lean dovish.",
        "market_mood": "Elevated volatility; Goldman Sachs constructive with lower index return expectations vs 2025. S&P 500 target 7,800 (+14%) per Morgan Stanley.",
        "ai_cycle": "AMD CEO: 'Year 2 of a 10-year AI build-out cycle'. AI spending structurally intact."
    },
    "stocks": {
        "RKLB": {
            "sentiment": "MIXED/CAUTIOUS",
            "headlines": [
                "Rocket Lab jumped 28.5% in April — price target upgrades, backlog >$2B, SpaceX IPO halo effect",
                "Q1 2026 earnings due May 7 after close — revenue consensus $191M (+56% YoY)",
                "P/S ratio ~70, one of highest globally — valuation stretched",
                "Sanctuary Advisors LLC reduces holdings",
                "Neutron rocket full test delayed to Q4 2026",
                "Stifel raised price target to $105"
            ],
            "key_risk": "Earnings event risk May 7; extreme valuation; institutional selling"
        },
        "AMD": {
            "sentiment": "CAUTIOUS (near-term)",
            "headlines": [
                "Q1 2026 earnings May 5 — revenue expected $9.84B (+32% YoY)",
                "AMD YTD +68%, April +64% — already pricing in strong results",
                "Cathie Wood sold $79.9M AMD — large institutional exit signal",
                "CEO Lisa Su: customers 'anxious' for MI450 GPU; AI inference use case strong",
                "DA Davidson reset price target; Wall Street divided",
                "AMD data center revenue went from zero to threatening Intel in 36 months"
            ],
            "key_risk": "Earnings binary event May 5; expensive valuation 33x 2027e P/E; Cathie Wood selling"
        },
        "TSLA": {
            "sentiment": "POSITIVE (fundamentals) / OVERBOUGHT (technical)",
            "headlines": [
                "Tesla projecting significant increase in AI investments to scale high-margin businesses",
                "Elon Musk announced news positive for NVDA stock (AI collaboration signal)",
                "AI agenda scaling — self-driving, robotics as long-term catalysts"
            ],
            "key_risk": "RSI 77 overbought; near-term extended after April run"
        },
        "SLV": {
            "sentiment": "POSITIVE (structural) / OVERBOUGHT (near-term)",
            "headlines": [
                "iShares Silver Trust returned 127% in past 12 months — outperforms IAU",
                "Silver's dual industrial demand: solar panels + AI data centers",
                "2026 expected to continue silver outperformance vs gold",
                "Fed rate cuts anticipated — favorable for non-yielding metals"
            ],
            "key_risk": "RSI 77; very extended; sharp volatile nature — entry timing critical"
        },
        "GOOG": {
            "sentiment": "STRONG POSITIVE (fundamental) / OVERBOUGHT (near-term)",
            "headlines": [
                "Google (GOOGL) had best month since 2004 in April 2026",
                "AI-driven ad revenue and cloud growth thesis intact",
                "Broad market leadership confirmed"
            ],
            "key_risk": "RSI 80.5 — most overbought in the watchlist; pullback risk elevated"
        },
        "IAU": {
            "sentiment": "POSITIVE",
            "headlines": [
                "Gold up 16% YTD as of March 2026",
                "Powell term ending May — next chair may favor rate cuts (gold positive)",
                "IAU lower expense ratio (0.25%) vs SLV (0.5%) — better for long-term hold",
                "Defensive safe-haven demand intact amid tariff/macro uncertainty"
            ],
            "key_risk": "RSI 69 moderately elevated; slower upside than SLV but lower drawdown risk"
        },
        "TSM": {
            "sentiment": "POSITIVE",
            "headlines": [
                "TSMC fiscal 2026 revenue +35.1% YoY — AI demand structural",
                "TSMC solidifying AI hardware partnerships",
                "Nvidia vs TSM earnings reveal AI hardware power split",
                "Geopolitical Taiwan risk remains a discount factor"
            ],
            "key_risk": "Geopolitical risk premium; tariff impact on chip supply chain"
        },
        "NVDA": {
            "sentiment": "POSITIVE",
            "headlines": [
                "NVIDIA fiscal 2026 revenue +73.21% — AI data center dominance",
                "Jensen Huang announced new quantum AI model 'Ising'",
                "Elon Musk announced positive news for NVIDIA investors",
                "AMD CEO: 'Year 2 of 10-year AI build-out' — NVDA primary beneficiary"
            ],
            "key_risk": "RSI 42 moderate — minor pullback underway; strong support at $195 region"
        }
    }
}

with open(os.path.join(SCRIPT_DIR, 'us_sentiment_data.json'), 'w') as f:
    json.dump(sentiment_data, f, ensure_ascii=False, indent=2)

print("JSON files saved successfully.")
