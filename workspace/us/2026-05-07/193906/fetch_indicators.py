#!/usr/bin/env python3
"""Fetch real-time quotes and technical indicators for all watchlist tickers."""
import sys, os, json
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../../.claude/skills/moomoo-trading'))
sys.path.insert(0, SKILL_DIR)

from scripts import (
    get_realtime_quote, get_kline_data,
    calculate_rsi, calculate_macd, calculate_bollinger_bands,
    calculate_sma, calculate_atr, make_serializable
)
import moomoo as ft

TICKERS = [
    'US.PLTR', 'US.CRCL', 'US.RKLB', 'US.AMD', 'US.TSLA',
    'US.SLV', 'US.GOOG', 'US.IAU', 'US.TSM', 'US.NVDA'
]

def fetch_ticker(ticker):
    print(f"  Processing {ticker}...")
    result = {'code': ticker}
    try:
        # Real-time quote
        quote_df = get_realtime_quote([ticker])
        if quote_df is not None and len(quote_df) > 0:
            row = quote_df.iloc[0]
            result['realtime'] = {
                'last_price': float(row.get('last_price', 0)),
                'prev_close_price': float(row.get('prev_close_price', 0)),
                'open_price': float(row.get('open_price', 0)),
                'high_price': float(row.get('high_price', 0)),
                'low_price': float(row.get('low_price', 0)),
                'volume': int(row.get('volume', 0)),
                'turnover': float(row.get('turnover', 0)),
                'update_time': str(row.get('update_time', '')),
                'change_rate': float(row.get('change_rate', 0)),
            }

        # K-line data (120 days)
        kline = get_kline_data(ticker, ktype=ft.KLType.K_DAY, count=120)
        if kline is not None and len(kline) >= 20:
            # RSI
            rsi_df = calculate_rsi(kline)
            rsi_val = float(rsi_df['RSI'].iloc[-1]) if 'RSI' in rsi_df.columns else None

            # MACD
            macd_df = calculate_macd(kline)
            macd_val = float(macd_df['MACD'].iloc[-1]) if 'MACD' in macd_df.columns else None
            signal_val = float(macd_df['Signal'].iloc[-1]) if 'Signal' in macd_df.columns else None
            hist_val = float(macd_df['Histogram'].iloc[-1]) if 'Histogram' in macd_df.columns else None

            # Bollinger Bands
            bb_df = calculate_bollinger_bands(kline)
            bb_upper = float(bb_df['Upper'].iloc[-1]) if 'Upper' in bb_df.columns else None
            bb_middle = float(bb_df['Middle'].iloc[-1]) if 'Middle' in bb_df.columns else None
            bb_lower = float(bb_df['Lower'].iloc[-1]) if 'Lower' in bb_df.columns else None
            bb_pct = float(bb_df['%B'].iloc[-1]) if '%B' in bb_df.columns else None

            # SMA 20/50
            sma20_df = calculate_sma(kline, window=20)
            sma50_df = calculate_sma(kline, window=50)
            sma20 = float(sma20_df['SMA'].iloc[-1]) if 'SMA' in sma20_df.columns else None
            sma50 = float(sma50_df['SMA'].iloc[-1]) if 'SMA' in sma50_df.columns else None

            # ATR
            atr_df = calculate_atr(kline)
            atr_val = float(atr_df['ATR'].iloc[-1]) if 'ATR' in atr_df.columns else None

            # Volume ratio (vs 20-day avg)
            vol_col = 'Volume' if 'Volume' in kline.columns else 'volume'
            close_col = 'Close' if 'Close' in kline.columns else 'close'
            vol_20_avg = float(kline[vol_col].iloc[-21:-1].mean()) if len(kline) >= 21 else None
            vol_ratio = float(kline[vol_col].iloc[-1] / vol_20_avg) if vol_20_avg and vol_20_avg > 0 else None

            # Recent closes
            recent_closes = kline[close_col].iloc[-5:].tolist()

            result['indicators'] = {
                'rsi14': rsi_val,
                'macd': macd_val,
                'macd_signal': signal_val,
                'macd_histogram': hist_val,
                'bb_upper': bb_upper,
                'bb_middle': bb_middle,
                'bb_lower': bb_lower,
                'bb_pct_b': bb_pct,
                'sma20': sma20,
                'sma50': sma50,
                'atr14': atr_val,
                'vol_20avg': vol_20_avg,
                'vol_ratio': vol_ratio,
                'recent_closes': [float(x) for x in recent_closes],
                'kline_date': str(kline.index[-1]) if hasattr(kline.index[-1], '__str__') else str(kline['time_key'].iloc[-1] if 'time_key' in kline.columns else ''),
                'kline_count': len(kline),
            }
            print(f"    RSI={rsi_val:.1f} MACD_hist={hist_val:.3f} BB%B={bb_pct:.2f} last={result.get('realtime',{}).get('last_price','?')}")
        else:
            print(f"    Insufficient kline data")

    except Exception as e:
        print(f"    Error: {e}")
        result['error'] = str(e)

    return result

def main():
    print("Fetching indicators for all tickers...")
    all_data = {}
    for ticker in TICKERS:
        data = fetch_ticker(ticker)
        all_data[ticker] = data

    all_data['fetch_time'] = datetime.now().isoformat()

    out_path = os.path.join(SCRIPT_DIR, 'us_indicators_data.json')
    with open(out_path, 'w') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2, default=str)
    print(f"\nSaved to {out_path}")
    return all_data

if __name__ == '__main__':
    main()
