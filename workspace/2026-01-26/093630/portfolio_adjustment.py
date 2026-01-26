#!/usr/bin/env python3
"""
持仓调整分析脚本 (Portfolio Adjustment Analysis)
生成时间: 2026-01-26 09:36:30

分析所有持仓和关注标的的技术指标，为调仓决策提供数据支持。
"""

import sys
import os
import json
import pandas as pd

# 设置路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../.agent/skills/quantitative-trading'))
sys.path.append(SKILL_DIR)

from scripts import (
    fetch_stock_data, 
    calculate_rsi, 
    calculate_macd, 
    calculate_bollinger_bands,
    calculate_sma,
    calculate_atr
)
from scripts.utils import make_serializable

# 当前持仓标的 (基于用户截图)
HOLDINGS = {
    '510150': {'name': '消费ETF', 'shares': 10000, 'cost': 0.5721, 'current': 0.5590, 'pnl': -131.50, 'pnl_pct': -2.29},
    '510880': {'name': '红利ETF', 'shares': 8500, 'cost': 3.0589, 'current': 3.0680, 'pnl': 75.70, 'pnl_pct': 0.30},
    '512660': {'name': '军工ETF', 'shares': 6000, 'cost': 1.5276, 'current': 1.5440, 'pnl': 98.00, 'pnl_pct': 1.07},
    '513180': {'name': '恒指科技', 'shares': 800, 'cost': 0.7686, 'current': 0.7570, 'pnl': -9.80, 'pnl_pct': -1.51},
    '515050': {'name': '5GETF', 'shares': 1000, 'cost': 2.3200, 'current': 2.3520, 'pnl': 31.50, 'pnl_pct': 1.38},
    '515070': {'name': 'AI智能', 'shares': 400, 'cost': 1.9388, 'current': 2.1350, 'pnl': 78.00, 'pnl_pct': 10.12},
    '588000': {'name': '科创50', 'shares': 1000, 'cost': 0.3019, 'current': 1.6510, 'pnl': 1348.60, 'pnl_pct': 446.87},
    '159241': {'name': '航空TH', 'shares': 6000, 'cost': 1.5319, 'current': 1.5460, 'pnl': 84.00, 'pnl_pct': 0.92},
    '159770': {'name': '机器人AI', 'shares': 200, 'cost': 0.7670, 'current': 1.1860, 'pnl': 83.30, 'pnl_pct': 54.63},
    '159830': {'name': '上海金', 'shares': 200, 'cost': 11.3945, 'current': 11.3780, 'pnl': -3.80, 'pnl_pct': -0.14},
    '161226': {'name': '白银基金', 'shares': 500, 'cost': 3.8750, 'current': 3.8750, 'pnl': -138.50, 'pnl_pct': -6.65},
}

# ETFs.csv 中的所有标的 (包含持仓和非持仓)
ALL_ETFS = {
    '510150': '消费ETF',
    '512660': '军工ETF',
    '159241': '航空航天ETF天弘',
    '159206': '卫星ETF',
    '515790': '光伏ETF',
    '516780': '稀土ETF',
    '512170': '医疗ETF',
    '561330': '矿业ETF',
    '159870': '化工ETF',
    '561560': '电力ETF',
    '159830': '上海金ETF',
    '159770': '机器人ETF',
    '515070': '人工智能AIETF',
    '159326': '电网设备ETF',
    '159516': '半导体设备ETF',
    '515050': '通信ETF华夏',
    '161226': '国投白银LOF',
    '518880': '黄金ETF',
    '512400': '有色金属ETF',
    '510880': '红利ETF',
    '513180': '恒生科技指数ETF',
    '513630': '港股红利指数ETF',
    '588000': '科创50ETF',
}

def analyze_etf(code, name):
    """分析单个ETF的技术指标"""
    try:
        print(f"正在分析: {code} - {name}")
        
        # 获取历史数据 (6个月)
        data = fetch_stock_data(code, period='6mo')
        
        if data is None or data.empty:
            return None
        
        # 计算技术指标
        rsi_6 = calculate_rsi(data, window=6)
        rsi_14 = calculate_rsi(data, window=14)
        macd = calculate_macd(data)
        bb = calculate_bollinger_bands(data)
        sma_20 = calculate_sma(data, window=20)
        sma_60 = calculate_sma(data, window=60)
        atr = calculate_atr(data, window=14)
        
        # 提取最新值
        latest = data.iloc[-1]
        close = latest['Close']
        volume = latest['Volume']
        
        # 计算成交量比率
        avg_volume_5 = data['Volume'].tail(5).mean()
        volume_ratio = volume / avg_volume_5 if avg_volume_5 > 0 else 1
        
        # 计算布林带位置 (%B)
        bb_upper = bb['Upper'].iloc[-1]
        bb_lower = bb['Lower'].iloc[-1]
        bb_middle = bb['Middle'].iloc[-1]
        pct_b = (close - bb_lower) / (bb_upper - bb_lower) if (bb_upper - bb_lower) > 0 else 0.5
        
        # 计算20日涨跌幅
        if len(data) >= 20:
            price_20d_ago = data['Close'].iloc[-20]
            change_20d = (close - price_20d_ago) / price_20d_ago * 100
        else:
            change_20d = 0
        
        # 趋势判断
        sma_20_val = sma_20['SMA'].iloc[-1]
        sma_60_val = sma_60['SMA'].iloc[-1] if len(sma_60) > 0 and not pd.isna(sma_60['SMA'].iloc[-1]) else sma_20_val
        
        result = {
            'code': code,
            'name': name,
            'close': close,
            'volume': volume,
            'volume_ratio': volume_ratio,
            'rsi_6': rsi_6['RSI'].iloc[-1],
            'rsi_14': rsi_14['RSI'].iloc[-1],
            'macd': macd['MACD'].iloc[-1],
            'macd_signal': macd['Signal'].iloc[-1],
            'macd_hist': macd['Histogram'].iloc[-1],
            'bb_upper': bb_upper,
            'bb_middle': bb_middle,
            'bb_lower': bb_lower,
            'pct_b': pct_b,
            'sma_20': sma_20_val,
            'sma_60': sma_60_val,
            'atr': atr['ATR'].iloc[-1],
            'change_20d': change_20d,
        }
        
        return result
        
    except Exception as e:
        print(f"分析 {code} 失败: {e}")
        return None

def main():
    import pandas as pd
    
    results = {}
    
    # 分析所有ETF
    for code, name in ALL_ETFS.items():
        result = analyze_etf(code, name)
        if result:
            results[code] = result
    
    # 保存结果
    clean_results = make_serializable(results)
    output_path = os.path.join(SCRIPT_DIR, 'portfolio_adjustment_data.json')
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(clean_results, f, indent=4, ensure_ascii=False)
    
    print(f"\n数据已保存至: {output_path}")
    
    # 输出摘要
    print("\n" + "="*80)
    print("技术分析摘要")
    print("="*80)
    
    # 按RSI(6)排序
    sorted_results = sorted(results.values(), key=lambda x: x['rsi_6'], reverse=True)
    
    print(f"\n{'代码':<10} {'名称':<15} {'现价':>10} {'RSI(6)':>8} {'%B':>8} {'20日涨幅':>10}")
    print("-" * 70)
    
    for r in sorted_results:
        print(f"{r['code']:<10} {r['name']:<15} {r['close']:>10.4f} {r['rsi_6']:>8.1f} {r['pct_b']:>8.2f} {r['change_20d']:>9.2f}%")
    
    return results

if __name__ == "__main__":
    main()
