#!/usr/bin/env python3
"""
持仓调整分析脚本 - 2026-01-28
分析所有持仓标的和ETFs.csv中的观察标的
"""

import sys
import os
import json
from datetime import datetime

# Robust Import: Use absolute path relative to this script
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

def analyze_etf(code, name, period='3mo'):
    """对单个ETF进行全面技术分析"""
    try:
        # 获取数据
        data = fetch_stock_data(code, period=period)
        if data is None or len(data) < 20:
            return {"error": f"无法获取 {code} 的数据"}
        
        # 计算指标
        rsi_6 = calculate_rsi(data, window=6)['RSI']
        rsi_14 = calculate_rsi(data, window=14)['RSI']
        macd_data = calculate_macd(data)
        bb_data = calculate_bollinger_bands(data, window=20)
        sma_20 = calculate_sma(data, window=20)['SMA']
        sma_5 = calculate_sma(data, window=5)['SMA']
        atr = calculate_atr(data, window=14)['ATR']
        
        # 获取最新值
        current_price = float(data['Close'].iloc[-1])
        prev_price = float(data['Close'].iloc[-2])
        daily_change = (current_price - prev_price) / prev_price * 100
        
        # 计算20日涨幅
        if len(data) >= 20:
            price_20d_ago = float(data['Close'].iloc[-20])
            gain_20d = (current_price - price_20d_ago) / price_20d_ago * 100
        else:
            gain_20d = 0
        
        # 成交量分析
        vol_ma = data['Volume'].rolling(20).mean()
        vol_ratio = float(data['Volume'].iloc[-1] / vol_ma.iloc[-1]) if vol_ma.iloc[-1] > 0 else 1.0
        
        # 计算%B (布林带位置)
        upper = float(bb_data['Upper'].iloc[-1])
        lower = float(bb_data['Lower'].iloc[-1])
        middle = float(bb_data['Middle'].iloc[-1])
        percent_b = (current_price - lower) / (upper - lower) if (upper - lower) > 0 else 0.5
        
        return {
            "代码": code,
            "名称": name,
            "现价": round(current_price, 4),
            "日涨跌": round(daily_change, 2),
            "20日涨幅": round(gain_20d, 2),
            "RSI_6": round(float(rsi_6.iloc[-1]), 2),
            "RSI_14": round(float(rsi_14.iloc[-1]), 2),
            "MACD": round(float(macd_data['MACD'].iloc[-1]), 4),
            "MACD_Signal": round(float(macd_data['Signal'].iloc[-1]), 4),
            "MACD_Hist": round(float(macd_data['Histogram'].iloc[-1]), 4),
            "BB_Upper": round(upper, 4),
            "BB_Middle": round(middle, 4),
            "BB_Lower": round(lower, 4),
            "%B": round(percent_b, 2),
            "SMA_5": round(float(sma_5.iloc[-1]), 4),
            "SMA_20": round(float(sma_20.iloc[-1]), 4),
            "ATR": round(float(atr.iloc[-1]), 4),
            "成交量比": round(vol_ratio, 2)
        }
    except Exception as e:
        return {"代码": code, "名称": name, "error": str(e)}

def main():
    # 当前持仓标的
    holdings = [
        ("510150", "消费ETF", 13000, 0.5670, 0.5510),
        ("510880", "红利ETF", 10000, 3.0671, 3.0810),
        ("512660", "军工ETF", 6000, 1.5276, 1.5250),
        ("513180", "恒指科技", 800, 0.7686, 0.7590),
        ("515050", "5GETF", 1000, 2.3200, 2.3810),
        ("515070", "AI智能", 400, 1.9388, 2.1280),
        ("588000", "科创50", 1000, 0.3019, 1.6400),
        ("159241", "航空TH", 6000, 1.5319, 1.5350),
        ("159770", "机器人AI", 200, 0.7670, 1.1420),
        ("161226", "白银基金", 500, 4.1510, 4.3360),
    ]
    
    # ETFs.csv中的观察标的 (排除已持有的)
    watch_list = [
        ("159985", "豆粕ETF"),
        ("512890", "红利低波ETF"),
        ("159206", "卫星ETF"),
        ("515790", "光伏ETF"),
        ("516780", "稀土ETF"),
        ("512170", "医疗ETF"),
        ("561330", "矿业ETF"),
        ("159870", "化工ETF"),
        ("561560", "电力ETF"),
        ("159830", "上海金"),
        ("159326", "电网设备ETF"),
        ("159516", "半导体设备ETF"),
        ("518880", "黄金ETF"),
        ("512400", "有色金属ETF"),
        ("513630", "港股红利ETF"),
    ]
    
    print("=" * 60)
    print("持仓调整技术分析 - 2026-01-28")
    print("=" * 60)
    
    # 分析持仓标的
    print("\n>>> 分析持仓标的...")
    holdings_analysis = []
    for code, name, shares, cost, price in holdings:
        print(f"  分析 {name} ({code})...")
        result = analyze_etf(code, name)
        if "error" not in result:
            result["持仓数量"] = shares
            result["成本价"] = cost
            result["市值"] = round(price * shares, 2)
            result["浮盈浮亏"] = round((price - cost) * shares, 2)
            result["盈亏比例"] = round((price - cost) / cost * 100, 2) if cost > 0 else 0
        holdings_analysis.append(result)
    
    # 分析观察标的
    print("\n>>> 分析观察标的...")
    watch_analysis = []
    for code, name in watch_list:
        print(f"  分析 {name} ({code})...")
        result = analyze_etf(code, name)
        watch_analysis.append(result)
    
    # 汇总结果
    all_results = {
        "分析时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "持仓分析": holdings_analysis,
        "观察标的分析": watch_analysis
    }
    
    # 保存为JSON
    output_file = os.path.join(SCRIPT_DIR, 'portfolio_adjustment_data.json')
    clean_results = make_serializable(all_results)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(clean_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 分析完成，数据已保存至: {output_file}")
    
    # 打印持仓诊断摘要
    print("\n" + "=" * 60)
    print("持仓诊断摘要")
    print("=" * 60)
    print(f"{'代码':<10}{'名称':<12}{'现价':<10}{'RSI(6)':<10}{'%B':<10}{'日涨跌%':<10}{'20日涨幅%':<10}")
    print("-" * 60)
    for item in holdings_analysis:
        if "error" not in item:
            print(f"{item['代码']:<10}{item['名称']:<12}{item['现价']:<10}{item['RSI_6']:<10}{item['%B']:<10}{item['日涨跌']:<10}{item['20日涨幅']:<10}")
    
    print("\n" + "=" * 60)
    print("观察标的诊断摘要")
    print("=" * 60)
    print(f"{'代码':<10}{'名称':<12}{'现价':<10}{'RSI(6)':<10}{'%B':<10}{'日涨跌%':<10}{'20日涨幅%':<10}")
    print("-" * 60)
    for item in watch_analysis:
        if "error" not in item:
            print(f"{item['代码']:<10}{item['名称']:<12}{item['现价']:<10}{item['RSI_6']:<10}{item['%B']:<10}{item['日涨跌']:<10}{item['20日涨幅']:<10}")

if __name__ == "__main__":
    main()
