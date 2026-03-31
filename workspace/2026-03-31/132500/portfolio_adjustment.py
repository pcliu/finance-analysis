#!/usr/bin/env python3
"""Portfolio Adjustment Technical Analysis — 2026-03-31 午间"""

import sys
import os
import json
import traceback

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../.agent/skills/quantitative-trading'))
sys.path.append(SKILL_DIR)

from scripts import (
    fetch_stock_data, calculate_rsi, calculate_macd,
    calculate_bollinger_bands, calculate_stochastic, calculate_atr, calculate_sma
)
from scripts import fetch_realtime_quote
from scripts.utils import make_serializable

# ====== All tickers (holdings + watchlist) ======
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

def analyze_ticker(ticker, name):
    """Full technical analysis for a single ticker."""
    try:
        # Fetch 6-month historical data
        data = fetch_stock_data(ticker, period='6mo')
        if data is None or data.empty or len(data) < 30:
            return {'ticker': ticker, 'name': name, 'error': 'Insufficient data'}

        # Core indicators
        rsi_df = calculate_rsi(data, window=14)
        macd_df = calculate_macd(data)
        bb_df = calculate_bollinger_bands(data)
        stoch_df = calculate_stochastic(data)
        atr_df = calculate_atr(data, window=14)
        sma20_df = calculate_sma(data, window=20)
        sma5_df = calculate_sma(data, window=5)
        sma10_df = calculate_sma(data, window=10)
        sma60_df = calculate_sma(data, window=60)

        # Latest values
        close = data['Close'].iloc[-1]
        close_prev = data['Close'].iloc[-2] if len(data) > 1 else close
        
        rsi_val = rsi_df['RSI'].iloc[-1]
        rsi_prev = rsi_df['RSI'].iloc[-2] if len(rsi_df) > 1 else rsi_val

        macd_line = macd_df['MACD'].iloc[-1]
        signal_line = macd_df['Signal'].iloc[-1]
        hist = macd_df['Histogram'].iloc[-1]
        hist_prev = macd_df['Histogram'].iloc[-2] if len(macd_df) > 1 else hist
        hist_prev2 = macd_df['Histogram'].iloc[-3] if len(macd_df) > 2 else hist_prev

        bb_upper = bb_df['Upper'].iloc[-1]
        bb_lower = bb_df['Lower'].iloc[-1]
        bb_middle = bb_df['Middle'].iloc[-1]
        pct_b = (close - bb_lower) / (bb_upper - bb_lower) if (bb_upper - bb_lower) != 0 else 0.5

        stoch_k = stoch_df['K'].iloc[-1]
        stoch_d = stoch_df['D'].iloc[-1]

        atr_val = atr_df['ATR'].iloc[-1]
        sma20_val = sma20_df['SMA'].iloc[-1]
        sma5_val = sma5_df['SMA'].iloc[-1]
        sma60_val = sma60_df['SMA'].iloc[-1]

        # Volume analysis
        vol = data['Volume'].iloc[-1]
        vol_20_avg = data['Volume'].iloc[-20:].mean() if len(data) >= 20 else data['Volume'].mean()
        vol_ratio = vol / vol_20_avg if vol_20_avg > 0 else 1.0

        # Price changes
        close_5d_ago = data['Close'].iloc[-6] if len(data) >= 6 else data['Close'].iloc[0]
        close_10d_ago = data['Close'].iloc[-11] if len(data) >= 11 else data['Close'].iloc[0]
        close_20d_ago = data['Close'].iloc[-21] if len(data) >= 21 else data['Close'].iloc[0]
        pct_5d = ((close - close_5d_ago) / close_5d_ago) * 100
        pct_10d = ((close - close_10d_ago) / close_10d_ago) * 100
        pct_20d = ((close - close_20d_ago) / close_20d_ago) * 100

        # MACD cross state
        if hist > 0 and hist_prev > 0:
            macd_state = '金叉延续'
        elif hist > 0 and hist_prev <= 0:
            macd_state = '金叉形成'
        elif hist < 0 and hist_prev < 0:
            if abs(hist) < abs(hist_prev):
                macd_state = '死叉收窄'
            else:
                macd_state = '死叉加深'
        elif hist < 0 and hist_prev >= 0:
            macd_state = '死叉形成'
        elif hist == 0:
            macd_state = '零轴'
        else:
            macd_state = '金叉延续' if hist > 0 else '死叉'

        # Daily change
        daily_change = ((close - close_prev) / close_prev) * 100

        return {
            'ticker': ticker,
            'name': name,
            'close': round(close, 4),
            'daily_change_pct': round(daily_change, 2),
            'rsi': round(rsi_val, 1),
            'rsi_prev': round(rsi_prev, 1),
            'rsi_trend': 'up' if rsi_val > rsi_prev else ('down' if rsi_val < rsi_prev else 'flat'),
            'macd': round(macd_line, 4),
            'macd_signal': round(signal_line, 4),
            'macd_hist': round(hist, 4),
            'macd_hist_prev': round(hist_prev, 4),
            'macd_state': macd_state,
            'bb_upper': round(bb_upper, 4),
            'bb_middle': round(bb_middle, 4),
            'bb_lower': round(bb_lower, 4),
            'pct_b': round(pct_b, 2),
            'stoch_k': round(stoch_k, 1),
            'stoch_d': round(stoch_d, 1),
            'atr': round(atr_val, 4),
            'sma20': round(sma20_val, 4),
            'sma5': round(sma5_val, 4),
            'sma60': round(sma60_val, 4),
            'volume': int(vol),
            'vol_20_avg': int(vol_20_avg),
            'vol_ratio': round(vol_ratio, 2),
            'pct_5d': round(pct_5d, 2),
            'pct_10d': round(pct_10d, 2),
            'pct_20d': round(pct_20d, 2),
            'vs_sma20': round(((close - sma20_val) / sma20_val) * 100, 2),
            'vs_sma60': round(((close - sma60_val) / sma60_val) * 100, 2),
        }

    except Exception as e:
        return {'ticker': ticker, 'name': name, 'error': str(e), 'traceback': traceback.format_exc()}


