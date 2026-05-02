#!/usr/bin/env python3
"""
Portfolio Adjustment Technical Analysis — 2026-04-27
Analyzes all holdings + ETFs.csv watchlist with RSI, MACD, Bollinger, Stochastic, Volume Ratio
"""

import sys
import os
import json
import traceback

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Add skill path
SKILL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../.agent/skills/quantitative-trading'))
sys.path.append(SKILL_DIR)

from scripts import (
    fetch_stock_data, calculate_rsi, calculate_macd,
    calculate_bollinger_bands, calculate_sma, calculate_stochastic,
    fetch_realtime_quote
)
from scripts.utils import make_serializable

# ── All tickers ──────────────────────────────────────────────────────
# Current holdings
HOLDINGS = {
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
    '159870': '化工ETF',
}

# ETFs.csv watchlist (non-holding)
WATCHLIST = {
    '510150': '消费ETF',
    '159985': '豆粕ETF',
    '159689': '粮食ETF',
    '561330': '矿业ETF',
    '159326': '电网设备ETF',
    '560280': '工程机械ETF',
    '159241': '航空航天ETF',
    '159830': '上海金ETF',
    '161226': '国投白银LOF',
    '159516': '半导体设备ETF',
    '513630': '港股红利ETF',
}

ALL_TICKERS = {**HOLDINGS, **WATCHLIST}


def analyze_ticker(ticker, name, is_holding=True):
    """Full technical analysis for a single ticker."""
    result = {
        'ticker': ticker,
        'name': name,
        'is_holding': is_holding,
        'error': None,
    }

    try:
        # Fetch 8 months of daily data
        data = fetch_stock_data(ticker, period='8mo')
        if data is None or len(data) < 30:
            result['error'] = f"Insufficient data: {len(data) if data is not None else 0} rows"
            return result

        close = data['Close']
        volume = data['Volume'] if 'Volume' in data.columns else None

        # Current price info
        result['latest_price'] = float(close.iloc[-1])
        result['prev_close'] = float(close.iloc[-2])
        result['daily_change_pct'] = float((close.iloc[-1] / close.iloc[-2] - 1) * 100)

        # Price changes over periods
        if len(close) >= 5:
            result['5d_change_pct'] = float((close.iloc[-1] / close.iloc[-5] - 1) * 100)
        if len(close) >= 10:
            result['10d_change_pct'] = float((close.iloc[-1] / close.iloc[-10] - 1) * 100)
        if len(close) >= 20:
            result['20d_change_pct'] = float((close.iloc[-1] / close.iloc[-20] - 1) * 100)

        # RSI (14)
        rsi_df = calculate_rsi(data, window=14)
        result['rsi'] = float(rsi_df['RSI'].iloc[-1])
        if len(rsi_df) >= 2:
            result['rsi_prev'] = float(rsi_df['RSI'].iloc[-2])

        # MACD
        macd_df = calculate_macd(data)
        result['macd'] = float(macd_df['MACD'].iloc[-1])
        result['macd_signal'] = float(macd_df['Signal'].iloc[-1])
        result['macd_hist'] = float(macd_df['Histogram'].iloc[-1])
        if len(macd_df) >= 2:
            result['macd_hist_prev'] = float(macd_df['Histogram'].iloc[-2])

        # Bollinger Bands
        bb_df = calculate_bollinger_bands(data)
        upper = bb_df['Upper'].iloc[-1]
        lower = bb_df['Lower'].iloc[-1]
        middle = bb_df['Middle'].iloc[-1]
        price = close.iloc[-1]
        if upper != lower:
            result['bb_pct_b'] = float((price - lower) / (upper - lower))
        result['bb_upper'] = float(upper)
        result['bb_middle'] = float(middle)
        result['bb_lower'] = float(lower)

        # Stochastic
        stoch_df = calculate_stochastic(data)
        result['stoch_k'] = float(stoch_df['K'].iloc[-1])
        result['stoch_d'] = float(stoch_df['D'].iloc[-1])

        # SMA 20 / 60
        sma20 = calculate_sma(data, window=20)
        result['sma20'] = float(sma20['SMA'].iloc[-1])
        if len(data) >= 60:
            sma60 = calculate_sma(data, window=60)
            result['sma60'] = float(sma60['SMA'].iloc[-1])

        # Volume ratio (today vol / 20d avg vol)
        if volume is not None and len(volume) >= 20:
            avg_vol_20 = volume.iloc[-20:].mean()
            if avg_vol_20 > 0:
                result['vol_ratio'] = float(volume.iloc[-1] / avg_vol_20)

        # MACD golden/death cross
        if result['macd_hist'] > 0 and result.get('macd_hist_prev', 0) <= 0:
            result['macd_cross'] = 'golden_cross_today'
        elif result['macd_hist'] < 0 and result.get('macd_hist_prev', 0) >= 0:
            result['macd_cross'] = 'death_cross_today'
        elif result['macd_hist'] > 0:
            result['macd_cross'] = 'above_signal'
        else:
            result['macd_cross'] = 'below_signal'

        # Price vs SMA
        result['price_vs_sma20'] = float((price / result['sma20'] - 1) * 100) if result.get('sma20') else None
        if result.get('sma60'):
            result['price_vs_sma60'] = float((price / result['sma60'] - 1) * 100)

    except Exception as e:
        result['error'] = f"{type(e).__name__}: {str(e)}"
        traceback.print_exc()

    return result


