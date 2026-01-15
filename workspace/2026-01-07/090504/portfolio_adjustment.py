#!/usr/bin/env python3
"""Portfolio analysis script for investment recommendations."""

import sys
import os
import json
from datetime import datetime

# Add path for imports
sys.path.insert(0, '/Users/liupengcheng/Documents/Code/finance-analysis/.agent/skills/quantitative-trading')

from scripts import (
    fetch_stock_data, 
    calculate_rsi, 
    calculate_sma, 
    calculate_ema,
    calculate_macd, 
    calculate_bollinger_bands
)

# Output directory
output_dir = '/Users/liupengcheng/Documents/Code/finance-analysis/.agent/skills/quantitative-trading/workspace/2026-01-07/090504'
os.makedirs(output_dir, exist_ok=True)

# Current holdings from user's screenshot
holdings = {
    '510880.SS': {'name': '红利ETF', 'shares': 1000, 'value': 3180.00, 'pnl': -26.00, 'pnl_pct': -0.80},
    '515050.SS': {'name': '5GETF', 'shares': 500, 'value': 1164.00, 'pnl': 0.00, 'pnl_pct': 0.04},
    '515070.SS': {'name': 'AI智能', 'shares': 500, 'value': 1002.50, 'pnl': 6.50, 'pnl_pct': 0.70},
    '588000.SS': {'name': '科创50', 'shares': 8000, 'value': 11832.00, 'pnl': 447.51, 'pnl_pct': 3.94},
    '159516.SZ': {'name': '半导体设备', 'shares': 1000, 'value': 1635.00, 'pnl': 16.00, 'pnl_pct': 1.02},
    '159770.SZ': {'name': '机器人AI', 'shares': 1000, 'value': 1074.00, 'pnl': 5.00, 'pnl_pct': 0.51},
    '159830.SZ': {'name': '上海金', 'shares': 400, 'value': 3956.00, 'pnl': 66.70, 'pnl_pct': 1.73},
    '161226.SZ': {'name': '白银基金', 'shares': 500, 'value': 1186.00, 'pnl': 20.50, 'pnl_pct': 1.80},
}

# New ETFs to consider
new_etfs = {
    '159241.SZ': {'name': '航空航天ETF天弘'},
    '513630.SS': {'name': '恒生科技指数ETF'},  # Also noted as 港股红利 - user may have error
    '159691.SZ': {'name': '港股红利指数ETF'},  # Correct code for HK dividend ETF
}

def analyze_stock(ticker, name):
    """Analyze a single stock and return metrics."""
    try:
        data = fetch_stock_data(ticker, period='3mo')
        if data is None or len(data) < 20:
            return None
        
        # Calculate indicators
        rsi = calculate_rsi(data, period=14)
        sma_5 = calculate_sma(data, window=5)
        sma_10 = calculate_sma(data, window=10)
        sma_20 = calculate_sma(data, window=20)
        ema_12 = calculate_ema(data, window=12)
        macd = calculate_macd(data)
        bb = calculate_bollinger_bands(data)
        
        current_price = float(data['Close'].iloc[-1])
        prev_price = float(data['Close'].iloc[-2]) if len(data) > 1 else current_price
        
        # Trend analysis
        trend = 'bullish' if sma_5.iloc[-1] > sma_20.iloc[-1] else 'bearish'
        momentum = 'strong' if abs(macd['Histogram'].iloc[-1]) > abs(macd['Histogram'].iloc[-5]) else 'weak'
        
        # BB position
        bb_position = 'upper' if current_price > bb['Upper'].iloc[-1] else (
            'lower' if current_price < bb['Lower'].iloc[-1] else 'middle'
        )
        
        return {
            'ticker': ticker,
            'name': name,
            'current_price': current_price,
            'prev_price': prev_price,
            'change_pct': (current_price - prev_price) / prev_price * 100,
            'rsi': float(rsi.iloc[-1]),
            'sma_5': float(sma_5.iloc[-1]),
            'sma_10': float(sma_10.iloc[-1]),
            'sma_20': float(sma_20.iloc[-1]),
            'ema_12': float(ema_12.iloc[-1]),
            'macd': float(macd['MACD'].iloc[-1]),
            'macd_signal': float(macd['Signal'].iloc[-1]),
            'macd_histogram': float(macd['Histogram'].iloc[-1]),
            'bb_upper': float(bb['Upper'].iloc[-1]),
            'bb_middle': float(bb['Middle'].iloc[-1]),
            'bb_lower': float(bb['Lower'].iloc[-1]),
            'trend': trend,
            'momentum': momentum,
            'bb_position': bb_position,
            'price_vs_sma20': (current_price - sma_20.iloc[-1]) / sma_20.iloc[-1] * 100,
        }
    except Exception as e:
        print(f"Error analyzing {ticker}: {e}")
        return None

# Analyze all holdings
print("=" * 60)
print("Analyzing current holdings...")
print("=" * 60)

results = {'holdings': [], 'new_etfs': [], 'timestamp': datetime.now().isoformat()}

for ticker, info in holdings.items():
    print(f"\nAnalyzing {info['name']} ({ticker})...")
    analysis = analyze_stock(ticker, info['name'])
    if analysis:
        analysis['shares'] = info['shares']
        analysis['current_value'] = info['value']
        analysis['pnl'] = info['pnl']
        analysis['pnl_pct'] = info['pnl_pct']
        results['holdings'].append(analysis)
        print(f"  RSI: {analysis['rsi']:.2f}, Trend: {analysis['trend']}, Price: {analysis['current_price']:.4f}")

# Analyze new ETFs
print("\n" + "=" * 60)
print("Analyzing potential new investments...")
print("=" * 60)

for ticker, info in new_etfs.items():
    print(f"\nAnalyzing {info['name']} ({ticker})...")
    analysis = analyze_stock(ticker, info['name'])
    if analysis:
        results['new_etfs'].append(analysis)
        print(f"  RSI: {analysis['rsi']:.2f}, Trend: {analysis['trend']}, Price: {analysis['current_price']:.4f}")

# Calculate portfolio summary
total_value = sum(h.get('current_value', 0) for h in results['holdings'])
results['portfolio_summary'] = {
    'total_value': total_value,
    'available_cash': 68024.96,
    'total_assets': 93054.46,
    'position_ratio': 26.90,
    'budget_for_increase': 2000,  # User's constraint
}

# Save results
output_file = f'{output_dir}/analysis_result.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"\n\nResults saved to: {output_file}")
print("=" * 60)
