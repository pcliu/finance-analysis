#!/usr/bin/env python3
"""
投资组合分析脚本 - 2026年1月9日
基于用户最新持仓数据生成调仓建议
"""

import sys
import os
import json
from datetime import datetime

# 添加项目路径
sys.path.insert(0, '/Users/liupengcheng/Documents/Code/finance-analysis/quantitative-trading-skills/quantitative-trading')

from scripts import (
    fetch_stock_data, 
    calculate_rsi, 
    calculate_macd, 
    calculate_bollinger_bands,
    calculate_sma
)

# 输出目录
OUTPUT_DIR = '/Users/liupengcheng/Documents/Code/finance-analysis/quantitative-trading-skills/quantitative-trading/workspace/2026-01-09/090128'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 用户持仓数据 (来自截图)
CURRENT_HOLDINGS = {
    '510880': {'name': '红利ETF', 'shares': 1000, 'cost_price': 3.206, 'profit': 15.00, 'profit_pct': 0.48},
    '512400': {'name': '有色ETF', 'shares': 1000, 'cost_price': 2.020, 'profit': 12.00, 'profit_pct': 0.62},
    '513180': {'name': '恒指科技', 'shares': 800, 'cost_price': 0.619, 'profit': -14.60, 'profit_pct': -2.29},
    '513630': {'name': '香港红利', 'shares': 1000, 'cost_price': 1.615, 'profit': -12.00, 'profit_pct': -0.71},
    '515050': {'name': '5GETF', 'shares': 500, 'cost_price': 2.328, 'profit': -1.50, 'profit_pct': -0.09},
    '515070': {'name': 'AI智能', 'shares': 500, 'cost_price': 1.992, 'profit': 17.50, 'profit_pct': 1.81},
    '588000': {'name': '科创50', 'shares': 10000, 'cost_price': 1.424, 'profit': 962.83, 'profit_pct': 6.72},
    '159516': {'name': '半导体设备', 'shares': 200, 'cost_price': 1.389, 'profit': 83.60, 'profit_pct': 30.37},
    '159770': {'name': '机器人AI', 'shares': 1000, 'cost_price': 1.069, 'profit': 10.00, 'profit_pct': 0.98},
    '159830': {'name': '上海金', 'shares': 400, 'cost_price': 9.773, 'profit': 75.50, 'profit_pct': 1.95},
    '161226': {'name': '白银基金', 'shares': 300, 'cost_price': 2.156, 'profit': 103.60, 'profit_pct': 16.12},
}

# 关注标的
POTENTIAL_ETFS = {
    '159241': {'name': '航空航天ETF天弘'},
}

def analyze_stock(symbol, name):
    """分析单支股票/ETF的技术指标"""
    try:
        # 为中国A股添加后缀
        yf_symbol = f"{symbol}.SZ" if symbol.startswith('1') else f"{symbol}.SS"
        
        # 获取6个月数据
        data = fetch_stock_data(yf_symbol, period='6mo')
        
        if data is None or data.empty:
            print(f"警告: 无法获取 {symbol} {name} 的数据")
            return None
        
        # 计算技术指标
        rsi = calculate_rsi(data, period=14)
        macd_data = calculate_macd(data)
        bb = calculate_bollinger_bands(data)
        sma_5 = calculate_sma(data, window=5)
        sma_20 = calculate_sma(data, window=20)
        
        latest_close = data['Close'].iloc[-1]
        
        # 判断趋势
        if sma_5.iloc[-1] > sma_20.iloc[-1]:
            trend = '多头'
        elif sma_5.iloc[-1] < sma_20.iloc[-1]:
            trend = '空头'
        else:
            trend = '震荡'
        
        # 计算价格变化
        change_1d = ((data['Close'].iloc[-1] / data['Close'].iloc[-2]) - 1) * 100 if len(data) > 1 else 0
        change_5d = ((data['Close'].iloc[-1] / data['Close'].iloc[-5]) - 1) * 100 if len(data) > 5 else 0
        change_20d = ((data['Close'].iloc[-1] / data['Close'].iloc[-20]) - 1) * 100 if len(data) > 20 else 0
        
        # 判断动量强弱
        if macd_data['Histogram'].iloc[-1] > macd_data['Histogram'].iloc[-2]:
            momentum = '强'
        else:
            momentum = '弱'
        
        result = {
            'symbol': symbol,
            'name': name,
            'latest_close': round(float(latest_close), 4),
            'rsi': round(float(rsi.iloc[-1]), 2),
            'sma_5': round(float(sma_5.iloc[-1]), 4),
            'sma_20': round(float(sma_20.iloc[-1]), 4),
            'macd': round(float(macd_data['MACD'].iloc[-1]), 4),
            'signal': round(float(macd_data['Signal'].iloc[-1]), 4),
            'histogram': round(float(macd_data['Histogram'].iloc[-1]), 4),
            'bb_upper': round(float(bb['Upper'].iloc[-1]), 4),
            'bb_middle': round(float(bb['Middle'].iloc[-1]), 4),
            'bb_lower': round(float(bb['Lower'].iloc[-1]), 4),
            'change_1d': round(change_1d, 2),
            'change_5d': round(change_5d, 2),
            'change_20d': round(change_20d, 2),
            'trend': trend,
            'momentum': momentum,
        }
        
        return result
        
    except Exception as e:
        print(f"分析 {symbol} {name} 时出错: {str(e)}")
        return None


