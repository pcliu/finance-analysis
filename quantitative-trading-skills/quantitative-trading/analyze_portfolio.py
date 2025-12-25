#!/usr/bin/env python3
"""
分析用户持仓 ETF 的技术指标和投资建议
"""

import sys
sys.path.insert(0, '/Users/liupengcheng/Documents/Code/finance-analysis/quantitative-trading-skills/quantitative-trading')

from scripts import fetch_stock_data, calculate_rsi, calculate_sma, calculate_macd
from scripts.risk_manager import RiskManager
import pandas as pd
import json

# 用户持仓
holdings = {
    '510880': {'name': '红利ETF', 'shares': 500, 'value': 1583.00, 'pnl': -2.10},
    '513180': {'name': '恒指科技', 'shares': 2000, 'value': 1466.00, 'pnl': -0.31},
    '513630': {'name': '香港红利', 'shares': 1000, 'value': 1623.00, 'pnl': -1.64},
    '588000': {'name': '科创50', 'shares': 2000, 'value': 2840.00, 'pnl': 2.50},
    '159830': {'name': '上海金', 'shares': 400, 'value': 3991.20, 'pnl': 2.63},
    '159980': {'name': '有色ETF', 'shares': 1000, 'value': 1940.00, 'pnl': 0.49},
    '161226': {'name': '白银基金', 'shares': 3000, 'value': 9348.00, 'pnl': 60.93},
}

available_cash = 10000  # 可用资金

def analyze_etf(code, name):
    """分析单个 ETF"""
    try:
        # 使用 tushare 获取 A 股 ETF 数据
        data = fetch_stock_data(code, period='3mo', provider='tushare', market='cn')
        
        if data is None or data.empty:
            return {'code': code, 'name': name, 'error': 'No data'}
        
        # 计算技术指标
        rsi = calculate_rsi(data, period=14)
        sma_5 = calculate_sma(data, window=5)
        sma_20 = calculate_sma(data, window=20)
        macd = calculate_macd(data)
        
        current_price = float(data['Close'].iloc[-1])
        current_rsi = float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50
        current_sma_5 = float(sma_5.iloc[-1]) if not pd.isna(sma_5.iloc[-1]) else current_price
        current_sma_20 = float(sma_20.iloc[-1]) if not pd.isna(sma_20.iloc[-1]) else current_price
        current_macd = float(macd['MACD'].iloc[-1]) if not pd.isna(macd['MACD'].iloc[-1]) else 0
        current_signal = float(macd['Signal'].iloc[-1]) if not pd.isna(macd['Signal'].iloc[-1]) else 0
        
        # 趋势判断
        trend = 'bullish' if current_sma_5 > current_sma_20 else 'bearish'
        macd_signal = 'buy' if current_macd > current_signal else 'sell'
        
        # RSI 信号
        if current_rsi > 70:
            rsi_signal = 'overbought'
        elif current_rsi < 30:
            rsi_signal = 'oversold'
        else:
            rsi_signal = 'neutral'
        
        # 计算最近收益率
        returns_1m = (current_price / data['Close'].iloc[-20] - 1) * 100 if len(data) >= 20 else 0
        
        return {
            'code': code,
            'name': name,
            'current_price': current_price,
            'rsi': round(current_rsi, 2),
            'rsi_signal': rsi_signal,
            'sma_5': round(current_sma_5, 4),
            'sma_20': round(current_sma_20, 4),
            'trend': trend,
            'macd': round(current_macd, 4),
            'macd_signal_line': round(current_signal, 4),
            'macd_signal': macd_signal,
            'returns_1m': round(returns_1m, 2),
        }
    except Exception as e:
        return {'code': code, 'name': name, 'error': str(e)}

print("=" * 60)
print("ETF 持仓技术分析报告")
print("=" * 60)

results = []
for code, info in holdings.items():
    print(f"\n分析 {info['name']} ({code})...")
    result = analyze_etf(code, info['name'])
    result['holding_value'] = info['value']
    result['current_pnl'] = info['pnl']
    results.append(result)

