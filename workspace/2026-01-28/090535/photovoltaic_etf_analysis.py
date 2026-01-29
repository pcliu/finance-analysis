#!/usr/bin/env python3
"""
光伏ETF (515790) 深度技术分析
分析MACD金叉、趋势启动信号
"""

import sys
import os
import json
from datetime import datetime

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

def analyze_macd_crossover(macd_data, lookback=10):
    """分析MACD金叉/死叉情况"""
    macd_line = macd_data['MACD']
    signal_line = macd_data['Signal']
    histogram = macd_data['Histogram']
    
    crossovers = []
    for i in range(-lookback, 0):
        prev_hist = histogram.iloc[i-1]
        curr_hist = histogram.iloc[i]
        
        # 金叉：柱状图从负转正
        if prev_hist < 0 and curr_hist > 0:
            crossovers.append({
                'index': i,
                'type': '金叉',
                'date': str(histogram.index[i].date()),
                'macd': float(macd_line.iloc[i]),
                'signal': float(signal_line.iloc[i]),
                'histogram': float(curr_hist)
            })
        # 死叉：柱状图从正转负
        elif prev_hist > 0 and curr_hist < 0:
            crossovers.append({
                'index': i,
                'type': '死叉',
                'date': str(histogram.index[i].date()),
                'macd': float(macd_line.iloc[i]),
                'signal': float(signal_line.iloc[i]),
                'histogram': float(curr_hist)
            })
    
    return crossovers

