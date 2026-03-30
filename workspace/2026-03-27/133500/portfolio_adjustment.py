#!/usr/bin/env python3
"""Portfolio adjustment analysis - 2026-03-27 13:35 session
Covers all holdings + ETFs.csv watchlist"""

import sys
import os
import json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../.agent/skills/quantitative-trading'))
sys.path.append(SKILL_DIR)

from scripts import (
    fetch_stock_data, fetch_realtime_quote,
    calculate_rsi, calculate_macd, calculate_bollinger_bands,
    calculate_sma, calculate_atr, calculate_stochastic
)
from scripts.utils import make_serializable

# All tickers: holdings + watchlist
ALL_TICKERS = {
    # Current holdings
    '510150': '消费ETF',
    '510880': '红利ETF',
    '512170': '医疗ETF',
    '512660': '军工ETF',
    '513180': '恒指科技',
    '515050': '5GETF',
    '515070': 'AI智能',
    '515790': '光伏ETF',
    '561560': '电力ETF',
    '588000': '科创50',
    '603993': '洛阳钼业',
    '159770': '机器人AI',
    # Watchlist (non-held)
    '159985': '豆粕ETF',
    '159689': '粮食ETF',
    '159870': '化工ETF',
    '561330': '矿业ETF',
    '159326': '电网设备ETF',
    '560280': '工程机械ETF',
    '159241': '航空航天ETF',
    '159830': '上海金ETF',
    '161226': '国投白银LOF',
    '159516': '半导体设备ETF',
    '513630': '港股红利ETF',
}

HOLDINGS = ['510150', '510880', '512170', '512660', '513180', '515050',
            '515070', '515790', '561560', '588000', '603993', '159770']

results = {}

# 1. Fetch real-time quotes for all tickers
print("=== Fetching real-time quotes ===")
all_codes = list(ALL_TICKERS.keys())
try:
    rt_quotes = fetch_realtime_quote(all_codes)
    if rt_quotes is not None:
        for _, row in rt_quotes.iterrows():
            code = str(row.get('代码', '')).strip()
            # Clean up code - remove prefix
            for prefix in ['sh', 'sz', 'SH', 'SZ']:
                if code.startswith(prefix):
                    code = code[2:]
            results[code] = {
                'name': ALL_TICKERS.get(code, row.get('名称', '')),
                'realtime': {
                    'price': float(row.get('最新价', 0)),
                    'change': float(row.get('涨跌额', 0)),
                    'change_pct': float(row.get('涨跌幅', 0)),
                    'prev_close': float(row.get('昨收', 0)),
                    'open': float(row.get('今开', 0)),
                    'high': float(row.get('最高', 0)),
                    'low': float(row.get('最低', 0)),
                    'volume': float(row.get('成交量', 0)),
                    'amount': float(row.get('成交额', 0)),
                }
            }
            print(f"  {code} {ALL_TICKERS.get(code, '')}: {row.get('最新价', '?')} ({row.get('涨跌幅', '?')}%)")
except Exception as e:
    print(f"Real-time quote error: {e}")

# 2. Fetch historical data and calculate indicators
print("\n=== Computing technical indicators ===")
for code, name in ALL_TICKERS.items():
    print(f"\nProcessing {code} ({name})...")
    try:
        data = fetch_stock_data(code, period='6mo')
        if data is None or data.empty:
            print(f"  WARNING: No data for {code}")
            continue

        rsi = calculate_rsi(data, window=14)
        macd = calculate_macd(data)
        bb = calculate_bollinger_bands(data)
        sma20 = calculate_sma(data, window=20)
        sma60 = calculate_sma(data, window=60)
        atr = calculate_atr(data, window=14)
        stoch = calculate_stochastic(data)

        # Volume ratio (current vs 20-day average)
        vol = data['Volume']
        vol_20ma = vol.rolling(20).mean()
        vol_ratio = vol.iloc[-1] / vol_20ma.iloc[-1] if vol_20ma.iloc[-1] > 0 else 0

        # %B calculation
        upper = bb['Upper'].iloc[-1]
        lower = bb['Lower'].iloc[-1]
        close = data['Close'].iloc[-1]
        pct_b = (close - lower) / (upper - lower) if (upper - lower) > 0 else 0.5

        # 5-day and 10-day price change
        if len(data) >= 6:
            pct_5d = (data['Close'].iloc[-1] / data['Close'].iloc[-6] - 1) * 100
        else:
            pct_5d = 0
        if len(data) >= 11:
            pct_10d = (data['Close'].iloc[-1] / data['Close'].iloc[-11] - 1) * 100
        else:
            pct_10d = 0

        # MACD crossover status
        hist = macd['Histogram']
        hist_today = hist.iloc[-1]
        hist_yesterday = hist.iloc[-2] if len(hist) >= 2 else 0
        hist_2days = hist.iloc[-3] if len(hist) >= 3 else 0

        if hist_today > 0 and hist_yesterday <= 0:
            macd_status = 'golden_cross_new'
        elif hist_today > 0 and hist_yesterday > 0:
            macd_status = 'golden_cross'
        elif hist_today < 0 and hist_yesterday >= 0:
            macd_status = 'death_cross_new'
        elif hist_today < 0 and hist_yesterday < 0:
            if abs(hist_today) < abs(hist_yesterday):
                macd_status = 'death_cross_narrowing'
            else:
                macd_status = 'death_cross_widening'
        else:
            macd_status = 'neutral'

        # Previous RSI for tracking
        rsi_prev = rsi['RSI'].iloc[-2] if len(rsi) >= 2 else None

        indicators = {
            'close': float(close),
            'rsi': float(rsi['RSI'].iloc[-1]),
            'rsi_prev': float(rsi_prev) if rsi_prev is not None else None,
            'macd_line': float(macd['MACD'].iloc[-1]),
            'macd_signal': float(macd['Signal'].iloc[-1]),
            'macd_hist': float(hist_today),
            'macd_hist_prev': float(hist_yesterday),
            'macd_status': macd_status,
            'bb_upper': float(upper),
            'bb_middle': float(bb['Middle'].iloc[-1]),
            'bb_lower': float(lower),
            'pct_b': float(pct_b),
            'sma20': float(sma20['SMA'].iloc[-1]),
            'sma60': float(sma60['SMA'].iloc[-1]),
            'atr': float(atr['ATR'].iloc[-1]),
            'stoch_k': float(stoch['K'].iloc[-1]),
            'stoch_d': float(stoch['D'].iloc[-1]),
            'vol_ratio': float(vol_ratio),
            'pct_5d': float(pct_5d),
            'pct_10d': float(pct_10d),
        }

        if code not in results:
            results[code] = {'name': name}
        results[code]['indicators'] = indicators

        print(f"  RSI={indicators['rsi']:.1f}, %B={indicators['pct_b']:.2f}, "
              f"MACD Hist={indicators['macd_hist']:.4f} ({macd_status}), "
              f"Vol Ratio={indicators['vol_ratio']:.2f}")

    except Exception as e:
        print(f"  ERROR processing {code}: {e}")
        import traceback
        traceback.print_exc()

# 3. Save results
output_path = os.path.join(SCRIPT_DIR, 'portfolio_adjustment_data.json')
clean_results = make_serializable(results)
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(clean_results, f, indent=2, ensure_ascii=False)

print(f"\n=== Results saved to {output_path} ===")
print(f"Total tickers processed: {len(results)}")
