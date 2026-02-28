#!/usr/bin/env python3
"""
GOOG (Alphabet Inc.) 技术面分析
分析日期: 2026-02-24
"""

import sys
import os
import json

# Robust Import
SKILL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../.agent/skills/quantitative-trading'))
sys.path.append(SKILL_DIR)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

from scripts import (
    fetch_stock_data,
    calculate_rsi,
    calculate_sma,
    calculate_macd,
    calculate_bollinger_bands,
    calculate_atr,
    calculate_adx,
    calculate_stochastic,
    calculate_williams_r,
)
from scripts.utils import make_serializable

TICKER = 'GOOG'

# ── 1. 获取数据 ──────────────────────────────────────────
print(f"[1/6] 获取 {TICKER} 历史数据 (1年)...")
data = fetch_stock_data(TICKER, period='1y')
if data is None or data.empty:
    print(f"ERROR: 无法获取 {TICKER} 数据")
    sys.exit(1)

print(f"  数据范围: {data.index[0].strftime('%Y-%m-%d')} → {data.index[-1].strftime('%Y-%m-%d')}")
print(f"  数据条数: {len(data)}")

# ── 2. 计算技术指标 ──────────────────────────────────────
print(f"\n[2/6] 计算技术指标...")

# RSI
rsi_df = calculate_rsi(data, window=14)
current_rsi = rsi_df['RSI'].iloc[-1]
prev_rsi = rsi_df['RSI'].iloc[-2]

# MACD
macd_df = calculate_macd(data)
current_macd = macd_df['MACD'].iloc[-1]
current_signal = macd_df['Signal'].iloc[-1]
current_histogram = macd_df['Histogram'].iloc[-1]
prev_histogram = macd_df['Histogram'].iloc[-2]

# SMA
sma5_df = calculate_sma(data, window=5)
sma10_df = calculate_sma(data, window=10)
sma20_df = calculate_sma(data, window=20)
sma50_df = calculate_sma(data, window=50)
sma120_df = calculate_sma(data, window=120)
sma200_df = calculate_sma(data, window=200)

current_sma5 = sma5_df['SMA'].iloc[-1]
current_sma10 = sma10_df['SMA'].iloc[-1]
current_sma20 = sma20_df['SMA'].iloc[-1]
current_sma50 = sma50_df['SMA'].iloc[-1]
current_sma120 = sma120_df['SMA'].iloc[-1]
current_sma200 = sma200_df['SMA'].iloc[-1] if len(sma200_df['SMA'].dropna()) > 0 else None

# Bollinger Bands
bb_df = calculate_bollinger_bands(data, window=20, num_std=2)
current_bb_upper = bb_df['Upper'].iloc[-1]
current_bb_middle = bb_df['Middle'].iloc[-1]
current_bb_lower = bb_df['Lower'].iloc[-1]

# %B (Bollinger %B)
current_price = data['Close'].iloc[-1]
bb_pct_b = (current_price - current_bb_lower) / (current_bb_upper - current_bb_lower) if (current_bb_upper - current_bb_lower) != 0 else 0.5
bb_width = (current_bb_upper - current_bb_lower) / current_bb_middle * 100  # 带宽百分比

# ATR
atr_df = calculate_atr(data, window=14)
current_atr = atr_df['ATR'].iloc[-1]
atr_pct = current_atr / current_price * 100  # ATR占价格百分比

# ADX
adx_df = calculate_adx(data, window=14)
current_adx = adx_df['ADX'].iloc[-1]

# Stochastic
stoch_df = calculate_stochastic(data)
current_k = stoch_df['K'].iloc[-1]
current_d = stoch_df['D'].iloc[-1]

# Williams %R
wr_df = calculate_williams_r(data, window=14)
current_wr = wr_df['Williams_R'].iloc[-1]

# ── 3. 成交量分析 ──────────────────────────────────────
print(f"\n[3/6] 成交量分析...")
vol_5 = data['Volume'].tail(5).mean()
vol_20 = data['Volume'].tail(20).mean()
vol_60 = data['Volume'].tail(60).mean()
vol_ratio = vol_5 / vol_20 if vol_20 > 0 else 1.0
current_vol = data['Volume'].iloc[-1]