def main():
    code = "515790"
    name = "光伏ETF"
    
    print("=" * 70)
    print(f"光伏ETF (515790) 深度技术分析")
    print("=" * 70)
    
    # 获取数据
    data = fetch_stock_data(code, period='6mo')
    if data is None or len(data) < 50:
        print("无法获取足够的历史数据")
        return
    
    # 计算指标
    rsi_6 = calculate_rsi(data, window=6)['RSI']
    rsi_14 = calculate_rsi(data, window=14)['RSI']
    macd_data = calculate_macd(data)
    bb_data = calculate_bollinger_bands(data, window=20)
    sma_5 = calculate_sma(data, window=5)['SMA']
    sma_10 = calculate_sma(data, window=10)['SMA']
    sma_20 = calculate_sma(data, window=20)['SMA']
    sma_60 = calculate_sma(data, window=60)['SMA']
    atr = calculate_atr(data, window=14)['ATR']
    
    # 当前值
    current_price = float(data['Close'].iloc[-1])
    current_macd = float(macd_data['MACD'].iloc[-1])
    current_signal = float(macd_data['Signal'].iloc[-1])
    current_hist = float(macd_data['Histogram'].iloc[-1])
    
    # %B计算
    upper = float(bb_data['Upper'].iloc[-1])
    lower = float(bb_data['Lower'].iloc[-1])
    percent_b = (current_price - lower) / (upper - lower)
    
    print(f"\n📊 当前技术指标 ({data.index[-1].date()})")
    print("-" * 70)
    print(f"  现价: {current_price:.4f}")
    print(f"  RSI(6): {rsi_6.iloc[-1]:.2f}")
    print(f"  RSI(14): {rsi_14.iloc[-1]:.2f}")
    print(f"  %B: {percent_b:.2f}")
    print(f"\n  MACD线: {current_macd:.4f}")
    print(f"  Signal线: {current_signal:.4f}")
    print(f"  MACD柱: {current_hist:.4f} {'(正)' if current_hist > 0 else '(负)'}")
    
    # 分析MACD金叉
    print(f"\n📈 MACD交叉分析 (近20日)")
    print("-" * 70)
    crossovers = analyze_macd_crossover(macd_data, lookback=20)
    
    if crossovers:
        for cross in crossovers:
            symbol = "🔺" if cross['type'] == '金叉' else "🔻"
            print(f"  {symbol} {cross['date']}: {cross['type']}")
            print(f"     MACD={cross['macd']:.4f}, Signal={cross['signal']:.4f}, Hist={cross['histogram']:.4f}")
    else:
        print("  近20日内无明显金叉/死叉信号")
    
    # 判断当前MACD状态
    print(f"\n🔍 MACD状态诊断")
    print("-" * 70)
    
    # MACD线趋势
    macd_trend = "上升" if macd_data['MACD'].iloc[-1] > macd_data['MACD'].iloc[-3] else "下降"
    signal_trend = "上升" if macd_data['Signal'].iloc[-1] > macd_data['Signal'].iloc[-3] else "下降"
    hist_trend = "放大" if abs(current_hist) > abs(macd_data['Histogram'].iloc[-3]) else "收缩"
    
    print(f"  MACD线趋势: {macd_trend}")
    print(f"  Signal线趋势: {signal_trend}")
    print(f"  柱状图趋势: {hist_trend}")
    print(f"  MACD > Signal: {'是' if current_macd > current_signal else '否'} (金叉状态)")
    print(f"  MACD > 0轴: {'是' if current_macd > 0 else '否'} (多头区域)")
    
    # 显示近10日MACD走势
    print(f"\n📉 近10日MACD柱状图走势")
    print("-" * 70)
    for i in range(-10, 0):
        date = data.index[i].date()
        hist = macd_data['Histogram'].iloc[i]
        price = data['Close'].iloc[i]
        bar = "▊" * min(int(abs(hist) * 200), 30)
        sign = "+" if hist > 0 else "-"
        color = "🟢" if hist > 0 else "🔴"
        print(f"  {date} | 价格:{price:.3f} | {color} {sign}{abs(hist):.4f} {bar}")
    
    # 均线分析
    print(f"\n📊 均线系统分析")
    print("-" * 70)
    print(f"  SMA5:  {sma_5.iloc[-1]:.4f} (价格{'>' if current_price > sma_5.iloc[-1] else '<'}MA5)")
    print(f"  SMA10: {sma_10.iloc[-1]:.4f} (价格{'>' if current_price > sma_10.iloc[-1] else '<'}MA10)")
    print(f"  SMA20: {sma_20.iloc[-1]:.4f} (价格{'>' if current_price > sma_20.iloc[-1] else '<'}MA20)")
    print(f"  SMA60: {sma_60.iloc[-1]:.4f} (价格{'>' if current_price > sma_60.iloc[-1] else '<'}MA60)")
    
    # 均线排列
    ma_order = []
    if sma_5.iloc[-1] > sma_10.iloc[-1] > sma_20.iloc[-1]:
        ma_order.append("短期多头排列 (MA5>MA10>MA20)")
    if sma_10.iloc[-1] > sma_20.iloc[-1] > sma_60.iloc[-1]:
        ma_order.append("中期多头排列 (MA10>MA20>MA60)")
    if current_price > sma_5.iloc[-1] > sma_10.iloc[-1] > sma_20.iloc[-1] > sma_60.iloc[-1]:
        ma_order.append("完美多头排列 (价格>MA5>MA10>MA20>MA60)")
    
    if ma_order:
        for order in ma_order:
            print(f"  ✅ {order}")
    else:
        print(f"  ⚠️ 均线系统尚未完全多头排列")
    
    # 成交量分析
    print(f"\n📊 成交量分析")
    print("-" * 70)
    vol_ma5 = data['Volume'].rolling(5).mean()
    vol_ma20 = data['Volume'].rolling(20).mean()
    current_vol = data['Volume'].iloc[-1]
    
    print(f"  今日成交量: {current_vol:,.0f}")
    print(f"  5日均量: {vol_ma5.iloc[-1]:,.0f}")
    print(f"  20日均量: {vol_ma20.iloc[-1]:,.0f}")
    print(f"  量比(vs 20日均): {current_vol/vol_ma20.iloc[-1]:.2f}x")
    
    # 综合判断
    print(f"\n" + "=" * 70)
    print("📋 综合技术诊断")
    print("=" * 70)
    
    # 计算趋势得分
    score = 0
    details = []
    
    # MACD信号
    if current_hist > 0:
        score += 2
        details.append("✅ MACD柱状图为正 (+2)")
    if current_macd > current_signal:
        score += 2
        details.append("✅ MACD线在Signal线上方 (+2)")
    if current_macd > 0:
        score += 1
        details.append("✅ MACD在0轴上方 (+1)")
    if hist_trend == "放大" and current_hist > 0:
        score += 2
        details.append("✅ MACD红柱放大 (+2)")
    
    # RSI信号
    if 50 < rsi_6.iloc[-1] < 80:
        score += 1
        details.append(f"✅ RSI(6)={rsi_6.iloc[-1]:.1f}处于健康上升区 (+1)")
    elif rsi_6.iloc[-1] >= 80:
        score -= 1
        details.append(f"⚠️ RSI(6)={rsi_6.iloc[-1]:.1f}已进入超买区 (-1)")
    
    # 均线信号
    if current_price > sma_20.iloc[-1]:
        score += 1
        details.append("✅ 价格站上MA20 (+1)")
    if sma_5.iloc[-1] > sma_20.iloc[-1]:
        score += 1
        details.append("✅ MA5上穿MA20 (+1)")
    
    # 布林带信号
    if 0.5 < percent_b < 0.95:
        score += 1
        details.append(f"✅ %B={percent_b:.2f}处于上升通道 (+1)")
    elif percent_b >= 0.95:
        score -= 1
        details.append(f"⚠️ %B={percent_b:.2f}逼近上轨 (-1)")
    
    for d in details:
        print(f"  {d}")
    
    print(f"\n  📊 综合得分: {score}/11")
    
    if score >= 8:
        verdict = "🟢 强烈看多 - 趋势确认，可积极布局"
    elif score >= 6:
        verdict = "🟢 看多 - 趋势启动，可择机介入"
    elif score >= 4:
        verdict = "🟡 中性偏多 - 趋势形成中，可小仓位试探"
    elif score >= 2:
        verdict = "🟡 中性 - 方向不明，建议观望"
    else:
        verdict = "🔴 看空/观望 - 趋势未确立"
    
    print(f"\n  📌 技术面结论: {verdict}")
    
    # 输出完整数据
    results = {
        "代码": code,
        "名称": name,
        "分析时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "当前指标": {
            "现价": current_price,
            "RSI_6": float(rsi_6.iloc[-1]),
            "RSI_14": float(rsi_14.iloc[-1]),
            "%B": round(percent_b, 2),
            "MACD": current_macd,
            "Signal": current_signal,
            "Histogram": current_hist,
            "SMA_5": float(sma_5.iloc[-1]),
            "SMA_10": float(sma_10.iloc[-1]),
            "SMA_20": float(sma_20.iloc[-1]),
            "SMA_60": float(sma_60.iloc[-1]),
        },
        "MACD交叉": crossovers,
        "综合得分": score,
        "结论": verdict
    }
    
    output_file = os.path.join(SCRIPT_DIR, 'photovoltaic_etf_analysis.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(make_serializable(results), f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 详细数据已保存至: {output_file}")

if __name__ == "__main__":
    main()