# 输出分析结果
print("\n" + "=" * 60)
print("技术指标汇总")
print("=" * 60)

buy_recommendations = []
sell_recommendations = []
hold_recommendations = []

for r in results:
    if 'error' in r:
        print(f"\n{r['name']} ({r['code']}): 数据获取失败 - {r['error']}")
        continue
    
    print(f"\n【{r['name']}】({r['code']})")
    print(f"  当前价格: {r['current_price']:.4f}")
    print(f"  RSI(14): {r['rsi']} ({r['rsi_signal']})")
    print(f"  趋势: {r['trend']} (5日均线 vs 20日均线)")
    print(f"  MACD: {r['macd_signal']}")
    print(f"  近1月收益: {r['returns_1m']}%")
    print(f"  当前持仓盈亏: {r['current_pnl']}%")
    
    # 综合建议
    score = 0
    
    # RSI 评分
    if r['rsi_signal'] == 'oversold':
        score += 2
    elif r['rsi_signal'] == 'overbought':
        score -= 2
    
    # 趋势评分
    if r['trend'] == 'bullish':
        score += 1
    else:
        score -= 1
    
    # MACD 评分
    if r['macd_signal'] == 'buy':
        score += 1
    else:
        score -= 1
    
    # 持仓盈亏评分 (大幅盈利考虑止盈)
    if r['current_pnl'] > 50:
        score -= 2  # 建议部分止盈
    elif r['current_pnl'] < -5:
        score -= 1  # 观望
    
    if score >= 2:
        buy_recommendations.append(r)
        r['recommendation'] = '建议买入'
    elif score <= -2:
        sell_recommendations.append(r)
        r['recommendation'] = '建议卖出/减仓'
    else:
        hold_recommendations.append(r)
        r['recommendation'] = '持有观望'
    
    print(f"  综合建议: {r['recommendation']} (评分: {score})")

# 投资建议总结
print("\n" + "=" * 60)
print("投资建议总结 (可用资金: ¥10,000)")
print("=" * 60)

print("\n📈 建议买入:")
if buy_recommendations:
    for r in buy_recommendations:
        print(f"  - {r['name']} ({r['code']}): RSI={r['rsi']}, 趋势={r['trend']}")
else:
    print("  暂无强烈买入信号")

print("\n📉 建议卖出/减仓:")
if sell_recommendations:
    for r in sell_recommendations:
        print(f"  - {r['name']} ({r['code']}): 盈利{r['current_pnl']}%, RSI={r['rsi']}")
else:
    print("  暂无强烈卖出信号")

print("\n⏸️ 持有观望:")
if hold_recommendations:
    for r in hold_recommendations:
        print(f"  - {r['name']} ({r['code']})")

# 资金配置建议
print("\n" + "=" * 60)
print("¥10,000 资金配置建议")
print("=" * 60)

total_holding = sum(info['value'] for info in holdings.values())
print(f"\n当前持仓总市值: ¥{total_holding:,.2f}")
print(f"可用现金: ¥{available_cash:,.2f}")
print(f"总资产: ¥{total_holding + available_cash:,.2f}")

# 计算持仓占比
print("\n当前持仓占比:")
for code, info in sorted(holdings.items(), key=lambda x: x[1]['value'], reverse=True):
    pct = info['value'] / total_holding * 100
    print(f"  {info['name']}: {pct:.1f}% (¥{info['value']:,.2f})")

# 保存结果
with open('workspace/portfolio_analysis.json', 'w', encoding='utf-8') as f:
    json.dump({
        'holdings': holdings,
        'analysis': results,
        'buy_recommendations': [r['code'] for r in buy_recommendations],
        'sell_recommendations': [r['code'] for r in sell_recommendations],
    }, f, ensure_ascii=False, indent=2)

print("\n分析结果已保存到 workspace/portfolio_analysis.json")
