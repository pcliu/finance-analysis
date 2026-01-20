#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
布林带突破分析 - 2026-01-20
分析当前持仓和候选ETF的布林带突破情况
"""

import sys
import os
import json
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../.agent/skills/quantitative-trading'))
sys.path.append(SKILL_DIR)

from scripts import fetch_stock_data, calculate_bollinger_bands, calculate_rsi
from scripts.utils import make_serializable

# 当前持仓
CURRENT_HOLDINGS = {
    '510150': {'name': '消费ETF', 'shares': 10000},
    '510880': {'name': '红利ETF', 'shares': 3500},
    '512660': {'name': '军工ETF', 'shares': 5000},
    '513180': {'name': '恒指科技', 'shares': 800},
    '513630': {'name': '香港红利', 'shares': 500},
    '515050': {'name': '5GETF', 'shares': 1000},
    '515070': {'name': 'AI智能', 'shares': 400},
    '588000': {'name': '科创50', 'shares': 1000},
    '159241': {'name': '航空TH', 'shares': 5000},
    '159770': {'name': '机器人AI', 'shares': 500},
    '159830': {'name': '上海金', 'shares': 400},
    '161226': {'name': '白银基金', 'shares': 300},
}

# 非持仓品种
NON_HOLDINGS = {
    '159352': 'A500ETF 南方',
    '159326': '电网设备 ETF',
    '159516': '半导体设备 ETF',
    '518880': '黄金 ETF',
    '512400': '有色金属 ETF',
}

def analyze_bollinger(ticker, name):
    """分析布林带突破情况"""
    try:
        symbol = ticker
        if ticker.startswith('5'):
            symbol = ticker + '.SS'
        elif ticker.startswith('1'):
            symbol = ticker + '.SZ'
        
        data = fetch_stock_data(symbol, period='3mo')
        if data.empty:
            return None
        
        # 计算布林带
        bb = calculate_bollinger_bands(data, window=20, num_std=2)
        rsi = calculate_rsi(data, window=6)
        
        current_price = float(data['Close'].iloc[-1])
        upper_band = float(bb['Upper'].iloc[-1])
        middle_band = float(bb['Middle'].iloc[-1])
        lower_band = float(bb['Lower'].iloc[-1])
        bandwidth = float(bb['Bandwidth'].iloc[-1])
        percent_b = float(bb['Percent_B'].iloc[-1])
        current_rsi = float(rsi['RSI'].iloc[-1])
        
        # 判断突破状态
        if current_price > upper_band:
            status = "🔴 突破上轨"
            signal = "超买信号,价格过热"
            action = "考虑止盈或减仓"
            risk_level = "高风险"
        elif current_price < lower_band:
            status = "🟢 突破下轨"
            signal = "超卖信号,价格低估"
            action = "可考虑建仓或加仓"
            risk_level = "低风险"
        elif percent_b > 0.8:
            status = "🟠 接近上轨"
            signal = "价格偏高"
            action = "谨慎持有"
            risk_level = "中高风险"
        elif percent_b < 0.2:
            status = "🟡 接近下轨"
            signal = "价格偏低"
            action = "可关注建仓"
            risk_level = "中低风险"
        else:
            status = "✅ 正常区间"
            signal = "价格健康"
            action = "持有或观望"
            risk_level = "中性"
        
        # 计算距离上下轨的距离百分比
        distance_to_upper = ((upper_band - current_price) / current_price) * 100
        distance_to_lower = ((current_price - lower_band) / current_price) * 100
        
        return {
            'ticker': ticker,
            'name': name,
            'price': current_price,
            'upper_band': upper_band,
            'middle_band': middle_band,
            'lower_band': lower_band,
            'bandwidth': bandwidth,
            'percent_b': percent_b,
            'rsi_6': current_rsi,
            'distance_to_upper': distance_to_upper,
            'distance_to_lower': distance_to_lower,
            'status': status,
            'signal': signal,
            'action': action,
            'risk_level': risk_level,
        }
    except Exception as e:
        print(f"分析 {ticker} 时出错: {e}")
        return None

def main():
    print("="*80)
    print("开始布林带突破分析...")
    print("="*80)
    
    results = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'holdings': [],
        'non_holdings': [],
        'breakthrough': {
            'upper': [],  # 突破上轨
            'lower': [],  # 突破下轨
            'near_upper': [],  # 接近上轨
            'near_lower': [],  # 接近下轨
        }
    }
    
    # 1. 分析持仓品种
    print("\n[1/2] 分析持仓品种布林带...")
    for ticker, info in CURRENT_HOLDINGS.items():
        print(f"  - 分析 {ticker} ({info['name']})...")
        analysis = analyze_bollinger(ticker, info['name'])
        if analysis:
            analysis['is_holding'] = True
            analysis['shares'] = info['shares']
            results['holdings'].append(analysis)
            
            # 分类
            if '突破上轨' in analysis['status']:
                results['breakthrough']['upper'].append(analysis)
            elif '突破下轨' in analysis['status']:
                results['breakthrough']['lower'].append(analysis)
            elif '接近上轨' in analysis['status']:
                results['breakthrough']['near_upper'].append(analysis)
            elif '接近下轨' in analysis['status']:
                results['breakthrough']['near_lower'].append(analysis)
    
    # 2. 分析非持仓品种
    print("\n[2/2] 分析非持仓品种布林带...")
    for ticker, name in NON_HOLDINGS.items():
        print(f"  - 分析 {ticker} ({name})...")
        analysis = analyze_bollinger(ticker, name)
        if analysis:
            analysis['is_holding'] = False
            results['non_holdings'].append(analysis)
            
            # 分类
            if '突破上轨' in analysis['status']:
                results['breakthrough']['upper'].append(analysis)
            elif '突破下轨' in analysis['status']:
                results['breakthrough']['lower'].append(analysis)
            elif '接近上轨' in analysis['status']:
                results['breakthrough']['near_upper'].append(analysis)
            elif '接近下轨' in analysis['status']:
                results['breakthrough']['near_lower'].append(analysis)
    
    # 3. 按PercentB排序
    results['holdings'].sort(key=lambda x: x['percent_b'], reverse=True)
    results['non_holdings'].sort(key=lambda x: x['percent_b'], reverse=True)
    
    # 4. 保存结果
    output_file = os.path.join(SCRIPT_DIR, 'bollinger_analysis_data.json')
    clean_results = make_serializable(results)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(clean_results, f, indent=4, ensure_ascii=False)
    
    print(f"\n✅ 分析完成! 结果已保存至: {output_file}")
    print("="*80)
    
    # 5. 输出摘要
    print(f"\n📊 布林带突破摘要:")
    print(f"  - 突破上轨(超买): {len(results['breakthrough']['upper'])} 只")
    print(f"  - 突破下轨(超卖): {len(results['breakthrough']['lower'])} 只")
    print(f"  - 接近上轨: {len(results['breakthrough']['near_upper'])} 只")
    print(f"  - 接近下轨: {len(results['breakthrough']['near_lower'])} 只")
    
    if results['breakthrough']['upper']:
        print(f"\n🔴 突破上轨品种:")
        for item in results['breakthrough']['upper']:
            print(f"    - {item['ticker']} ({item['name']}): "
                  f"价格{item['price']:.3f} > 上轨{item['upper_band']:.3f}, "
                  f"RSI(6)={item['rsi_6']:.1f}")
    
    if results['breakthrough']['lower']:
        print(f"\n🟢 突破下轨品种:")
        for item in results['breakthrough']['lower']:
            print(f"    - {item['ticker']} ({item['name']}): "
                  f"价格{item['price']:.3f} < 下轨{item['lower_band']:.3f}, "
                  f"RSI(6)={item['rsi_6']:.1f}")

if __name__ == '__main__':
    main()
