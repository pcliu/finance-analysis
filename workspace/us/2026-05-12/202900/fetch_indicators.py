#!/usr/bin/env python3
"""Fetch realtime quotes and calculate technical indicators for watchlist."""
import sys, os, json
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../../.claude/skills/moomoo-trading'))
sys.path.append(SKILL_DIR)

from dotenv import load_dotenv
load_dotenv(os.path.join(SCRIPT_DIR, '../../../../.env.local'))

from scripts import (
    get_realtime_quote, get_kline_data, make_serializable,
    calculate_rsi, calculate_macd, calculate_bollinger_bands,
    calculate_sma, calculate_atr
)
import moomoo as ft
import pandas as pd

WATCHLIST = ['US.PLTR', 'US.CRCL', 'US.RKLB', 'US.AMD', 'US.TSLA',
             'US.SLV', 'US.GOOG', 'US.IAU', 'US.TSM', 'US.NVDA']

def safe_last(series):
    """Return last non-NaN value from a series."""
    s = series.dropna()
    return float(s.iloc[-1]) if len(s) > 0 else None

def main():
    result = {}
    fetch_time = datetime.now().isoformat()

    # 1. Realtime quotes
    print("Fetching realtime quotes...")
    quotes = get_realtime_quote(WATCHLIST)
    print(quotes[['code','last_price','prev_close_price','volume','turnover','update_time']] if not quotes.empty else "Empty")
    result['quotes'] = make_serializable(quotes)

    # 2. K-line + indicators for each ticker
    indicators = {}
    for ticker in WATCHLIST:
        print(f"\nProcessing {ticker}...")
        try:
            # Use explicit start/end to avoid count truncation cutting off recent days
            from datetime import date, timedelta
            kline_start = (date.today() - timedelta(days=250)).strftime('%Y-%m-%d')
            kline_end = date.today().strftime('%Y-%m-%d')
            kline = get_kline_data(ticker, ktype=ft.KLType.K_DAY, count=200,
                                   adjust_type=ft.AuType.QFQ,
                                   start=kline_start, end=kline_end)
            if kline is None or kline.empty:
                print(f"  No kline data for {ticker}")
                continue

            rsi = calculate_rsi(kline)
            macd = calculate_macd(kline)
            bb = calculate_bollinger_bands(kline)
            sma20 = calculate_sma(kline, window=20)
            sma50 = calculate_sma(kline, window=50)
            atr = calculate_atr(kline, window=14)

            # Volume stats (columns are capitalized in moomoo kline)
            vol_20avg = float(kline['Volume'].rolling(20).mean().iloc[-1]) if len(kline) >= 20 else None
            vol_last = float(kline['Volume'].iloc[-1])
            vol_ratio = vol_last / vol_20avg if vol_20avg else None

            # Price vs MAs
            last_close = float(kline['Close'].iloc[-1])
            sma20_val = safe_last(sma20['SMA']) if sma20 is not None and 'SMA' in sma20 else None
            sma50_val = safe_last(sma50['SMA']) if sma50 is not None and 'SMA' in sma50 else None

            # 52w high/low
            high_52w = float(kline['High'].rolling(252).max().iloc[-1]) if len(kline) >= 60 else None
            low_52w = float(kline['Low'].rolling(252).min().iloc[-1]) if len(kline) >= 60 else None

            # Recent price change
            pct_1d = float((kline['Close'].iloc[-1] / kline['Close'].iloc[-2] - 1) * 100) if len(kline) >= 2 else None
            pct_5d = float((kline['Close'].iloc[-1] / kline['Close'].iloc[-6] - 1) * 100) if len(kline) >= 6 else None
            pct_20d = float((kline['Close'].iloc[-1] / kline['Close'].iloc[-21] - 1) * 100) if len(kline) >= 21 else None

            indicators[ticker] = {
                'last_close': last_close,
                'rsi_14': safe_last(rsi['RSI']) if rsi is not None and 'RSI' in rsi else None,
                'macd': safe_last(macd['MACD']) if macd is not None and 'MACD' in macd else None,
                'macd_signal': safe_last(macd['Signal']) if macd is not None and 'Signal' in macd else None,
                'macd_hist': safe_last(macd['Histogram']) if macd is not None and 'Histogram' in macd else None,
                'bb_upper': safe_last(bb['Upper']) if bb is not None and 'Upper' in bb else None,
                'bb_middle': safe_last(bb['Middle']) if bb is not None and 'Middle' in bb else None,
                'bb_lower': safe_last(bb['Lower']) if bb is not None and 'Lower' in bb else None,
                'bb_pct_b': safe_last(bb['%B']) if bb is not None and '%B' in bb else None,
                'sma20': sma20_val,
                'sma50': sma50_val,
                'atr_14': safe_last(atr['ATR']) if atr is not None and 'ATR' in atr else None,
                'vol_last': vol_last,
                'vol_20avg': vol_20avg,
                'vol_ratio': vol_ratio,
                'high_52w': high_52w,
                'low_52w': low_52w,
                'pct_1d': pct_1d,
                'pct_5d': pct_5d,
                'pct_20d': pct_20d,
                'kline_last_date': str(kline.index[-1]) if hasattr(kline.index[-1], '__str__') else kline['time_key'].iloc[-1] if 'time_key' in kline.columns else None,
            }
            print(f"  RSI={indicators[ticker]['rsi_14']:.1f}, MACD_hist={indicators[ticker]['macd_hist']:.4f}, %B={indicators[ticker]['bb_pct_b']:.2f}")
        except Exception as e:
            print(f"  Error for {ticker}: {e}")
            import traceback; traceback.print_exc()

    result['indicators'] = indicators
    result['fetch_time'] = fetch_time

    out_path = os.path.join(SCRIPT_DIR, 'us_indicators_data.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\nSaved to {out_path}")
    return result

if __name__ == '__main__':
    main()
