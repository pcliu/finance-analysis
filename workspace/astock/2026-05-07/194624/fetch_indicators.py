#!/usr/bin/env python3
"""Fetch technical indicators for A-stock ETF portfolio analysis."""
import os, json, warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
import tushare as ts
import akshare as ak
from datetime import datetime, timedelta

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# All symbols to analyze
PORTFOLIO = {
    "510150": {"name": "消费ETF", "shares": 10000, "cost": 0.5191, "value": 5180.00},
    "510880": {"name": "红利ETF", "shares": 10000, "cost": 3.0671, "value": 32720.00},
    "512170": {"name": "医疗ETF", "shares": 16000, "cost": 0.3562, "value": 5408.00},
    "512660": {"name": "军工ETF", "shares": 4000, "cost": 1.6496, "value": 5784.00},
    "513180": {"name": "恒指科技", "shares": 5000, "cost": 0.6531, "value": 3270.00},
    "515050": {"name": "5GETF", "shares": 2000, "cost": 2.1545, "value": 6328.00},
    "515070": {"name": "AI智能", "shares": 800, "cost": 2.1650, "value": 1926.40},
    "515790": {"name": "光伏ETF", "shares": 3000, "cost": 1.1510, "value": 3303.00},
    "561560": {"name": "电力ETF", "shares": 2000, "cost": 1.3623, "value": 2786.00},
    "588000": {"name": "科创50", "shares": 500, "cost": 0.0, "value": 884.50},
    "159516": {"name": "半导体设备", "shares": 8000, "cost": 0.9910, "value": 8400.00},
    "159770": {"name": "机器人AI", "shares": 200, "cost": 0.7670, "value": 227.20},
    "159870": {"name": "化工ETF", "shares": 6000, "cost": 0.9033, "value": 5622.00},
}

WATCHLIST = {
    "159985": {"name": "豆粕ETF"},
    "159689": {"name": "粮食ETF"},
    "561330": {"name": "矿业ETF"},
    "159326": {"name": "电网设备ETF"},
    "560280": {"name": "工程机械ETF"},
    "159241": {"name": "航空航天ETF"},
    "159830": {"name": "上海金ETF"},
    "161226": {"name": "国投白银LOF"},
    "513630": {"name": "港股红利ETF"},
}

ALL_SYMBOLS = {**PORTFOLIO, **WATCHLIST}

def calc_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / (loss + 1e-10)
    return 100 - 100 / (1 + rs)

def calc_macd(series, fast=12, slow=26, signal=9):
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd = ema_fast - ema_slow
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    hist = macd - signal_line
    return macd, signal_line, hist

def calc_bollinger(series, period=20, std=2):
    sma = series.rolling(period).mean()
    band = series.rolling(period).std()
    upper = sma + std * band
    lower = sma - std * band
    pct_b = (series - lower) / (upper - lower + 1e-10)
    return upper, sma, lower, pct_b

def get_tushare_data(symbol, start_date, end_date):
    """Get historical data via tushare."""
    try:
        pro = ts.pro_api()
        # Try ETF daily data
        suffix = "SH" if symbol.startswith(("5", "6", "9")) else "SZ"
        ts_code = f"{symbol}.{suffix}"
        df = pro.fund_daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
        if df is None or df.empty:
            df = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
        if df is not None and not df.empty:
            df = df.sort_values('trade_date').reset_index(drop=True)
            return df
    except Exception as e:
        print(f"  Tushare error for {symbol}: {e}")
    return None

def get_akshare_realtime(symbol):
    """Get realtime quote via akshare."""
    try:
        # Determine market
        if symbol.startswith(("5", "6", "9")):
            market_symbol = f"sh{symbol}"
        else:
            market_symbol = f"sz{symbol}"
        df = ak.stock_zh_a_spot_em()
        row = df[df['代码'] == symbol]
        if not row.empty:
            return {
                "price": float(row['最新价'].values[0]),
                "pct_chg": float(row['涨跌幅'].values[0]),
                "volume": float(row['成交量'].values[0]),
                "turnover": float(row['成交额'].values[0]),
            }
    except Exception as e:
        print(f"  AKShare realtime error for {symbol}: {e}")
    return None

