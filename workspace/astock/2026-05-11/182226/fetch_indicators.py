#!/usr/bin/env python3
"""Fetch technical indicators for all A-stock ETF holdings and watchlist."""

import os
import sys
import json
import time
import warnings
warnings.filterwarnings('ignore')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Add project path
sys.path.insert(0, '/Users/liupengcheng/Code/finance-analysis')

import tushare as ts
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import akshare as ak

# Tushare token
try:
    import subprocess
    result = subprocess.run(['cat', os.path.expanduser('~/.tushare_token')], capture_output=True, text=True)
    TOKEN = result.stdout.strip()
except:
    TOKEN = ''

if not TOKEN:
    # Try from env
    TOKEN = os.environ.get('TUSHARE_TOKEN', '')

# Initialize tushare
pro = ts.pro_api(TOKEN) if TOKEN else None

# All ETFs to analyze
HOLDINGS = [
    {'name': '消费ETF', 'code': '510150', 'exchange': 'SH', 'shares': 10000, 'cost': 0.5191, 'market_val': 5200.00, 'pnl_pct': 0.17},
    {'name': '红利ETF', 'code': '510880', 'exchange': 'SH', 'shares': 7000, 'cost': 2.9866, 'market_val': 22841.00, 'pnl_pct': 9.25},
    {'name': '医疗ETF', 'code': '512170', 'exchange': 'SH', 'shares': 16000, 'cost': 0.3562, 'market_val': 5440.00, 'pnl_pct': -4.55},
    {'name': '军工ETF', 'code': '512660', 'exchange': 'SH', 'shares': 4000, 'cost': 1.6496, 'market_val': 5932.00, 'pnl_pct': -10.10},
    {'name': '恒指科技', 'code': '513180', 'exchange': 'SH', 'shares': 5000, 'cost': 0.6531, 'market_val': 3255.00, 'pnl_pct': -0.32},
    {'name': '5GETF', 'code': '515050', 'exchange': 'SH', 'shares': 2000, 'cost': 2.1545, 'market_val': 6598.00, 'pnl_pct': 53.12},
    {'name': 'AI智能', 'code': '515070', 'exchange': 'SH', 'shares': 800, 'cost': 2.1650, 'market_val': 1973.60, 'pnl_pct': 13.95},
    {'name': '光伏ETF', 'code': '515790', 'exchange': 'SH', 'shares': 3000, 'cost': 1.1510, 'market_val': 3369.00, 'pnl_pct': -2.43},
    {'name': '电力ETF', 'code': '561560', 'exchange': 'SH', 'shares': 2000, 'cost': 1.3623, 'market_val': 2824.00, 'pnl_pct': 3.65},
    {'name': '半导体设备', 'code': '159516', 'exchange': 'SZ', 'shares': 6000, 'cost': 0.9788, 'market_val': 6600.00, 'pnl_pct': 12.38},
    {'name': '机器人AI', 'code': '159770', 'exchange': 'SZ', 'shares': 200, 'cost': 0.7670, 'market_val': 236.20, 'pnl_pct': 53.98},
    {'name': '化工ETF', 'code': '159870', 'exchange': 'SZ', 'shares': 5000, 'cost': 0.9005, 'market_val': 4620.00, 'pnl_pct': 2.61},
]

WATCHLIST = [
    {'name': '豆粕ETF', 'code': '159985', 'exchange': 'SZ'},
    {'name': '粮食ETF', 'code': '159689', 'exchange': 'SZ'},
    {'name': '矿业ETF', 'code': '561330', 'exchange': 'SH'},
    {'name': '电网设备ETF', 'code': '159326', 'exchange': 'SZ'},
    {'name': '工程机械ETF', 'code': '560280', 'exchange': 'SH'},
    {'name': '航空航天ETF', 'code': '159241', 'exchange': 'SZ'},
    {'name': '上海金ETF', 'code': '159830', 'exchange': 'SZ'},
    {'name': '国投白银LOF', 'code': '161226', 'exchange': 'SZ'},
    {'name': '科创50ETF', 'code': '588000', 'exchange': 'SH'},
    {'name': '港股红利ETF', 'code': '513630', 'exchange': 'SH'},
]

def get_ts_code(code, exchange):
    return f"{code}.{exchange}"

def fetch_history_akshare(code, exchange, days=60):
    """Fetch historical data via akshare."""
    try:
        symbol = f"sh{code}" if exchange == 'SH' else f"sz{code}"
        df = ak.fund_etf_hist_sina(symbol=symbol)
        if df is None or len(df) == 0:
            return None
        df = df.rename(columns={'date': 'trade_date', 'open': 'open', 'high': 'high',
                                  'low': 'low', 'close': 'close', 'volume': 'vol'})
        df['trade_date'] = pd.to_datetime(df['trade_date'])
        df = df.sort_values('trade_date').tail(days).reset_index(drop=True)
        return df
    except Exception as e:
        print(f"  akshare error for {code}: {e}")
        return None

def fetch_history_tushare(code, exchange, days=60):
    """Fetch historical data via tushare."""
    if not pro:
        return None
    try:
        ts_code = get_ts_code(code, exchange)
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=90)).strftime('%Y%m%d')
        df = pro.fund_daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
        if df is None or len(df) == 0:
            return None
        df = df.sort_values('trade_date').tail(days).reset_index(drop=True)
        return df
    except Exception as e:
        print(f"  tushare error for {code}: {e}")
        return None

