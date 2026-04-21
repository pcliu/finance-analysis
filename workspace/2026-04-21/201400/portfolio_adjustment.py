#!/usr/bin/env python3
"""
Portfolio Adjustment Analysis — 2026-04-21
持仓调整分析脚本

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
# 1. 投资组合定义
# ─────────────────────────────────────────────

HOLDINGS = {
    '510150': {'name': '消费ETF',     'shares': 13000, 'cost': 0.5980},
    '510880': {'name': '红利ETF',     'shares': 10000, 'cost': 3.0671},
    '512170': {'name': '医疗ETF',     'shares': 16000, 'cost': 0.3562},
    '512660': {'name': '军工ETF',     'shares': 4000,  'cost': 1.6496},
    '513180': {'name': '恒指科技',    'shares': 8000,  'cost': 0.6874},
    '515050': {'name': '5GETF',       'shares': 3000,  'cost': 2.4202},
    '515070': {'name': 'AI智能',      'shares': 400,   'cost': 1.9388},
    '515790': {'name': '光伏ETF',     'shares': 3000,  'cost': 1.1510},
    '588000': {'name': '科创50',      'shares': 1000,  'cost': 0.3019},
    '603993': {'name': '洛阳钼业',    'shares': 300,   'cost': 19.5169},
    '159770': {'name': '机器人AI',    'shares': 200,   'cost': 0.7670},
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

ALL_TICKERS = list(set(list(HOLDINGS.keys()) + list(WATCHLIST.keys())))

# ─────────────────────────────────────────────
# 2. 数据获取
# ─────────────────────────────────────────────

def fetch_technical_data(ticker, period='3mo'):
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

        result = {
            'close':       last_close,
            'prev_close':  prev_close,
            'daily_chg':   (last_close / prev_close - 1) * 100,
            'rsi':         float(rsi_df['RSI'].iloc[-1]),
            'rsi_prev':    float(rsi_df['RSI'].iloc[-2]),
            'macd':        float(macd_df['MACD'].iloc[-1]),
            'signal':      float(macd_df['Signal'].iloc[-1]),
            'hist':        float(macd_df['Histogram'].iloc[-1]),
            'hist_prev':   float(macd_df['Histogram'].iloc[-2]),
            'bb_upper':    float(upper),
            'bb_lower':    float(lower),
            'bb_mid':      float(bb_df['Middle'].iloc[-1]),
            'pct_b':       float(pct_b),
            'stoch_k':     float(stoch_df['K'].iloc[-1]),
            'stoch_d':     float(stoch_df['D'].iloc[-1]),
            'sma20':       float(sma20_df['SMA'].iloc[-1]),
            'sma60':       float(sma60_df['SMA'].iloc[-1]) if len(data) >= 60 else None,
            'vol_ratio':   float(vol_ratio),
            'ret_5d':      float(ret_5d) if ret_5d is not None else None,
            'ret_20d':     float(ret_20d) if ret_20d is not None else None,
        }
        return result

    except Exception as e:
        print(f"  ❌ {ticker} error: {e}")
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
    print("📊 持仓调整分析 — 2026-04-21")
    print("=" * 60)

    # 3.1 获取实时报价
    print("\n[1/3] 获取实时行情...")
    rt_quotes = fetch_all_realtime()
    print(f"  ✅ 获取到 {len(rt_quotes)} 只实时报价")

    # 3.2 逐只计算技术指标
    print("\n[2/3] 计算技术指标 (全量 ~20只)...")
    tech_data = {}
    for ticker in ALL_TICKERS:
        name_map = {**{k: v['name'] for k, v in HOLDINGS.items()},
                    **{k: v['name'] for k, v in WATCHLIST.items()}}
        name = name_map.get(ticker, ticker)
        print(f"  → {name} ({ticker})")
        result = fetch_technical_data(ticker, period='3mo')
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
        if not td:
            continue
        rt_price   = td['realtime_price']
        cost       = info['cost']
        shares     = info['shares']
        mkt_val    = rt_price * shares
        cost_val   = cost * shares
        pnl        = mkt_val - cost_val
        pnl_pct    = (pnl / cost_val) * 100
        total_market_value += mkt_val
        total_cost_value   += cost_val

        holdings_summary[ticker] = {
            'name':       info['name'],
            'shares':     shares,
            'cost':       cost,
            'rt_price':   rt_price,
            'mkt_val':    mkt_val,
            'pnl':        pnl,
            'pnl_pct':    pnl_pct,
        }
        print(f"  {info['name']:12s}: 价格={rt_price:.4f} | 市值={mkt_val:.2f} | "
              f"盈亏={pnl:+.2f} ({pnl_pct:+.2f}%)")

    total_pnl = total_market_value - total_cost_value
    print(f"\n  📊 持仓总市值: ¥{total_market_value:,.2f}")
    print(f"  📊 持仓总盈亏: ¥{total_pnl:+,.2f}")

    # ─────────────────────────────────────────────
    # 4. 保存结果
    # ─────────────────────────────────────────────
    output = {
        'date':              '2026-04-21',
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
