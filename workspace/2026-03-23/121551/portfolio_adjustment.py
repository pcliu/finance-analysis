#!/usr/bin/env python3
"""
Portfolio Adjustment Technical Analysis — 2026-03-23 (午盘后)
Comprehensive technical analysis for all holdings + ETFs.csv watchlist
Data as of 2026-03-23 morning close (screenshot at 12:12)
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

# ========== Portfolio Holdings (from screenshot 2026-03-23 12:12) ==========
HOLDINGS = {
    '510150': {'name': '消费ETF',    'shares': 13000, 'cost': 0.5980, 'latest': 0.5020, 'market_value': 6526.00, 'daily_pnl': -182.00, 'daily_pnl_pct': -2.71, 'total_pnl': -1249.00, 'total_pnl_pct': -16.05, 'weight': 6.48},
    '510880': {'name': '红利ETF',    'shares': 10000, 'cost': 3.0671, 'latest': 3.2700, 'market_value': 32700.00, 'daily_pnl': -260.00, 'daily_pnl_pct': -0.79, 'total_pnl': 2027.36, 'total_pnl_pct': 6.62, 'weight': 32.49},
    '512170': {'name': '医疗ETF',    'shares': 14000, 'cost': 0.3585, 'latest': 0.3170, 'market_value': 4438.00, 'daily_pnl': -126.00, 'daily_pnl_pct': -2.76, 'total_pnl': -581.50, 'total_pnl_pct': -11.58, 'weight': 4.41},
    '512660': {'name': '军工ETF',    'shares': 4000,  'cost': 1.6496, 'latest': 1.2870, 'market_value': 5148.00, 'daily_pnl': -152.00, 'daily_pnl_pct': -2.87, 'total_pnl': -1451.00, 'total_pnl_pct': -21.98, 'weight': 5.11},
    '513180': {'name': '恒指科技',    'shares': 8000,  'cost': 0.6874, 'latest': 0.6140, 'market_value': 4912.00, 'daily_pnl': -128.00, 'daily_pnl_pct': -2.54, 'total_pnl': -587.50, 'total_pnl_pct': -10.68, 'weight': 4.88},
    '515050': {'name': '5GETF',      'shares': 3000,  'cost': 2.4202, 'latest': 2.3370, 'market_value': 7011.00, 'daily_pnl': -315.00, 'daily_pnl_pct': -4.30, 'total_pnl': -250.00, 'total_pnl_pct': -3.44, 'weight': 6.97},
    '515070': {'name': 'AI智能',     'shares': 400,   'cost': 1.9388, 'latest': 1.8670, 'market_value': 746.80, 'daily_pnl': -24.40, 'daily_pnl_pct': -3.16, 'total_pnl': -29.20, 'total_pnl_pct': -3.70, 'weight': 0.74},
    '515790': {'name': '光伏ETF',    'shares': 3000,  'cost': 1.1510, 'latest': 1.1370, 'market_value': 3411.00, 'daily_pnl': -3.00, 'daily_pnl_pct': -0.09, 'total_pnl': -42.50, 'total_pnl_pct': -1.22, 'weight': 3.39},
    '588000': {'name': '科创50',     'shares': 1000,  'cost': 0.3019, 'latest': 1.3490, 'market_value': 1349.00, 'daily_pnl': -39.00, 'daily_pnl_pct': -2.81, 'total_pnl': 1046.60, 'total_pnl_pct': 346.84, 'weight': 1.34},
    '603993': {'name': '洛阳钼业',    'shares': 300,   'cost': 19.5169, 'latest': 16.8000, 'market_value': 5040.00, 'daily_pnl': -225.00, 'daily_pnl_pct': -4.27, 'total_pnl': -823.13, 'total_pnl_pct': -13.92, 'weight': 5.01},
    '159770': {'name': '机器人AI',    'shares': 200,   'cost': 0.7670, 'latest': 0.9550, 'market_value': 191.00, 'daily_pnl': -5.40, 'daily_pnl_pct': -2.75, 'total_pnl': 37.10, 'total_pnl_pct': 24.51, 'weight': 0.19},
}

# All ETFs from ETFs.csv + holdings + extra positions
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
    '159770': '机器人AI',
    # ETFs.csv watchlist (non-holdings)
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
    '159241': '航空航天ETF天弘',
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
        
        # SMA 5, 10, 20, 60
        for w in [5, 10, 20, 60]:
            sma_df = calculate_sma(data, window=w)
            if len(sma_df.dropna()) > 0:
                result[f'sma_{w}'] = float(sma_df['SMA'].iloc[-1])
        
        # ATR
        atr_df = calculate_atr(data, window=14)
        if len(atr_df.dropna()) > 0:
            result['atr'] = float(atr_df['ATR'].iloc[-1])
        
        # Stochastic
        stoch_df = calculate_stochastic(data)
        if len(stoch_df.dropna()) > 0:
            result['stoch_k'] = float(stoch_df['K'].iloc[-1])
            result['stoch_d'] = float(stoch_df['D'].iloc[-1])
        
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
            result['total_pnl'] = h['total_pnl']
            result['total_pnl_pct'] = h['total_pnl_pct']
            result['daily_pnl'] = h['daily_pnl']
            result['daily_pnl_pct'] = h['daily_pnl_pct']
            result['weight'] = h['weight']
        
    except Exception as e:
        result['error'] = f'{str(e)}\n{traceback.format_exc()}'
    
    return result

def main():
    print("=" * 60)
    print("Portfolio Adjustment Technical Analysis — 2026-03-23 (午盘后)")
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
        'total_assets': 100654.57,
        'holding_value': 71472.80,
        'holding_pnl': -1825.67,
        'available_cash': 29181.77,
        'daily_pnl': -1459.80,
        'date': '2026-03-23 12:12 (午盘)',
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
