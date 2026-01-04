#!/usr/bin/env python3
"""Portfolio analysis and rebalancing recommendations"""

import sys
sys.path.insert(0, '/Users/liupengcheng/Documents/Code/finance-analysis/quantitative-trading-skills/quantitative-trading')

from scripts import fetch_stock_data, calculate_rsi, calculate_sma, calculate_macd, calculate_bollinger_bands
from scripts.risk_manager import RiskManager
from scripts.portfolio_analyzer import PortfolioAnalyzer
import pandas as pd
import numpy as np
import json
from datetime import datetime

# User's current portfolio
portfolio = {
    '510880.SH': {'name': '红利ETF', 'shares': 500, 'value': 1586.50, 'pnl': -31.00, 'pnl_pct': -1.89},
    '513180.SH': {'name': '恒指科技', 'shares': 2400, 'value': 1761.60, 'pnl': -3.60, 'pnl_pct': -0.18},
    '513630.SH': {'name': '香港红利', 'shares': 500, 'value': 812.00, 'pnl': -28.00, 'pnl_pct': -3.28},
    '588000.SH': {'name': '科创50', 'shares': 4800, 'value': 6840.00, 'pnl': 103.80, 'pnl_pct': 1.55},
    '159830.SZ': {'name': '上海金', 'shares': 400, 'value': 4022.00, 'pnl': 132.70, 'pnl_pct': 3.43},
    '159980.SZ': {'name': '有色ETF', 'shares': 1000, 'value': 1991.00, 'pnl': 60.00, 'pnl_pct': 3.13},
    '161226.SZ': {'name': '白银基金', 'shares': 2000, 'value': 5608.00, 'pnl': 2914.00, 'pnl_pct': 108.20},
}

total_assets = 103162.56
position_value = 22621.10
available_cash = 80541.46
position_ratio = 21.93