# ── 4. 价格变动分析 ──────────────────────────────────────
print(f"\n[4/6] 价格变动分析...")
# 近期涨跌幅
price_1d = (data['Close'].iloc[-1] / data['Close'].iloc[-2] - 1) * 100
price_5d = (data['Close'].iloc[-1] / data['Close'].iloc[-5] - 1) * 100
price_20d = (data['Close'].iloc[-1] / data['Close'].iloc[-20] - 1) * 100
price_60d = (data['Close'].iloc[-1] / data['Close'].iloc[-60] - 1) * 100

# 52周高低点
high_52w = data['High'].max()
low_52w = data['Low'].min()
pct_from_high = (current_price / high_52w - 1) * 100
pct_from_low = (current_price / low_52w - 1) * 100

# ── 5. 综合研判 ──────────────────────────────────────
print(f"\n[5/6] 综合技术研判...")

# 信号分析
signals = []
bullish_count = 0
bearish_count = 0
neutral_count = 0

# RSI 信号
if current_rsi > 70:
    signals.append(("RSI", "⚠️ 超买", f"RSI={current_rsi:.1f}, 处于超买区域，存在回调风险"))
    bearish_count += 1
elif current_rsi < 30:
    signals.append(("RSI", "🟢 超卖", f"RSI={current_rsi:.1f}, 处于超卖区域，可能迎来反弹"))
    bullish_count += 1
elif current_rsi > 60:
    signals.append(("RSI", "🟢 偏强", f"RSI={current_rsi:.1f}, 动能较强"))
    bullish_count += 1
elif current_rsi < 40:
    signals.append(("RSI", "🔴 偏弱", f"RSI={current_rsi:.1f}, 动能较弱"))
    bearish_count += 1
else:
    signals.append(("RSI", "⚪ 中性", f"RSI={current_rsi:.1f}, 处于中性区域"))
    neutral_count += 1

# MACD 信号
if current_macd > current_signal and current_histogram > 0:
    if prev_histogram <= 0:
        signals.append(("MACD", "🟢 金叉", f"MACD({current_macd:.2f}) > Signal({current_signal:.2f}), 刚形成金叉"))
    else:
        signals.append(("MACD", "🟢 多头", f"MACD({current_macd:.2f}) > Signal({current_signal:.2f}), 维持多头"))
    bullish_count += 1
elif current_macd < current_signal and current_histogram < 0:
    if prev_histogram >= 0:
        signals.append(("MACD", "🔴 死叉", f"MACD({current_macd:.2f}) < Signal({current_signal:.2f}), 刚形成死叉"))
    else:
        signals.append(("MACD", "🔴 空头", f"MACD({current_macd:.2f}) < Signal({current_signal:.2f}), 维持空头"))
    bearish_count += 1

# 均线排列
if current_sma5 > current_sma10 > current_sma20 > current_sma50:
    signals.append(("均线", "🟢 多头排列", "MA5>MA10>MA20>MA50, 强势多头排列"))
    bullish_count += 1
elif current_sma5 < current_sma10 < current_sma20 < current_sma50:
    signals.append(("均线", "🔴 空头排列", "MA5<MA10<MA20<MA50, 空头排列"))
    bearish_count += 1
else:
    signals.append(("均线", "⚪ 交织", "均线系统交织，趋势不明"))
    neutral_count += 1

# 布林带位置
if bb_pct_b > 0.8:
    signals.append(("布林带", "⚠️ 接近上轨", f"%B={bb_pct_b:.2f}, 可能面临压力"))
    bearish_count += 1
elif bb_pct_b < 0.2:
    signals.append(("布林带", "🟢 接近下轨", f"%B={bb_pct_b:.2f}, 可能获得支撑"))
    bullish_count += 1
else:
    signals.append(("布林带", "⚪ 通道中部", f"%B={bb_pct_b:.2f}, 处于通道中部"))
    neutral_count += 1

# ADX 趋势强度
if current_adx > 25:
    signals.append(("ADX", "📈 趋势明确", f"ADX={current_adx:.1f}, 当前趋势较强"))
else:
    signals.append(("ADX", "〰️ 无明确趋势", f"ADX={current_adx:.1f}, 当前趋势不明确，震荡市"))

# Stochastic
if current_k > 80 and current_d > 80:
    signals.append(("KDJ", "⚠️ 超买", f"K={current_k:.1f}, D={current_d:.1f}"))
    bearish_count += 1
elif current_k < 20 and current_d < 20:
    signals.append(("KDJ", "🟢 超卖", f"K={current_k:.1f}, D={current_d:.1f}"))
    bullish_count += 1