def main():
    results = {}

    # Analyze all tickers
    for ticker, name in ALL_TICKERS.items():
        print(f"Analyzing {ticker} ({name})...")
        result = analyze_ticker(ticker, name)
        results[ticker] = result
        if 'error' in result:
            print(f"  ERROR: {result['error']}")
        else:
            print(f"  RSI={result['rsi']} MACD_Hist={result['macd_hist']} %B={result['pct_b']} StochK={result['stoch_k']} VolRatio={result['vol_ratio']}")

    # Fetch realtime quotes
    print("\nFetching realtime quotes...")
    try:
        all_codes = list(ALL_TICKERS.keys())
        realtime = fetch_realtime_quote(all_codes)
        if realtime is not None:
            realtime_data = {}
            for _, row in realtime.iterrows():
                code = str(row.get('代码', '')).replace('sh', '').replace('sz', '')
                realtime_data[code] = {
                    'name': row.get('名称', ''),
                    'price': row.get('最新价', 0),
                    'change': row.get('涨跌额', 0),
                    'change_pct': row.get('涨跌幅', 0),
                    'prev_close': row.get('昨收', 0),
                    'open': row.get('今开', 0),
                    'high': row.get('最高', 0),
                    'low': row.get('最低', 0),
                    'volume': row.get('成交量', 0),
                    'amount': row.get('成交额', 0),
                }
            results['_realtime'] = realtime_data
            print(f"  Got {len(realtime_data)} realtime quotes")
    except Exception as e:
        print(f"  Realtime quote error: {e}")
        results['_realtime'] = {'error': str(e)}

    # Save
    output = make_serializable(results)
    output_path = os.path.join(SCRIPT_DIR, 'portfolio_adjustment_data.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nSaved to {output_path}")
    print("Done!")


if __name__ == '__main__':
    main()
