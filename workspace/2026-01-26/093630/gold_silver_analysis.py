#!/usr/bin/env python3
"""
黄金白银深度分析脚本
分析要点:
1. 成交量与布林带突破的关系 (真突破 vs 假突破)
2. 国际金价/银价趋势对比国内ETF
"""

import sys
import os
import json
import pandas as pd
import numpy as np

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

def analyze_volume_breakout(code, name, data, bb):
    """分析量价配合与布林带突破"""
    
    close = data['Close']
    volume = data['Volume']
    bb_upper = bb['Upper']
    bb_lower = bb['Lower']
    bb_middle = bb['Middle']
    
    # 计算成交量指标
    vol_ma_5 = volume.rolling(5).mean()
    vol_ma_20 = volume.rolling(20).mean()
    
    # 最近5天的分析
    print(f"\n{'='*60}")
    print(f"{name} ({code}) 近期量价分析")
    print(f"{'='*60}")
    
    print(f"\n📊 近5个交易日详情:")
    print(f"{'日期':<12} {'收盘价':>10} {'BB上轨':>10} {'BB下轨':>10} {'%B':>8} {'成交量':>15} {'量比(5日)':>10}")
    print("-" * 85)
    
    for i in range(-5, 0):
        date = data.index[i].strftime('%Y-%m-%d')
        c = close.iloc[i]
        upper = bb_upper.iloc[i]
        lower = bb_lower.iloc[i]
        middle = bb_middle.iloc[i]
        pct_b = (c - lower) / (upper - lower) if (upper - lower) > 0 else 0.5
        vol = volume.iloc[i]
        vol_ratio = vol / vol_ma_5.iloc[i] if vol_ma_5.iloc[i] > 0 else 1
        
        # 标记突破
        status = ""
        if pct_b > 1.0:
            status = "⬆️ 破上轨"
        elif pct_b < 0:
            status = "⬇️ 破下轨"
        
        print(f"{date:<12} {c:>10.4f} {upper:>10.4f} {lower:>10.4f} {pct_b:>8.2f} {vol:>15,.0f} {vol_ratio:>10.2f}x {status}")
    
    # 判断布林带突破类型
    latest_pct_b = (close.iloc[-1] - bb_lower.iloc[-1]) / (bb_upper.iloc[-1] - bb_lower.iloc[-1])
    latest_vol_ratio = volume.iloc[-1] / vol_ma_5.iloc[-1]
    vol_20_ratio = volume.iloc[-1] / vol_ma_20.iloc[-1]
    
    # 计算布林带宽度变化
    bb_width = (bb_upper - bb_lower) / bb_middle
    bb_width_expansion = bb_width.iloc[-1] / bb_width.iloc[-5] - 1  # 带宽扩张率
    
    print(f"\n📈 突破性质判断:")
    print(f"  • 当前%B位置: {latest_pct_b:.2f} {'(突破上轨)' if latest_pct_b > 1 else ''}")
    print(f"  • 5日量比: {latest_vol_ratio:.2f}x")
    print(f"  • 20日量比: {vol_20_ratio:.2f}x")
    print(f"  • 布林带带宽扩张: {bb_width_expansion*100:.1f}%")
    
    # 连续突破天数
    breakout_days = 0
    for i in range(-1, -11, -1):
        pct_b = (close.iloc[i] - bb_lower.iloc[i]) / (bb_upper.iloc[i] - bb_lower.iloc[i])
        if pct_b > 1.0:
            breakout_days += 1
        else:
            break
    
    print(f"  • 连续突破上轨天数: {breakout_days} 天")
    
    return {
        'pct_b': latest_pct_b,
        'vol_ratio_5': latest_vol_ratio,
        'vol_ratio_20': vol_20_ratio,
        'bb_width_expansion': bb_width_expansion,
        'breakout_days': breakout_days
    }