else:
    signals.append(("KDJ", "⚪ 中性", f"K={current_k:.1f}, D={current_d:.1f}"))
    neutral_count += 1

# 量价配合
if vol_ratio > 1.5:
    signals.append(("成交量", "📊 放量", f"5日均量/20日均量={vol_ratio:.2f}, 显著放量"))
elif vol_ratio < 0.7:
    signals.append(("成交量", "📉 缩量", f"5日均量/20日均量={vol_ratio:.2f}, 明显缩量"))
else:
    signals.append(("成交量", "⚪ 正常", f"5日均量/20日均量={vol_ratio:.2f}, 量能正常"))

# 价格相对均线
if current_price > current_sma20:
    signals.append(("价格位置", "🟢 在20日均线上方", f"价格({current_price:.2f}) > SMA20({current_sma20:.2f})"))
    bullish_count += 1
else:
    signals.append(("价格位置", "🔴 在20日均线下方", f"价格({current_price:.2f}) < SMA20({current_sma20:.2f})"))
    bearish_count += 1

# 综合评估
total = bullish_count + bearish_count + neutral_count
if bullish_count > bearish_count + 2:
    overall = "🟢 强势看多"
    overall_desc = "多项技术指标呈现多头信号，短期趋势偏强。"
elif bullish_count > bearish_count:
    overall = "🟢 偏多"
    overall_desc = "多头信号略占上风，但需关注潜在风险因素。"
elif bearish_count > bullish_count + 2:
    overall = "🔴 强势看空"
    overall_desc = "多项技术指标呈现空头信号，短期趋势偏弱。"
elif bearish_count > bullish_count:
    overall = "🔴 偏空"
    overall_desc = "空头信号略占上风，注意防范下行风险。"
else:
    overall = "⚪ 中性震荡"
    overall_desc = "多空力量相当，市场处于震荡整理阶段。"

# ── 6. 输出结果 ──────────────────────────────────────
print(f"\n[6/6] 生成报告...")

results = {
    "ticker": TICKER,
    "analysis_date": data.index[-1].strftime('%Y-%m-%d'),
    "data_range": f"{data.index[0].strftime('%Y-%m-%d')} ~ {data.index[-1].strftime('%Y-%m-%d')}",
    "price": {
        "current": current_price,
        "change_1d": price_1d,
        "change_5d": price_5d,
        "change_20d": price_20d,
        "change_60d": price_60d,
        "high_52w": high_52w,
        "low_52w": low_52w,
        "pct_from_high": pct_from_high,
        "pct_from_low": pct_from_low,
    },
    "indicators": {
        "rsi_14": current_rsi,
        "macd": current_macd,
        "macd_signal": current_signal,
        "macd_histogram": current_histogram,
        "sma5": current_sma5,
        "sma10": current_sma10,
        "sma20": current_sma20,
        "sma50": current_sma50,
        "sma120": current_sma120,
        "sma200": current_sma200,
        "bb_upper": current_bb_upper,
        "bb_middle": current_bb_middle,
        "bb_lower": current_bb_lower,
        "bb_pct_b": bb_pct_b,
        "bb_width_pct": bb_width,
        "atr_14": current_atr,
        "atr_pct": atr_pct,
        "adx_14": current_adx,
        "stoch_k": current_k,
        "stoch_d": current_d,
        "williams_r": current_wr,
    },
    "volume": {
        "current": current_vol,
        "avg_5d": vol_5,
        "avg_20d": vol_20,
        "avg_60d": vol_60,
        "vol_ratio_5_20": vol_ratio,
    },
    "signals": [{"indicator": s[0], "signal": s[1], "detail": s[2]} for s in signals],
    "summary": {
        "bullish_count": bullish_count,
        "bearish_count": bearish_count,
        "neutral_count": neutral_count,
        "overall": overall,
        "description": overall_desc,
    }
}

# 保存 JSON 数据
clean_results = make_serializable(results)
json_path = os.path.join(SCRIPT_DIR, 'technical_analysis_GOOG_data.json')
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(clean_results, f, indent=4, ensure_ascii=False)
print(f"  ✅ 数据已保存: {json_path}")

# ── 生成 Markdown 报告 ──────────────────────────────────
sma200_str = f"${current_sma200:.2f}" if current_sma200 is not None else "N/A (数据不足)"

