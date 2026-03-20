#!/usr/bin/env python3
"""
Portfolio Adjustment Technical Analysis — 2026-03-18
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

# ========== Portfolio Holdings (from screenshot 3/17 17:25-17:26 收盘) ==========
# Note: 恒指科技 executed 3/17 buy 3000 shares → now 8000 shares
# Note: 洛阳钼业 603993 NEW position — bought 300 shares @ 19.50 on 3/17
HOLDINGS = {
    '510150': {'name': '消费ETF',    'shares': 13000, 'cost': 0.5980, 'market_value': 6890.00, 'pnl': -885.00, 'pnl_pct': -11.37, 'weight': 6.67},
    '510880': {'name': '红利ETF',    'shares': 10000, 'cost': 3.0671, 'market_value': 33090.00, 'pnl': 2417.35, 'pnl_pct': 7.89, 'weight': 32.04},
    '512170': {'name': '医疗ETF',    'shares': 14000, 'cost': 0.3585, 'market_value': 4746.00, 'pnl': -273.50, 'pnl_pct': -5.44, 'weight': 4.60},
    '512660': {'name': '军工ETF',    'shares': 8000,  'cost': 1.5128, 'market_value': 11008.00, 'pnl': -1094.55, 'pnl_pct': -9.04, 'weight': 10.66},
    '513180': {'name': '恒指科技',    'shares': 8000,  'cost': 0.6874, 'market_value': 5296.00, 'pnl': -203.50, 'pnl_pct': -3.70, 'weight': 5.13},
    '515050': {'name': '5GETF',      'shares': 3000,  'cost': 2.4202, 'market_value': 7017.00, 'pnl': -244.00, 'pnl_pct': -3.36, 'weight': 6.79},
    '515070': {'name': 'AI智能',     'shares': 400,   'cost': 1.9388, 'market_value': 759.20, 'pnl': -16.80, 'pnl_pct': -2.10, 'weight': 0.74},
    '515790': {'name': '光伏ETF',    'shares': 3000,  'cost': 1.1510, 'market_value': 3345.00, 'pnl': -108.50, 'pnl_pct': -3.13, 'weight': 3.24},
    '588000': {'name': '科创50',     'shares': 1000,  'cost': 0.3019, 'market_value': 1428.60, 'pnl': 1125.60, 'pnl_pct': 373.00, 'weight': 1.38},
    '603993': {'name': '洛阳钼业',    'shares': 300,   'cost': 19.5185, 'market_value': 5826.00, 'pnl': -29.56, 'pnl_pct': -0.50, 'weight': 5.64},
    '159241': {'name': '航空TH',     'shares': 4000,  'cost': 1.6151, 'market_value': 5464.00, 'pnl': -997.00, 'pnl_pct': -15.42, 'weight': 5.29},
}

# Today's closing data from screenshots (3/17 17:25-17:26)
TODAY_DATA = {
    '510150': {'latest': 0.5300, 'daily_pnl': 13.00, 'daily_pct': 0.19},
    '510880': {'latest': 3.3090, 'daily_pnl': -260.00, 'daily_pct': -0.78},
    '512170': {'latest': 0.3390, 'daily_pnl': 0.00, 'daily_pct': 0.00},
    '512660': {'latest': 1.3760, 'daily_pnl': -312.00, 'daily_pct': -2.76},
    '513180': {'latest': 0.6620, 'daily_pnl': -27.50, 'daily_pct': -0.52},
    '515050': {'latest': 2.3390, 'daily_pnl': -300.00, 'daily_pct': -4.10},
    '515070': {'latest': 1.8980, 'daily_pnl': -19.60, 'daily_pct': -2.52},
    '515790': {'latest': 1.1150, 'daily_pnl': -60.00, 'daily_pct': -1.76},
    '588000': {'latest': 1.4280, 'daily_pnl': -30.00, 'daily_pct': -2.06},
    '603993': {'latest': 19.4200, 'daily_pnl': -38.03, 'daily_pct': -0.50},
    '159241': {'latest': 1.3660, 'daily_pnl': -140.00, 'daily_pct': -2.50},
}

# All ETFs from ETFs.csv + holdings (including 603993 new)
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
    '512170': '医疗ETF',
    '603993': '洛阳钼业',
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
    print("Portfolio Adjustment Technical Analysis — 2026-03-18")
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
    ACCOUNT = {
        'total_assets': 103268.53,
        'holding_value': 85073.40,
        'holding_pnl': -193.67,
        'available_cash': 103268.53 - 85073.40,  # ~18195.13
        'daily_pnl': -1169.26,
        'date': '2026-03-17 close',
    }
    
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
