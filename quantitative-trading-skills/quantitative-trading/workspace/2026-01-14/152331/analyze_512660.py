#!/usr/bin/env python3
"""
Analysis script for ETF 512660 (Military ETF)
"""

import sys
import os
import json
import pandas as pd
import numpy as np
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from scripts.data_fetcher import DataFetcher
from scripts.strategies import TradingStrategy
from scripts.indicators import TechnicalIndicators

def analyze():
    # Setup
    ticker = '512660.SH' # Military ETF
    print(f"Analyzing {ticker}...")
    
    # Fetch Data
    fetcher = DataFetcher()
    data = fetcher.fetch_stock_data(ticker, period='1y', provider='tushare')
    
    if data is None or data.empty:
        print(f"Failed to fetch data for {ticker}")
        return

    # Initialize Strategy
    strategy = TradingStrategy()
    
    # Run Multi-Strategy
    strategies_list = ['ma_crossover', 'rsi', 'macd', 'bollinger', 'stochastic', 'momentum', 'mean_reversion']
    results = strategy.multi_strategy_signals(data, strategies=strategies_list)
    
    # Calculate indicators explicitly for reporting
    ti = TechnicalIndicators()
    rsi_df = ti.calculate_rsi(data, window=14)
    macd_df = ti.calculate_macd(data)
    
    # Get latest data
    latest = results.iloc[-1]
    latest_rsi = rsi_df.iloc[-1]['RSI']
    latest_macd = macd_df.iloc[-1]
    
    # DEBUG: Print recent history
    print("\n--- DEBUG: Recent Data (Last 5 Days) ---")
    cols_to_show = ['Close', 'p_change'] if 'p_change' in results.columns else ['Close']
    signal_cols = [col for col in results.columns if 'Signal' in col]
    cols_to_show.extend(signal_cols)
    existing_cols = [c for c in cols_to_show if c in results.columns]
    print(results[existing_cols].tail(5))
    print("----------------------------------------")
    
    # Find last active signals
    print("\n--- Last Active Signals ---")
    for col in existing_cols:
        if 'Signal' in col:
            non_zero = results[results[col] != 0]
            if not non_zero.empty:
                last_date = non_zero.index[-1].strftime('%Y-%m-%d')
                last_val = non_zero[col].iloc[-1]
                print(f"{col}: {last_val} on {last_date}")
            else:
                print(f"{col}: No signals in period")
    print("---------------------------\n")

    analysis_summary = {
        'date': results.index[-1].strftime('%Y-%m-%d'),
        'close': float(latest['Close']),
        'signals': {
            'ma_crossover': int(latest.get('MA_Signal', 0)),
            'rsi': int(latest.get('RSI_Signal', 0)),
            'macd': int(latest.get('MACD_Signal', 0)),
            'bollinger': int(latest.get('BB_Signal', 0)),
            'stochastic': int(latest.get('Stoch_Signal', 0)),
            'momentum': int(latest.get('Momentum_Signal', 0)),
            'mean_reversion': int(latest.get('MeanRev_Signal', 0)),
            'consensus': float(latest.get('Consensus_Signal', 0)),
            'final': int(latest.get('Final_Signal', 0))
        },
        'indicators': {
            'rsi_value': float(latest_rsi),
            'macd_value': float(latest_macd['MACD']),
            'macd_signal': float(latest_macd['Signal']),
            'volatility': float(latest.get('Volatility', 0))
        }
    }
    
    # Save results
    output_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(output_dir, 'analysis_result.json')
    with open(json_path, 'w') as f:
        json.dump(analysis_summary, f, indent=2)
        
    print(json.dumps(analysis_summary, indent=2))
    print(f"Analysis saved to {json_path}")

    # Generate Report Content suggestion
    print("\n--- REPORT SUGGESTION ---")
    recommendation = "HOLD/NEUTRAL"
    if analysis_summary['signals']['final'] == 1:
        recommendation = "BUY"
    elif analysis_summary['signals']['final'] == -1:
        recommendation = "SELL"
        
    print(f"Ticker: {ticker}")
    print(f"Price: {analysis_summary['close']}")
    print(f"Recommendation: {recommendation}")
    print(f"Consensus Score: {analysis_summary['signals']['consensus']}")
    print("-------------------------")

if __name__ == "__main__":
    analyze()