report = f"""# GOOG (Alphabet Inc.) 技术指标分析

**分析日期**: 2026-02-24 | **数据截止**: {data.index[-1].strftime('%Y-%m-%d')} | **数据范围**: {data.index[0].strftime('%Y-%m-%d')} ~ {data.index[-1].strftime('%Y-%m-%d')}

---

## 📊 综合研判: {overall}

> {overall_desc}

| 多头信号 | 空头信号 | 中性信号 |
|:---:|:---:|:---:|
| {bullish_count} | {bearish_count} | {neutral_count} |

---

## 1. 💰 价格概览

| 指标 | 数值 |
|:---|:---:|
| **当前价格** | **${current_price:.2f}** |
| 1日涨跌幅 | {price_1d:+.2f}% |
| 5日涨跌幅 | {price_5d:+.2f}% |
| 20日涨跌幅 | {price_20d:+.2f}% |
| 60日涨跌幅 | {price_60d:+.2f}% |
| 52周最高 | ${high_52w:.2f} (距今 {pct_from_high:+.1f}%) |
| 52周最低 | ${low_52w:.2f} (距今 {pct_from_low:+.1f}%) |

---

## 2. 📈 核心指标状态

### RSI (14): {current_rsi:.1f}
- **前值**: {prev_rsi:.1f}
- **状态**: {"⚠️ 超买 (>70)" if current_rsi > 70 else "🟢 超卖 (<30)" if current_rsi < 30 else "偏强 (>60)" if current_rsi > 60 else "偏弱 (<40)" if current_rsi < 40 else "中性 (40-60)"}
- *解读*: RSI 当前为 {current_rsi:.1f}，{"进入超买区域，短期内存在获利回吐风险，需关注是否出现顶背离。" if current_rsi > 70 else "进入超卖区域，存在超跌反弹的可能，可关注是否出现底背离信号。" if current_rsi < 30 else "动能偏强，多头占据优势。" if current_rsi > 60 else "动能偏弱，空头略占优势。" if current_rsi < 40 else "多空力量相当，处于均衡状态。"}

### MACD
| 指标 | 数值 |
|:---|:---:|
| DIF (MACD Line) | {current_macd:.4f} |
| DEA (Signal Line) | {current_signal:.4f} |
| Histogram | {current_histogram:.4f} |

- **状态**: {"🟢 多头区域" if current_macd > current_signal else "🔴 空头区域"} | {"金叉刚形成" if current_histogram > 0 and prev_histogram <= 0 else "死叉刚形成" if current_histogram < 0 and prev_histogram >= 0 else "多头持续" if current_histogram > 0 else "空头持续"}
- *解读*: {"MACD 线位于信号线上方，柱状图为正，上升趋势保持中。" if current_histogram > 0 else "MACD 线位于信号线下方，柱状图为负，下降趋势延续。"}{"柱状图较前一日" + ("扩大" if abs(current_histogram) > abs(prev_histogram) else "收窄") + "，趋势" + ("加速" if abs(current_histogram) > abs(prev_histogram) else "减弱") + "。"}

---

## 3. 📐 趋势与通道

### 均线系统 (Moving Averages)

| 均线 | 数值 | 与当前价格比较 |
|:---|:---:|:---:|
| SMA 5 (周线) | ${current_sma5:.2f} | {("🟢 上方" if current_price > current_sma5 else "🔴 下方")} ({(current_price/current_sma5-1)*100:+.2f}%) |
| SMA 10 | ${current_sma10:.2f} | {("🟢 上方" if current_price > current_sma10 else "🔴 下方")} ({(current_price/current_sma10-1)*100:+.2f}%) |
| SMA 20 (月线) | ${current_sma20:.2f} | {("🟢 上方" if current_price > current_sma20 else "🔴 下方")} ({(current_price/current_sma20-1)*100:+.2f}%) |
| SMA 50 (季线) | ${current_sma50:.2f} | {("🟢 上方" if current_price > current_sma50 else "🔴 下方")} ({(current_price/current_sma50-1)*100:+.2f}%) |
| SMA 120 (半年线) | ${current_sma120:.2f} | {("🟢 上方" if current_price > current_sma120 else "🔴 下方")} ({(current_price/current_sma120-1)*100:+.2f}%) |
| SMA 200 (年线) | {sma200_str} | {("🟢 上方" if current_sma200 and current_price > current_sma200 else "🔴 下方" if current_sma200 else "N/A")} |

- **均线排列**: {"🟢 多头排列 (MA5>MA10>MA20>MA50)" if current_sma5 > current_sma10 > current_sma20 > current_sma50 else "🔴 空头排列 (MA5<MA10<MA20<MA50)" if current_sma5 < current_sma10 < current_sma20 < current_sma50 else "⚪ 交织排列，趋势不明确"}

### 布林带 (Bollinger Bands, 20日, 2σ)

| 指标 | 数值 |
|:---|:---:|
| 上轨 (Upper) | ${current_bb_upper:.2f} |
| 中轨 (Middle) | ${current_bb_middle:.2f} |
| 下轨 (Lower) | ${current_bb_lower:.2f} |
| %B | {bb_pct_b:.2f} |
| 带宽 | {bb_width:.2f}% |

- **位置**: {"接近上轨 (可能面临压力)" if bb_pct_b > 0.8 else "接近下轨 (可能获得支撑)" if bb_pct_b < 0.2 else "通道中部"}
- *解读*: 价格当前 %B 为 {bb_pct_b:.2f}，{"表明处于强势区间上沿，但需注意回落风险。" if bb_pct_b > 0.8 else "表明处于弱势区间下沿，可能出现技术性反弹。" if bb_pct_b < 0.2 else "处于布林带中部区域，价格运行相对平稳。"}布林带宽为 {bb_width:.2f}%，{"较窄，暗示波动率收敛，可能酝酿变盘。" if bb_width < 5 else "较宽，表明市场波动较大。" if bb_width > 15 else "处于正常水平。"}

---

## 4. 📉 波动性与趋势强度

| 指标 | 数值 | 解读 |
|:---|:---:|:---|
| ATR (14) | ${current_atr:.2f} ({atr_pct:.2f}%) | {"高波动" if atr_pct > 3 else "中等波动" if atr_pct > 1.5 else "低波动"} |
| ADX (14) | {current_adx:.1f} | {"强趋势 (>40)" if current_adx > 40 else "趋势明确 (25-40)" if current_adx > 25 else "弱趋势/震荡 (<25)"} |

- *ATR 解读*: 14日平均真实波幅为 ${current_atr:.2f}，占当前价格的 {atr_pct:.2f}%。这意味着 GOOG 每日平均波动约 ${current_atr:.2f}。
- *ADX 解读*: ADX 为 {current_adx:.1f}，{"趋势非常明确，适合趋势跟踪策略。" if current_adx > 40 else "趋势较为明确，可以顺势操作。" if current_adx > 25 else "当前处于震荡市，趋势不明确，需谨慎追涨杀跌。"}

---

## 5. 📊 震荡指标

### Stochastic (KDJ)

| 指标 | 数值 |
|:---|:---:|
| %K | {current_k:.1f} |
| %D | {current_d:.1f} |

- **状态**: {"⚠️ 超买区 (K>80, D>80)" if current_k > 80 and current_d > 80 else "🟢 超卖区 (K<20, D<20)" if current_k < 20 and current_d < 20 else "⚪ 中性区域"}
- *解读*: {"KD 均进入超买区域，短期内可能面临调整压力。" if current_k > 80 and current_d > 80 else "KD 均进入超卖区域，可能出现反弹。" if current_k < 20 and current_d < 20 else f"K={current_k:.1f}, D={current_d:.1f}，处于中间区域。" + (" K 在 D 上方，短期偏强。" if current_k > current_d else " K 在 D 下方，短期偏弱。")}

### Williams %R (14)
- **当前值**: {current_wr:.1f}
- **状态**: {"⚠️ 超买 (>-20)" if current_wr > -20 else "🟢 超卖 (<-80)" if current_wr < -80 else "⚪ 中性"}

---

## 6. 📊 成交量分析

| 指标 | 数值 |
|:---|:---:|
| 最近交易日成交量 | {current_vol:,.0f} |
| 5日均量 | {vol_5:,.0f} |
| 20日均量 | {vol_20:,.0f} |
| 60日均量 | {vol_60:,.0f} |
| 量比 (5日/20日) | {vol_ratio:.2f} |

- **量能状态**: {"📊 显著放量 (>1.5)" if vol_ratio > 1.5 else "📉 明显缩量 (<0.7)" if vol_ratio < 0.7 else "⚪ 量能正常"}
- *解读*: 5日均量相对20日均量的比值为 {vol_ratio:.2f}，{"成交量明显放大，市场关注度提升，需结合价格方向判断是突破还是出货。" if vol_ratio > 1.5 else "成交量明显萎缩，市场观望情绪浓厚。" if vol_ratio < 0.7 else "量能处于正常水平。"}

---

## 7. 🎯 技术信号汇总

| # | 指标 | 信号 | 详情 |
|:---:|:---|:---|:---|
"""