print("=" * 60)
print("📊 仓位分析报告 - Portfolio Analysis Report")
print(f"📅 分析日期: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
print("=" * 60)

print("\n📈 当前持仓概览:")
print("-" * 40)
print(f"{'总资产:':<15} ¥{total_assets:,.2f}")
print(f"{'持仓市值:':<15} ¥{position_value:,.2f}")
print(f"{'可用资金:':<15} ¥{available_cash:,.2f}")
print(f"{'当前仓位:':<15} {position_ratio:.2f}%")

# Calculate asset allocation
print("\n📊 资产配置分析:")
print("-" * 40)

# Group by asset type
categories = {
    '股息/红利类': ['510880.SH', '513630.SH'],
    '科技成长类': ['513180.SH', '588000.SH'],
    '贵金属类': ['159830.SZ', '159980.SZ', '161226.SZ'],
}

category_values = {}
for cat, tickers in categories.items():
    total = sum(portfolio[t]['value'] for t in tickers if t in portfolio)
    pct = total / position_value * 100
    category_values[cat] = {'value': total, 'pct': pct}
    print(f"  {cat}: ¥{total:,.2f} ({pct:.1f}%)")

# Analyze individual holdings
print("\n🔍 个股技术分析:")
print("-" * 60)

rm = RiskManager()
analysis_results = []

for ticker, info in portfolio.items():
    print(f"\n  📌 {info['name']} ({ticker})")
    try:
        # Fetch historical data
        data = fetch_stock_data(ticker, period='3mo')
        
        if data is not None and len(data) > 20:
            # Calculate indicators
            rsi = calculate_rsi(data)
            sma_20 = calculate_sma(data, window=20)
            macd_data = calculate_macd(data)
            bb = calculate_bollinger_bands(data)
            
            current_price = data['Close'].iloc[-1]
            rsi_value = rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50
            sma_value = sma_20.iloc[-1]
            
            # Price vs SMA analysis
            price_vs_sma = (current_price - sma_value) / sma_value * 100
            
            # Check Bollinger Bands position
            upper = bb['Upper'].iloc[-1]
            lower = bb['Lower'].iloc[-1]
            bb_position = (current_price - lower) / (upper - lower) * 100 if upper != lower else 50
            
            # Calculate returns and risk metrics
            if 'Returns' in data.columns:
                returns = data['Returns'].dropna()
                volatility = returns.std() * np.sqrt(252) * 100
                # Calculate max drawdown manually
                cumulative = (1 + returns).cumprod()
                running_max = cumulative.cummax()
                drawdown = (cumulative - running_max) / running_max
                max_dd = abs(drawdown.min()) * 100
            else:
                volatility = 0
                max_dd = 0
            
            # Generate signal
            signal = "持有"
            if rsi_value < 30:
                signal = "🟢 超卖区 - 可考虑加仓"
            elif rsi_value > 70:
                signal = "🔴 超买区 - 可考虑减仓"
            elif price_vs_sma < -5:
                signal = "🟡 低于均线 - 观望或少量加仓"
            elif price_vs_sma > 5:
                signal = "🟡 高于均线 - 谨慎追高"
            
            result = {
                'ticker': ticker,
                'name': info['name'],
                'current_value': info['value'],
                'pnl_pct': info['pnl_pct'],
                'rsi': round(rsi_value, 2),
                'price_vs_sma_20': round(price_vs_sma, 2),
                'bb_position': round(bb_position, 2),
                'volatility': round(volatility, 2),
                'max_drawdown': round(max_dd, 2),
                'signal': signal
            }
            analysis_results.append(result)
            
            print(f"     RSI(14): {rsi_value:.2f}")
            print(f"     价格vs20日均线: {price_vs_sma:+.2f}%")
            print(f"     布林带位置: {bb_position:.1f}%")
            print(f"     年化波动率: {volatility:.2f}%")
            print(f"     最大回撤: {max_dd:.2f}%")
            print(f"     📍 信号: {signal}")
        else:
            print(f"     ⚠️ 数据不足，无法分析")
    except Exception as e:
        print(f"     ⚠️ 获取数据失败: {str(e)}")

# Portfolio recommendations
print("\n" + "=" * 60)
print("💡 仓位调整建议")
print("=" * 60)

print("\n1️⃣ 整体仓位建议:")
print("-" * 40)
print(f"   当前仓位 {position_ratio:.1f}% 较为保守")
print(f"   可用资金 ¥{available_cash:,.2f} 仍有较大配置空间")
print(f"   建议: 可根据市场情况逐步提升仓位至 30-40%")

print("\n2️⃣ 资产配置建议:")
print("-" * 40)
print(f"   • 贵金属类占比过高 ({category_values['贵金属类']['pct']:.1f}%)")
print(f"     - 白银基金盈利 +108% 可考虑部分止盈")
print(f"     - 建议减持贵金属至总仓位的 30-40%")
print(f"   • 股息红利类占比较低 ({category_values['股息/红利类']['pct']:.1f}%)")
print(f"     - 红利ETF虽小幅亏损但具有防守价值")
print(f"     - 可逢低适当加仓")
print(f"   • 科技成长类占比 ({category_values['科技成长类']['pct']:.1f}%)")
print(f"     - 科创50表现较好可继续持有")
print(f"     - 恒指科技关注港股走势")

print("\n3️⃣ 具体操作建议:")
print("-" * 40)

# Specific recommendations based on analysis
recommendations = []

for result in analysis_results:
    name = result['name']
    if result['pnl_pct'] > 50:
        recommendations.append(f"   ✂️ {name}: 盈利丰厚 (+{result['pnl_pct']:.1f}%), 建议止盈 30-50%")
    elif result['pnl_pct'] < -5:
        if result.get('rsi', 50) < 40:
            recommendations.append(f"   💰 {name}: 亏损 {result['pnl_pct']:.1f}% 但RSI偏低, 可考虑逢低补仓")
        else:
            recommendations.append(f"   ⏳ {name}: 小幅亏损 {result['pnl_pct']:.1f}%, 建议观望")
    elif result.get('rsi', 50) < 35:
        recommendations.append(f"   💰 {name}: RSI={result['rsi']:.0f} 超卖区, 可考虑加仓")
    elif result.get('rsi', 50) > 70:
        recommendations.append(f"   ⚠️ {name}: RSI={result['rsi']:.0f} 超买区, 注意风险")

if recommendations:
    for rec in recommendations:
        print(rec)
else:
    print("   当前持仓风险可控，建议维持现状")

print("\n4️⃣ 风险提示:")
print("-" * 40)
print("   ⚠️ 贵金属持仓集中度较高，注意分散风险")
print("   ⚠️ 港股相关ETF受外部环境影响较大")
print("   ⚠️ 白银基金盈利丰厚，及时锁定利润")
print("   ✅ 整体仓位较低，抗风险能力较强")

print("\n" + "=" * 60)
