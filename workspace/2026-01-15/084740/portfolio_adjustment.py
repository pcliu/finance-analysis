#!/usr/bin/env python3
import sys
import os
import json
import pandas as pd

# Setup project path
PROJECT_ROOT = '/Users/liupengcheng/Documents/Code/finance-analysis/.agent/skills/quantitative-trading'
sys.path.insert(0, PROJECT_ROOT)

from scripts.data_fetcher import DataFetcher
from scripts.indicators import TechnicalIndicators

def analyze():
    # 1. Output directory - use script's own directory
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    abs_output_dir = SCRIPT_DIR
    
    fetcher = DataFetcher(default_provider='tushare')
    ti = TechnicalIndicators()
    
    # 2. Define Assets
    holdings = {
        '510150.SH': {'name': '消费ETF', 'qty': 5000},
        '510880.SH': {'name': '红利ETF', 'qty': 1000},
        '513180.SH': {'name': '恒指科技', 'qty': 800},
        '513630.SH': {'name': '香港红利', 'qty': 500},
        '515050.SH': {'name': '5GETF', 'qty': 1000},
        '515070.SH': {'name': 'AI智能', 'qty': 400},
        '588000.SH': {'name': '科创50', 'qty': 2000},
        '159770.SZ': {'name': '机器人AI', 'qty': 700},
        '159830.SZ': {'name': '上海金', 'qty': 400},
        '161226.SZ': {'name': '白银基金', 'qty': 300},
    }
    
    candidates = [
        '512660.SH', '159241.SZ', '159352.SZ', '159326.SZ', 
        '159516.SZ', '518880.SH', '512400.SH'
    ]
    
    all_tickers = list(holdings.keys()) + candidates
    
    # 3. Fetch Data and Calculate Indicators
    results = {}
    for ticker in all_tickers:
        print(f"Analyzing {ticker}...")
        data = fetcher.fetch_stock_data(ticker, period='6mo')
        if data is not None and not data.empty:
            rsi = ti.calculate_rsi(data, window=14)
            macd = ti.calculate_macd(data)
            bb = ti.calculate_bollinger_bands(data)
            
            results[ticker] = {
                'price': float(data['Close'].iloc[-1]),
                'rsi': float(rsi.iloc[-1]),
                'macd': float(macd['MACD'].iloc[-1]),
                'macd_signal': float(macd['Signal'].iloc[-1]),
                'bb_upper': float(bb['Upper'].iloc[-1]),
                'bb_middle': float(bb['Middle'].iloc[-1]),
                'bb_lower': float(bb['Lower'].iloc[-1]),
                'pct_change_5d': float((data['Close'].iloc[-1] / data['Close'].iloc[-6] - 1) * 100) if len(data) > 6 else 0,
                'pct_change_20d': float((data['Close'].iloc[-1] / data['Close'].iloc[-21] - 1) * 100) if len(data) > 21 else 0
            }
            
    # 4. Save results
    with open(os.path.join(abs_output_dir, 'analysis_result.json'), 'w') as f:
        json.dump(results, f, indent=2)
        
    print(f"Saved results to {abs_output_dir}")
    return abs_output_dir

if __name__ == "__main__":
    analyze()
