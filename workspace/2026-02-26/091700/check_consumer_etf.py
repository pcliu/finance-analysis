#!/usr/bin/env python3
"""Quick check on 消费ETF (510150) after today's close"""

import sys
import os
import json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../.agent/skills/quantitative-trading'))
sys.path.append(SKILL_DIR)

from scripts import fetch_stock_data, calculate_rsi, calculate_macd, calculate_bollinger_bands
from scripts.utils import make_serializable

code = '510150'
print(f"=== 消费ETF ({code}) 收盘后诊断 ===\n")

data = fetch_stock_data(code, period='6mo')

# RSI
rsi_df = calculate_rsi(data, window=14)
rsi_now = rsi_df['RSI'].iloc[-1]
rsi_prev = rsi_df['RSI'].iloc[-2]
rsi_prev2 = rsi_df['RSI'].iloc[-3]

# MACD
macd_df = calculate_macd(data)
macd_now = macd_df['MACD'].iloc[-1]
signal_now = macd_df['Signal'].iloc[-1]
hist_now = macd_df['Histogram'].iloc[-1]
hist_prev = macd_df['Histogram'].iloc[-2]

# Bollinger
bb_df = calculate_bollinger_bands(data)
close = data['Close'].iloc[-1]
bb_upper = bb_df['Upper'].iloc[-1]
bb_lower = bb_df['Lower'].iloc[-1]
bb_middle = bb_df['Middle'].iloc[-1]
pct_b = (close - bb_lower) / (bb_upper - bb_lower) if (bb_upper - bb_lower) > 0 else 0.5

# Volume
vol = data['Volume']
vol_ma20 = vol.rolling(window=20).mean()
vol_ratio = vol.iloc[-1] / vol_ma20.iloc[-1] if vol_ma20.iloc[-1] > 0 else 0

# Price changes
change_1d = (data['Close'].iloc[-1] / data['Close'].iloc[-2] - 1) * 100
change_3d = (data['Close'].iloc[-1] / data['Close'].iloc[-4] - 1) * 100
change_5d = (data['Close'].iloc[-1] / data['Close'].iloc[-6] - 1) * 100
change_10d = (data['Close'].iloc[-1] / data['Close'].iloc[-11] - 1) * 100

# Recent prices
print("最近5日价格走势：")
for i in range(-5, 0):
    d = data.index[i].strftime('%m/%d')
    c = data['Close'].iloc[i]
    r = rsi_df['RSI'].iloc[i]
    print(f"  {d}: 收盘 {c:.3f}, RSI={r:.1f}")

print(f"\n--- 关键指标 ---")
print(f"今日收盘价: {close:.3f}")
print(f"RSI: {rsi_now:.1f} (前日 {rsi_prev:.1f}, 前前日 {rsi_prev2:.1f})")
print(f"%B: {pct_b:.3f}")
print(f"MACD: {macd_now:.6f}, Signal: {signal_now:.6f}")
print(f"Histogram: {hist_now:.6f} (前日 {hist_prev:.6f})")
print(f"MACD状态: {'金叉' if macd_now > signal_now else '死叉'}")
print(f"  死叉加深: {'是' if abs(hist_now) > abs(hist_prev) and hist_now < 0 else '否'}")
print(f"布林带: 上轨={bb_upper:.3f}, 中轨={bb_middle:.3f}, 下轨={bb_lower:.3f}")
print(f"成交量比: {vol_ratio:.2f}")
print(f"\n--- 涨跌幅 ---")
print(f"1日: {change_1d:+.2f}%")
print(f"3日: {change_3d:+.2f}%")
print(f"5日: {change_5d:+.2f}%")
print(f"10日: {change_10d:+.2f}%")

# Position analysis
cost = 0.5559
shares = 38000
market_value = close * shares
profit = (close - cost) * shares
profit_pct = (close / cost - 1) * 100

print(f"\n--- 持仓分析 ---")
print(f"成本: {cost:.4f}")
print(f"现价: {close:.3f}")
print(f"市值: {market_value:.0f} 元")
print(f"浮盈/亏: {profit:+.0f} 元 ({profit_pct:+.2f}%)")

# Alert check
print(f"\n--- 风控检查 ---")
print(f"RSI < 38 减仓线: {'⚠️ 触发!' if rsi_now < 38 else f'未触发 (当前 {rsi_now:.1f})'}")
print(f"RSI < 38 连续2日: {'⚠️ 触发!' if rsi_now < 38 and rsi_prev < 38 else '未触发'}")
print(f"%B < 0.15 减仓线: {'⚠️ 触发!' if pct_b < 0.15 else f'未触发 (当前 {pct_b:.3f})'}")
print(f"止损线 0.535: {'⚠️ 接近!' if close < 0.540 else f'未触发 (距离 {(close-0.535)/close*100:.1f}%)'}")
print(f"连续下跌天数: ", end="")
consecutive_down = 0
for i in range(-1, -11, -1):
    if data['Close'].iloc[i] < data['Close'].iloc[i-1]:
        consecutive_down += 1
    else:
        break
print(f"{consecutive_down} 天")
