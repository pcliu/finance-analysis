#!/usr/bin/env python3
"""
持仓调整分析 — 2026-03-16（盘中）
技术指标分析：RSI、布林带（%B）、MACD、成交量比
"""

import sys
import os
import json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../.agent/skills/quantitative-trading'))
sys.path.append(SKILL_DIR)

from scripts import fetch_stock_data, calculate_rsi, calculate_macd, calculate_bollinger_bands
from scripts.utils import make_serializable

# All ETFs to analyze (holdings + watchlist)
ALL_ETFS = {
    # Current holdings (updated from screenshot 3/16)
    '510150': '消费ETF',
    '510880': '红利ETF',
    '512170': '医疗ETF',
    '512660': '军工ETF',
    '513180': '恒生科技指数ETF',
    '515050': '5GETF',
    '515070': 'AI智能',
    '515790': '光伏ETF',
    '588000': '科创50ETF',
    '159241': '航空航天ETF天弘',
    '159770': '机器人ETF',
    # Watchlist from ETFs.csv (non-held)
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

HOLDINGS = ['510150', '510880', '512170', '512660', '513180', '515050', '515070', '515790', '588000', '159241', '159770']

def analyze_etf(code, name):
    """Analyze a single ETF and return its technical indicators."""
    try:
        data = fetch_stock_data(code, period='8mo')
        if data is None or len(data) < 30:
            return {'code': code, 'name': name, 'error': 'Insufficient data'}

        # Calculate indicators
        rsi_df = calculate_rsi(data, window=14)
        macd_df = calculate_macd(data)
        bb_df = calculate_bollinger_bands(data, window=20)

        # Current values
        current_close = float(data['Close'].iloc[-1])
        prev_close = float(data['Close'].iloc[-2]) if len(data) > 1 else current_close

        # RSI
        current_rsi = float(rsi_df['RSI'].iloc[-1])

        # MACD
        macd_line = float(macd_df['MACD'].iloc[-1])
        signal_line = float(macd_df['Signal'].iloc[-1])
        histogram = float(macd_df['Histogram'].iloc[-1])
        prev_histogram = float(macd_df['Histogram'].iloc[-2]) if len(macd_df) > 1 else 0

        # Determine MACD cross status
        if histogram > 0 and prev_histogram <= 0:
            macd_status = '新金叉'
        elif histogram > 0:
            macd_status = '金叉延续'
        elif histogram < 0 and prev_histogram >= 0:
            macd_status = '新死叉'
        else:
            macd_status = '死叉延续'

        # Bollinger Bands %B
        upper = float(bb_df['Upper'].iloc[-1])
        lower = float(bb_df['Lower'].iloc[-1])
        middle = float(bb_df['Middle'].iloc[-1])
        bb_width = upper - lower
        pct_b = (current_close - lower) / bb_width if bb_width > 0 else 0.5

        # Volume analysis
        if 'Volume' in data.columns:
            vol_20 = data['Volume'].rolling(20).mean()
            current_vol = float(data['Volume'].iloc[-1])
            avg_vol = float(vol_20.iloc[-1]) if not vol_20.isna().iloc[-1] else current_vol
            vol_ratio = current_vol / avg_vol if avg_vol > 0 else 1.0
        else:
            vol_ratio = 1.0

        # Price changes
        daily_change = (current_close - prev_close) / prev_close * 100

        # 5-day change
        if len(data) >= 6:
            five_day_ago = float(data['Close'].iloc[-6])
            five_day_change = (current_close - five_day_ago) / five_day_ago * 100
        else:
            five_day_change = 0

        return {
            'code': code,
            'name': name,
            'close': round(current_close, 4),
            'rsi': round(current_rsi, 1),
            'pct_b': round(pct_b, 2),
            'macd_line': round(macd_line, 4),
            'signal_line': round(signal_line, 4),
            'histogram': round(histogram, 4),
            'prev_histogram': round(prev_histogram, 4),
            'macd_status': macd_status,
            'bb_upper': round(upper, 4),
            'bb_middle': round(middle, 4),
            'bb_lower': round(lower, 4),
            'vol_ratio': round(vol_ratio, 2),
            'daily_change': round(daily_change, 2),
            'five_day_change': round(five_day_change, 2),
            'is_holding': code in HOLDINGS,
            'error': None,
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {'code': code, 'name': name, 'error': str(e)}


def main():
    results = {}
    for code, name in ALL_ETFS.items():
        print(f"Analyzing {code} ({name})...")
        result = analyze_etf(code, name)
        results[code] = result
        if result.get('error'):
            print(f"  ERROR: {result['error']}")
        else:
            print(f"  RSI={result['rsi']}, %B={result['pct_b']}, MACD={result['macd_status']} (Hist={result['histogram']}), Daily={result['daily_change']}%")

    # Save to JSON
    clean_results = make_serializable(results)
    output_path = os.path.join(SCRIPT_DIR, 'portfolio_adjustment_data.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(clean_results, f, indent=4, ensure_ascii=False)
    print(f"\nResults saved to {output_path}")


if __name__ == '__main__':
    main()
