#!/usr/bin/env python3
"""
Portfolio Adjustment - Technical Analysis
Date: 2026-02-11
Based on 2026-02-10 (Monday) closing data

Analyzes all 25 ETFs (10 holdings + 15 watchlist) with:
- RSI (14-day)
- MACD (12/26/9)
- Bollinger Bands (%B)
- Volume ratio (vs 20-day average)
- Price changes (1d, 5d, 20d)
"""

import sys
import os
import json
import warnings
warnings.filterwarnings('ignore')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../.agent/skills/quantitative-trading'))
sys.path.append(SKILL_DIR)

from scripts import fetch_stock_data, calculate_rsi, calculate_macd, calculate_bollinger_bands
from scripts.utils import make_serializable

# All 25 ETFs to analyze
ALL_ETFS = {
    # Current holdings (10)
    '510150': {'name': '消费ETF', 'holding': True, 'shares': 38000, 'cost': 0.5559},
    '510880': {'name': '红利ETF', 'holding': True, 'shares': 10000, 'cost': 3.0671},
    '512170': {'name': '医疗ETF', 'holding': True, 'shares': 14000, 'cost': 0.3585},
    '512660': {'name': '军工ETF', 'holding': True, 'shares': 8000, 'cost': 1.5128},
    '515050': {'name': '5GETF', 'holding': True, 'shares': 1000, 'cost': 2.3200},
    '515070': {'name': 'AI智能', 'holding': True, 'shares': 400, 'cost': 1.9388},
    '515790': {'name': '光伏ETF', 'holding': True, 'shares': 1000, 'cost': 1.1005},
    '588000': {'name': '科创50', 'holding': True, 'shares': 1000, 'cost': 0.3019},
    '159241': {'name': '航天TH', 'holding': True, 'shares': 8000, 'cost': 1.5185},
    '159770': {'name': '机器人AI', 'holding': True, 'shares': 200, 'cost': 0.7670},
    # Watchlist from ETFs.csv (15)
    '159985': {'name': '豆粕ETF', 'holding': False},
    '512890': {'name': '红利低波ETF', 'holding': False},
    '159206': {'name': '卫星ETF', 'holding': False},
    '516780': {'name': '稀土ETF', 'holding': False},
    '561330': {'name': '矿业ETF', 'holding': False},
    '159870': {'name': '化工ETF', 'holding': False},
    '561560': {'name': '电力ETF', 'holding': False},
    '159830': {'name': '上海金ETF', 'holding': False},
    '159326': {'name': '电网设备ETF', 'holding': False},
    '159516': {'name': '半导体设备ETF', 'holding': False},
    '161226': {'name': '白银LOF', 'holding': False},
    '518880': {'name': '黄金ETF', 'holding': False},
    '512400': {'name': '有色金属ETF', 'holding': False},
    '513180': {'name': '恒生科技ETF', 'holding': False},
    '513630': {'name': '港股红利ETF', 'holding': False},
}

results = {}