def main():
    all_results = {}

    # Analyze holdings
    print("=" * 60)
    print("Analyzing HOLDINGS...")
    print("=" * 60)
    for ticker, name in HOLDINGS.items():
        print(f"\n>>> {name} ({ticker})")
        res = analyze_ticker(ticker, name, is_holding=True)
        all_results[ticker] = res
        if res.get('error'):
            print(f"    ERROR: {res['error']}")
        else:
            print(f"    Price: {res['latest_price']:.4f} | RSI: {res.get('rsi', 'N/A'):.1f} | %B: {res.get('bb_pct_b', 'N/A'):.2f} | Hist: {res.get('macd_hist', 'N/A'):.4f} | StochK: {res.get('stoch_k', 'N/A'):.1f}")

    # Analyze watchlist
    print("\n" + "=" * 60)
    print("Analyzing WATCHLIST...")
    print("=" * 60)
    for ticker, name in WATCHLIST.items():
        print(f"\n>>> {name} ({ticker})")
        res = analyze_ticker(ticker, name, is_holding=False)
        all_results[ticker] = res
        if res.get('error'):
            print(f"    ERROR: {res['error']}")
        else:
            print(f"    Price: {res['latest_price']:.4f} | RSI: {res.get('rsi', 'N/A'):.1f} | %B: {res.get('bb_pct_b', 'N/A'):.2f} | Hist: {res.get('macd_hist', 'N/A'):.4f} | StochK: {res.get('stoch_k', 'N/A'):.1f}")

    # Fetch real-time quotes
    print("\n" + "=" * 60)
    print("Fetching real-time quotes...")
    print("=" * 60)
    try:
        all_codes = list(ALL_TICKERS.keys())
        rt_quotes = fetch_realtime_quote(all_codes)
        if rt_quotes is not None:
            print(rt_quotes.to_string())
            # Save real-time data
            rt_path = os.path.join(SCRIPT_DIR, 'realtime_quotes.json')
            rt_quotes.to_json(rt_path, orient='records', force_ascii=False, indent=2)
    except Exception as e:
        print(f"Real-time quote error: {e}")
        traceback.print_exc()

    # Save results
    clean = make_serializable(all_results)
    output_path = os.path.join(SCRIPT_DIR, 'portfolio_adjustment_data.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(clean, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Results saved to {output_path}")
    print(f"Total tickers analyzed: {len(all_results)}")

    # Summary table
    print("\n" + "=" * 80)
    print(f"{'Name':<16} {'Code':<8} {'RSI':>6} {'%B':>6} {'Hist':>8} {'StK':>6} {'5d%':>7} {'VolR':>6} {'Cross':<16}")
    print("-" * 80)
    for ticker, r in sorted(all_results.items(), key=lambda x: x[1].get('rsi', 0), reverse=True):
        if r.get('error'):
            print(f"{r['name']:<16} {ticker:<8} {'ERROR':>6}")
            continue
        print(f"{r['name']:<16} {ticker:<8} {r.get('rsi', 0):>6.1f} {r.get('bb_pct_b', 0):>6.2f} {r.get('macd_hist', 0):>8.4f} {r.get('stoch_k', 0):>6.1f} {r.get('5d_change_pct', 0):>6.1f}% {r.get('vol_ratio', 0):>5.2f} {r.get('macd_cross', 'N/A'):<16}")


if __name__ == '__main__':
    main()
