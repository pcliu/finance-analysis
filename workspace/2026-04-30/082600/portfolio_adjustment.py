#!/usr/bin/env python3
"""
Portfolio Adjustment Technical Analysis — 2026-04-30
Covers all current holdings + ETFs.csv watchlist candidates.
"""

import sys
import os
import json
import warnings
warnings.filterwarnings('ignore')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../.agent/skills/quantitative-trading'))
sys.path.append(SKILL_DIR)

from scripts import (
    fetch_stock_data, calculate_rsi, calculate_macd,
    calculate_bollinger_bands, calculate_stochastic, calculate_atr
)
from scripts.utils import make_serializable

# ── Current Holdings (11 positions after selling 恒指科技 513180) ──
HOLDINGS = {
    '510880': {'name': '红利ETF',    'shares': 10000, 'cost': 3.0671, 'market_value': 33470.00, 'pnl': 2797.33, 'pnl_pct': 9.13},
    '512170': {'name': '医疗ETF',    'shares': 16000, 'cost': 0.3562, 'market_value': 5408.00,  'pnl': -292.00, 'pnl_pct': -5.11},
    '512660': {'name': '军工ETF',    'shares': 4000,  'cost': 1.6496, 'market_value': 5508.00,  'pnl': -1091.00, 'pnl_pct': -16.53},
    '515050': {'name': '5GETF',      'shares': 2000,  'cost': 2.1545, 'market_value': 5944.00,  'pnl': 1634.50, 'pnl_pct': 37.94},
    '515070': {'name': 'AI智能',     'shares': 400,   'cost': 1.9388, 'market_value': 882.40,   'pnl': 106.40, 'pnl_pct': 13.78},
    '515790': {'name': '光伏ETF',    'shares': 3000,  'cost': 1.1510, 'market_value': 3177.00,  'pnl': -276.50, 'pnl_pct': -7.99},
    '561560': {'name': '电力ETF',    'shares': 2000,  'cost': 1.3623, 'market_value': 2728.00,  'pnl': 3.00,   'pnl_pct': 0.12},
    '588000': {'name': '科创50',     'shares': 1000,  'cost': 0.3019, 'market_value': 1575.00,  'pnl': 1272.60, 'pnl_pct': 421.70},
    '159516': {'name': '半导体设备', 'shares': 5000,  'cost': 0.9921, 'market_value': 4870.00,  'pnl': -91.00, 'pnl_pct': -1.82},
    '159770': {'name': '机器人AI',   'shares': 200,   'cost': 0.7670, 'market_value': 211.20,   'pnl': 57.30,  'pnl_pct': 37.68},
    '159870': {'name': '化工ETF',    'shares': 7000,  'cost': 0.9071, 'market_value': 6692.00,  'pnl': 342.00, 'pnl_pct': 5.39},
}

# ── ETFs.csv watchlist (excluding those already held) ──
WATCHLIST = {
    '510150': {'name': '消费ETF'},
    '159985': {'name': '豆粕ETF'},
    '159689': {'name': '粮食ETF'},
    '561330': {'name': '矿业ETF'},
    '159326': {'name': '电网设备ETF'},
    '560280': {'name': '工程机械ETF'},
    '159241': {'name': '航空航天ETF'},
    '159830': {'name': '上海金ETF'},
    '161226': {'name': '国投白银LOF'},
    '513180': {'name': '恒指科技ETF'},  # just sold, still on watchlist
    '513630': {'name': '港股红利ETF'},
}