for i, s in enumerate(signals, 1):
    report += f"| {i} | {s[0]} | {s[1]} | {s[2]} |\n"

report += f"""
---

## 8. 💡 关键支撑与压力位

| 类型 | 位置 | 来源 |
|:---|:---:|:---|
| **强压力** | ${high_52w:.2f} | 52周新高 |
| **压力1** | ${current_bb_upper:.2f} | 布林带上轨 |
| **当前价格** | **${current_price:.2f}** | — |
| **支撑1** | ${current_sma20:.2f} | 20日均线 |
| **支撑2** | ${current_bb_lower:.2f} | 布林带下轨 |
| **支撑3** | ${current_sma50:.2f} | 50日均线 |
| **强支撑** | ${low_52w:.2f} | 52周新低 |

---

## 9. 📋 操作建议

"""

# 生成操作建议
if overall.startswith("🟢 强势"):
    report += """- **短线**: 趋势向好，可在回踩均线时逢低吸纳，止损设在 SMA20 下方。
- **中线**: 多头排列完好，持有为主，关注MACD是否出现顶背离。
- **风险提示**: 注意 RSI 是否进入超买区域后出现顶背离，以及成交量是否跟上。
"""
elif overall.startswith("🟢 偏"):
    report += """- **短线**: 趋势偏多但并非全面看多，建议轻仓参与，设好止损。
- **中线**: 观察均线是否进一步形成多头排列，若确认可加仓。
- **风险提示**: 关注部分空头信号是否恶化，如MACD柱状图收窄或RSI跌破50。
"""
elif overall.startswith("🔴 强势"):
    report += """- **短线**: 空头信号明确，不建议抄底，可等待企稳信号再介入。
- **中线**: 趋势偏空，持币观望为主，等待技术面修复。
- **风险提示**: 关注是否出现加速下跌，以及成交量是否在下跌时放大。
"""
elif overall.startswith("🔴 偏"):
    report += """- **短线**: 技术面偏弱，短期操作需谨慎，控制仓位。
- **中线**: 等待 MACD 金叉或 RSI 底背离等反转信号。
- **风险提示**: 如果跌破重要支撑位（如 SMA50），可能加速下行。
"""
else:
    report += """- **短线**: 市场处于震荡区间，可在支撑位附近低吸，压力位附近减仓。
- **中线**: 等待方向确认，即突破布林带上轨或跌破下轨后的方向选择。
- **风险提示**: 震荡市中避免追涨杀跌，注意控制仓位和止损。
"""