def main():
    print("=" * 60)
    print("投资组合分析 - 2026年1月9日")
    print("=" * 60)
    
    results = {
        'analysis_time': datetime.now().isoformat(),
        'current_holdings': {},
        'potential_etfs': {}
    }
    
    # 分析现有持仓
    print("\n【分析现有持仓】")
    for symbol, holding in CURRENT_HOLDINGS.items():
        print(f"  分析: {symbol} {holding['name']}")
        analysis = analyze_stock(symbol, holding['name'])
        if analysis:
            analysis['current_shares'] = holding['shares']
            analysis['cost_price'] = holding['cost_price']
            analysis['profit'] = holding['profit']
            analysis['profit_pct'] = holding['profit_pct']
            # 计算当前市值
            analysis['current_value'] = round(analysis['latest_close'] * holding['shares'], 2)
            results['current_holdings'][symbol] = analysis
    
    # 分析关注的ETF
    print("\n【分析关注标的】")
    for symbol, etf in POTENTIAL_ETFS.items():
        print(f"  分析: {symbol} {etf['name']}")
        analysis = analyze_stock(symbol, etf['name'])
        if analysis:
            results['potential_etfs'][symbol] = analysis
    
    # 保存结果
    output_file = os.path.join(OUTPUT_DIR, 'analysis_result.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n分析结果已保存到: {output_file}")
    
    # 输出分析摘要
    print("\n" + "=" * 60)
    print("【分析摘要】")
    print("=" * 60)
    
    # 计算总市值
    total_value = sum(h.get('current_value', 0) for h in results['current_holdings'].values())
    print(f"\n持仓总市值: {total_value:.2f} 元")
    
    print("\n【现有持仓技术指标】")
    print("-" * 100)
    print(f"{'代码':<8} {'名称':<10} {'现价':>8} {'RSI':>6} {'趋势':>6} {'动量':>4} {'1日涨跌':>8} {'5日涨跌':>8} {'盈亏%':>8}")
    print("-" * 100)
    for symbol, h in results['current_holdings'].items():
        print(f"{symbol:<8} {h['name']:<10} {h['latest_close']:>8.3f} {h['rsi']:>6.2f} {h['trend']:>6} {h['momentum']:>4} {h['change_1d']:>7.2f}% {h['change_5d']:>7.2f}% {h['profit_pct']:>7.2f}%")
    
    print("\n【关注标的技术指标】")
    print("-" * 80)
    print(f"{'代码':<8} {'名称':<16} {'现价':>8} {'RSI':>6} {'趋势':>6} {'1日涨跌':>8} {'5日涨跌':>8}")
    print("-" * 80)
    for symbol, p in results['potential_etfs'].items():
        print(f"{symbol:<8} {p['name']:<16} {p['latest_close']:>8.3f} {p['rsi']:>6.2f} {p['trend']:>6} {p['change_1d']:>7.2f}% {p['change_5d']:>7.2f}%")
    
    return results


if __name__ == '__main__':
    main()
