#!/usr/bin/env python3
"""
调仓方案评估分析
评估用户提出的军工/航空减仓、恒指清仓、光伏建仓方案
"""

import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../.agent/skills/quantitative-trading'))
sys.path.append(SKILL_DIR)

from scripts import fetch_stock_data, calculate_rsi, calculate_macd, calculate_bollinger_bands, calculate_sma

def analyze_etf(code, name):
    """获取ETF技术指标"""
    data = fetch_stock_data(code, period='3mo')
    if data is None or len(data) < 20:
        return None
    
    rsi_6 = calculate_rsi(data, window=6)['RSI']
    macd_data = calculate_macd(data)
    bb_data = calculate_bollinger_bands(data, window=20)
    sma_20 = calculate_sma(data, window=20)['SMA']
    
    current_price = float(data['Close'].iloc[-1])
    upper = float(bb_data['Upper'].iloc[-1])
    lower = float(bb_data['Lower'].iloc[-1])
    percent_b = (current_price - lower) / (upper - lower)
    
    # 检查近5日MACD柱状图趋势
    hist_recent = macd_data['Histogram'].iloc[-5:]
    hist_trend = "放大" if abs(hist_recent.iloc[-1]) > abs(hist_recent.iloc[-3]) else "收缩"
    
    return {
        "代码": code,
        "名称": name,
        "现价": current_price,
        "RSI_6": float(rsi_6.iloc[-1]),
        "MACD": float(macd_data['MACD'].iloc[-1]),
        "Signal": float(macd_data['Signal'].iloc[-1]),
        "Histogram": float(macd_data['Histogram'].iloc[-1]),
        "MACD状态": "金叉" if macd_data['Histogram'].iloc[-1] > 0 else "死叉",
        "柱状图趋势": hist_trend,
        "%B": round(percent_b, 2),
        "SMA_20": float(sma_20.iloc[-1]),
        "距MA20": round((current_price - sma_20.iloc[-1]) / sma_20.iloc[-1] * 100, 2)
    }

def main():
    targets = [
        ("512660", "军工ETF"),
        ("159241", "航空TH"),
        ("513180", "恒指科技"),
        ("515790", "光伏ETF"),
    ]
    
    print("=" * 80)
    print("调仓方案技术面评估")
    print("=" * 80)
    
    for code, name in targets:
        result = analyze_etf(code, name)
        if result:
            print(f"\n📊 {name} ({code})")
            print("-" * 60)
            print(f"  现价: {result['现价']:.4f} | RSI(6): {result['RSI_6']:.1f} | %B: {result['%B']:.2f}")
            print(f"  MACD: {result['MACD']:.4f} | Signal: {result['Signal']:.4f}")
            print(f"  MACD柱: {result['Histogram']:.4f} | 状态: {result['MACD状态']} | 趋势: {result['柱状图趋势']}")
            print(f"  SMA20: {result['SMA_20']:.4f} | 距MA20: {result['距MA20']:+.2f}%")
            
            # 技术面判断
            if result['Histogram'] > 0:
                print(f"  ✅ MACD金叉状态")
            else:
                print(f"  ⚠️ MACD死叉状态")
            
            if result['RSI_6'] > 70:
                print(f"  ⚠️ RSI偏高，注意追高风险")
            elif result['RSI_6'] < 40:
                print(f"  🟢 RSI偏低，可能存在低吸机会")
            else:
                print(f"  🟡 RSI处于健康区间")

if __name__ == "__main__":
    main()
