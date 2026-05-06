#!/usr/bin/env python3
"""
A股组合技术分析 — 2026-05-06
持仓11只 + ETFs.csv观察池11只
"""

import sys
import os
import json
import warnings
warnings.filterwarnings('ignore')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../../.claude/skills/quantitative-trading'))
sys.path.append(SKILL_DIR)

from scripts import (
    fetch_stock_data, calculate_rsi, calculate_macd,
    calculate_bollinger_bands, calculate_stochastic, calculate_atr
)
from scripts.utils import make_serializable

# ── 当前持仓（截图读取 2026-05-06）──
HOLDINGS = {
    '510880': {'name': '红利ETF',    'shares': 10000, 'cost': 3.0671, 'market_value': 33410.00, 'pnl': 2737.33, 'pnl_pct': 8.93,  'today_pnl': 0.00},
    '512170': {'name': '医疗ETF',    'shares': 16000, 'cost': 0.3562, 'market_value': 5360.00,  'pnl': -340.00, 'pnl_pct': -5.95, 'today_pnl': -16.00},
    '512660': {'name': '军工ETF',    'shares': 4000,  'cost': 1.6496, 'market_value': 5720.00,  'pnl': -879.00, 'pnl_pct': -13.31,'today_pnl': 124.00},
    '515050': {'name': '5GETF',      'shares': 2000,  'cost': 2.1545, 'market_value': 6072.00,  'pnl': 1762.50, 'pnl_pct': 40.91, 'today_pnl': 138.00},
    '515070': {'name': 'AI智能',     'shares': 400,   'cost': 1.9388, 'market_value': 938.80,   'pnl': 162.80,  'pnl_pct': 21.05, 'today_pnl': 32.40},
    '515790': {'name': '光伏ETF',    'shares': 3000,  'cost': 1.1510, 'market_value': 3258.00,  'pnl': -195.50, 'pnl_pct': -5.65, 'today_pnl': 69.00},
    '561560': {'name': '电力ETF',    'shares': 2000,  'cost': 1.3623, 'market_value': 2748.00,  'pnl': 23.00,   'pnl_pct': 0.86,  'today_pnl': 56.00},
    '588000': {'name': '科创50',     'shares': 1000,  'cost': 0.3019, 'market_value': 1744.00,  'pnl': 1441.60, 'pnl_pct': 477.67,'today_pnl': 90.00},
    '159516': {'name': '半导体设备', 'shares': 8000,  'cost': 0.9910, 'market_value': 8208.00,  'pnl': 279.50,  'pnl_pct': 3.53,  'today_pnl': 168.00},
    '159770': {'name': '机器人AI',   'shares': 200,   'cost': 0.7670, 'market_value': 218.40,   'pnl': 64.50,   'pnl_pct': 42.37, 'today_pnl': 4.60},
    '159870': {'name': '化工ETF',    'shares': 7000,  'cost': 0.9071, 'market_value': 6776.00,  'pnl': 426.00,  'pnl_pct': 6.71,  'today_pnl': 91.00},
}

# ── ETFs.csv 观察池（未持仓品种）──
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
    '513180': {'name': '恒指科技ETF'},
    '513630': {'name': '港股红利ETF'},
}

