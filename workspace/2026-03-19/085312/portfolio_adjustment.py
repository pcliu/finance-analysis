#!/usr/bin/env python3
"""
Portfolio Adjustment Technical Analysis — 2026-03-19
Comprehensive technical analysis for all holdings + ETFs.csv watchlist
"""

import sys
import os
import json
import traceback

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../.agent/skills/quantitative-trading'))
sys.path.append(SKILL_DIR)

from scripts import (
    fetch_stock_data, fetch_realtime_quote,
    calculate_rsi, calculate_macd, calculate_bollinger_bands,
    calculate_sma, calculate_atr, calculate_stochastic
)
from scripts.utils import make_serializable

# ========== Portfolio Holdings (from screenshot 3/19 08:49) ==========
HOLDINGS = {
    '510150': {'name': '消费ETF',    'shares': 13000, 'cost': 0.5980, 'market_value': 6890.00, 'pnl': -884.00, 'pnl_pct': -11.37, 'weight': 6.65},
    '510880': {'name': '红利ETF',    'shares': 10000, 'cost': 3.0671, 'market_value': 32960.00, 'pnl': 2289.00, 'pnl_pct': 7.46, 'weight': 31.82},
    '512170': {'name': '医疗ETF',    'shares': 14000, 'cost': 0.3585, 'market_value': 4732.00, 'pnl': -287.00, 'pnl_pct': -5.72, 'weight': 4.57},
    '512660': {'name': '军工ETF',    'shares': 4000,  'cost': 1.6496, 'market_value': 5600.00, 'pnl': -998.40, 'pnl_pct': -15.13, 'weight': 5.41},
    '513180': {'name': '恒指科技',    'shares': 8000,  'cost': 0.6874, 'market_value': 5288.00, 'pnl': -211.20, 'pnl_pct': -3.84, 'weight': 5.11},
    '515050': {'name': '5GETF',      'shares': 3000,  'cost': 2.4202, 'market_value': 7305.00, 'pnl': 44.40, 'pnl_pct': 0.61, 'weight': 7.05},
    '515070': {'name': 'AI智能',     'shares': 400,   'cost': 1.9388, 'market_value': 784.80, 'pnl': 9.28, 'pnl_pct': 1.20, 'weight': 0.76},
    '515790': {'name': '光伏ETF',    'shares': 3000,  'cost': 1.1510, 'market_value': 3360.00, 'pnl': -93.00, 'pnl_pct': -2.69, 'weight': 3.24},
    '588000': {'name': '科创50',     'shares': 1000,  'cost': 0.3019, 'market_value': 1445.00, 'pnl': 1143.10, 'pnl_pct': 378.64, 'weight': 1.40},
    '603993': {'name': '洛阳钼业',    'shares': 300,   'cost': 19.5169, 'market_value': 5823.00, 'pnl': -32.07, 'pnl_pct': -0.55, 'weight': 5.62},
}

# The screenshot shows no daily PnL because it is pre-market. Data is from previous close mostly.
# All ETFs from ETFs.csv + holdings
ALL_ETFS = {
    # Holdings
    '510880': '红利ETF',
    '510150': '消费ETF',
    '515790': '光伏ETF',
    '512660': '军工ETF',
    '513180': '恒生科技指数ETF',
    '588000': '科创50ETF',
    '515050': '5GETF',
    '515070': 'AI智能',
    '512170': '医疗ETF',
    '603993': '洛阳钼业',
    # KPIs non-holdings
    '159985': '豆粕ETF',
    '159689': '粮食ETF',
    '159870': '化工ETF',
    '561330': '矿业ETF',
    '561560': '电力ETF',
    '159326': '电网设备ETF',
    '159830': '上海金ETF',
    '161226': '国投白银LOF',
    '159516': '半导体设备ETF',
    '513630': '港股红利指数ETF',
    '159241': '航空航天ETF天弘', # Previously held, now a watchlist
}

