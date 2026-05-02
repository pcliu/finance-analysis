#!/usr/bin/env python3
"""
Portfolio Adjustment Analysis — 2026-04-22
持仓调整分析脚本（午间收盘后）

Coverage:
  - 11 current holdings
  - All ETFs from ETFs.csv (watchlist)
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
    fetch_stock_data, fetch_realtime_quote,
    calculate_rsi, calculate_macd, calculate_bollinger_bands,
    calculate_stochastic, calculate_sma
)
from scripts.utils import make_serializable

# ─────────────────────────────────────────────
# 1. 投资组合定义 (Updated from 4/22 screenshots)
# ─────────────────────────────────────────────

HOLDINGS = {
    '510150': {'name': '消费ETF',     'shares': 13000, 'cost': 0.5980, 'mkt_val': 6682.00, 'pnl': -1093.00, 'pnl_pct': -14.05, 'today_pnl': -39.00,  'today_pct': -0.58, 'latest': 0.5140, 'position_pct': 6.38},
    '510880': {'name': '红利ETF',     'shares': 10000, 'cost': 3.0671, 'mkt_val': 32700.00, 'pnl': 2027.36, 'pnl_pct': 6.62,  'today_pnl': 50.00,   'today_pct': 0.15,  'latest': 3.2700, 'position_pct': 31.22},
    '512170': {'name': '医疗ETF',     'shares': 16000, 'cost': 0.3562, 'mkt_val': 5328.00,  'pnl': -372.00, 'pnl_pct': -6.51, 'today_pnl': 16.00,   'today_pct': 0.30,  'latest': 0.3330, 'position_pct': 5.09},
    '512660': {'name': '军工ETF',     'shares': 4000,  'cost': 1.6496, 'mkt_val': 5636.00,  'pnl': -963.00, 'pnl_pct': -14.59,'today_pnl': -28.00,  'today_pct': -0.49, 'latest': 1.4090, 'position_pct': 5.38},
    '513180': {'name': '恒指科技',    'shares': 8000,  'cost': 0.6874, 'mkt_val': 5088.00,  'pnl': -411.50, 'pnl_pct': -7.48, 'today_pnl': -96.00,  'today_pct': -1.85, 'latest': 0.6360, 'position_pct': 4.86},
    '515050': {'name': '5GETF',       'shares': 3000,  'cost': 2.4202, 'mkt_val': 9096.00,  'pnl': 1835.00, 'pnl_pct': 25.28, 'today_pnl': 282.00,  'today_pct': 3.20,  'latest': 3.0320, 'position_pct': 8.68},
    '515070': {'name': 'AI智能',      'shares': 400,   'cost': 1.9388, 'mkt_val': 886.00,   'pnl': 110.00,  'pnl_pct': 14.25, 'today_pnl': 14.40,   'today_pct': 1.65,  'latest': 2.2150, 'position_pct': 0.85},
    '515790': {'name': '光伏ETF',     'shares': 3000,  'cost': 1.1510, 'mkt_val': 3240.00,  'pnl': -213.50, 'pnl_pct': -6.17, 'today_pnl': -6.00,   'today_pct': -0.18, 'latest': 1.0800, 'position_pct': 3.09},
    '588000': {'name': '科创50',      'shares': 1000,  'cost': 0.3019, 'mkt_val': 1511.00,  'pnl': 1208.60, 'pnl_pct': 400.50,'today_pnl': 7.00,    'today_pct': 0.47,  'latest': 1.5110, 'position_pct': 1.44},
    '603993': {'name': '洛阳钼业',    'shares': 300,   'cost': 19.5169,'mkt_val': 6069.00,  'pnl': 205.35,  'pnl_pct': 3.65,  'today_pnl': 45.00,   'today_pct': 0.75,  'latest': 20.2300,'position_pct': 5.79},
    '159770': {'name': '机器人AI',    'shares': 200,   'cost': 0.7670, 'mkt_val': 210.40,   'pnl': 56.50,   'pnl_pct': 37.16, 'today_pnl': 0.60,    'today_pct': 0.29,  'latest': 1.0520, 'position_pct': 0.20},
}

# Account summary from screenshots
ACCOUNT = {
    'total_assets': 104744.02,
    'holding_value': 76446.40,
    'total_pnl': 2484.02,
    'available': 28297.62,         # 可用 = 总资产 - 持仓市值 (includes money fund)
    'withdrawable': 297.04,
    'today_pnl': 246.00,
    'position_ratio': 72.98,
}

WATCHLIST = {
    '510880': {'name': '红利ETF'},
    '510150': {'name': '消费ETF'},
    '159985': {'name': '豆粕ETF'},
    '159689': {'name': '粮食ETF'},
    '159870': {'name': '化工ETF'},
    '561330': {'name': '矿业ETF'},
    '561560': {'name': '电力ETF'},
    '159326': {'name': '电网设备ETF'},
    '515790': {'name': '光伏ETF'},
    '560280': {'name': '工程机械ETF'},
    '512660': {'name': '军工ETF'},
    '159241': {'name': '航空航天ETF'},
    '159830': {'name': '上海金ETF'},
    '161226': {'name': '国投白银LOF'},
    '159516': {'name': '半导体设备ETF'},
    '588000': {'name': '科创50ETF'},
    '513180': {'name': '恒生科技ETF'},
    '513630': {'name': '港股红利ETF'},
}

# Combine all unique tickers
ALL_TICKERS = list(set(list(HOLDINGS.keys()) + list(WATCHLIST.keys())))

# ─────────────────────────────────────────────
# 2. 数据获取
# ─────────────────────────────────────────────

def fetch_technical_data(ticker, period='6mo'):
    """获取历史数据并计算技术指标"""
    try:
        data = fetch_stock_data(ticker, period=period)
        if data is None or len(data) < 20:
            print(f"  ⚠️  {ticker}: 数据不足 (len={len(data) if data is not None else 0})")
            return None

        rsi_df    = calculate_rsi(data, window=14)
        macd_df   = calculate_macd(data)
        bb_df     = calculate_bollinger_bands(data)
        stoch_df  = calculate_stochastic(data)
        sma20_df  = calculate_sma(data, window=20)
        sma60_df  = calculate_sma(data, window=60)

        last_close = float(data['Close'].iloc[-1])
        prev_close = float(data['Close'].iloc[-2]) if len(data) > 1 else last_close

        # %B = (price - lower) / (upper - lower)
        upper = bb_df['Upper'].iloc[-1]
        lower = bb_df['Lower'].iloc[-1]
        pct_b = (last_close - lower) / (upper - lower) if (upper - lower) > 0 else 0.5

        # Volume ratio (vs 20-day avg)
        vol_avg = data['Volume'].rolling(20).mean().iloc[-1]
        vol_ratio = float(data['Volume'].iloc[-1] / vol_avg) if vol_avg > 0 else 1.0

        # 5-day and 20-day returns
        ret_5d  = (last_close / float(data['Close'].iloc[-6])  - 1) * 100 if len(data) >= 6  else None
        ret_20d = (last_close / float(data['Close'].iloc[-21]) - 1) * 100 if len(data) >= 21 else None

        # Price vs SMA20 position
        sma20_val = float(sma20_df['SMA'].iloc[-1])
        price_vs_sma20 = ((last_close / sma20_val) - 1) * 100 if sma20_val > 0 else 0

        result = {
            'close':         last_close,
            'prev_close':    prev_close,
            'daily_chg':     (last_close / prev_close - 1) * 100,
            'rsi':           float(rsi_df['RSI'].iloc[-1]),
            'rsi_prev':      float(rsi_df['RSI'].iloc[-2]),
            'rsi_5d_ago':    float(rsi_df['RSI'].iloc[-6]) if len(rsi_df) >= 6 else None,
            'macd':          float(macd_df['MACD'].iloc[-1]),
            'signal':        float(macd_df['Signal'].iloc[-1]),
            'hist':          float(macd_df['Histogram'].iloc[-1]),
            'hist_prev':     float(macd_df['Histogram'].iloc[-2]),
            'bb_upper':      float(upper),
            'bb_lower':      float(lower),
            'bb_mid':        float(bb_df['Middle'].iloc[-1]),
            'pct_b':         float(pct_b),
            'stoch_k':       float(stoch_df['K'].iloc[-1]),
            'stoch_d':       float(stoch_df['D'].iloc[-1]),
            'sma20':         sma20_val,
            'sma60':         float(sma60_df['SMA'].iloc[-1]) if len(data) >= 60 else None,
            'price_vs_sma20': price_vs_sma20,
            'vol_ratio':     float(vol_ratio),
            'ret_5d':        float(ret_5d) if ret_5d is not None else None,
            'ret_20d':       float(ret_20d) if ret_20d is not None else None,
        }
        return result

    except Exception as e:
        print(f"  ❌ {ticker} error: {e}")
        import traceback
        traceback.print_exc()
        return None


def fetch_all_realtime():
    """批量获取实时行情"""
    try:
        quotes = fetch_realtime_quote(ALL_TICKERS)
        if isinstance(quotes, list):
            quote_map = {}
            for q in quotes:
                if isinstance(q, dict):
                    code = str(q.get('代码', q.get('code', '')))
                    price = q.get('最新价', q.get('price', None))
                    quote_map[code] = price
            return quote_map
        elif isinstance(quotes, dict):
            return {str(k): v for k, v in quotes.items()}
    except Exception as e:
        print(f"  ⚠️ 实时行情获取失败: {e}")
    return {}


# ─────────────────────────────────────────────
# 3. 主分析流程
# ─────────────────────────────────────────────

def main():
    print("=" * 60)
    print("📊 持仓调整分析 — 2026-04-22 (午间)")
    print("=" * 60)

    # 3.1 获取实时报价
    print("\n[1/3] 获取实时行情...")
    rt_quotes = fetch_all_realtime()
    print(f"  ✅ 获取到 {len(rt_quotes)} 只实时报价")
    if rt_quotes:
        for code, price in rt_quotes.items():
            name_map = {**{k: v['name'] for k, v in HOLDINGS.items()},
                        **{k: v['name'] for k, v in WATCHLIST.items()}}
            name = name_map.get(code, code)
            print(f"    {name}({code}): {price}")

    # 3.2 逐只计算技术指标
    print("\n[2/3] 计算技术指标 (全量 ~22只, 6个月)...")
    tech_data = {}
    for ticker in sorted(ALL_TICKERS):
        name_map = {**{k: v['name'] for k, v in HOLDINGS.items()},
                    **{k: v['name'] for k, v in WATCHLIST.items()}}
        name = name_map.get(ticker, ticker)
        print(f"  → {name} ({ticker})")
        result = fetch_technical_data(ticker, period='6mo')
        if result:
            # 覆盖实时价格（若可用）
            rt_price = rt_quotes.get(ticker)
            if rt_price and float(rt_price) > 0:
                result['realtime_price'] = float(rt_price)
            else:
                result['realtime_price'] = result['close']
            tech_data[ticker] = result

    print(f"  ✅ 成功分析 {len(tech_data)}/{len(ALL_TICKERS)} 只标的")

    # 3.3 持仓盈亏计算
    print("\n[3/3] 计算持仓盈亏...")
    holdings_summary = {}
    total_market_value = 0
    total_cost_value   = 0

    for ticker, info in HOLDINGS.items():
        td = tech_data.get(ticker)
        rt_price = info['latest']  # Use screenshot price as primary
        cost       = info['cost']
        shares     = info['shares']
        mkt_val    = info['mkt_val']
        cost_val   = cost * shares
        pnl        = info['pnl']
        pnl_pct    = info['pnl_pct']
        total_market_value += mkt_val
        total_cost_value   += cost_val

        # Merge tech data if available
        tech_info = {}
        if td:
            tech_info = {
                'rsi': td['rsi'],
                'pct_b': td['pct_b'],
                'hist': td['hist'],
                'stoch_k': td['stoch_k'],
                'vol_ratio': td['vol_ratio'],
                'ret_5d': td['ret_5d'],
                'ret_20d': td['ret_20d'],
                'sma20': td['sma20'],
                'price_vs_sma20': td['price_vs_sma20'],
            }

        holdings_summary[ticker] = {
            'name':       info['name'],
            'shares':     shares,
            'cost':       cost,
            'rt_price':   rt_price,
            'mkt_val':    mkt_val,
            'pnl':        pnl,
            'pnl_pct':    pnl_pct,
            'today_pnl':  info['today_pnl'],
            'today_pct':  info['today_pct'],
            'position_pct': info['position_pct'],
            **tech_info,
        }
        print(f"  {info['name']:12s}: 价格={rt_price:.4f} | 市值={mkt_val:.2f} | "
              f"盈亏={pnl:+.2f} ({pnl_pct:+.2f}%) | 今日={info['today_pnl']:+.2f}")

    total_pnl = total_market_value - total_cost_value
    print(f"\n  📊 持仓总市值: ¥{total_market_value:,.2f}")
    print(f"  📊 持仓总盈亏: ¥{total_pnl:+,.2f}")
    print(f"  📊 今日盈亏:   ¥{ACCOUNT['today_pnl']:+,.2f}")

    # ─────────────────────────────────────────────
    # 4. 保存结果
    # ─────────────────────────────────────────────
    output = {
        'date':              '2026-04-22',
        'session':           'midday',
        'account':           ACCOUNT,
        'total_market_value': total_market_value,
        'total_cost_value':   total_cost_value,
        'total_pnl':          total_pnl,
        'holdings_summary':   holdings_summary,
        'technical_data':     tech_data,
        'realtime_quotes':    rt_quotes,
    }

    out_path = os.path.join(SCRIPT_DIR, 'portfolio_adjustment_data.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(make_serializable(output), f, ensure_ascii=False, indent=2)

    print(f"\n✅ 数据已保存至: {out_path}")
    return output


if __name__ == '__main__':
    main()
