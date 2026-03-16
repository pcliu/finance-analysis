#!/usr/bin/env python3
"""Portfolio adjustment technical analysis - 2026-03-06"""

import sys
import os
import json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../.agent/skills/quantitative-trading'))
sys.path.append(SKILL_DIR)

from scripts import (
    fetch_stock_data, calculate_rsi, calculate_macd,
    calculate_bollinger_bands, calculate_sma
)
from scripts.utils import make_serializable

# All ETFs to analyze (holdings + watchlist from ETFs.csv)
ALL_ETFS = {
    '510150': '消费ETF',
    '510880': '红利ETF',
    '512170': '医疗ETF',
    '512660': '军工ETF',
    '513180': '恒生科技指数ETF',
    '515050': '5GETF',
    '515070': 'AI智能ETF',
    '515790': '光伏ETF',
    '588000': '科创50ETF',
    '159241': '航空航天ETF',
    '159770': '机器人ETF',
    # Non-holdings from ETFs.csv
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
    '513630': '港股红利指数ETF',
}

HOLDINGS = {
    '510150': 13000, '510880': 10000, '512170': 14000, '512660': 8000,
    '513180': 5000, '515050': 1000, '515070': 400, '515790': 1000,
    '588000': 1000, '159241': 8000, '159770': 200
}

COSTS = {
    '510150': 0.5980, '510880': 3.0671, '512170': 0.3585, '512660': 1.5128,
    '513180': 0.7001, '515050': 2.3200, '515070': 1.9388, '515790': 1.1005,
    '588000': 0.3019, '159241': 1.5185, '159770': 0.7670
}

results = {}

for code, name in ALL_ETFS.items():
    print(f"Analyzing {code} ({name})...")
    try:
        data = fetch_stock_data(code, period='8mo')
        if data is None or data.empty:
            print(f"  WARNING: No data for {code}")
            results[code] = {'name': name, 'error': 'No data'}
            continue

        rsi = calculate_rsi(data, window=14)
        macd = calculate_macd(data)
        bb = calculate_bollinger_bands(data)
        sma20 = calculate_sma(data, window=20)

        close = data['Close']
        volume = data['Volume'] if 'Volume' in data.columns else None

        current_price = float(close.iloc[-1])
        prev_price = float(close.iloc[-2]) if len(close) > 1 else current_price
        daily_change_pct = (current_price - prev_price) / prev_price * 100

        # 5-day change
        if len(close) >= 6:
            price_5d_ago = float(close.iloc[-6])
            change_5d_pct = (current_price - price_5d_ago) / price_5d_ago * 100
        else:
            change_5d_pct = None

        # RSI
        current_rsi = float(rsi['RSI'].iloc[-1]) if not rsi['RSI'].isna().iloc[-1] else None
        prev_rsi = float(rsi['RSI'].iloc[-2]) if len(rsi) > 1 and not rsi['RSI'].isna().iloc[-2] else None

        # MACD
        macd_line = float(macd['MACD'].iloc[-1])
        signal_line = float(macd['Signal'].iloc[-1])
        histogram = float(macd['Histogram'].iloc[-1])
        prev_histogram = float(macd['Histogram'].iloc[-2]) if len(macd) > 1 else None

        # Determine MACD status
        if histogram > 0 and (prev_histogram is not None and prev_histogram <= 0):
            macd_status = 'golden_cross_new'
        elif histogram > 0:
            macd_status = 'golden_cross'
        elif histogram <= 0 and (prev_histogram is not None and prev_histogram > 0):
            macd_status = 'death_cross_new'
        else:
            macd_status = 'death_cross'

        # Bollinger Bands
        upper = float(bb['Upper'].iloc[-1])
        lower = float(bb['Lower'].iloc[-1])
        middle = float(bb['Middle'].iloc[-1])
        pct_b = (current_price - lower) / (upper - lower) if (upper - lower) != 0 else 0.5

        # Volume ratio
        vol_ratio = None
        if volume is not None and len(volume) >= 20:
            avg_vol_20 = float(volume.iloc[-21:-1].mean())
            if avg_vol_20 > 0:
                vol_ratio = float(volume.iloc[-1]) / avg_vol_20

        # Holdings info
        shares = HOLDINGS.get(code, 0)
        cost = COSTS.get(code, 0)
        if shares > 0:
            pnl = (current_price - cost) * shares
            pnl_pct = (current_price - cost) / cost * 100
        else:
            pnl = 0
            pnl_pct = 0

        results[code] = {
            'name': name,
            'price': current_price,
            'prev_price': prev_price,
            'daily_change_pct': round(daily_change_pct, 2),
            'change_5d_pct': round(change_5d_pct, 2) if change_5d_pct else None,
            'rsi': round(current_rsi, 1) if current_rsi else None,
            'prev_rsi': round(prev_rsi, 1) if prev_rsi else None,
            'macd': round(macd_line, 4),
            'signal': round(signal_line, 4),
            'histogram': round(histogram, 4),
            'prev_histogram': round(prev_histogram, 4) if prev_histogram else None,
            'macd_status': macd_status,
            'bb_upper': round(upper, 4),
            'bb_middle': round(middle, 4),
            'bb_lower': round(lower, 4),
            'pct_b': round(pct_b, 2),
            'vol_ratio': round(vol_ratio, 2) if vol_ratio else None,
            'shares': shares,
            'cost': cost,
            'pnl': round(pnl, 2) if shares > 0 else 0,
            'pnl_pct': round(pnl_pct, 2) if shares > 0 else 0,
        }
        print(f"  RSI={results[code]['rsi']}, MACD_status={macd_status}, "
              f"Hist={histogram:.4f}, %B={pct_b:.2f}, price={current_price}")

    except Exception as e:
        print(f"  ERROR: {e}")
        results[code] = {'name': name, 'error': str(e)}

# Save results
clean = make_serializable(results)
output_path = os.path.join(SCRIPT_DIR, 'portfolio_adjustment_data.json')
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(clean, f, indent=4, ensure_ascii=False)

print(f"\n✅ Results saved to {output_path}")
print(f"Total ETFs analyzed: {len(results)}")
