#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
持仓调整分析 - 2026-01-29
Portfolio Adjustment Analysis
"""

import sys
import os
import json
from datetime import datetime

# Robust Import: Use absolute path relative to this script
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

# Output directory (same as script directory)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Define portfolios
CURRENT_HOLDINGS = {
    '510150': {'name': '消费ETF', 'shares': 23000, 'cost': None},  # Updated from image
    '510880': {'name': '红利ETF', 'shares': 10000, 'cost': 3.155},
    '512660': {'name': '军工ETF', 'shares': 6000, 'cost': 1.483},
    '515050': {'name': '5GETF', 'shares': 1000, 'cost': 2.354},
    '515070': {'name': 'AI智能', 'shares': 400, 'cost': 2.101},
    '515790': {'name': '光伏ETF', 'shares': 1000, 'cost': 1.098},
    '588000': {'name': '科创50', 'shares': 1000, 'cost': 1.599},
    '159241': {'name': '航空TH', 'shares': 6000, 'cost': 1.498},
    '159770': {'name': '机器人AI', 'shares': 200, 'cost': 1.114},
}

# All ETFs from ETFs.csv
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
    '515070': 'AI智能AIETF',
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

def calculate_technical_indicators(ticker, name, period='3mo'):
    """Calculate comprehensive technical indicators for a given ticker"""
    try:
        print(f"Fetching data for {name} ({ticker})...")
        data = fetch_stock_data(ticker, period=period)
        
        if data is None or len(data) < 30:
            print(f"  ⚠️ Insufficient data for {name}")
            return None
        
        # Calculate indicators
        rsi_6 = calculate_rsi(data, window=6)['RSI']
        rsi_14 = calculate_rsi(data, window=14)['RSI']
        bb = calculate_bollinger_bands(data, window=20, num_std=2)
        macd_data = calculate_macd(data)
        sma_20 = calculate_sma(data, window=20)['SMA']
        
        # Get latest values
        latest_price = data['Close'].iloc[-1]
        prev_price = data['Close'].iloc[-2] if len(data) >= 2 else latest_price
        price_change = ((latest_price - prev_price) / prev_price) * 100
        
        # Calculate %B (Bollinger Band position)
        bb_upper = bb['Upper'].iloc[-1]
        bb_lower = bb['Lower'].iloc[-1]
        bb_middle = bb['Middle'].iloc[-1]
        percent_b = (latest_price - bb_lower) / (bb_upper - bb_lower) if (bb_upper - bb_lower) != 0 else 0.5
        
        # MACD values
        macd_line = macd_data['MACD'].iloc[-1]
        macd_signal = macd_data['Signal'].iloc[-1]
        macd_hist = macd_data['Histogram'].iloc[-1]
        
        # Volume analysis (if available)
        volume_ratio = 1.0
        if 'Volume' in data.columns and len(data) >= 20:
            avg_volume = data['Volume'].iloc[-20:-1].mean()
            current_volume = data['Volume'].iloc[-1]
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
        
        # 20-day return
        if len(data) >= 20:
            price_20d_ago = data['Close'].iloc[-20]
            return_20d = ((latest_price - price_20d_ago) / price_20d_ago) * 100
        else:
            return_20d = 0
        
        result = {
            'ticker': ticker,
            'name': name,
            'price': float(latest_price),
            'price_change': float(price_change),
            'rsi_6': float(rsi_6.iloc[-1]),
            'rsi_14': float(rsi_14.iloc[-1]),
            'percent_b': float(percent_b),
            'bb_upper': float(bb_upper),
            'bb_lower': float(bb_lower),
            'bb_middle': float(bb_middle),
            'macd': float(macd_line),
            'macd_signal': float(macd_signal),
            'macd_hist': float(macd_hist),
            'sma_20': float(sma_20.iloc[-1]),
            'volume_ratio': float(volume_ratio),
            'return_20d': float(return_20d),
        }
        
        print(f"  ✓ {name}: Price={latest_price:.3f}, RSI(6)={result['rsi_6']:.2f}, %B={percent_b:.2f}")
        return result
        
    except Exception as e:
        print(f"  ✗ Error processing {name} ({ticker}): {str(e)}")
        return None

def main():
    """Main analysis workflow"""
    print("="*80)
    print("持仓调整分析 - Portfolio Adjustment Analysis")
    print(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'holdings': {},
        'watchlist': {},
        'summary': {}
    }
    
    # Analyze current holdings
    print("\n📊 分析当前持仓 (Current Holdings)...")
    print("-"*80)
    for ticker, info in CURRENT_HOLDINGS.items():
        analysis = calculate_technical_indicators(ticker, info['name'])
        if analysis:
            analysis['shares'] = info['shares']
            analysis['cost'] = info['cost']
            if info['cost']:
                analysis['position_pnl'] = ((analysis['price'] - info['cost']) / info['cost']) * 100
                analysis['position_value'] = analysis['price'] * info['shares']
            results['holdings'][ticker] = analysis
    
    # Analyze watchlist (non-holdings)
    print("\n\n🔍 分析观察标的 (Watchlist - Non-Holdings)...")
    print("-"*80)
    for ticker, name in ALL_ETFS.items():
        if ticker not in CURRENT_HOLDINGS:
            analysis = calculate_technical_indicators(ticker, name)
            if analysis:
                results['watchlist'][ticker] = analysis
    
    # Save results to JSON
    output_file = os.path.join(SCRIPT_DIR, 'portfolio_adjustment_data.json')
    clean_results = make_serializable(results)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(clean_results, f, indent=2, ensure_ascii=False)
    
    print("\n"+"="*80)
    print(f"✅ 分析完成！数据已保存至: {output_file}")
    print("="*80)
    
    # Print summary statistics
    print("\n📈 市场概览 (Market Overview):")
    print("-"*80)
    
    # Categorize by RSI
    extreme_overbought = []  # RSI > 80
    overbought = []  # 70 < RSI <= 80
    healthy = []  # 40 <= RSI <= 70
    oversold = []  # RSI < 40
    
    all_tickers = {**results['holdings'], **results['watchlist']}
    for ticker, data in all_tickers.items():
        rsi = data['rsi_6']
        item = f"{data['name']}({ticker})"
        if rsi > 80:
            extreme_overbought.append((item, rsi, data.get('percent_b', 0)))
        elif rsi > 70:
            overbought.append((item, rsi, data.get('percent_b', 0)))
        elif rsi >= 40:
            healthy.append((item, rsi, data.get('percent_b', 0)))
        else:
            oversold.append((item, rsi, data.get('percent_b', 0)))
    
    print(f"🔴 极度超买区 (RSI>80): {len(extreme_overbought)}个")
    for item, rsi, pb in sorted(extreme_overbought, key=lambda x: x[1], reverse=True)[:5]:
        print(f"   - {item}: RSI={rsi:.1f}, %B={pb:.2f}")
    
    print(f"\n🟠 超买震荡区 (70<RSI≤80): {len(overbought)}个")
    for item, rsi, pb in sorted(overbought, key=lambda x: x[1], reverse=True)[:5]:
        print(f"   - {item}: RSI={rsi:.1f}, %B={pb:.2f}")
    
    print(f"\n✅ 健康趋势区 (40≤RSI≤70): {len(healthy)}个")
    print(f"   (共{len(healthy)}个品种)")
    
    print(f"\n🟢 超卖区 (RSI<40): {len(oversold)}个")
    for item, rsi, pb in sorted(oversold, key=lambda x: x[1]):
        print(f"   - {item}: RSI={rsi:.1f}, %B={pb:.2f}")
    
    return results

if __name__ == '__main__':
    main()