report += f"""
---

## 📂 生成文件

| 文件 | 路径 |
|:---|:---|
| 分析脚本 | `workspace/2026-02-24/165647/technical_analysis_GOOG.py` |
| 指标数据 (JSON) | `workspace/2026-02-24/165647/technical_analysis_GOOG_data.json` |
| 分析报告 | `workspace/2026-02-24/165647/technical_analysis_GOOG_report.md` |

> ⚠️ **免责声明**: 以上分析仅基于历史数据和技术指标，不构成投资建议。投资有风险，入市需谨慎。
"""

# 保存报告
report_path = os.path.join(SCRIPT_DIR, 'technical_analysis_GOOG_report.md')
with open(report_path, 'w', encoding='utf-8') as f:
    f.write(report)
print(f"  ✅ 报告已保存: {report_path}")

# 打印关键信息到控制台
print(f"\n{'='*60}")
print(f"  GOOG 技术面分析摘要")
print(f"{'='*60}")
print(f"  当前价格: ${current_price:.2f}")
print(f"  综合研判: {overall}")
print(f"  {overall_desc}")
print(f"{'='*60}")
print(f"  RSI(14)  : {current_rsi:.1f}")
print(f"  MACD     : {current_macd:.4f} (Signal: {current_signal:.4f})")
print(f"  ADX(14)  : {current_adx:.1f}")
print(f"  Stoch K/D: {current_k:.1f} / {current_d:.1f}")
print(f"  ATR(14)  : ${current_atr:.2f} ({atr_pct:.2f}%)")
print(f"  布林 %B  : {bb_pct_b:.2f}")
print(f"{'='*60}")
print(f"  多头信号: {bullish_count} | 空头信号: {bearish_count} | 中性: {neutral_count}")
print(f"{'='*60}")
print(f"\n✅ 分析完成!")