for code, info in ALL_ETFS.items():
    print(f"\n{'='*50}")
    print(f"Analyzing {info['name']} ({code})...")
    try:
        # Fetch 8 months of data
        data = fetch_stock_data(code, period='8mo')
        if data is None or len(data) < 30:
            print(f"  WARNING: Insufficient data for {code}, got {len(data) if data is not None else 0} rows")
            continue

        # Calculate indicators
        rsi_df = calculate_rsi(data, window=14)
        macd_df = calculate_macd(data, fast=12, slow=26, signal=9)
        bb_df = calculate_bollinger_bands(data, window=20, num_std=2)

        # Get latest values
        latest = data.iloc[-1]
        prev = data.iloc[-2] if len(data) > 1 else latest

        # Volume ratio (current vs 20-day average)
        vol_col = 'Volume' if 'Volume' in data.columns else 'Vol'
        if vol_col in data.columns:
            vol_20ma = data[vol_col].rolling(20).mean().iloc[-1]
            vol_ratio = data[vol_col].iloc[-1] / vol_20ma if vol_20ma > 0 else 0
        else:
            vol_ratio = 0

        # Price changes
        close_col = 'Close'
        current_price = data[close_col].iloc[-1]
        price_1d_ago = data[close_col].iloc[-2] if len(data) > 1 else current_price
        price_5d_ago = data[close_col].iloc[-6] if len(data) > 5 else current_price
        price_20d_ago = data[close_col].iloc[-21] if len(data) > 20 else current_price

        change_1d = (current_price - price_1d_ago) / price_1d_ago * 100
        change_5d = (current_price - price_5d_ago) / price_5d_ago * 100
        change_20d = (current_price - price_20d_ago) / price_20d_ago * 100

        # RSI values (last 5 days for trend)
        rsi_values = rsi_df['RSI'].dropna().tail(5).tolist()
        current_rsi = rsi_values[-1] if rsi_values else None

        # MACD values
        macd_line = macd_df['MACD'].iloc[-1]
        signal_line = macd_df['Signal'].iloc[-1]
        histogram = macd_df['Histogram'].iloc[-1]
        prev_histogram = macd_df['Histogram'].iloc[-2] if len(macd_df) > 1 else 0

        # MACD crossover detection
        if len(macd_df) > 1:
            prev_macd = macd_df['MACD'].iloc[-2]
            prev_signal = macd_df['Signal'].iloc[-2]
            if prev_macd <= prev_signal and macd_line > signal_line:
                macd_status = '金叉'
            elif prev_macd >= prev_signal and macd_line < signal_line:
                macd_status = '死叉'
            elif macd_line > signal_line:
                macd_status = '金叉延续'
            else:
                macd_status = '死叉延续'
        else:
            macd_status = '未知'

        # Bollinger Bands
        bb_upper = bb_df['Upper'].iloc[-1]
        bb_middle = bb_df['Middle'].iloc[-1]
        bb_lower = bb_df['Lower'].iloc[-1]
        pct_b = (current_price - bb_lower) / (bb_upper - bb_lower) if (bb_upper - bb_lower) > 0 else 0.5

        # 5-day RSI trend
        rsi_5d_trend = 'up' if len(rsi_values) >= 2 and rsi_values[-1] > rsi_values[0] else 'down'

        result = {
            'name': info['name'],
            'code': code,
            'holding': info.get('holding', False),
            'shares': info.get('shares', 0),
            'cost': info.get('cost', 0),
            'current_price': current_price,
            'change_1d': change_1d,
            'change_5d': change_5d,
            'change_20d': change_20d,
            'rsi': current_rsi,
            'rsi_5d': rsi_values,
            'rsi_5d_trend': rsi_5d_trend,
            'macd_line': macd_line,
            'signal_line': signal_line,
            'histogram': histogram,
            'prev_histogram': prev_histogram,
            'macd_status': macd_status,
            'bb_upper': bb_upper,
            'bb_middle': bb_middle,
            'bb_lower': bb_lower,
            'pct_b': pct_b,
            'vol_ratio': vol_ratio,
        }

        # P&L for holdings
        if info.get('holding'):
            result['pnl'] = (current_price - info['cost']) * info['shares']
            result['pnl_pct'] = (current_price - info['cost']) / info['cost'] * 100
            result['market_value'] = current_price * info['shares']

        results[code] = result
        print(f"  Price: {current_price:.4f} | RSI: {current_rsi:.1f} | MACD: {macd_status} | %B: {pct_b:.2f} | Vol Ratio: {vol_ratio:.2f}")

    except Exception as e:
        print(f"  ERROR analyzing {code}: {e}")
        import traceback
        traceback.print_exc()

# Summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

# Sort by RSI
sorted_results = sorted(results.values(), key=lambda x: x.get('rsi', 0) or 0, reverse=True)

print(f"\n{'Code':<8} {'Name':<12} {'Price':>8} {'RSI':>6} {'MACD':>8} {'%B':>6} {'1D%':>7} {'5D%':>7} {'20D%':>7} {'Hold':>5}")
print("-" * 85)
for r in sorted_results:
    hold_mark = "★" if r['holding'] else ""
    print(f"{r['code']:<8} {r['name']:<12} {r['current_price']:>8.4f} {r.get('rsi', 0):>6.1f} {r['macd_status']:>8} {r['pct_b']:>6.2f} {r['change_1d']:>7.2f} {r['change_5d']:>7.2f} {r['change_20d']:>7.2f} {hold_mark:>5}")

# Save results
output_path = os.path.join(SCRIPT_DIR, 'portfolio_adjustment_data.json')
clean_results = make_serializable(results)
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(clean_results, f, indent=4, ensure_ascii=False)
print(f"\nData saved to: {output_path}")