def analyze_ticker(code, name, period='8mo'):
    try:
        data = fetch_stock_data(code, period=period)
        if data is None or data.empty or len(data) < 30:
            return {'code': code, 'name': name, 'error': 'Insufficient data'}

        rsi_df    = calculate_rsi(data, window=14)
        macd_df   = calculate_macd(data)
        bb_df     = calculate_bollinger_bands(data)
        stoch_df  = calculate_stochastic(data)
        atr_df    = calculate_atr(data, window=14)

        vol_20    = data['Volume'].rolling(20).mean()
        vol_ratio = data['Volume'].iloc[-1] / vol_20.iloc[-1] if vol_20.iloc[-1] > 0 else 1.0

        close     = data['Close']
        price_now = close.iloc[-1]
        price_1d  = close.iloc[-2] if len(close) >= 2  else price_now
        price_5d  = close.iloc[-6] if len(close) >= 6  else price_now
        price_20d = close.iloc[-21] if len(close) >= 21 else price_now

        sma5  = close.rolling(5).mean().iloc[-1]
        sma10 = close.rolling(10).mean().iloc[-1]
        sma20 = close.rolling(20).mean().iloc[-1]
        sma60 = close.rolling(60).mean().iloc[-1] if len(close) >= 60 else None

        upper = bb_df['Upper'].iloc[-1]
        lower = bb_df['Lower'].iloc[-1]
        pct_b = (price_now - lower) / (upper - lower) if (upper - lower) > 0 else 0.5

        return {
            'code': code, 'name': name,
            'price': float(price_now),
            'change_1d_pct':  float((price_now - price_1d)  / price_1d  * 100),
            'change_5d_pct':  float((price_now - price_5d)  / price_5d  * 100),
            'change_20d_pct': float((price_now - price_20d) / price_20d * 100),
            'rsi':        float(rsi_df['RSI'].iloc[-1]),
            'macd':       float(macd_df['MACD'].iloc[-1]),
            'macd_signal':float(macd_df['Signal'].iloc[-1]),
            'macd_hist':  float(macd_df['Histogram'].iloc[-1]),
            'bb_upper':   float(upper),
            'bb_lower':   float(lower),
            'bb_middle':  float(bb_df['Middle'].iloc[-1]),
            'bb_pct_b':   float(pct_b),
            'stoch_k':    float(stoch_df['K'].iloc[-1]),
            'stoch_d':    float(stoch_df['D'].iloc[-1]),
            'atr':        float(atr_df['ATR'].iloc[-1]),
            'volume_ratio': float(vol_ratio),
            'sma5': float(sma5), 'sma10': float(sma10),
            'sma20': float(sma20),
            'sma60': float(sma60) if sma60 is not None else None,
        }
    except Exception as e:
        return {'code': code, 'name': name, 'error': str(e)}


def main():
    all_results = {
        'holdings': {}, 'watchlist': {},
        'account': {
            'total_assets':    105987.10,
            'market_value':    74453.20,
            'available_cash':  31533.90,   # 总资产 - 持仓市值（含货基）
            'position_pnl':    5588.07,
            'today_pnl':       757.00,
            'position_ratio':  70.25,
            'date': '2026-05-06',
            'note': '五一假期后首个交易日（假期4/30-5/5）。半导体设备持仓从5000增至8000股（+3000股）。'
        }
    }

    print("=" * 60)
    print("持仓技术分析 — Holdings")
    print("=" * 60)
    for code, info in HOLDINGS.items():
        print(f"\n📊 {info['name']} ({code})...")
        result = analyze_ticker(code, info['name'])
        if 'error' not in result:
            result.update({k: info[k] for k in ('shares', 'cost', 'market_value', 'pnl', 'pnl_pct', 'today_pnl')})
            print(f"   RSI={result['rsi']:.1f}  %B={result['bb_pct_b']:.2f}  "
                  f"Hist={result['macd_hist']:.4f}  StochK={result['stoch_k']:.1f}  "
                  f"VolR={result['volume_ratio']:.2f}  5d%={result['change_5d_pct']:.2f}")
        else:
            print(f"   ❌ {result['error']}")
        all_results['holdings'][code] = result

    print("\n" + "=" * 60)
    print("观察池分析 — Watchlist")
    print("=" * 60)
    for code, info in WATCHLIST.items():
        print(f"\n📊 {info['name']} ({code})...")
        result = analyze_ticker(code, info['name'])
        if 'error' not in result:
            print(f"   RSI={result['rsi']:.1f}  %B={result['bb_pct_b']:.2f}  "
                  f"Hist={result['macd_hist']:.4f}  StochK={result['stoch_k']:.1f}  "
                  f"VolR={result['volume_ratio']:.2f}  5d%={result['change_5d_pct']:.2f}")
        else:
            print(f"   ❌ {result['error']}")
        all_results['watchlist'][code] = result

    output_path = os.path.join(SCRIPT_DIR, 'astock_indicators_data.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(make_serializable(all_results), f, indent=2, ensure_ascii=False)
    print(f"\n✅ 指标数据已保存: {output_path}")


if __name__ == '__main__':
    main()
