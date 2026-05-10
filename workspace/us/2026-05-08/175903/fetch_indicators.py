"""
Step 2: Fetch K-line data and calculate technical indicators for all symbols
"""

import sys
import os
import json
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../../.claude/skills/moomoo-trading'))
sys.path.insert(0, SKILL_DIR)

from scripts import get_kline_data, calculate_all, make_serializable
import moomoo as ft

SYMBOLS = ['US.NVDA', 'US.IAU', 'US.PLTR', 'US.CRCL', 'US.RKLB', 'US.AMD', 'US.TSLA', 'US.SLV', 'US.GOOG', 'US.TSM']

indicators_data = {}

for sym in SYMBOLS:
    print(f"\n--- {sym} ---")
    try:
        df = get_kline_data(sym, ktype=ft.KLType.K_DAY, count=120)
        if df.empty:
            print(f"  No data for {sym}")
            continue

        indic = calculate_all(df)
        row = indic.iloc[-1]

        rsi = float(row.get('RSI', float('nan')))
        bb_b = float(row.get('%B', float('nan')))
        macd = float(row.get('MACD', float('nan')))
        signal = float(row.get('Signal', float('nan')))
        hist = float(row.get('Histogram', float('nan')))
        upper = float(row.get('Upper', float('nan')))
        middle = float(row.get('Middle', float('nan')))
        lower = float(row.get('Lower', float('nan')))
        atr = float(row.get('ATR', float('nan')))
        k_val = float(row.get('K', float('nan')))
        d_val = float(row.get('D', float('nan')))
        sma = float(row.get('SMA', float('nan')))
        ema = float(row.get('EMA', float('nan')))

        vol_20ma = float(df['Volume'].iloc[-20:].mean())
        last_vol = float(df['Volume'].iloc[-1])

        indicators_data[sym] = {
            'last_bar_date': str(df.index[-1]),
            'last_close': float(df['Close'].iloc[-1]),
            'last_volume': last_vol,
            'vol_20ma': vol_20ma,
            'vol_ratio': last_vol / vol_20ma if vol_20ma > 0 else 0,
            'recent_10_closes': [float(x) for x in df['Close'].iloc[-10:].tolist()],
            'rsi': rsi,
            'macd': macd,
            'macd_signal': signal,
            'macd_hist': hist,
            'bb_upper': upper,
            'bb_middle': middle,
            'bb_lower': lower,
            'bb_pct_b': bb_b,
            'atr': atr,
            'stoch_k': k_val,
            'stoch_d': d_val,
            'sma20': sma,
            'ema20': ema,
        }

        print(f"  {len(df)} bars up to {df.index[-1].date()}  close={df['Close'].iloc[-1]:.2f}")
        print(f"  RSI={rsi:.1f}  BB_%B={bb_b:.2f}  MACD_Hist={hist:.3f}  StochK={k_val:.1f}  Vol/20MA={last_vol/vol_20ma:.2f}x")
        print(f"  BB: L={lower:.2f} M={middle:.2f} U={upper:.2f}  ATR={atr:.2f}  SMA20={sma:.2f}")

    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback; traceback.print_exc()
        indicators_data[sym] = {'error': str(e)}

out_path = os.path.join(SCRIPT_DIR, 'us_indicators_data.json')
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(indicators_data, f, indent=2, default=make_serializable, ensure_ascii=False)

print(f"\n✓ Saved to {out_path}")
