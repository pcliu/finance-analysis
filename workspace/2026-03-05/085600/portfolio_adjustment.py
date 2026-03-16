#!/usr/bin/env python3
"""
持仓调整分析 - 2026-03-05 盘前
全量技术诊断：11项持仓 + 14项观察标的 = 25标的
"""
import sys
import os
import json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../.agent/skills/quantitative-trading'))
sys.path.append(SKILL_DIR)

from scripts import (
    fetch_stock_data, calculate_rsi, calculate_macd,
    calculate_bollinger_bands, calculate_sma
)
from scripts.utils import make_serializable

# === 全部标的列表 ===
ALL_ETFS = {
    # 当前持仓
    '510150': '消费ETF',
    '510880': '红利ETF',
    '512170': '医疗ETF',
    '512660': '军工ETF',
    '513180': '恒指科技',
    '515050': '5GETF',
    '515070': 'AI智能',
    '515790': '光伏ETF',
    '588000': '科创50',
    '159241': '航空TH',
    '159770': '机器人AI',
    # 观察池（ETFs.csv中非持仓）
    '159985': '豆粕ETF',
    '512890': '红利低波ETF',
    '159206': '卫星ETF',
    '516780': '稀土ETF',
    '561330': '矿业ETF',
    '159870': '化工ETF',
    '561560': '电力ETF',
    '159830': '上海金ETF',
    '159326': '电网设备ETF',
    '159516': '半导体设备ETF',
    '161226': '国投白银LOF',
    '518880': '黄金ETF',
    '512400': '有色金属ETF',
    '513630': '港股红利ETF',
}

results = {}

for code, name in ALL_ETFS.items():
    print(f"分析 {name} ({code})...", flush=True)
    try:
        data = fetch_stock_data(code, period='9mo')
        if data is None or data.empty:
            print(f"  ⚠️ 无数据: {code}")
            results[code] = {'name': name, 'error': '无数据'}
            continue

        # 计算技术指标
        rsi = calculate_rsi(data, window=14)
        macd = calculate_macd(data)
        bb = calculate_bollinger_bands(data)
        sma20 = calculate_sma(data, window=20)

        # 成交量分析
        vol = data['Volume']
        vol_ma20 = vol.rolling(20).mean()
        vol_ratio = (vol / vol_ma20).iloc[-1] if vol_ma20.iloc[-1] > 0 else 0

        # 最新价
        close = data['Close'].iloc[-1]
        close_prev = data['Close'].iloc[-2] if len(data) > 1 else close
        close_5d = data['Close'].iloc[-6] if len(data) > 5 else close

        # MACD金叉/死叉判断
        macd_line = macd['MACD']
        signal_line = macd['Signal']
        hist = macd['Histogram']

        # 判断当前是金叉还是死叉
        current_cross = 'golden' if macd_line.iloc[-1] > signal_line.iloc[-1] else 'dead'
        prev_cross = 'golden' if macd_line.iloc[-2] > signal_line.iloc[-2] else 'dead'

        is_new_cross = (current_cross != prev_cross)

        # 布林带 %B
        upper = bb['Upper'].iloc[-1]
        lower = bb['Lower'].iloc[-1]
        middle = bb['Middle'].iloc[-1]
        pct_b = (close - lower) / (upper - lower) if (upper - lower) > 0 else 0.5

        # 5日涨跌幅
        chg_1d = (close - close_prev) / close_prev * 100 if close_prev > 0 else 0
        chg_5d = (close - close_5d) / close_5d * 100 if close_5d > 0 else 0

        results[code] = {
            'name': name,
            'close': round(close, 4),
            'rsi': round(rsi['RSI'].iloc[-1], 1),
            'rsi_prev': round(rsi['RSI'].iloc[-2], 1),
            'macd': round(macd_line.iloc[-1], 4),
            'signal': round(signal_line.iloc[-1], 4),
            'histogram': round(hist.iloc[-1], 4),
            'histogram_prev': round(hist.iloc[-2], 4),
            'cross_type': current_cross,
            'is_new_cross': is_new_cross,
            'pct_b': round(pct_b, 2),
            'bb_upper': round(upper, 4),
            'bb_middle': round(middle, 4),
            'bb_lower': round(lower, 4),
            'sma20': round(sma20['SMA'].iloc[-1], 4),
            'vol_ratio': round(vol_ratio, 2),
            'chg_1d': round(chg_1d, 2),
            'chg_5d': round(chg_5d, 2),
        }
        print(f"  ✅ RSI={results[code]['rsi']}, MACD={current_cross}{'(新)' if is_new_cross else ''}, %B={results[code]['pct_b']}, 1d={chg_1d:+.2f}%")
    except Exception as e:
        print(f"  ❌ 错误: {e}")
        results[code] = {'name': name, 'error': str(e)}

# 保存数据
clean = make_serializable(results)
output_path = os.path.join(SCRIPT_DIR, 'portfolio_adjustment_data.json')
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(clean, f, indent=4, ensure_ascii=False)

print(f"\n✅ 技术分析完成，数据已保存至 {output_path}")
print(f"共分析 {len(results)} 只标的")