def analyze_single_etf(ticker, name, period='6mo'):
    """Fetch data and compute all technical indicators for one ETF."""
    result = {
        'ticker': ticker,
        'name': name,
        'is_holding': ticker in HOLDINGS,
    }
    
    try:
        # Fetch historical data
        data = fetch_stock_data(ticker, period=period)
        if data is None or data.empty:
            result['error'] = 'No data returned'
            return result
        
        result['data_points'] = len(data)
        result['latest_close'] = float(data['Close'].iloc[-1])
        result['prev_close'] = float(data['Close'].iloc[-2]) if len(data) > 1 else None
        
        # Price changes
        if len(data) >= 2:
            result['daily_change_pct'] = float((data['Close'].iloc[-1] / data['Close'].iloc[-2] - 1) * 100)
        if len(data) >= 6:
            result['5d_change_pct'] = float((data['Close'].iloc[-1] / data['Close'].iloc[-6] - 1) * 100)
        if len(data) >= 21:
            result['20d_change_pct'] = float((data['Close'].iloc[-1] / data['Close'].iloc[-21] - 1) * 100)
        
        # RSI
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
        
        # Determine MACD cross status
        hist = macd_df['Histogram']
        if result['macd_hist'] > 0:
            result['macd_status'] = '金叉'
            if len(hist) >= 2 and hist.iloc[-2] <= 0:
                result['macd_status'] = '新金叉'
            elif len(hist) >= 2 and hist.iloc[-1] > hist.iloc[-2]:
                result['macd_status'] = '金叉加速'
            elif len(hist) >= 2 and hist.iloc[-1] < hist.iloc[-2]:
                result['macd_status'] = '金叉减速'
        else:
            result['macd_status'] = '死叉'
            if len(hist) >= 2 and hist.iloc[-2] >= 0:
                result['macd_status'] = '新死叉'
            elif len(hist) >= 2 and hist.iloc[-1] < hist.iloc[-2]:
                result['macd_status'] = '死叉加深'
            elif len(hist) >= 2 and hist.iloc[-1] > hist.iloc[-2]:
                result['macd_status'] = '死叉收窄'
        
        # Bollinger Bands
        bb_df = calculate_bollinger_bands(data)
        upper = float(bb_df['Upper'].iloc[-1])
        lower = float(bb_df['Lower'].iloc[-1])
        middle = float(bb_df['Middle'].iloc[-1])
        close = float(data['Close'].iloc[-1])
        
        if upper != lower:
            result['bb_pct_b'] = float((close - lower) / (upper - lower))
        else:
            result['bb_pct_b'] = 0.5
        result['bb_upper'] = upper
        result['bb_middle'] = middle
        result['bb_lower'] = lower
        
        # Volume analysis
        if 'Volume' in data.columns:
            vol = data['Volume']
            result['volume_latest'] = float(vol.iloc[-1])
            vol_20ma = vol.rolling(20).mean()
            if len(vol_20ma.dropna()) > 0 and vol_20ma.iloc[-1] > 0:
                result['volume_ratio'] = float(vol.iloc[-1] / vol_20ma.iloc[-1])
            else:
                result['volume_ratio'] = 1.0
        
        # Holding-specific info
        if ticker in HOLDINGS:
            h = HOLDINGS[ticker]
            result['shares'] = h['shares']
            result['cost'] = h['cost']
            result['market_value'] = h['market_value']
            result['pnl'] = h['pnl']
            result['pnl_pct'] = h['pnl_pct']
            result['weight'] = h['weight']
        
    except Exception as e:
        result['error'] = f'{str(e)}\n{traceback.format_exc()}'
    
    return result

def main():
    print("=" * 60)
    print("Portfolio Adjustment Technical Analysis — 2026-03-19")
    print("=" * 60)
    
    all_results = {}
    
    total = len(ALL_ETFS)
    for i, (ticker, name) in enumerate(ALL_ETFS.items(), 1):
        print(f"\n[{i}/{total}] Analyzing {name} ({ticker})...")
        result = analyze_single_etf(ticker, name)
        all_results[ticker] = result
        
        if 'error' in result:
            print(f"  ⚠️ Error: {result['error'][:100]}")
        else:
            status_icon = '🟢' if result.get('macd_hist', 0) > 0 else '🔴'
            print(f"  {status_icon} RSI={result.get('rsi', 'N/A'):.1f} | "
                  f"%B={result.get('bb_pct_b', 'N/A'):.2f} | "
                  f"MACD Hist={result.get('macd_hist', 'N/A'):.4f} ({result.get('macd_status', 'N/A')}) | "
                  f"Vol Ratio={result.get('volume_ratio', 'N/A'):.2f}")
    
    golden_cross = [r for r in all_results.values() if r.get('macd_hist', 0) > 0 and 'error' not in r]
    death_cross = [r for r in all_results.values() if r.get('macd_hist', 0) <= 0 and 'error' not in r]
    
    ACCOUNT = {
        'total_assets': 103572.76,
        'holding_value': 74393.20,
        'holding_pnl': 1092.11,
        'available_cash': 29179.56,
        'date': '2026-03-19 pre-market',
    }
    
    output = {
        'account': make_serializable(ACCOUNT),
        'holdings': make_serializable(HOLDINGS),
        'analysis': make_serializable(all_results),
        'summary': {
            'golden_cross_count': len(golden_cross),
            'death_cross_count': len(death_cross),
            'golden_cross_tickers': [r['ticker'] for r in golden_cross],
            'death_cross_tickers': [r['ticker'] for r in death_cross],
        }
    }
    
    output_path = os.path.join(SCRIPT_DIR, 'portfolio_adjustment_data.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\n✅ Data saved to: {output_path}")

if __name__ == '__main__':
    main()
