#!/usr/bin/env python3
"""Portfolio Adjustment Technical Analysis - 2026-03-25 Post-Close"""
import sys
import os
import json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../.agent/skills/quantitative-trading'))
sys.path.append(SKILL_DIR)

from scripts import fetch_stock_data, calculate_rsi, calculate_macd, calculate_bollinger_bands, calculate_sma, calculate_atr, calculate_stochastic
from scripts import fetch_realtime_quote
from scripts.utils import make_serializable

# All tickers to analyze: current holdings + ETFs.csv watchlist
ALL_TICKERS = {
    # Current Holdings
    '510150': '消费ETF',
    '510880': '红利ETF',
    '512170': '医疗ETF',
    '512660': '军工ETF',
    '513180': '恒指科技ETF',
    '515050': '5GETF',
    '515070': 'AI智能',
    '515790': '光伏ETF',
    '588000': '科创50',
    '603993': '洛阳钼业',
    '159770': '机器人AI',
    # ETFs.csv watchlist (non-held)
    '159985': '豆粕ETF',
    '159689': '粮食ETF',
    '159870': '化工ETF',
    '561330': '矿业ETF',
    '561560': '电力ETF',
    '159326': '电网设备ETF',
    '560280': '工程机械ETF',
    '159241': '航空航天ETF',
    '159830': '上海金ETF',
    '161226': '国投白银LOF',
    '159516': '半导体设备ETF',
    '513630': '港股红利指数ETF',
}

HOLDINGS = {
    '510150': {'shares': 13000, 'cost': 0.5980, 'market_value': 6591.00},
    '510880': {'shares': 10000, 'cost': 3.0671, 'market_value': 32480.00},
    '512170': {'shares': 14000, 'cost': 0.3585, 'market_value': 4508.00},
    '512660': {'shares': 4000, 'cost': 1.6496, 'market_value': 5204.00},
    '513180': {'shares': 8000, 'cost': 0.6874, 'market_value': 5000.00},
    '515050': {'shares': 3000, 'cost': 2.4202, 'market_value': 7224.00},
    '515070': {'shares': 400, 'cost': 1.9388, 'market_value': 760.80},
    '515790': {'shares': 3000, 'cost': 1.1510, 'market_value': 3396.00},
    '588000': {'shares': 1000, 'cost': 0.3019, 'market_value': 1374.00},
    '603993': {'shares': 300, 'cost': 19.5169, 'market_value': 5340.00},
    '159770': {'shares': 200, 'cost': 0.7670, 'market_value': 192.60},
}

ACCOUNT = {
    'total_assets': 101253.55,
    'holdings_value': 72070.40,
    'available': 29183.15,
    'total_pnl': -1227.06,
    'today_pnl': 341.80,
}

results = {}

# Fetch real-time quotes
print("=" * 60)
print("Fetching real-time quotes...")
print("=" * 60)
try:
    all_codes = list(ALL_TICKERS.keys())
    quotes = fetch_realtime_quote(all_codes)
    print(f"Got {len(quotes) if hasattr(quotes, '__len__') else 'N/A'} quotes")
    if quotes is not None:
        print(quotes.to_string())
        results['realtime_quotes'] = make_serializable(quotes.to_dict('records') if hasattr(quotes, 'to_dict') else str(quotes))
except Exception as e:
    print(f"Real-time quote error: {e}")
    import traceback
    traceback.print_exc()
    results['realtime_quotes'] = str(e)

# Fetch technical data for each ticker
print("\n" + "=" * 60)
print("Fetching historical data and calculating indicators...")
print("=" * 60)

