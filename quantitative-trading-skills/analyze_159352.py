#!/usr/bin/env python3
"""Analyze ETF 159352 and compare with existing holdings"""

import sys
sys.path.insert(0, '/Users/liupengcheng/Documents/Code/finance-analysis/quantitative-trading-skills/quantitative-trading')

from scripts import fetch_stock_data, calculate_rsi, calculate_sma, calculate_macd, calculate_bollinger_bands
from scripts.data_fetcher import DataFetcher
import pandas as pd
import numpy as np
from datetime import datetime

# Target ETF to analyze
target_ticker = '159352.SZ'
target_name = 'A500ETF南方'  # 跟踪中证A500指数

# User's existing holdings
existing_holdings = {
    '510880.SH': '红利ETF',
    '513180.SH': '恒指科技',
    '513630.SH': '香港红利',
    '588000.SH': '科创50',
    '159830.SZ': '上海金',
    '159980.SZ': '有色ETF',
    '161226.SZ': '白银基金',
}

print("=" * 70)
print(f"📊 ETF分析报告: {target_name} ({target_ticker})")
print(f"📅 分析日期: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
print("=" * 70)

# Fetch data for target ETF
print("\n🔍 获取目标ETF数据...")
try:
    target_data = fetch_stock_data(target_ticker, period='6mo')
    
    if target_data is not None and len(target_data) > 20:
        print(f"   ✅ 成功获取 {len(target_data)} 条数据")
        
        # Calculate technical indicators
        rsi = calculate_rsi(target_data)
        sma_20 = calculate_sma(target_data, window=20)
        sma_60 = calculate_sma(target_data, window=60)
        macd_data = calculate_macd(target_data)
        bb = calculate_bollinger_bands(target_data)
        
        current_price = target_data['Close'].iloc[-1]
        rsi_value = rsi.iloc[-1]
        sma_20_value = sma_20.iloc[-1]
        sma_60_value = sma_60.iloc[-1] if len(target_data) > 60 else np.nan
        
        # Price analysis
        price_vs_sma20 = (current_price - sma_20_value) / sma_20_value * 100
        price_vs_sma60 = (current_price - sma_60_value) / sma_60_value * 100 if not np.isnan(sma_60_value) else 0
        
        # Bollinger Bands position
        upper = bb['Upper'].iloc[-1]
        lower = bb['Lower'].iloc[-1]
        bb_position = (current_price - lower) / (upper - lower) * 100 if upper != lower else 50
        
        # MACD analysis
        macd_line = macd_data['MACD'].iloc[-1]
        signal_line = macd_data['Signal'].iloc[-1]
        macd_histogram = macd_data['Histogram'].iloc[-1]
        
        # Volatility and Returns
        if 'Returns' in target_data.columns:
            returns = target_data['Returns'].dropna()
            volatility = returns.std() * np.sqrt(252) * 100
            cumulative = (1 + returns).cumprod()
            running_max = cumulative.cummax()
            drawdown = (cumulative - running_max) / running_max
            max_dd = abs(drawdown.min()) * 100
            
            # Recent performance
            if len(returns) >= 20:
                return_1m = (cumulative.iloc[-1] / cumulative.iloc[-20] - 1) * 100
            else:
                return_1m = 0
            if len(returns) >= 60:
                return_3m = (cumulative.iloc[-1] / cumulative.iloc[-60] - 1) * 100
            else:
                return_3m = 0
        else:
            volatility = 0
            max_dd = 0
            return_1m = 0
            return_3m = 0
        
        print("\n" + "=" * 70)
        print(f"📈 {target_name} ({target_ticker}) 技术分析")
        print("=" * 70)
        
        print(f"\n💰 价格信息:")
        print(f"   当前价格: ¥{current_price:.3f}")
        print(f"   20日均线: ¥{sma_20_value:.3f} ({price_vs_sma20:+.2f}%)")
        if not np.isnan(sma_60_value):
            print(f"   60日均线: ¥{sma_60_value:.3f} ({price_vs_sma60:+.2f}%)")
        
        print(f"\n📊 技术指标:")
        print(f"   RSI(14): {rsi_value:.2f}", end="")
        if rsi_value < 30:
            print(" 🟢 超卖区")
        elif rsi_value > 70:
            print(" 🔴 超买区")
        elif rsi_value < 40:
            print(" 🟡 偏低")
        elif rsi_value > 60:
            print(" 🟡 偏高")
        else:
            print(" ⚪ 中性")
        
        print(f"   布林带位置: {bb_position:.1f}%")
        print(f"   MACD: {macd_line:.4f}, Signal: {signal_line:.4f}")
        print(f"   MACD柱状图: {macd_histogram:.4f}", end="")
        if macd_histogram > 0:
            print(" 📈 多头")
        else:
            print(" 📉 空头")
        
        print(f"\n📉 风险指标:")
        print(f"   年化波动率: {volatility:.2f}%")
        print(f"   最大回撤: {max_dd:.2f}%")
        print(f"   近1月收益: {return_1m:+.2f}%")
        print(f"   近3月收益: {return_3m:+.2f}%")
        
        # Generate trading signal
        print(f"\n🎯 建仓信号判断:")
        signals = []
        score = 0
        
        if rsi_value < 30:
            signals.append("✅ RSI超卖，买入信号强")
            score += 2
        elif rsi_value < 40:
            signals.append("🟡 RSI偏低，可考虑建仓")
            score += 1
        elif rsi_value > 70:
            signals.append("❌ RSI超买，不宜建仓")
            score -= 2
        elif rsi_value > 60:
            signals.append("⚠️ RSI偏高，谨慎建仓")
            score -= 1
        else:
            signals.append("⚪ RSI中性")
        
        if price_vs_sma20 < -5:
            signals.append("✅ 价格低于均线5%+，低位机会")
            score += 1
        elif price_vs_sma20 > 5:
            signals.append("⚠️ 价格高于均线5%+，注意追高风险")
            score -= 1
        
        if macd_histogram > 0 and macd_line > signal_line:
            signals.append("✅ MACD金叉，多头趋势")
            score += 1
        elif macd_histogram < 0 and macd_line < signal_line:
            signals.append("⚠️ MACD死叉，空头趋势")
            score -= 1
        
        if bb_position < 20:
            signals.append("✅ 接近布林下轨，可能反弹")
            score += 1
        elif bb_position > 80:
            signals.append("⚠️ 接近布林上轨，可能回调")
            score -= 1
        
        for sig in signals:
            print(f"   {sig}")
        
        print(f"\n   📊 综合得分: {score} ", end="")
        if score >= 2:
            print("🟢 建议建仓")
            recommendation = "建议建仓"
        elif score >= 0:
            print("🟡 可少量建仓观望")
            recommendation = "可少量建仓"
        else:
            print("🔴 暂不建议建仓")
            recommendation = "暂不建议"
        
    else:
        print(f"   ⚠️ 数据不足，无法分析")
        sys.exit(1)
        
except Exception as e:
    print(f"   ❌ 获取数据失败: {str(e)}")
    sys.exit(1)

# Correlation Analysis
print("\n" + "=" * 70)
print("🔗 与现有持仓相关性分析")
print("=" * 70)

# Fetch data for all holdings
all_returns = {}
print("\n📥 获取持仓数据...")

# Add target ticker
target_returns = target_data['Returns'].dropna() if 'Returns' in target_data.columns else target_data['Close'].pct_change().dropna()
all_returns[target_ticker] = target_returns

for ticker, name in existing_holdings.items():
    try:
        data = fetch_stock_data(ticker, period='6mo')
        if data is not None and len(data) > 20:
            if 'Returns' in data.columns:
                all_returns[ticker] = data['Returns'].dropna()
            else:
                all_returns[ticker] = data['Close'].pct_change().dropna()
            print(f"   ✅ {name} ({ticker})")
        else:
            print(f"   ⚠️ {name} - 数据不足")
    except Exception as e:
        print(f"   ❌ {name} - {str(e)}")

# Calculate correlation matrix
print("\n📊 相关性矩阵 (与目标ETF):")
print("-" * 50)

if len(all_returns) > 1:
    # Align all returns to same dates
    returns_df = pd.DataFrame(all_returns)
    returns_df = returns_df.dropna()
    
    if len(returns_df) > 20:
        # Calculate correlation with target
        correlations = returns_df.corr()[target_ticker].drop(target_ticker).sort_values(ascending=False)
        
        print(f"\n   {'ETF':<20} {'相关系数':<12} {'相关程度':<15}")
        print("   " + "-" * 47)
        
        high_corr_etfs = []
        for ticker, corr in correlations.items():
            name = existing_holdings.get(ticker, ticker)
            
            if corr > 0.7:
                level = "🔴 高度相关"
                high_corr_etfs.append((name, corr))
            elif corr > 0.4:
                level = "🟡 中度相关"
            elif corr > 0:
                level = "🟢 弱相关"
            elif corr > -0.3:
                level = "⚪ 无相关"
            else:
                level = "🔵 负相关"
            
            print(f"   {name:<20} {corr:>+.4f}       {level}")
        
        # Overlap analysis
        print("\n" + "=" * 70)
        print("📋 持仓重合度分析")
        print("=" * 70)
        
        if high_corr_etfs:
            print("\n⚠️ 发现高度相关ETF (相关系数 > 0.7):")
            for name, corr in high_corr_etfs:
                print(f"   • {name}: 相关系数 {corr:.4f}")
            print("\n   💡 这些ETF与目标ETF走势高度一致，存在较大重合风险")
            print("   💡 建议：若已持有上述ETF，可考虑不再建仓或减少目标仓位")
        else:
            print("\n✅ 未发现高度相关的持仓")
            print("   💡 目标ETF与现有持仓分散度较好，可作为组合补充")
        
        # Category analysis
        print("\n📊 资产类别分析:")
        print("-" * 50)
        print(f"   • {target_name} ({target_ticker}): 宽基指数 (中证A500)")
        print("\n   与您现有持仓的对比:")
        print("   • 科创50 (588000): 科技成长风格，与A500有一定重合")
        print("   • 红利类ETF: 偏价值风格，与A500风格互补")
        print("   • 贵金属类: 完全不同资产类别，相关性低")
        
    else:
        print("   ⚠️ 共同交易日数据不足，无法计算相关性")

# Final recommendation
print("\n" + "=" * 70)
print("💡 综合建仓建议")
print("=" * 70)

print(f"""
📌 目标ETF: {target_name} ({target_ticker})

1️⃣ 技术面判断: {recommendation}
   • RSI: {rsi_value:.2f}
   • 趋势: {'多头' if macd_histogram > 0 else '空头'}
   • 波动率: {volatility:.2f}%

2️⃣ 与现有持仓关系:
   • 与科技类ETF (科创50、恒指科技) 可能有中高度相关
   • 与红利类、贵金属类 相关性较低
   • 可增加组合的科技行业暴露

3️⃣ 建仓建议:
""")

if score >= 2:
    print("   🟢 技术面较好，可以建仓")
    print("   💰 建议仓位: 3-5% 的总资产")
    print("   📍 分批建仓，首次投入 50%")
elif score >= 0:
    print("   🟡 技术面中性，可少量试探建仓")
    print("   💰 建议仓位: 1-3% 的总资产")
    print("   📍 先建底仓，观察走势")
else:
    print("   🔴 技术面偏弱，暂不建议建仓")
    print("   ⏳ 建议等待更好的入场时机")
    print("   📍 关注RSI降至40以下或MACD金叉")

print("""
4️⃣ 风险提示:
   ⚠️ A500为宽基指数，覆盖A股核心资产
   ⚠️ 注意与科创50等成长类持仓的风格重合
   ⚠️ 当前市场环境复杂，建议分批建仓
""")

print("=" * 70)
