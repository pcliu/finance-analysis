import sys
import os
import json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../../.claude/skills/moomoo-trading'))
sys.path.append(SKILL_DIR)

from scripts import (
    get_kline_data, get_realtime_quote,
    calculate_rsi, calculate_macd, calculate_bollinger_bands,
    calculate_sma, calculate_atr, make_serializable
)
import moomoo as ft
import pandas as pd

TICKERS = ['US.RKLB', 'US.AMD', 'US.TSLA', 'US.SLV', 'US.GOOG', 'US.IAU', 'US.TSM', 'US.NVDA']

results = {}

for ticker in TICKERS:
    print(f"\nFetching {ticker}...")
    try:
        kline = get_kline_data(ticker, ktype=ft.KLType.K_DAY, count=120)
        if kline is None or len(kline) < 30:
            print(f"  Insufficient data for {ticker}")
            continue

        # Moomoo kline uses capitalized column names
        vol_col = 'Volume' if 'Volume' in kline.columns else 'volume'

        rsi = calculate_rsi(kline, window=14)
        macd_df = calculate_macd(kline)
        bb = calculate_bollinger_bands(kline)
        sma20 = calculate_sma(kline, window=20)
        sma50 = calculate_sma(kline, window=50)
        atr = calculate_atr(kline, window=14)

        kline['RSI'] = rsi['RSI']
        kline['MACD'] = macd_df['MACD']
        kline['Signal'] = macd_df['Signal']
        kline['Histogram'] = macd_df['Histogram']
        kline['BB_Upper'] = bb['Upper']
        kline['BB_Middle'] = bb['Middle']
        kline['BB_Lower'] = bb['Lower']
        kline['BB_Pct'] = bb['%B']
        kline['SMA20'] = sma20['SMA']
        kline['SMA50'] = sma50['SMA']
        kline['ATR'] = atr['ATR']
        kline['Vol_Ratio'] = kline[vol_col] / kline[vol_col].rolling(20).mean()

        latest = kline.iloc[-1]
        prev = kline.iloc[-2]

        def safe_float(val):
            try:
                v = float(val)
                return None if pd.isna(v) else v
            except:
                return None

        summary = {
            'close': safe_float(latest['Close']),
            'prev_close': safe_float(prev['Close']),
            'change_pct': safe_float((latest['Close'] - prev['Close']) / prev['Close'] * 100),
            'volume': safe_float(latest[vol_col]),
            'vol_ratio': safe_float(latest['Vol_Ratio']),
            'rsi': safe_float(latest['RSI']),
            'macd': safe_float(latest['MACD']),
            'macd_signal': safe_float(latest['Signal']),
            'macd_hist': safe_float(latest['Histogram']),
            'bb_pct': safe_float(latest['BB_Pct']),
            'bb_upper': safe_float(latest['BB_Upper']),
            'bb_middle': safe_float(latest['BB_Middle']),
            'bb_lower': safe_float(latest['BB_Lower']),
            'sma20': safe_float(latest['SMA20']),
            'sma50': safe_float(latest['SMA50']),
            'atr': safe_float(latest['ATR']),
            'high_52w': float(kline['Close'].tail(252).max()),
            'low_52w': float(kline['Close'].tail(252).min()),
            'above_sma20': bool(latest['Close'] > latest['SMA20']) if safe_float(latest['SMA20']) else None,
            'above_sma50': bool(latest['Close'] > latest['SMA50']) if safe_float(latest['SMA50']) else None,
            'macd_bullish': bool(latest['Histogram'] > 0) if safe_float(latest['Histogram']) is not None else None,
            'macd_cross_up': bool(prev['Histogram'] < 0 and latest['Histogram'] > 0) if (safe_float(latest['Histogram']) is not None and safe_float(prev['Histogram']) is not None) else False,
        }

        results[ticker] = summary
        rsi_str = f"{summary['rsi']:.1f}" if summary['rsi'] is not None else 'N/A'
        bb_str = f"{summary['bb_pct']:.2f}" if summary['bb_pct'] is not None else 'N/A'
        hist_str = f"{summary['macd_hist']:.3f}" if summary['macd_hist'] is not None else 'N/A'
        print(f"  Close: {summary['close']:.2f} | RSI: {rsi_str} | BB%: {bb_str} | MACD hist: {hist_str}")

    except Exception as e:
        import traceback
        print(f"  Error fetching {ticker}: {e}")
        traceback.print_exc()
        results[ticker] = {'error': str(e)}

# Real-time quotes
print("\n=== Real-time Quotes ===")
try:
    quotes = get_realtime_quote(TICKERS)
    rt_cols = ['code', 'last_price', 'open_price', 'high_price', 'low_price', 'volume', 'prev_close_price', 'amplitude', 'turnover']
    available_cols = [c for c in rt_cols if c in quotes.columns]
    print(quotes[available_cols].to_string())
    results['realtime'] = make_serializable(quotes)
except Exception as e:
    print(f"Error getting real-time quotes: {e}")

out_path = os.path.join(SCRIPT_DIR, 'us_indicators_data.json')
with open(out_path, 'w') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(f"\nSaved to {out_path}")
