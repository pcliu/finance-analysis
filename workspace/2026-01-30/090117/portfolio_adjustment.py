#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Portfolio Adjustment Analysis - 2026-01-30
持仓调整分析 - 基于多因子技术诊断
"""

import sys
import os
import json
from datetime import datetime, timedelta

# Setup path for skill import
SKILL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../.agent/skills/quantitative-trading'))
sys.path.append(SKILL_DIR)

from scripts import (
    fetch_stock_data,
    calculate_rsi,
    calculate_bollinger_bands,
    calculate_macd,
    calculate_sma
)
from scripts.utils import make_serializable

# Output directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Current holdings from user's image
CURRENT_HOLDINGS = {
    '510150': {'name': '消费ETF', 'shares': 33000, 'cost': 0.560},  # Estimated
    '510880': {'name': '红利ETF', 'shares': 10000, 'cost': 3.166},
    '512170': {'name': '医疗ETF', 'shares': 10000, 'cost': 0.362},
    '512660': {'name': '军工ETF', 'shares': 6000, 'cost': 1.473},
    '515050': {'name': '5GETF', 'shares': 1000, 'cost': 2.340},
    '515070': {'name': 'AI智能', 'shares': 400, 'cost': 2.091},
    '515790': {'name': '光伏ETF', 'shares': 1000, 'cost': 1.094},
    '588000': {'name': '科创50', 'shares': 1000, 'cost': 1.589},
    '159241': {'name': '航空TH', 'shares': 6000, 'cost': 1.485},
    '159770': {'name': '机器人AI', 'shares': 200, 'cost': 1.107},
}

# All ETFs from ETFs.csv (watchlist)
ALL_ETFS = {
    '510150': '消费ETF',
    '159985': '豆粕ETF',
    '512890': '红利低波ETF',
    '512660': '军工ETF',
    '159241': '航空航天ETF天弘',
    '159206': '卫星ETF',
    '515790': '光伏ETF',
    '516780': '稀土ETF',
    '512170': '医疗ETF',
    '561330': '矿业ETF',
    '159870': '化工ETF',
    '561560': '电力ETF',
    '159830': '上海金ETF',
    '159770': '机器人ETF',
    '515070': '人工智能AIETF',
    '159326': '电网设备ETF',
    '159516': '半导体设备ETF',
    '515050': '通信ETF华夏',
    '161226': '国投白银LOF',
    '518880': '黄金ETF',
    '512400': '有色金属ETF',
    '510880': '红利ETF',
    '513180': '恒生科技指数ETF',
    '513630': '港股红利指数ETF',
    '588000': '科创50ETF',
}

def convert_ts_code(code):
    """Convert code to tushare format"""
    if len(code) == 6:
        if code.startswith('6'):
            return f"{code}.SH"
        elif code.startswith(('0', '3')):
            return f"{code}.SZ"
        elif code.startswith('5'):
            return f"{code}.SH"
        elif code.startswith('1'):
            if code.startswith('15'):
                return f"{code}.SZ"
            else:
                return f"{code}.SZ"
        else:
            return f"{code}.SH"
    return code

def analyze_etf(code, name, period='3mo'):
    """Analyze single ETF with technical indicators"""
    print(f"  Analyzing {name} ({code})...")
    
    try:
        # Fetch data
        ts_code = convert_ts_code(code)
        data = fetch_stock_data(ts_code, period=period)
        
        if data is None or len(data) < 20:
            print(f"    ⚠️ Insufficient data for {name}")
            return None
        
        # Calculate indicators
        rsi_6 = calculate_rsi(data, window=6)
        rsi_14 = calculate_rsi(data, window=14)
        bb = calculate_bollinger_bands(data, window=20, num_std=2)
        macd_data = calculate_macd(data)
        sma_20 = calculate_sma(data, window=20)
        sma_60 = calculate_sma(data, window=60)
        
        # Get latest values
        latest = data.iloc[-1]
        prev = data.iloc[-2] if len(data) > 1 else latest
        
        current_price = float(latest['Close'])
        prev_price = float(prev['Close'])
        daily_change = ((current_price - prev_price) / prev_price * 100) if prev_price > 0 else 0
        
        # 20-day performance
        if len(data) >= 20:
            price_20_days_ago = float(data.iloc[-20]['Close'])
            change_20d = ((current_price - price_20_days_ago) / price_20_days_ago * 100)
        else:
            change_20d = 0
        
        # Volume ratio
        current_volume = float(latest['Volume'])
        avg_volume_20 = float(data['Volume'].tail(20).mean())
        volume_ratio = current_volume / avg_volume_20 if avg_volume_20 > 0 else 1.0
        
        # Calculate Bollinger Bands %B
        result_bb_upper = float(bb['Upper'].iloc[-1])
        result_bb_middle = float(bb['Middle'].iloc[-1])
        result_bb_lower = float(bb['Lower'].iloc[-1])
        price_range = result_bb_upper - result_bb_lower if (result_bb_upper - result_bb_lower) > 0 else 1
        percent_b = (current_price - result_bb_lower) / price_range if price_range > 0 else 0.5
        
        result = {
            'code': code,
            'name': name,
            'price': current_price,
            'daily_change_pct': daily_change,
            'change_20d_pct': change_20d,
            'rsi_6': float(rsi_6['RSI'].iloc[-1]),
            'rsi_14': float(rsi_14['RSI'].iloc[-1]),
            'bb_upper': result_bb_upper,
            'bb_middle': result_bb_middle,
            'bb_lower': result_bb_lower,
            'bb_percent_b': percent_b,
            'macd': float(macd_data['MACD'].iloc[-1]),
            'macd_signal': float(macd_data['Signal'].iloc[-1]),
            'macd_histogram': float(macd_data['Histogram'].iloc[-1]),
            'sma_20': float(sma_20['SMA'].iloc[-1]),
            'sma_60': float(sma_60['SMA'].iloc[-1]),
            'volume_ratio': volume_ratio,
        }
        
        return result
        
    except Exception as e:
        print(f"    ❌ Error analyzing {name}: {str(e)}")
        return None

def categorize_by_risk(analysis_results):
    """Categorize ETFs by technical risk levels"""
    extreme_danger = []  # RSI > 85 or %B > 1.0
    high_risk = []       # 70 < RSI <= 85
    healthy = []         # 40 <= RSI <= 70
    oversold = []        # RSI < 40
    
    for result in analysis_results:
        if result is None:
            continue
            
        rsi = result['rsi_6']
        percent_b = result['bb_percent_b']
        
        if rsi > 85 or percent_b > 1.0:
            extreme_danger.append(result)
        elif rsi > 70:
            high_risk.append(result)
        elif rsi >= 40:
            healthy.append(result)
        else:
            oversold.append(result)
    
    # Sort by RSI within each category
    extreme_danger.sort(key=lambda x: x['rsi_6'], reverse=True)
    high_risk.sort(key=lambda x: x['rsi_6'], reverse=True)
    healthy.sort(key=lambda x: x['rsi_6'], reverse=True)
    oversold.sort(key=lambda x: x['rsi_6'])
    
    return {
        'extreme_danger': extreme_danger,
        'high_risk': high_risk,
        'healthy': healthy,
        'oversold': oversold,
    }

def main():
    print("="*80)
    print("Portfolio Adjustment Analysis - 2026-01-30")
    print("="*80)
    
    # Analyze all ETFs
    print("\n📊 Starting comprehensive market analysis...")
    all_analysis = []
    
    for code, name in ALL_ETFS.items():
        result = analyze_etf(code, name)
        if result:
            all_analysis.append(result)
    
    print(f"\n✅ Analyzed {len(all_analysis)} ETFs successfully")
    
    # Categorize by risk
    categorized = categorize_by_risk(all_analysis)
    
    # Save results
    output_data = {
        'timestamp': datetime.now().isoformat(),
        'current_holdings': CURRENT_HOLDINGS,
        'all_analysis': all_analysis,
        'categorized': categorized,
    }
    
    output_file = os.path.join(SCRIPT_DIR, 'portfolio_adjustment_data.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(make_serializable(output_data), f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Data saved to: {output_file}")
    
    # Print summary
    print("\n" + "="*80)
    print("MARKET SUMMARY")
    print("="*80)
    print(f"🔴 Extreme Danger Zone (RSI>85 or %B>1.0): {len(categorized['extreme_danger'])} ETFs")
    print(f"🟠 High Risk Zone (70<RSI≤85): {len(categorized['high_risk'])} ETFs")
    print(f"✅ Healthy Zone (40≤RSI≤70): {len(categorized['healthy'])} ETFs")
    print(f"🟢 Oversold Zone (RSI<40): {len(categorized['oversold'])} ETFs")
    
    if categorized['extreme_danger']:
        print("\n🔴 EXTREME DANGER - ABSOLUTE NO ENTRY:")
        for item in categorized['extreme_danger'][:5]:
            print(f"  {item['name']} ({item['code']}): RSI={item['rsi_6']:.2f}, %B={item['bb_percent_b']:.2f}, Price={item['price']:.3f}")
    
    if categorized['oversold']:
        print("\n🟢 OVERSOLD - POTENTIAL BUY OPPORTUNITIES:")
        for item in categorized['oversold']:
            print(f"  {item['name']} ({item['code']}): RSI={item['rsi_6']:.2f}, %B={item['bb_percent_b']:.2f}, Price={item['price']:.3f}")
    
    print("\n" + "="*80)
    print("Analysis complete! Check the report for detailed recommendations.")
    print("="*80)

if __name__ == '__main__':
    main()
