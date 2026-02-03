#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
分析黄金和白银近期走势
"""

import sys
import os
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

# 设置输出目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 添加 quantitative-trading skill 路径
SKILL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../.agent/skills/quantitative-trading'))
sys.path.append(SKILL_DIR)

from scripts import calculate_rsi, calculate_macd, calculate_sma
from scripts.utils import make_serializable

print("=" * 60)
print("黄金和白银技术分析")
print("=" * 60)

# 获取黄金数据 (XAUUSD)
print("\n📊 获取黄金(XAUUSD)数据...")
try:
    gold = yf.download('GC=F', period='3mo', progress=False)  # Gold Futures
    print(f"✅ 成功获取 {len(gold)} 条数据")
    
    # 计算技术指标
    gold_rsi = calculate_rsi(gold, window=14)
    gold_macd = calculate_macd(gold)
    gold_sma20 = calculate_sma(gold, window=20)
    gold_sma50 = calculate_sma(gold, window=50)
    
    # 最新数据
    latest_gold = gold.iloc[-1]
    latest_rsi = gold_rsi['RSI'].iloc[-1]
    latest_macd = gold_macd['MACD'].iloc[-1]
    latest_signal = gold_macd['Signal'].iloc[-1]
    latest_sma20 = gold_sma20['SMA'].iloc[-1]
    latest_sma50 = gold_sma50['SMA'].iloc[-1]
    
    # 计算跌幅
    gold_1d_change = ((latest_gold['Close'] / gold.iloc[-2]['Close']) - 1) * 100
    gold_1w_change = ((latest_gold['Close'] / gold.iloc[-5]['Close']) - 1) * 100 if len(gold) >= 5 else 0
    gold_1m_change = ((latest_gold['Close'] / gold.iloc[-20]['Close']) - 1) * 100 if len(gold) >= 20 else 0
    
    print(f"\n【黄金技术分析】")
    print(f"  最新价格: ${latest_gold['Close']:.2f}")
    print(f"  1日涨跌: {gold_1d_change:+.2f}%")
    print(f"  1周涨跌: {gold_1w_change:+.2f}%")
    print(f"  1月涨跌: {gold_1m_change:+.2f}%")
    print(f"  RSI(14): {latest_rsi:.2f}")
    print(f"  MACD: {latest_macd:.2f} (Signal: {latest_signal:.2f})")
    print(f"  SMA20: ${latest_sma20:.2f}")
    print(f"  SMA50: ${latest_sma50:.2f}")
    
    # 技术信号
    print(f"\n  技术信号:")
    if latest_rsi < 30:
        print(f"    - RSI超卖 (< 30)")
    elif latest_rsi > 70:
        print(f"    - RSI超买 (> 70)")
    else:
        print(f"    - RSI中性区域")
    
    if latest_gold['Close'] < latest_sma20:
        print(f"    - 价格低于SMA20，短期趋势偏弱")
    if latest_gold['Close'] < latest_sma50:
        print(f"    - 价格低于SMA50，中期趋势偏弱")
    
    if latest_macd < latest_signal:
        print(f"    - MACD死叉，动能转弱")
    
except Exception as e:
    print(f"❌ 黄金数据获取失败: {e}")

# 获取白银数据 (XAGUSD)
print("\n📊 获取白银(XAGUSD)数据...")
try:
    silver = yf.download('SI=F', period='3mo', progress=False)  # Silver Futures
    print(f"✅ 成功获取 {len(silver)} 条数据")
    
    # 计算技术指标
    silver_rsi = calculate_rsi(silver, window=14)
    silver_macd = calculate_macd(silver)
    silver_sma20 = calculate_sma(silver, window=20)
    silver_sma50 = calculate_sma(silver, window=50)
    
    # 最新数据
    latest_silver = silver.iloc[-1]
    latest_rsi_s = silver_rsi['RSI'].iloc[-1]
    latest_macd_s = silver_macd['MACD'].iloc[-1]
    latest_signal_s = silver_macd['Signal'].iloc[-1]
    latest_sma20_s = silver_sma20['SMA'].iloc[-1]
    latest_sma50_s = silver_sma50['SMA'].iloc[-1]
    
    # 计算跌幅
    silver_1d_change = ((latest_silver['Close'] / silver.iloc[-2]['Close']) - 1) * 100
    silver_1w_change = ((latest_silver['Close'] / silver.iloc[-5]['Close']) - 1) * 100 if len(silver) >= 5 else 0
    silver_1m_change = ((latest_silver['Close'] / silver.iloc[-20]['Close']) - 1) * 100 if len(silver) >= 20 else 0
    
    print(f"\n【白银技术分析】")
    print(f"  最新价格: ${latest_silver['Close']:.2f}")
    print(f"  1日涨跌: {silver_1d_change:+.2f}%")
    print(f"  1周涨跌: {silver_1w_change:+.2f}%")
    print(f"  1月涨跌: {silver_1m_change:+.2f}%")
    print(f"  RSI(14): {latest_rsi_s:.2f}")
    print(f"  MACD: {latest_macd_s:.2f} (Signal: {latest_signal_s:.2f})")
    print(f"  SMA20: ${latest_sma20_s:.2f}")
    print(f"  SMA50: ${latest_sma50_s:.2f}")
    
    # 技术信号
    print(f"\n  技术信号:")
    if latest_rsi_s < 30:
        print(f"    - RSI超卖 (< 30)")
    elif latest_rsi_s > 70:
        print(f"    - RSI超买 (> 70)")
    else:
        print(f"    - RSI中性区域")
    
    if latest_silver['Close'] < latest_sma20_s:
        print(f"    - 价格低于SMA20，短期趋势偏弱")
    if latest_silver['Close'] < latest_sma50_s:
        print(f"    - 价格低于SMA50，中期趋势偏弱")
    
    if latest_macd_s < latest_signal_s:
        print(f"    - MACD死叉，动能转弱")
    
except Exception as e:
    print(f"❌ 白银数据获取失败: {e}")

print("\n" + "=" * 60)
print("技术分析完成")
print("=" * 60)