def analyze_international_prices():
    """分析国际金价银价"""
    
    print("\n" + "="*60)
    print("🌍 国际金银价格分析 (XAUUSD / XAGUSD)")
    print("="*60)
    
    # 获取国际金价
    try:
        gold_intl = fetch_stock_data('GC=F', period='3mo')  # COMEX Gold Futures
        if gold_intl is not None and not gold_intl.empty:
            gold_rsi = calculate_rsi(gold_intl, window=6)
            gold_bb = calculate_bollinger_bands(gold_intl)
            
            print(f"\n🥇 国际金价 (COMEX Gold Futures)")
            print(f"  • 最新价: ${gold_intl['Close'].iloc[-1]:.2f}")
            print(f"  • RSI(6): {gold_rsi['RSI'].iloc[-1]:.1f}")
            
            gold_pct_b = (gold_intl['Close'].iloc[-1] - gold_bb['Lower'].iloc[-1]) / \
                        (gold_bb['Upper'].iloc[-1] - gold_bb['Lower'].iloc[-1])
            print(f"  • %B位置: {gold_pct_b:.2f}")
            
            # 计算涨跌幅
            gold_return_5d = (gold_intl['Close'].iloc[-1] / gold_intl['Close'].iloc[-5] - 1) * 100
            gold_return_20d = (gold_intl['Close'].iloc[-1] / gold_intl['Close'].iloc[-20] - 1) * 100
            print(f"  • 5日涨幅: {gold_return_5d:+.2f}%")
            print(f"  • 20日涨幅: {gold_return_20d:+.2f}%")
            
            # 趋势判断
            sma_20 = gold_intl['Close'].rolling(20).mean().iloc[-1]
            sma_60 = gold_intl['Close'].rolling(60).mean().iloc[-1]
            print(f"  • SMA20: ${sma_20:.2f}")
            print(f"  • SMA60: ${sma_60:.2f}")
            print(f"  • 趋势: {'多头排列 📈' if gold_intl['Close'].iloc[-1] > sma_20 > sma_60 else '需观察'}")
    except Exception as e:
        print(f"获取国际金价失败: {e}")
    
    # 获取国际银价
    try:
        silver_intl = fetch_stock_data('SI=F', period='3mo')  # COMEX Silver Futures
        if silver_intl is not None and not silver_intl.empty:
            silver_rsi = calculate_rsi(silver_intl, window=6)
            silver_bb = calculate_bollinger_bands(silver_intl)
            
            print(f"\n🥈 国际银价 (COMEX Silver Futures)")
            print(f"  • 最新价: ${silver_intl['Close'].iloc[-1]:.2f}")
            print(f"  • RSI(6): {silver_rsi['RSI'].iloc[-1]:.1f}")
            
            silver_pct_b = (silver_intl['Close'].iloc[-1] - silver_bb['Lower'].iloc[-1]) / \
                          (silver_bb['Upper'].iloc[-1] - silver_bb['Lower'].iloc[-1])
            print(f"  • %B位置: {silver_pct_b:.2f}")
            
            silver_return_5d = (silver_intl['Close'].iloc[-1] / silver_intl['Close'].iloc[-5] - 1) * 100
            silver_return_20d = (silver_intl['Close'].iloc[-1] / silver_intl['Close'].iloc[-20] - 1) * 100
            print(f"  • 5日涨幅: {silver_return_5d:+.2f}%")
            print(f"  • 20日涨幅: {silver_return_20d:+.2f}%")
            
            sma_20 = silver_intl['Close'].rolling(20).mean().iloc[-1]
            sma_60 = silver_intl['Close'].rolling(60).mean().iloc[-1]
            print(f"  • SMA20: ${sma_20:.2f}")
            print(f"  • SMA60: ${sma_60:.2f}")
            print(f"  • 趋势: {'多头排列 📈' if silver_intl['Close'].iloc[-1] > sma_20 > sma_60 else '需观察'}")
    except Exception as e:
        print(f"获取国际银价失败: {e}")

def main():
    # 分析国内贵金属ETF
    etfs = [
        ('159830', '上海金ETF'),
        ('161226', '白银LOF'),
        ('518880', '黄金ETF'),
    ]
    
    results = {}
    
    for code, name in etfs:
        print(f"\n正在分析: {code} - {name}")
        data = fetch_stock_data(code, period='3mo')
        
        if data is not None and not data.empty:
            bb = calculate_bollinger_bands(data)
            rsi = calculate_rsi(data, window=6)
            
            result = analyze_volume_breakout(code, name, data, bb)
            result['rsi_6'] = rsi['RSI'].iloc[-1]
            result['close'] = data['Close'].iloc[-1]
            results[code] = result
    
    # 分析国际金银价格
    analyze_international_prices()
    
    # 综合判断
    print("\n" + "="*60)
    print("🔍 综合判断: 真突破 vs 假突破")
    print("="*60)
    
    print("""
📚 布林带突破判断框架:

【真突破特征】
1. 放量突破 + 带宽扩张 + 连续收于轨外
2. 成交量是5日均量的1.5倍以上
3. 布林带带宽明显扩张 (>10%)
4. 价格连续3天以上收于轨外
5. RSI未达到极值 (通常<80)

【假突破特征】
1. 缩量或正常量突破
2. 带宽未明显扩张
3. 仅1-2天触及轨外后回落
4. RSI已达极值 (>85-90)
5. 出现长上影线

【当前判断】
""")
    
    for code, r in results.items():
        print(f"\n{code}:")
        
        # 综合评分
        score = 0
        reasons = []
        
        if r['vol_ratio_5'] > 1.5:
            score += 1
            reasons.append(f"✅ 放量 ({r['vol_ratio_5']:.1f}x)")
        else:
            reasons.append(f"❌ 量能不足 ({r['vol_ratio_5']:.1f}x)")
        
        if r['bb_width_expansion'] > 0.1:
            score += 1
            reasons.append(f"✅ 带宽扩张 ({r['bb_width_expansion']*100:.0f}%)")
        else:
            reasons.append(f"⚠️ 带宽变化小 ({r['bb_width_expansion']*100:.0f}%)")
        
        if r['breakout_days'] >= 3:
            score += 1
            reasons.append(f"✅ 连续突破 ({r['breakout_days']}天)")
        else:
            reasons.append(f"⚠️ 连续性弱 ({r['breakout_days']}天)")
        
        if r['rsi_6'] < 80:
            score += 1
            reasons.append(f"✅ RSI未极值 ({r['rsi_6']:.1f})")
        else:
            reasons.append(f"❌ RSI极值 ({r['rsi_6']:.1f})")
        
        for reason in reasons:
            print(f"  {reason}")
        
        verdict = "真突破可能性高 📈" if score >= 3 else "假突破风险大 ⚠️" if score <= 1 else "需谨慎观察 🤔"
        print(f"  → 结论: {verdict} (得分 {score}/4)")
    
    # 保存结果
    output_path = os.path.join(SCRIPT_DIR, 'gold_silver_analysis.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(make_serializable(results), f, indent=4, ensure_ascii=False)
    
    print(f"\n数据已保存至: {output_path}")

if __name__ == "__main__":
    main()