def analyze_ticker(code, name, period='8mo'):
    """Fetch data and compute all key technical indicators."""
    try:
        data = fetch_stock_data(code, period=period)
        if data is None or data.empty or len(data) < 30:
            return {'code': code, 'name': name, 'error': 'Insufficient data'}
        
        # Core indicators
        rsi_df = calculate_rsi(data, window=14)
        macd_df = calculate_macd(data)
        bb_df = calculate_bollinger_bands(data)
        stoch_df = calculate_stochastic(data)
        atr_df = calculate_atr(data, window=14)
        
        # Volume ratio (current vs 20-day avg)
        vol_20 = data['Volume'].rolling(20).mean()
        vol_ratio = data['Volume'].iloc[-1] / vol_20.iloc[-1] if vol_20.iloc[-1] > 0 else 1.0
        
        # Price changes
        close = data['Close']
        price_now = close.iloc[-1]
        price_1d = close.iloc[-2] if len(close) >= 2 else price_now
        price_5d = close.iloc[-6] if len(close) >= 6 else price_now
        price_20d = close.iloc[-21] if len(close) >= 21 else price_now
        
        # SMA
        sma5 = close.rolling(5).mean().iloc[-1]
        sma10 = close.rolling(10).mean().iloc[-1]
        sma20 = close.rolling(20).mean().iloc[-1]
        sma60 = close.rolling(60).mean().iloc[-1] if len(close) >= 60 else None
        
        # Bollinger %B
        upper = bb_df['Upper'].iloc[-1]
        lower = bb_df['Lower'].iloc[-1]
        pct_b = (price_now - lower) / (upper - lower) if (upper - lower) > 0 else 0.5
        
        result = {
            'code': code,
            'name': name,
            'price': float(price_now),
            'change_1d_pct': float((price_now - price_1d) / price_1d * 100),
            'change_5d_pct': float((price_now - price_5d) / price_5d * 100),
            'change_20d_pct': float((price_now - price_20d) / price_20d * 100),
            'rsi': float(rsi_df['RSI'].iloc[-1]),
            'macd': float(macd_df['MACD'].iloc[-1]),
            'macd_signal': float(macd_df['Signal'].iloc[-1]),
            'macd_hist': float(macd_df['Histogram'].iloc[-1]),
            'bb_upper': float(upper),
            'bb_lower': float(lower),
            'bb_middle': float(bb_df['Middle'].iloc[-1]),
            'bb_pct_b': float(pct_b),
            'stoch_k': float(stoch_df['K'].iloc[-1]),
            'stoch_d': float(stoch_df['D'].iloc[-1]),
            'atr': float(atr_df['ATR'].iloc[-1]),
            'volume_ratio': float(vol_ratio),
            'sma5': float(sma5),
            'sma10': float(sma10),
            'sma20': float(sma20),
            'sma60': float(sma60) if sma60 is not None else None,
        }
        return result
    except Exception as e:
        return {'code': code, 'name': name, 'error': str(e)}


def main():
    all_results = {'holdings': {}, 'watchlist': {}, 'account': {}}
    
    # Account summary from screenshots
    all_results['account'] = {
        'total_assets': 104966.23,
        'market_value': 70465.60,
        'available_cash': 34500.63,
        'position_pnl': 4567.20,
        'today_pnl': 519.00,
        'position_ratio': 67.13,
        'date': '2026-04-29',
        'note': '4/29 sold 恒指科技 513180 4000 shares @ 0.6280 = 2512.00'
    }
    
    print("=" * 60)
    print("持仓分析 — Holdings Analysis")
    print("=" * 60)
    
    for code, info in HOLDINGS.items():
        print(f"\n📊 分析 {info['name']} ({code})...")
        result = analyze_ticker(code, info['name'])
        if 'error' not in result:
            result['shares'] = info['shares']
            result['cost'] = info['cost']
            result['market_value'] = info['market_value']
            result['pnl'] = info['pnl']
            result['pnl_pct'] = info['pnl_pct']
            print(f"   RSI={result['rsi']:.1f}  %B={result['bb_pct_b']:.2f}  "
                  f"Hist={result['macd_hist']:.4f}  StochK={result['stoch_k']:.1f}  "
                  f"VolR={result['volume_ratio']:.2f}")
        else:
            print(f"   ❌ Error: {result['error']}")
        all_results['holdings'][code] = result
    
    print("\n" + "=" * 60)
    print("观察标的分析 — Watchlist Analysis")
    print("=" * 60)
    
    for code, info in WATCHLIST.items():
        print(f"\n📊 分析 {info['name']} ({code})...")
        result = analyze_ticker(code, info['name'])
        if 'error' not in result:
            print(f"   RSI={result['rsi']:.1f}  %B={result['bb_pct_b']:.2f}  "
                  f"Hist={result['macd_hist']:.4f}  StochK={result['stoch_k']:.1f}  "
                  f"VolR={result['volume_ratio']:.2f}")
        else:
            print(f"   ❌ Error: {result['error']}")
        all_results['watchlist'][code] = result
    
    # Save results
    output_path = os.path.join(SCRIPT_DIR, 'portfolio_adjustment_data.json')
    clean_results = make_serializable(all_results)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(clean_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 数据已保存至: {output_path}")


if __name__ == '__main__':
    main()
