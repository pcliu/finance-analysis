#!/usr/bin/env python3
"""
Portfolio Adjustment Analysis — 2026-04-23
Technical indicators for all holdings + ETFs.csv watchlist.
"""

import sys
import os
import json
import traceback

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../.agent/skills/quantitative-trading'))
sys.path.append(SKILL_DIR)

from scripts import (
    fetch_stock_data, calculate_rsi, calculate_macd,
    calculate_bollinger_bands, calculate_stochastic, calculate_sma
)
from scripts.utils import make_serializable

# === All tickers to analyze ===
# Current holdings (12 items, including newly added 化工ETF and 电力ETF)
HOLDINGS = {
    '510880': {'name': '红利ETF', 'shares': 10000, 'cost': 3.0671, 'market': 'cn_etf'},
    '512170': {'name': '医疗ETF', 'shares': 16000, 'cost': 0.3562, 'market': 'cn_etf'},
    '512660': {'name': '军工ETF', 'shares': 4000, 'cost': 1.6496, 'market': 'cn_etf'},
    '513180': {'name': '恒指科技', 'shares': 8000, 'cost': 0.6874, 'market': 'cn_etf'},
    '515050': {'name': '5GETF', 'shares': 3000, 'cost': 2.4202, 'market': 'cn_etf'},
    '515070': {'name': 'AI智能', 'shares': 400, 'cost': 1.9388, 'market': 'cn_etf'},
    '515790': {'name': '光伏ETF', 'shares': 3000, 'cost': 1.1510, 'market': 'cn_etf'},
    '561560': {'name': '电力ETF', 'shares': 2000, 'cost': 1.3623, 'market': 'cn_etf'},
    '588000': {'name': '科创50', 'shares': 1000, 'cost': 0.3019, 'market': 'cn_etf'},
    '603993': {'name': '洛阳钼业', 'shares': 300, 'cost': 19.5169, 'market': 'cn_stock'},
    '159770': {'name': '机器人AI', 'shares': 200, 'cost': 0.7670, 'market': 'cn_etf'},
    '159870': {'name': '化工ETF', 'shares': 7000, 'cost': 0.9071, 'market': 'cn_etf'},
}

# ETFs.csv watchlist (non-holding items)
WATCHLIST = {
    '510150': {'name': '消费ETF', 'market': 'cn_etf'},
    '159985': {'name': '豆粕ETF', 'market': 'cn_etf'},
    '159689': {'name': '粮食ETF', 'market': 'cn_etf'},
    '561330': {'name': '矿业ETF', 'market': 'cn_etf'},
    '159326': {'name': '电网设备ETF', 'market': 'cn_etf'},
    '560280': {'name': '工程机械ETF', 'market': 'cn_etf'},
    '159241': {'name': '航空航天ETF', 'market': 'cn_etf'},
    '159830': {'name': '上海金ETF', 'market': 'cn_etf'},
    '161226': {'name': '国投白银LOF', 'market': 'cn_etf'},
    '159516': {'name': '半导体设备ETF', 'market': 'cn_etf'},
    '513630': {'name': '港股红利ETF', 'market': 'cn_etf'},
}