def fetch_realtime(code, exchange):
    """Fetch realtime quote."""
    try:
        symbol = f"sh{code}" if exchange == 'SH' else f"sz{code}"
        df = ak.stock_zh_a_spot_em()
        # Try ETF realtime
        try:
            etf_df = ak.fund_etf_spot_em()
            row = etf_df[etf_df['代码'] == code]
            if len(row) > 0:
                r = row.iloc[0]
                return {
                    'current': float(r.get('最新价', r.get('price', 0))),
                    'change_pct': float(r.get('涨跌幅', 0)),
                    'volume': float(r.get('成交量', 0)),
                }
        except:
            pass
        return None
    except Exception as e:
        print(f"  realtime error for {code}: {e}")
        return None

def calc_rsi(close, period=14):
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / (loss + 1e-10)
    return 100 - (100 / (1 + rs))

def calc_macd(close, fast=12, slow=26, signal=9):
    ema_fast = close.ewm(span=fast, adjust=False).mean()
    ema_slow = close.ewm(span=slow, adjust=False).mean()
    macd = ema_fast - ema_slow
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    hist = macd - signal_line
    return macd, signal_line, hist

def calc_bollinger(close, period=20, std_dev=2):
    ma = close.rolling(period).mean()
    std = close.rolling(period).std()
    upper = ma + std_dev * std
    lower = ma - std_dev * std
    pct_b = (close - lower) / (upper - lower + 1e-10)
    return ma, upper, lower, pct_b

def analyze_etf(item, is_holding=True):
    code = item['code']
    exchange = item['exchange']
    name = item['name']

    print(f"\n正在分析: {name} ({code})")

    result = {
        'name': name,
        'code': code,
        'is_holding': is_holding,
    }

    if is_holding:
        result.update({
            'shares': item.get('shares', 0),
            'cost': item.get('cost', 0),
            'market_val': item.get('market_val', 0),
            'pnl_pct': item.get('pnl_pct', 0),
        })

    # Fetch historical data
    df = fetch_history_akshare(code, exchange)
    if df is None or len(df) < 20:
        df = fetch_history_tushare(code, exchange)

    if df is None or len(df) < 10:
        print(f"  无法获取历史数据")
        result['error'] = '数据获取失败'
        return result

    close = df['close'].astype(float)
    vol = df['vol'].astype(float) if 'vol' in df.columns else df.get('amount', pd.Series([0]*len(df))).astype(float)

    # Technical indicators
    rsi14 = calc_rsi(close, 14)
    rsi6 = calc_rsi(close, 6)
    macd, signal, hist = calc_macd(close)
    ma20, bb_upper, bb_lower, pct_b = calc_bollinger(close, 20)
    ma5 = close.rolling(5).mean()
    ma10 = close.rolling(10).mean()
    vol_ma20 = vol.rolling(20).mean()

    latest = {
        'price': round(float(close.iloc[-1]), 4),
        'rsi14': round(float(rsi14.iloc[-1]), 2),
        'rsi6': round(float(rsi6.iloc[-1]), 2),
        'macd': round(float(macd.iloc[-1]), 4),
        'macd_signal': round(float(signal.iloc[-1]), 4),
        'macd_hist': round(float(hist.iloc[-1]), 4),
        'bb_pct_b': round(float(pct_b.iloc[-1]), 3),
        'bb_upper': round(float(bb_upper.iloc[-1]), 4),
        'bb_lower': round(float(bb_lower.iloc[-1]), 4),
        'ma5': round(float(ma5.iloc[-1]), 4),
        'ma10': round(float(ma10.iloc[-1]), 4),
        'ma20': round(float(ma20.iloc[-1]), 4),
        'vol_ratio': round(float(vol.iloc[-1] / (vol_ma20.iloc[-1] + 1e-10)), 2),
        'data_points': len(df),
    }

    # 5-day trend
    if len(close) >= 5:
        latest['5d_chg_pct'] = round(float((close.iloc[-1] - close.iloc[-5]) / close.iloc[-5] * 100), 2)
    if len(close) >= 20:
        latest['20d_chg_pct'] = round(float((close.iloc[-1] - close.iloc[-20]) / close.iloc[-20] * 100), 2)

    # Price vs MAs
    latest['above_ma5'] = float(close.iloc[-1]) > float(ma5.iloc[-1])
    latest['above_ma10'] = float(close.iloc[-1]) > float(ma10.iloc[-1])
    latest['above_ma20'] = float(close.iloc[-1]) > float(ma20.iloc[-1])

    # MACD momentum direction
    latest['macd_hist_direction'] = 'up' if len(hist) >= 2 and float(hist.iloc[-1]) > float(hist.iloc[-2]) else 'down'

    result['indicators'] = latest

    # Fetch realtime
    rt = fetch_realtime(code, exchange)
    if rt:
        result['realtime'] = rt

    time.sleep(0.3)
    return result

# Run analysis
all_results = {}

print("=== 持仓品种技术指标分析 ===")
holdings_results = []
for item in HOLDINGS:
    r = analyze_etf(item, is_holding=True)
    holdings_results.append(r)

print("\n=== 观察池品种技术指标分析 ===")
watchlist_results = []
for item in WATCHLIST:
    r = analyze_etf(item, is_holding=False)
    watchlist_results.append(r)

all_results = {
    'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    'account': {
        'total_assets': 106419.90,
        'market_value': 68888.80,
        'floating_pnl': -4582.80,
        'available_cash': 7531.10,
        'investable_cash': 106419.90 - 68888.80,  # 含货基可赎回
        'position_ratio': 64.73,
    },
    'holdings': holdings_results,
    'watchlist': watchlist_results,
}

output_path = os.path.join(SCRIPT_DIR, 'astock_indicators_data.json')
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(all_results, f, ensure_ascii=False, indent=2, default=str)

print(f"\n技术指标数据已保存: {output_path}")
print(f"持仓品种: {len(holdings_results)}, 观察池品种: {len(watchlist_results)}")
