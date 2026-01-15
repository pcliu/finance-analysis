#!/usr/bin/env python3
"""持仓组合分析与调仓建议生成脚本"""

import sys
sys.path.insert(0, '.agent/skills/quantitative-trading')

from scripts import (
    fetch_stock_data,
    calculate_rsi,
    calculate_macd,
    calculate_bollinger_bands,
    calculate_sma,
    calculate_ema,
    RiskManager
)
import pandas as pd
import json
from datetime import datetime

def analyze_single_stock(ticker, data, shares_held=0):
    """对单只股票进行全面技术分析"""
    analysis = {
        'ticker': ticker,
        'current_price': float(data['Close'].iloc[-1]),
        'shares_held': shares_held,
        'market_value': float(data['Close'].iloc[-1] * shares_held),
        'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    # 计算技术指标
    rsi = calculate_rsi(data, period=14)
    macd = calculate_macd(data)
    bb = calculate_bollinger_bands(data)
    sma_20 = calculate_sma(data, window=20)
    sma_50 = calculate_sma(data, window=50)
    ema_12 = calculate_ema(data, window=12)

    # RSI分析
    current_rsi = float(rsi.iloc[-1])
    analysis['rsi'] = current_rsi
    if current_rsi > 70:
        analysis['rsi_signal'] = 'overbought'
        analysis['rsi_interpretation'] = '超买，考虑减仓'
    elif current_rsi < 30:
        analysis['rsi_signal'] = 'oversold'
        analysis['rsi_interpretation'] = '超卖，考虑加仓'
    else:
        analysis['rsi_signal'] = 'neutral'
        analysis['rsi_interpretation'] = '中性区域'

    # MACD分析
    macd_line = float(macd['MACD'].iloc[-1])
    signal_line = float(macd['Signal'].iloc[-1])
    histogram = float(macd['Histogram'].iloc[-1])
    analysis['macd'] = {
        'macd_line': macd_line,
        'signal_line': signal_line,
        'histogram': histogram
    }

    if macd_line > signal_line and histogram > 0:
        analysis['macd_signal'] = 'bullish'
        analysis['macd_interpretation'] = '金叉，看涨信号'
    elif macd_line < signal_line and histogram < 0:
        analysis['macd_signal'] = 'bearish'
        analysis['macd_interpretation'] = '死叉，看跌信号'
    else:
        analysis['macd_signal'] = 'neutral'
        analysis['macd_interpretation'] = '震荡，观望'

    # 布林带分析
    upper_band = float(bb['Upper'].iloc[-1])
    lower_band = float(bb['Lower'].iloc[-1])
    middle_band = float(bb['Middle'].iloc[-1])
    current_price = float(data['Close'].iloc[-1])

    bb_position = (current_price - lower_band) / (upper_band - lower_band) * 100
    analysis['bollinger_bands'] = {
        'upper': upper_band,
        'middle': middle_band,
        'lower': lower_band,
        'position_percent': bb_position
    }

    if current_price > upper_band:
        analysis['bb_signal'] = 'overbought'
        analysis['bb_interpretation'] = '突破上轨，短期可能回调'
    elif current_price < lower_band:
        analysis['bb_signal'] = 'oversold'
        analysis['bb_interpretation'] = '跌破下轨，短期可能反弹'
    else:
        analysis['bb_signal'] = 'neutral'
        analysis['bb_interpretation'] = '在轨内运行'

    # 移动平均线分析
    sma_20_val = float(sma_20.iloc[-1])
    sma_50_val = float(sma_50.iloc[-1])
    ema_12_val = float(ema_12.iloc[-1])

    analysis['moving_averages'] = {
        'sma_20': sma_20_val,
        'sma_50': sma_50_val,
        'ema_12': ema_12_val
    }

    if current_price > sma_20_val > sma_50_val:
        analysis['trend'] = 'uptrend'
        analysis['trend_interpretation'] = '上升趋势，多头排列'
    elif current_price < sma_20_val < sma_50_val:
        analysis['trend'] = 'downtrend'
        analysis['trend_interpretation'] = '下降趋势，空头排列'
    else:
        analysis['trend'] = 'sideways'
        analysis['trend_interpretation'] = '横盘整理'

    # 计算收益率
    returns = data['Close'].pct_change().dropna()
    rm = RiskManager()

    # 波动率
    volatility = returns.std() * (252 ** 0.5) * 100  # 年化波动率
    analysis['volatility_annual'] = float(volatility)

    # 最大回撤
    drawdown_metrics = rm.calculate_drawdown_metrics(returns, is_returns=True)
    analysis['max_drawdown'] = float(drawdown_metrics['max_drawdown'] * 100)

    # 最近1个月收益率
    recent_return = float(returns.tail(20).sum() * 100)
    analysis['return_1m'] = recent_return

    # 综合信号打分 (0-100)
    score = 50
    if current_rsi < 30:
        score += 20
    elif current_rsi > 70:
        score -= 20

    if macd_line > signal_line and histogram > 0:
        score += 15
    elif macd_line < signal_line and histogram < 0:
        score -= 15

    if current_price < lower_band:
        score += 15
    elif current_price > upper_band:
        score -= 15

    if current_price > sma_20_val > sma_50_val:
        score += 10
    elif current_price < sma_20_val < sma_50_val:
        score -= 10

    analysis['score'] = max(0, min(100, score))

    return analysis


def generate_recommendation(analysis):
    """根据分析结果生成调仓建议"""
    score = analysis['score']
    current_shares = analysis['shares_held']
    current_price = analysis['current_price']

    if score >= 75:
        action = 'strong_buy'
        action_cn = '强烈建议增持'
        suggested_change = 0.30  # 增持30%
        reason = f"综合得分{score:.0f}分，多个技术指标显示强烈的买入信号"
    elif score >= 60:
        action = 'buy'
        action_cn = '建议增持'
        suggested_change = 0.15  # 增持15%
        reason = f"综合得分{score:.0f}分，多个技术指标偏向看涨"
    elif score >= 40:
        action = 'hold'
        action_cn = '继续持有'
        suggested_change = 0
        reason = f"综合得分{score:.0f}分，技术指标显示中性，建议持有观望"
    elif score >= 25:
        action = 'reduce'
        action_cn = '建议减持'
        suggested_change = -0.15  # 减持15%
        reason = f"综合得分{score:.0f}分，多个技术指标偏向看跌"
    else:
        action = 'strong_sell'
        action_cn = '建议清仓'
        suggested_change = -0.50  # 减持50%
        reason = f"综合得分{score:.0f}分，多个技术指标显示强烈的卖出信号"

    if current_shares > 0:
        shares_change = int(current_shares * suggested_change)
        value_change = abs(shares_change * current_price)
    else:
        shares_change = 0
        value_change = 0

    return {
        'action': action,
        'action_cn': action_cn,
        'suggested_change_percent': suggested_change * 100,
        'shares_change': shares_change,
        'value_change': value_change,
        'reason': reason,
        'target_shares': current_shares + shares_change if current_shares > 0 else 0
    }


def main():
    """主分析流程"""
    print("=" * 80)
    print("持仓组合量化分析与调仓建议报告")
    print("=" * 80)
    print()

    # 当前持仓
    portfolio = [
        {'ticker': '512480.SH', 'name': '半导体ETF', 'shares': 5000, 'current_value': 12145},
        {'ticker': '518880.SH', 'name': '黄金ETF', 'shares': 2000, 'current_value': 11020},
        {'ticker': '161129.SZ', 'name': '易方达原油', 'shares': 4289.82, 'current_value': 12845},
    ]

    # 待分析的标的（包括新标的）
    tickers_to_analyze = [item['ticker'] for item in portfolio] + ['161226.SZ']  # 国投白银LOF

    print(f"正在分析 {len(tickers_to_analyze)} 只标的...")
    print()

    results = []
    for ticker in tickers_to_analyze:
        try:
            print(f"获取 {ticker} 数据...")
            data = fetch_stock_data(ticker, period='6mo')

            # 查找是否在持仓中
            held_item = next((item for item in portfolio if item['ticker'] == ticker), None)
            shares_held = held_item['shares'] if held_item else 0

            print(f"分析 {ticker}...")
            analysis = analyze_single_stock(ticker, data, shares_held)

            # 生成调仓建议
            recommendation = generate_recommendation(analysis)
            analysis['recommendation'] = recommendation

            results.append(analysis)

            print(f"✓ {ticker} 分析完成")
            print()

        except Exception as e:
            print(f"✗ {ticker} 分析失败: {str(e)}")
            print()

    # 保存结果
    output_file = 'workspace/portfolio_analysis_results.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # 生成摘要报告
    print("=" * 80)
    print("调仓建议摘要")
    print("=" * 80)
    print()

    total_current_value = sum(item['current_value'] for item in portfolio)

    for result in results:
        ticker = result['ticker']
        rec = result['recommendation']
        shares_held = result['shares_held']

        print(f"【{ticker}】当前持仓: {shares_held:,.0f} 股")
        print(f"  当前价格: ¥{result['current_price']:.3f}")
        print(f"  综合评分: {result['score']:.0f}/100")
        print(f"  RSI: {result['rsi']:.2f} ({result['rsi_interpretation']})")
        print(f"  MACD: {result['macd_interpretation']}")
        print(f"  趋势: {result['trend_interpretation']}")
        print(f"  年化波动率: {result['volatility_annual']:.2f}%")
        print(f"  最大回撤: {result['max_drawdown']:.2f}%")
        print(f"  近1月收益: {result['return_1m']:.2f}%")
        print(f"  → {rec['action_cn']}")
        if rec['shares_change'] != 0:
            print(f"  → 建议调整: {rec['shares_change']:+,d} 股 (约{rec['suggested_change_percent']:+.1f}%)")
            print(f"  → 调整金额: ¥{rec['value_change']:,.2f}")
        print(f"  → 理由: {rec['reason']}")
        print()

    # 特别标注新标的
    silver_result = next((r for r in results if r['ticker'] == '161226.SZ'), None)
    if silver_result:
        print("=" * 80)
        print("国投白银LOF (161226) 建仓评估")
        print("=" * 80)
        print(f"当前价格: ¥{silver_result['current_price']:.3f}")
        print(f"综合评分: {silver_result['score']:.0f}/100")
        print(f"技术指标: {silver_result['trend_interpretation']}")
        print(f"RSI: {silver_result['rsi']:.2f} - {silver_result['rsi_interpretation']}")
        print(f"MACD: {silver_result['macd_interpretation']}")
        print(f"年化波动率: {silver_result['volatility_annual']:.2f}%")
        print(f"近1月收益: {silver_result['return_1m']:.2f}%")
        print()
        print("建仓建议:")
        rec = silver_result['recommendation']
        print(f"  {rec['action_cn']}")
        print(f"  理由: {rec['reason']}")

        # 如果建议买入，给出建议建仓金额
        if rec['action'] in ['strong_buy', 'buy']:
            suggested_amount = total_current_value * 0.1  # 建议用总资产的10%
            suggested_shares = int(suggested_amount / silver_result['current_price'])
            print(f"  建议建仓金额: ¥{suggested_amount:,.2f} (约总资产10%)")
            print(f"  建议建仓数量: {suggested_shares:,.0f} 股")
        print()

    print("=" * 80)
    print(f"详细分析结果已保存至: {output_file}")
    print("=" * 80)


if __name__ == '__main__':
    main()