def analyze_ticker(ticker, info, period='8mo'):
    """Analyze a single ticker with all technical indicators."""
    result = {
        'ticker': ticker,
        'name': info['name'],
        'status': 'ok',
        'error': None,
    }
    
    try:
        data = fetch_stock_data(ticker, period=period)
        if data is None or len(data) < 30:
            result['status'] = 'insufficient_data'
            result['error'] = f'Only {len(data) if data is not None else 0} rows'
            return result
        
        # Current price
        result['latest_price'] = float(data['Close'].iloc[-1])
        result['prev_close'] = float(data['Close'].iloc[-2])
        result['today_change_pct'] = round((result['latest_price'] / result['prev_close'] - 1) * 100, 2)
        
        # RSI
        rsi_df = calculate_rsi(data, window=14)
        result['rsi'] = round(float(rsi_df['RSI'].iloc[-1]), 1)
        result['rsi_prev'] = round(float(rsi_df['RSI'].iloc[-2]), 1)
        
        # MACD
        macd_df = calculate_macd(data)
        result['macd'] = round(float(macd_df['MACD'].iloc[-1]), 4)
        result['macd_signal'] = round(float(macd_df['Signal'].iloc[-1]), 4)
        result['macd_hist'] = round(float(macd_df['Histogram'].iloc[-1]), 4)
        result['macd_hist_prev'] = round(float(macd_df['Histogram'].iloc[-2]), 4)
        
        # Bollinger Bands
        bb_df = calculate_bollinger_bands(data)
        upper = float(bb_df['Upper'].iloc[-1])
        lower = float(bb_df['Lower'].iloc[-1])
        middle = float(bb_df['Middle'].iloc[-1])
        price = result['latest_price']
        result['bb_upper'] = round(upper, 4)
        result['bb_lower'] = round(lower, 4)
        result['bb_middle'] = round(middle, 4)
        result['bb_pct_b'] = round((price - lower) / (upper - lower), 2) if (upper - lower) > 0 else 0.5
        
        # Stochastic
        stoch_df = calculate_stochastic(data)
        result['stoch_k'] = round(float(stoch_df['K'].iloc[-1]), 1)
        result['stoch_d'] = round(float(stoch_df['D'].iloc[-1]), 1)
        
        # SMA 5, 20, 60
        sma5 = calculate_sma(data, window=5)
        sma20 = calculate_sma(data, window=20)
        sma60 = calculate_sma(data, window=60)
        result['sma5'] = round(float(sma5['SMA'].iloc[-1]), 4)
        result['sma20'] = round(float(sma20['SMA'].iloc[-1]), 4)
        result['sma60'] = round(float(sma60['SMA'].iloc[-1]), 4)
        result['price_vs_sma20_pct'] = round((price / result['sma20'] - 1) * 100, 2)
        
        # Volume analysis
        vol = data['Volume']
        result['volume_latest'] = int(vol.iloc[-1])
        result['volume_avg_20'] = int(vol.iloc[-20:].mean())
        result['volume_ratio'] = round(vol.iloc[-1] / vol.iloc[-20:].mean(), 2) if vol.iloc[-20:].mean() > 0 else 0
        
        # 5-day and 20-day return
        if len(data) >= 5:
            result['return_5d'] = round((price / float(data['Close'].iloc[-5]) - 1) * 100, 2)
        if len(data) >= 20:
            result['return_20d'] = round((price / float(data['Close'].iloc[-20]) - 1) * 100, 2)
        
        # Holdings-specific info
        if 'cost' in info:
            result['cost'] = info['cost']
            result['shares'] = info['shares']
            result['market_value'] = round(price * info['shares'], 2)
            result['pnl_pct'] = round((price / info['cost'] - 1) * 100, 2)
            result['pnl_amount'] = round((price - info['cost']) * info['shares'], 2)
        
    except Exception as e:
        result['status'] = 'error'
        result['error'] = f'{type(e).__name__}: {str(e)}'
        traceback.print_exc()
    
    return result


def main():
    print("=" * 80)
    print("Portfolio Adjustment Analysis — 2026-04-23")
    print("=" * 80)
    
    all_results = {}
    
    # Analyze holdings
    print("\n--- Analyzing Holdings ---")
    for ticker, info in HOLDINGS.items():
        print(f"  Analyzing {info['name']} ({ticker})...")
        result = analyze_ticker(ticker, info)
        all_results[ticker] = result
        if result['status'] == 'ok':
            rsi_str = f"RSI={result['rsi']}"
            hist_str = f"Hist={result['macd_hist']:+.4f}"
            pnl_str = f"PnL={result.get('pnl_pct', 'N/A')}%"
            print(f"    ✅ {rsi_str} | {hist_str} | %B={result['bb_pct_b']} | StochK={result['stoch_k']} | {pnl_str}")
        else:
            print(f"    ❌ {result['status']}: {result['error']}")
    
    # Analyze watchlist
    print("\n--- Analyzing Watchlist ---")
    for ticker, info in WATCHLIST.items():
        print(f"  Analyzing {info['name']} ({ticker})...")
        result = analyze_ticker(ticker, info)
        all_results[ticker] = result
        if result['status'] == 'ok':
            rsi_str = f"RSI={result['rsi']}"
            hist_str = f"Hist={result['macd_hist']:+.4f}"
            print(f"    ✅ {rsi_str} | {hist_str} | %B={result['bb_pct_b']} | StochK={result['stoch_k']}")
        else:
            print(f"    ❌ {result['status']}: {result['error']}")
    
    # Save results
    clean_results = make_serializable(all_results)
    output_path = os.path.join(SCRIPT_DIR, 'portfolio_adjustment_data.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(clean_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Results saved to {output_path}")
    print(f"Total tickers analyzed: {len(all_results)}")
    
    # Summary table
    print("\n" + "=" * 120)
    print(f"{'Name':<14} {'Ticker':<8} {'Price':>8} {'RSI':>6} {'%B':>6} {'Hist':>10} {'StochK':>7} {'5d%':>7} {'20d%':>7} {'VolR':>6} {'PnL%':>8}")
    print("-" * 120)
    for ticker, r in all_results.items():
        if r['status'] != 'ok':
            print(f"{r['name']:<14} {ticker:<8} {'ERROR':>8}")
            continue
        pnl = f"{r.get('pnl_pct', ''):>7}%" if 'pnl_pct' in r else "      —"
        print(f"{r['name']:<14} {ticker:<8} {r['latest_price']:>8.4f} {r['rsi']:>6.1f} {r['bb_pct_b']:>6.2f} {r['macd_hist']:>+10.4f} {r['stoch_k']:>7.1f} {r.get('return_5d', 0):>6.1f}% {r.get('return_20d', 0):>6.1f}% {r['volume_ratio']:>6.2f} {pnl}")
    print("=" * 120)


if __name__ == '__main__':
    main()
