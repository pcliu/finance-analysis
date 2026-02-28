#!/usr/bin/env python3
"""
Portfolio Adjustment Technical Analysis
Date: 2026-02-25
Covers: 11 holdings + 14 watchlist ETFs = 25 total
"""

import sys
import os
import json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Add skill path
SKILL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../.agent/skills/quantitative-trading'))
sys.path.append(SKILL_DIR)

from scripts import fetch_stock_data, calculate_rsi, calculate_macd, calculate_bollinger_bands, calculate_sma
from scripts.utils import make_serializable

# All ETFs to analyze (holdings + watchlist)
ALL_ETFS = {
    # Current Holdings (11)
    '510150': '消费ETF',
    '510880': '红利ETF',
    '512170': '医疗ETF',
    '512660': '军工ETF',
    '513180': '恒生科技ETF',
    '515050': '5GETF',
    '515070': 'AI智能',
    '515790': '光伏ETF',
    '588000': '科创50ETF',
    '159241': '航空TH',
    '159770': '机器人AI',
    # Watchlist (non-held, from ETFs.csv)
    '159985': '豆粕ETF',
    '512890': '红利低波ETF',
    '159206': '卫星ETF',
    '516780': '稀土ETF',
    '561330': '矿业ETF',
    '159870': '化工ETF',
    '561560': '电力ETF',
    '159830': '上海金ETF',
    '159326': '电网设备ETF',
    '159516': '半导体设备ETF',
    '161226': '国投白银LOF',
    '518880': '黄金ETF',
    '512400': '有色金属ETF',
    '513630': '港股红利ETF',
}

HOLDINGS = ['510150', '510880', '512170', '512660', '513180', '515050', '515070', '515790', '588000', '159241', '159770']

results = {}

for code, name in ALL_ETFS.items():
    try:
        print(f"Analyzing {code} ({name})...")
        data = fetch_stock_data(code, period='8mo')

        if data is None or data.empty:
            print(f"  WARNING: No data for {code}")
            results[code] = {'name': name, 'error': 'No data'}
            continue

        # Calculate indicators
        rsi_df = calculate_rsi(data, window=14)
        macd_df = calculate_macd(data)
        bb_df = calculate_bollinger_bands(data)
        sma20 = calculate_sma(data, window=20)

        # Volume analysis
        vol = data['Volume']
        vol_avg_20 = vol.rolling(20).mean()
        vol_ratio = vol.iloc[-1] / vol_avg_20.iloc[-1] if vol_avg_20.iloc[-1] > 0 else 0

        # Current values
        close = data['Close'].iloc[-1]
        prev_close = data['Close'].iloc[-2] if len(data) > 1 else close

        # Price changes
        close_5d = data['Close'].iloc[-6] if len(data) > 5 else data['Close'].iloc[0]
        close_10d = data['Close'].iloc[-11] if len(data) > 10 else data['Close'].iloc[0]
        close_20d = data['Close'].iloc[-21] if len(data) > 20 else data['Close'].iloc[0]
        chg_1d = (close - prev_close) / prev_close * 100
        chg_5d = (close - close_5d) / close_5d * 100
        chg_10d = (close - close_10d) / close_10d * 100
        chg_20d = (close - close_20d) / close_20d * 100

        # RSI
        current_rsi = rsi_df['RSI'].iloc[-1]

        # MACD
        macd_line = macd_df['MACD'].iloc[-1]
        signal_line = macd_df['Signal'].iloc[-1]
        histogram = macd_df['Histogram'].iloc[-1]
        # MACD cross detection
        prev_hist = macd_df['Histogram'].iloc[-2] if len(macd_df) > 1 else 0
        if histogram > 0 and prev_hist <= 0:
            macd_status = '金叉(新)'
        elif histogram > 0:
            macd_status = '金叉延续'
        elif histogram < 0 and prev_hist >= 0:
            macd_status = '死叉(新)'
        else:
            macd_status = '死叉延续'

        # Bollinger Bands
        bb_upper = bb_df['Upper'].iloc[-1]
        bb_middle = bb_df['Middle'].iloc[-1]
        bb_lower = bb_df['Lower'].iloc[-1]
        bb_pct_b = (close - bb_lower) / (bb_upper - bb_lower) if (bb_upper - bb_lower) > 0 else 0.5
        bb_width = (bb_upper - bb_lower) / bb_middle if bb_middle > 0 else 0

        # RSI trend (5 day)
        rsi_5d_ago = rsi_df['RSI'].iloc[-6] if len(rsi_df) > 5 else rsi_df['RSI'].iloc[0]
        rsi_trend = current_rsi - rsi_5d_ago

        # SMA20 position
        sma20_val = sma20['SMA'].iloc[-1]
        above_sma20 = close > sma20_val

        results[code] = {
            'name': name,
            'close': round(float(close), 4),
            'prev_close': round(float(prev_close), 4),
            'chg_1d': round(float(chg_1d), 2),
            'chg_5d': round(float(chg_5d), 2),
            'chg_10d': round(float(chg_10d), 2),
            'chg_20d': round(float(chg_20d), 2),
            'rsi': round(float(current_rsi), 1),
            'rsi_5d_ago': round(float(rsi_5d_ago), 1),
            'rsi_trend': round(float(rsi_trend), 1),
            'macd_line': round(float(macd_line), 6),
            'signal_line': round(float(signal_line), 6),
            'histogram': round(float(histogram), 6),
            'macd_status': macd_status,
            'bb_upper': round(float(bb_upper), 4),
            'bb_middle': round(float(bb_middle), 4),
            'bb_lower': round(float(bb_lower), 4),
            'bb_pct_b': round(float(bb_pct_b), 3),
            'bb_width': round(float(bb_width), 4),
            'vol_ratio': round(float(vol_ratio), 2),
            'sma20': round(float(sma20_val), 4),
            'above_sma20': bool(above_sma20),
            'is_holding': code in HOLDINGS,
        }
        print(f"  Done: RSI={current_rsi:.1f}, MACD={macd_status}, %B={bb_pct_b:.3f}")

    except Exception as e:
        print(f"  ERROR for {code}: {e}")
        results[code] = {'name': name, 'error': str(e)}

# Save results
clean_results = make_serializable(results)
output_path = os.path.join(SCRIPT_DIR, 'portfolio_adjustment_data.json')
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(clean_results, f, indent=4, ensure_ascii=False)

print(f"\nResults saved to {output_path}")
print(f"Total ETFs analyzed: {len(results)}")

# Summary
print("\n=== SUMMARY ===")
for code, info in sorted(results.items(), key=lambda x: x[1].get('rsi', 50)):
    if 'error' in info:
        print(f"  {code} {info['name']}: ERROR - {info['error']}")
    else:
        holding_tag = "[持仓]" if info['is_holding'] else "[观察]"
        print(f"  {code} {info['name']} {holding_tag}: RSI={info['rsi']}, MACD={info['macd_status']}, %B={info['bb_pct_b']:.3f}, 1d={info['chg_1d']:+.2f}%, 5d={info['chg_5d']:+.2f}%, vol_r={info['vol_ratio']:.2f}")
