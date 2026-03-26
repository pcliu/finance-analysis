#!/usr/bin/env python3
"""
Portfolio Adjustment Analysis Script - 2026-03-24 (收盘后)
Analyzes all holdings + ETFs.csv watchlist with technical indicators.
"""

import sys
import os
import json
import warnings
warnings.filterwarnings('ignore')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../.agent/skills/quantitative-trading'))
sys.path.append(SKILL_DIR)

from scripts import fetch_stock_data, calculate_rsi, calculate_macd, calculate_bollinger_bands, calculate_sma, calculate_atr, calculate_stochastic
from scripts.utils import make_serializable

# All tickers: holdings + ETFs.csv watchlist
ALL_TICKERS = {
    # Current holdings
    '510150': '消费ETF',
    '510880': '红利ETF',
    '512170': '医疗ETF',
    '512660': '军工ETF',
    '513180': '恒指科技',
    '515050': '5GETF',
    '515070': 'AI智能',
    '515790': '光伏ETF',
    '588000': '科创50',
    '603993': '洛阳钼业',
    '159770': '机器人AI',
    # ETFs.csv watchlist (non-holdings)
    '159985': '豆粕ETF',
    '159689': '粮食ETF',
    '159870': '化工ETF',
    '561330': '矿业ETF',
    '561560': '电力ETF',
    '159326': '电网设备ETF',
    '159241': '航空航天ETF',
    '159830': '上海金ETF',
    '161226': '国投白银LOF',
    '159516': '半导体设备ETF',
    '513630': '港股红利指数ETF',
}

HOLDINGS = ['510150', '510880', '512170', '512660', '513180', '515050', '515070', '515790', '588000', '603993', '159770']

results = {}

for ticker, name in ALL_TICKERS.items():
    print(f"分析 {name} ({ticker}) ...")
    try:
        data = fetch_stock_data(ticker, period='8mo')
        if data is None or len(data) < 20:
            print(f"  ⚠️ {name} 数据不足，跳过")
            results[ticker] = {'name': name, 'error': '数据不足'}
            continue

        # Calculate indicators
        rsi_df = calculate_rsi(data, window=14)
        macd_df = calculate_macd(data)
        bb_df = calculate_bollinger_bands(data)
        sma20 = calculate_sma(data, window=20)
        sma60 = calculate_sma(data, window=60)
        atr_df = calculate_atr(data, window=14)
        stoch_df = calculate_stochastic(data)

        # Volume analysis
        vol = data['Volume']
        vol_20_avg = vol.rolling(20).mean()
        vol_ratio = vol.iloc[-1] / vol_20_avg.iloc[-1] if vol_20_avg.iloc[-1] > 0 else 0

        # Bollinger %B
        upper = bb_df['Upper'].iloc[-1]
        lower = bb_df['Lower'].iloc[-1]
        close = data['Close'].iloc[-1]
        pct_b = (close - lower) / (upper - lower) if (upper - lower) > 0 else 0.5

        # Price changes
        closes = data['Close']
        chg_1d = (closes.iloc[-1] / closes.iloc[-2] - 1) * 100 if len(closes) >= 2 else 0
        chg_5d = (closes.iloc[-1] / closes.iloc[-6] - 1) * 100 if len(closes) >= 6 else 0
        chg_20d = (closes.iloc[-1] / closes.iloc[-21] - 1) * 100 if len(closes) >= 21 else 0

        # MACD histogram trend (last 3 days)
        hist = macd_df['Histogram']
        hist_current = hist.iloc[-1]
        hist_prev = hist.iloc[-2] if len(hist) >= 2 else 0
        hist_prev2 = hist.iloc[-3] if len(hist) >= 3 else 0

        # Determine MACD status
        if hist_current > 0 and hist_prev > 0:
            if hist_current > hist_prev:
                macd_status = "金叉加速"
            else:
                macd_status = "金叉减速"
        elif hist_current > 0 and hist_prev <= 0:
            macd_status = "新金叉"
        elif hist_current <= 0 and hist_prev > 0:
            macd_status = "新死叉"
        elif hist_current <= 0 and hist_prev <= 0:
            if hist_current > hist_prev:
                macd_status = "死叉收窄"
            else:
                macd_status = "死叉加深"
        else:
            macd_status = "中性"

        result = {
            'name': name,
            'is_holding': ticker in HOLDINGS,
            'close': float(close),
            'rsi': float(rsi_df['RSI'].iloc[-1]),
            'macd': float(macd_df['MACD'].iloc[-1]),
            'signal': float(macd_df['Signal'].iloc[-1]),
            'histogram': float(hist_current),
            'histogram_prev': float(hist_prev),
            'macd_status': macd_status,
            'bb_upper': float(upper),
            'bb_middle': float(bb_df['Middle'].iloc[-1]),
            'bb_lower': float(lower),
            'pct_b': float(pct_b),
            'sma20': float(sma20['SMA'].iloc[-1]),
            'sma60': float(sma60['SMA'].iloc[-1]) if len(sma60) >= 60 else None,
            'atr': float(atr_df['ATR'].iloc[-1]),
            'stoch_k': float(stoch_df['K'].iloc[-1]),
            'stoch_d': float(stoch_df['D'].iloc[-1]),
            'volume': float(vol.iloc[-1]),
            'vol_20_avg': float(vol_20_avg.iloc[-1]),
            'vol_ratio': float(vol_ratio),
            'chg_1d': float(chg_1d),
            'chg_5d': float(chg_5d),
            'chg_20d': float(chg_20d),
            'last_5_close': [float(c) for c in closes.tail(5).tolist()],
            'last_5_hist': [float(h) for h in hist.tail(5).tolist()],
        }
        results[ticker] = result
        print(f"  ✅ RSI={result['rsi']:.1f}, %B={result['pct_b']:.2f}, MACD={macd_status}, Hist={hist_current:.4f}, Vol比={vol_ratio:.2f}, 日涨跌={chg_1d:.2f}%")

    except Exception as e:
        print(f"  ❌ 错误: {e}")
        results[ticker] = {'name': name, 'error': str(e)}

# Save results
clean_results = make_serializable(results)
output_path = os.path.join(SCRIPT_DIR, 'portfolio_adjustment_data.json')
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(clean_results, f, indent=4, ensure_ascii=False)

print(f"\n✅ 分析完成，数据已保存到 {output_path}")
print(f"共分析 {len(results)} 个标的")