def analyze_symbol(symbol, info):
    """Fetch and compute indicators for a symbol."""
    print(f"  Analyzing {info['name']} ({symbol})...")
    end_date = "20260507"
    start_date = "20251101"  # ~6 months for enough history

    result = {
        "symbol": symbol,
        "name": info["name"],
        "indicators": {},
        "realtime": {},
        "error": None
    }

    # Get historical data
    df = get_tushare_data(symbol, start_date, end_date)

    if df is None or df.empty:
        result["error"] = "No historical data"
        print(f"    No data for {symbol}")
        return result

    close = df['close']
    vol = df['vol']

    # RSI
    rsi14 = calc_rsi(close, 14)
    rsi6 = calc_rsi(close, 6)

    # MACD
    macd, signal, hist = calc_macd(close)

    # Bollinger
    upper, mid, lower, pct_b = calc_bollinger(close, 20)

    # Volume ratio
    vol_ma20 = vol.rolling(20).mean()
    vol_ratio = vol / vol_ma20

    # SMA
    sma5 = close.rolling(5).mean()
    sma20 = close.rolling(20).mean()
    sma60 = close.rolling(60).mean()

    # ATR
    high = df['high']
    low = df['low']
    tr = pd.concat([
        high - low,
        (high - close.shift()).abs(),
        (low - close.shift()).abs()
    ], axis=1).max(axis=1)
    atr14 = tr.rolling(14).mean()

    latest = -1
    result["indicators"] = {
        "close": round(float(close.iloc[latest]), 4),
        "rsi14": round(float(rsi14.iloc[latest]), 2),
        "rsi6": round(float(rsi6.iloc[latest]), 2),
        "macd": round(float(macd.iloc[latest]), 4),
        "macd_signal": round(float(signal.iloc[latest]), 4),
        "macd_hist": round(float(hist.iloc[latest]), 4),
        "bb_upper": round(float(upper.iloc[latest]), 4),
        "bb_mid": round(float(mid.iloc[latest]), 4),
        "bb_lower": round(float(lower.iloc[latest]), 4),
        "bb_pct_b": round(float(pct_b.iloc[latest]), 3),
        "sma5": round(float(sma5.iloc[latest]), 4),
        "sma20": round(float(sma20.iloc[latest]), 4),
        "sma60": round(float(sma60.iloc[latest]), 4) if not pd.isna(sma60.iloc[latest]) else None,
        "vol_ratio": round(float(vol_ratio.iloc[latest]), 2),
        "atr14": round(float(atr14.iloc[latest]), 4),
        "data_days": len(df),
        "last_date": df['trade_date'].iloc[latest],
    }

    # Trend assessment
    c = float(close.iloc[latest])
    s5 = float(sma5.iloc[latest])
    s20 = float(sma20.iloc[latest])
    above_sma5 = c > s5
    above_sma20 = c > s20

    if not pd.isna(sma60.iloc[latest]):
        s60 = float(sma60.iloc[latest])
        above_sma60 = c > s60
    else:
        s60 = None
        above_sma60 = None

    result["indicators"]["above_sma5"] = above_sma5
    result["indicators"]["above_sma20"] = above_sma20
    result["indicators"]["above_sma60"] = above_sma60

    # Price change
    if len(close) >= 5:
        result["indicators"]["pct_5d"] = round((c / float(close.iloc[-5]) - 1) * 100, 2)
    if len(close) >= 20:
        result["indicators"]["pct_20d"] = round((c / float(close.iloc[-20]) - 1) * 100, 2)

    print(f"    RSI14={result['indicators']['rsi14']}, %B={result['indicators']['bb_pct_b']}, MACD_hist={result['indicators']['macd_hist']}")

    return result

print("=== A-Stock ETF Technical Indicator Fetcher ===")
print(f"Output dir: {SCRIPT_DIR}")
print()

results = {}

print("[1/2] Fetching technical indicators via Tushare...")
for symbol, info in ALL_SYMBOLS.items():
    results[symbol] = analyze_symbol(symbol, info)

print()
print("[2/2] Fetching realtime quotes via AKShare...")
try:
    df_spot = ak.stock_zh_a_spot_em()
    for symbol in ALL_SYMBOLS:
        row = df_spot[df_spot['代码'] == symbol]
        if not row.empty:
            results[symbol]["realtime"] = {
                "price": float(row['最新价'].values[0]),
                "pct_chg": float(row['涨跌幅'].values[0]),
                "volume": float(row['成交量'].values[0]),
                "amount": float(row['成交额'].values[0]),
            }
            print(f"  {ALL_SYMBOLS[symbol]['name']} ({symbol}): {results[symbol]['realtime']['price']} ({results[symbol]['realtime']['pct_chg']}%)")
        else:
            print(f"  {symbol}: not found in spot data")
except Exception as e:
    print(f"  AKShare spot error: {e}")

# Save results
output_path = os.path.join(SCRIPT_DIR, "astock_indicators_data.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2, default=str)

print(f"\nSaved indicators to {output_path}")
print("Done.")
