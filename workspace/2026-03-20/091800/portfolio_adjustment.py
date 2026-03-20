#!/usr/bin/env python3
"""
Portfolio Adjustment Technical Analysis — 2026-03-20
Comprehensive technical analysis for all holdings + ETFs.csv watchlist
Data as of 2026-03-19 close
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

# ========== Portfolio Holdings (from screenshot 2026-03-20 16:58) ==========
HOLDINGS = {
    '510150': {'name': '消费ETF',    'shares': 13000, 'cost': 0.5980, 'market_value': 6773.00, 'pnl': -1002.00, 'pnl_pct': -12.88, 'weight': 6.60, 'daily_pnl': -117.00, 'daily_pnl_pct': -1.70},
    '510880': {'name': '红利ETF',    'shares': 10000, 'cost': 3.0671, 'market_value': 33050.00, 'pnl': 2377.35, 'pnl_pct': 7.76, 'weight': 32.22, 'daily_pnl': 90.00, 'daily_pnl_pct': 0.27},
    '512170': {'name': '医疗ETF',    'shares': 14000, 'cost': 0.3585, 'market_value': 4648.00, 'pnl': -371.50, 'pnl_pct': -7.39, 'weight': 4.53, 'daily_pnl': -84.00, 'daily_pnl_pct': -1.78},
    '512660': {'name': '军工ETF',    'shares': 4000,  'cost': 1.6496, 'market_value': 5452.00, 'pnl': -1147.00, 'pnl_pct': -17.37, 'weight': 5.32, 'daily_pnl': -148.00, 'daily_pnl_pct': -2.64},
    '513180': {'name': '恒指科技',    'shares': 8000,  'cost': 0.6874, 'market_value': 5184.00, 'pnl': -315.50, 'pnl_pct': -5.73, 'weight': 5.05, 'daily_pnl': -104.00, 'daily_pnl_pct': -1.97},
    '515050': {'name': '5GETF',      'shares': 3000,  'cost': 2.4202, 'market_value': 7230.00, 'pnl': -31.00, 'pnl_pct': -0.42, 'weight': 7.05, 'daily_pnl': -75.00, 'daily_pnl_pct': -1.03},
    '515070': {'name': 'AI智能',     'shares': 400,   'cost': 1.9388, 'market_value': 776.40, 'pnl': 0.40, 'pnl_pct': 0.11, 'weight': 0.76, 'daily_pnl': -8.40, 'daily_pnl_pct': -1.07},
    '515790': {'name': '光伏ETF',    'shares': 3000,  'cost': 1.1510, 'market_value': 3315.00, 'pnl': -138.50, 'pnl_pct': -4.00, 'weight': 3.23, 'daily_pnl': -45.00, 'daily_pnl_pct': -1.34},
    '588000': {'name': '科创50',     'shares': 1000,  'cost': 0.3019, 'market_value': 1411.00, 'pnl': 1108.60, 'pnl_pct': 367.37, 'weight': 1.38, 'daily_pnl': -34.00, 'daily_pnl_pct': -2.35},
    '603993': {'name': '洛阳钼业',    'shares': 300,   'cost': 19.5169, 'market_value': 5355.00, 'pnl': -508.29, 'pnl_pct': -8.54, 'weight': 5.22, 'daily_pnl': -468.00, 'daily_pnl_pct': -8.04},
}

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
    # Watchlist (non-holdings from ETFs.csv)
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
        if len(macd_df) >= 3:
            result['macd_hist_prev2'] = float(macd_df['Histogram'].iloc[-3])
        
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
        
        # Previous day %B
        if len(data) >= 2 and len(bb_df) >= 2:
            upper_prev = float(bb_df['Upper'].iloc[-2])
            lower_prev = float(bb_df['Lower'].iloc[-2])
            close_prev = float(data['Close'].iloc[-2])
            if upper_prev != lower_prev:
                result['bb_pct_b_prev'] = float((close_prev - lower_prev) / (upper_prev - lower_prev))
        
        # SMA 20/60
        sma20 = calculate_sma(data, window=20)
        result['sma20'] = float(sma20['SMA'].iloc[-1])
        if len(data) >= 60:
            sma60 = calculate_sma(data, window=60)
            result['sma60'] = float(sma60['SMA'].iloc[-1])
        
        # ATR
        atr_df = calculate_atr(data, window=14)
        result['atr'] = float(atr_df['ATR'].iloc[-1])
        
        # Stochastic
        stoch_df = calculate_stochastic(data)
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
            result['pnl'] = h['pnl']
            result['pnl_pct'] = h['pnl_pct']
            result['weight'] = h['weight']
            result['daily_pnl'] = h['daily_pnl']
            result['daily_pnl_pct'] = h['daily_pnl_pct']
        
    except Exception as e:
        result['error'] = f'{str(e)}\n{traceback.format_exc()}'
    
    return result

def main():
    print("=" * 60)
    print("Portfolio Adjustment Technical Analysis — 2026-03-20")
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
        'total_assets': 102574.36,
        'holding_value': 73394.80,
        'holding_pnl': 93.95,
        'available_cash': 179.56,
        'effective_available': 102574.36 - 73394.80,  # ~29,179.56 (money market fund redeemable)
        'daily_pnl': -998.40,
        'date': '2026-03-20 pre-market (data from 2026-03-19 close)',
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