for ticker, name in ALL_TICKERS.items():
    print(f"\n--- {name} ({ticker}) ---")
    try:
        data = fetch_stock_data(ticker, period='9mo')
        if data is None or len(data) == 0:
            print(f"  No data for {ticker}")
            results[ticker] = {'name': name, 'error': 'No data'}
            continue

        print(f"  Data: {len(data)} rows, {data.index[0]} to {data.index[-1]}")

        # Calculate indicators
        rsi = calculate_rsi(data, window=14)
        macd = calculate_macd(data)
        bb = calculate_bollinger_bands(data)
        sma20 = calculate_sma(data, window=20)
        sma60 = calculate_sma(data, window=60)
        atr = calculate_atr(data, window=14)
        stoch = calculate_stochastic(data)

        # Volume analysis
        vol_20 = data['Volume'].rolling(20).mean()
        vol_ratio = data['Volume'].iloc[-1] / vol_20.iloc[-1] if vol_20.iloc[-1] > 0 else 0

        # Current values
        close = data['Close'].iloc[-1]
        prev_close = data['Close'].iloc[-2] if len(data) > 1 else close
        daily_change = (close - prev_close) / prev_close * 100

        # Bollinger %B
        pct_b = (close - bb['Lower'].iloc[-1]) / (bb['Upper'].iloc[-1] - bb['Lower'].iloc[-1]) if (bb['Upper'].iloc[-1] - bb['Lower'].iloc[-1]) > 0 else 0

        # MACD trend
        macd_hist = macd['Histogram'].iloc[-1]
        macd_hist_prev = macd['Histogram'].iloc[-2] if len(macd) > 1 else 0
        macd_signal = 'golden_cross' if macd['MACD'].iloc[-1] > macd['Signal'].iloc[-1] else 'death_cross'
        macd_trend = 'strengthening' if abs(macd_hist) > abs(macd_hist_prev) else 'weakening'

        # 5-day and 10-day performance
        perf_5d = (close - data['Close'].iloc[-6]) / data['Close'].iloc[-6] * 100 if len(data) > 5 else 0
        perf_10d = (close - data['Close'].iloc[-11]) / data['Close'].iloc[-11] * 100 if len(data) > 10 else 0

        ticker_result = {
            'name': name,
            'close': close,
            'daily_change_pct': daily_change,
            'perf_5d_pct': perf_5d,
            'perf_10d_pct': perf_10d,
            'rsi': rsi['RSI'].iloc[-1],
            'rsi_prev': rsi['RSI'].iloc[-2] if len(rsi) > 1 else None,
            'macd_line': macd['MACD'].iloc[-1],
            'macd_signal_line': macd['Signal'].iloc[-1],
            'macd_histogram': macd_hist,
            'macd_histogram_prev': macd_hist_prev,
            'macd_cross': macd_signal,
            'macd_trend': macd_trend,
            'bb_upper': bb['Upper'].iloc[-1],
            'bb_middle': bb['Middle'].iloc[-1],
            'bb_lower': bb['Lower'].iloc[-1],
            'pct_b': pct_b,
            'sma20': sma20['SMA'].iloc[-1],
            'sma60': sma60['SMA'].iloc[-1],
            'atr': atr['ATR'].iloc[-1],
            'stoch_k': stoch['K'].iloc[-1],
            'stoch_d': stoch['D'].iloc[-1],
            'volume': data['Volume'].iloc[-1],
            'vol_20avg': vol_20.iloc[-1],
            'vol_ratio': vol_ratio,
        }

        # Add holding info if applicable
        if ticker in HOLDINGS:
            h = HOLDINGS[ticker]
            ticker_result['is_holding'] = True
            ticker_result['shares'] = h['shares']
            ticker_result['cost'] = h['cost']
            ticker_result['market_value'] = h['market_value']
            ticker_result['pnl'] = (close - h['cost']) * h['shares']
            ticker_result['pnl_pct'] = (close - h['cost']) / h['cost'] * 100
            ticker_result['position_pct'] = h['market_value'] / ACCOUNT['total_assets'] * 100
        else:
            ticker_result['is_holding'] = False

        results[ticker] = ticker_result
        print(f"  Close: {close:.4f}, RSI: {rsi['RSI'].iloc[-1]:.1f}, %B: {pct_b:.2f}, MACD: {macd_signal}({macd_hist:.4f}), Vol: {vol_ratio:.2f}x")

    except Exception as e:
        print(f"  Error: {e}")
        import traceback
        traceback.print_exc()
        results[ticker] = {'name': name, 'error': str(e)}

# Add account info
results['account'] = ACCOUNT

# Save results
output_path = os.path.join(SCRIPT_DIR, 'portfolio_adjustment_data.json')
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(make_serializable(results), f, indent=2, ensure_ascii=False)
print(f"\nResults saved to {output_path}")
print("Done!")
