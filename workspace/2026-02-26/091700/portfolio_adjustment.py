#!/usr/bin/env python3
"""Portfolio adjustment technical analysis - 2026-02-26 盘前"""

import sys
import os
import json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../.agent/skills/quantitative-trading'))
sys.path.append(SKILL_DIR)

from scripts import fetch_stock_data, calculate_rsi, calculate_macd, calculate_bollinger_bands, calculate_sma
from scripts.utils import make_serializable

# All ETFs to analyze (holdings + watchlist from ETFs.csv)
ALL_ETFS = {
    # Current holdings
    '510150': '消费ETF',
    '510880': '红利ETF',
    '512170': '医疗ETF',
    '512660': '军工ETF',
    '513180': '恒生科技ETF',
    '515050': '5GETF',
    '515070': 'AI智能',
    '515790': '光伏ETF',
    '588000': '科创50',
    '159241': '航空TH',
    '159770': '机器人AI',
    # Watchlist from ETFs.csv (non-holdings)
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

results = {}

for code, name in ALL_ETFS.items():
    print(f"Analyzing {code} ({name})...")
    try:
        data = fetch_stock_data(code, period='6mo')
        if data is None or data.empty:
            print(f"  WARNING: No data for {code}")
            continue
        
        # Calculate indicators
        rsi_df = calculate_rsi(data, window=14)
        macd_df = calculate_macd(data)
        bb_df = calculate_bollinger_bands(data)
        sma20 = calculate_sma(data, window=20)
        
        # Volume analysis
        vol = data['Volume']
        vol_ma20 = vol.rolling(window=20).mean()
        vol_ratio = vol.iloc[-1] / vol_ma20.iloc[-1] if vol_ma20.iloc[-1] > 0 else 0
        
        # Bollinger %B
        close = data['Close'].iloc[-1]
        bb_upper = bb_df['Upper'].iloc[-1]
        bb_lower = bb_df['Lower'].iloc[-1]
        bb_middle = bb_df['Middle'].iloc[-1]
        bb_width = (bb_upper - bb_lower) / bb_middle if bb_middle > 0 else 0
        pct_b = (close - bb_lower) / (bb_upper - bb_lower) if (bb_upper - bb_lower) > 0 else 0.5
        
        # MACD signal
        macd_line = macd_df['MACD'].iloc[-1]
        signal_line = macd_df['Signal'].iloc[-1]
        histogram = macd_df['Histogram'].iloc[-1]
        
        # Previous day MACD for cross detection
        prev_macd = macd_df['MACD'].iloc[-2]
        prev_signal = macd_df['Signal'].iloc[-2]
        
        if macd_line > signal_line and prev_macd <= prev_signal:
            macd_status = '金叉(新)'
        elif macd_line > signal_line:
            macd_status = '金叉延续'
        elif macd_line < signal_line and prev_macd >= prev_signal:
            macd_status = '死叉(新)'
        elif macd_line < signal_line:
            macd_status = '死叉延续'
        else:
            macd_status = '中性'
        
        # Price changes
        if len(data) >= 2:
            change_1d = (data['Close'].iloc[-1] / data['Close'].iloc[-2] - 1) * 100
        else:
            change_1d = 0
        
        if len(data) >= 6:
            change_5d = (data['Close'].iloc[-1] / data['Close'].iloc[-6] - 1) * 100
        else:
            change_5d = 0
            
        if len(data) >= 21:
            change_20d = (data['Close'].iloc[-1] / data['Close'].iloc[-21] - 1) * 100
        else:
            change_20d = 0
        
        results[code] = {
            'name': name,
            'close': close,
            'rsi': rsi_df['RSI'].iloc[-1],
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram,
            'macd_status': macd_status,
            'bb_upper': bb_upper,
            'bb_middle': bb_middle,
            'bb_lower': bb_lower,
            'pct_b': pct_b,
            'bb_width': bb_width,
            'vol_ratio': vol_ratio,
            'change_1d': change_1d,
            'change_5d': change_5d,
            'change_20d': change_20d,
        }
        
        print(f"  RSI={rsi_df['RSI'].iloc[-1]:.1f}, %B={pct_b:.3f}, MACD={macd_status}, 1d={change_1d:+.2f}%")
        
    except Exception as e:
        print(f"  ERROR: {e}")
        continue

# Save results
clean_results = make_serializable(results)
output_path = os.path.join(SCRIPT_DIR, 'portfolio_adjustment_data.json')
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(clean_results, f, indent=4, ensure_ascii=False)

print(f"\nAnalysis complete. Results saved to {output_path}")
print(f"Total ETFs analyzed: {len(results)}/{len(ALL_ETFS)}")
