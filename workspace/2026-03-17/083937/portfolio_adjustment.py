#!/usr/bin/env python3
"""
Portfolio Adjustment Technical Analysis — 2026-03-17
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

# ========== Portfolio Holdings (from screenshot 3/17 17:51) ==========
HOLDINGS = {
    '510150': {'name': '消费ETF',    'shares': 13000, 'cost': 0.5980, 'market_value': 6877.00, 'pnl': -898.00, 'pnl_pct': -11.54, 'weight': 6.58},
    '510880': {'name': '红利ETF',    'shares': 10000, 'cost': 3.0671, 'market_value': 33350.00, 'pnl': 2677.33, 'pnl_pct': 8.73, 'weight': 31.93},
    '512170': {'name': '医疗ETF',    'shares': 14000, 'cost': 0.3585, 'market_value': 4746.00, 'pnl': -273.50, 'pnl_pct': -5.44, 'weight': 4.54},
    '512660': {'name': '军工ETF',    'shares': 8000,  'cost': 1.5128, 'market_value': 11320.00, 'pnl': -782.57, 'pnl_pct': -6.46, 'weight': 10.84},
    '513180': {'name': '恒指科技',    'shares': 5000,  'cost': 0.7001, 'market_value': 3325.00, 'pnl': -176.00, 'pnl_pct': -5.01, 'weight': 3.18},
    '515050': {'name': '5GETF',      'shares': 3000,  'cost': 2.4202, 'market_value': 7317.00, 'pnl': 56.00, 'pnl_pct': 0.78, 'weight': 7.01},
    '515070': {'name': 'AI智能',     'shares': 400,   'cost': 1.9388, 'market_value': 778.80, 'pnl': 2.80, 'pnl_pct': 0.42, 'weight': 0.75},
    '515790': {'name': '光伏ETF',    'shares': 3000,  'cost': 1.1510, 'market_value': 3405.00, 'pnl': -48.50, 'pnl_pct': -1.39, 'weight': 3.26},
    '588000': {'name': '科创50',     'shares': 1000,  'cost': 0.3019, 'market_value': 1458.00, 'pnl': 1155.60, 'pnl_pct': 382.94, 'weight': 1.40},
    '159241': {'name': '航空TH',     'shares': 4000,  'cost': 1.6151, 'market_value': 5604.00, 'pnl': -857.00, 'pnl_pct': -13.26, 'weight': 5.37},
    '159770': {'name': '机器人AI',   'shares': 200,   'cost': 0.7670, 'market_value': 207.80, 'pnl': 53.90, 'pnl_pct': 35.46, 'weight': 0.20},
}

# Today's intraday data from screenshot (3/17)
TODAY_DATA = {
    '510150': {'latest': 0.5290, 'daily_pnl': 52.00, 'daily_pct': 0.76},
    '510880': {'latest': 3.3350, 'daily_pnl': -290.00, 'daily_pct': -0.86},
    '512170': {'latest': 0.3390, 'daily_pnl': 14.00, 'daily_pct': 0.30},
    '512660': {'latest': 1.4150, 'daily_pnl': 8.00, 'daily_pct': 0.07},
    '513180': {'latest': 0.6650, 'daily_pnl': 95.00, 'daily_pct': 2.94},
    '515050': {'latest': 2.4390, 'daily_pnl': 108.00, 'daily_pct': 1.50},
    '515070': {'latest': 1.9470, 'daily_pnl': 5.60, 'daily_pct': 0.72},
    '515790': {'latest': 1.1350, 'daily_pnl': -87.00, 'daily_pct': -2.49},
    '588000': {'latest': 1.4580, 'daily_pnl': 8.00, 'daily_pct': 0.55},
    '159241': {'latest': 1.4010, 'daily_pnl': -16.00, 'daily_pct': -0.28},
    '159770': {'latest': 1.0390, 'daily_pnl': -0.20, 'daily_pct': -0.10},
}

# All ETFs from ETFs.csv + extra watchlist items
ALL_ETFS = {
    # Holdings
    '510880': '红利ETF',
    '510150': '消费ETF',
    '515790': '光伏ETF',
    '512660': '军工ETF',
    '159241': '航空航天ETF天弘',
    '513180': '恒生科技指数ETF',
    '588000': '科创50ETF',
    '515050': '5GETF',
    '515070': 'AI智能',
    '159770': '机器人AI',
    '512170': '医疗ETF',
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
}

# Account summary from screenshot
ACCOUNT = {
    'total_assets': 104437.28,
    'holding_value': 78388.60,
    'holding_pnl': 983.51,
    'available_cash': 104437.28 - 78388.60,  # ~26048.68
    'daily_pnl': -102.60,
    'date': '2026-03-17',
}


def analyze_single_etf(ticker, name, period='9mo'):
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
        
        # SMA 20, 60
        sma20 = calculate_sma(data, window=20)
        result['sma20'] = float(sma20['SMA'].iloc[-1])
        sma60 = calculate_sma(data, window=60)
        if len(sma60['SMA'].dropna()) > 0:
            result['sma60'] = float(sma60['SMA'].iloc[-1])
        
        # ATR
        atr_df = calculate_atr(data, window=14)
        result['atr'] = float(atr_df['ATR'].iloc[-1])
        
        # Stochastic
        stoch_df = calculate_stochastic(data)
        result['stoch_k'] = float(stoch_df['K'].iloc[-1])
        result['stoch_d'] = float(stoch_df['D'].iloc[-1])
        
        # Add holding-specific info
        if ticker in HOLDINGS:
            h = HOLDINGS[ticker]
            result['shares'] = h['shares']
            result['cost'] = h['cost']
            result['market_value'] = h['market_value']
            result['pnl'] = h['pnl']
            result['pnl_pct'] = h['pnl_pct']
            result['weight'] = h['weight']
        
        if ticker in TODAY_DATA:
            result['today_pnl'] = TODAY_DATA[ticker]['daily_pnl']
            result['today_pct'] = TODAY_DATA[ticker]['daily_pct']
        
    except Exception as e:
        result['error'] = f'{str(e)}\n{traceback.format_exc()}'
    
    return result


def main():
    print("=" * 60)
    print("Portfolio Adjustment Technical Analysis — 2026-03-17")
    print("=" * 60)
    
    all_results = {}
    
    # Analyze all ETFs
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
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    golden_cross = [r for r in all_results.values() if r.get('macd_hist', 0) > 0 and 'error' not in r]
    death_cross = [r for r in all_results.values() if r.get('macd_hist', 0) <= 0 and 'error' not in r]
    
    print(f"\n金叉品种 ({len(golden_cross)}):")
    for r in sorted(golden_cross, key=lambda x: x.get('macd_hist', 0), reverse=True):
        print(f"  {r['name']:12s} RSI={r.get('rsi', 0):.1f} %B={r.get('bb_pct_b', 0):.2f} Hist={r.get('macd_hist', 0):.4f} [{r.get('macd_status', '')}]")
    
    print(f"\n死叉品种 ({len(death_cross)}):")
    for r in sorted(death_cross, key=lambda x: x.get('macd_hist', 0)):
        print(f"  {r['name']:12s} RSI={r.get('rsi', 0):.1f} %B={r.get('bb_pct_b', 0):.2f} Hist={r.get('macd_hist', 0):.4f} [{r.get('macd_status', '')}]")
    
    # Account info
    output = {
        'account': make_serializable(ACCOUNT),
        'holdings': make_serializable(HOLDINGS),
        'analysis': make_serializable(all_results),
        'today_data': make_serializable(TODAY_DATA),
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
