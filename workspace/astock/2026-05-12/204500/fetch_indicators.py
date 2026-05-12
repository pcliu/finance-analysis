#!/usr/bin/env python3
"""Fetch technical indicators for A-stock ETF portfolio and watchlist."""
import os, json, sys
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, "/Users/liupengcheng/Code/finance-analysis/.claude/skills/quantitative-trading/scripts")

from data_fetcher import DataFetcher
from indicators import TechnicalIndicators

HOLDINGS = {
    "510150": "消费ETF",
    "510880": "红利ETF",
    "512170": "医疗ETF",
    "512660": "军工ETF",
    "513180": "恒指科技ETF",
    "513630": "香港红利ETF",
    "515050": "5GETF",
    "515070": "AI智能ETF",
    "515790": "光伏ETF",
    "561560": "电力ETF",
    "159516": "半导体设备ETF",
    "159770": "机器人AIETF",
    "159870": "化工ETF",
}

WATCHLIST = {
    "159985": "豆粕ETF",
    "159689": "粮食ETF",
    "561330": "矿业ETF",
    "159326": "电网设备ETF",
    "560280": "工程机械ETF",
    "159241": "航空航天ETF",
    "159830": "上海金ETF",
    "161226": "国投白银LOF",
    "588000": "科创50ETF",
}

ALL_SYMBOLS = {**HOLDINGS, **WATCHLIST}

fetcher = DataFetcher()
ti = TechnicalIndicators()
results = {}

for code, name in ALL_SYMBOLS.items():
    print(f"\n{'='*40}\nFetching {name} ({code})...")
    entry = {"name": name, "is_holding": code in HOLDINGS}
    try:
        df = fetcher.fetch_stock_data(code, period="3mo", market="CN")
        if df is None or df.empty:
            entry["error"] = "no historical data"
            results[code] = entry
            continue

        close = df["Close"].iloc[-1]
        vol = df["Volume"].iloc[-1]
        vol_ma20 = df["Volume"].rolling(20).mean().iloc[-1]

        # RSI
        rsi_df = ti.calculate_rsi(df, window=14)
        rsi14 = float(rsi_df["RSI"].iloc[-1])
        rsi_df6 = ti.calculate_rsi(df, window=6)
        rsi6 = float(rsi_df6["RSI"].iloc[-1])

        # Bollinger Bands
        bb = ti.calculate_bollinger_bands(df)
        pct_b = float(bb["Percent_B"].iloc[-1])
        bb_upper = float(bb["Upper"].iloc[-1])
        bb_lower = float(bb["Lower"].iloc[-1])
        bb_mid = float(bb["Middle"].iloc[-1])

        # MACD
        macd_df = ti.calculate_macd(df)
        macd_val = float(macd_df["MACD"].iloc[-1])
        macd_signal = float(macd_df["Signal"].iloc[-1])
        macd_hist = float(macd_df["Histogram"].iloc[-1])
        macd_hist_prev = float(macd_df["Histogram"].iloc[-2]) if len(macd_df) > 1 else None

        # SMA
        sma5 = float(ti.calculate_sma(df, window=5)["SMA"].iloc[-1])
        sma20 = float(ti.calculate_sma(df, window=20)["SMA"].iloc[-1])
        sma60 = float(ti.calculate_sma(df, window=60)["SMA"].iloc[-1]) if len(df) >= 60 else None

        # ATR
        atr_df = ti.calculate_atr(df)
        atr = float(atr_df["ATR"].iloc[-1])

        entry["indicators"] = {
            "close": round(float(close), 4),
            "rsi14": round(rsi14, 2),
            "rsi6": round(rsi6, 2),
            "pct_b": round(pct_b, 4),
            "bb_upper": round(bb_upper, 4),
            "bb_mid": round(bb_mid, 4),
            "bb_lower": round(bb_lower, 4),
            "macd": round(macd_val, 5),
            "macd_signal": round(macd_signal, 5),
            "macd_hist": round(macd_hist, 5),
            "macd_hist_prev": round(macd_hist_prev, 5) if macd_hist_prev is not None else None,
            "sma5": round(sma5, 4),
            "sma20": round(sma20, 4),
            "sma60": round(sma60, 4) if sma60 else None,
            "vol_ratio": round(float(vol) / float(vol_ma20), 2) if vol_ma20 and vol_ma20 > 0 else None,
            "atr": round(atr, 5),
        }
        print(f"  close={close:.4f} RSI14={rsi14:.1f} %B={pct_b:.3f} MACD_hist={macd_hist:.5f}")

    except Exception as e:
        entry["error"] = str(e)
        print(f"  ERROR: {e}")

    # Realtime quote
    try:
        rt_df = fetcher.fetch_realtime_quote([code], market="CN")
        if rt_df is not None and not rt_df.empty:
            row = rt_df.iloc[0]
            entry["realtime"] = {k: str(v) for k, v in row.to_dict().items()}
    except Exception as e:
        entry["realtime_error"] = str(e)

    results[code] = entry

out_path = os.path.join(SCRIPT_DIR, "astock_indicators_data.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2, default=str)
print(f"\n✅ Saved indicators to {out_path}")
