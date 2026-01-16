#!/usr/bin/env python3
import os
import sys
import json
import pandas as pd
import numpy as np

# Add the skill scripts to path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../.agent/skills/quantitative-trading'))
sys.path.append(SKILL_ROOT)

from scripts import DataFetcher, TechnicalIndicators

def analyze_tsla():
    ticker = 'TSLA'
    fetcher = DataFetcher()
    tech = TechnicalIndicators()
    
    # 1. Fetch data
    try:
        data = fetcher.fetch_stock_data(ticker, period='1y')
        if data is None or data.empty:
            print(f"Error: Could not fetch data for {ticker}")
            return
    except Exception as e:
        print(f"Exception fetching data: {e}")
        return

    # 2. Calculate technical indicators
    indicators_df = tech.calculate_all_indicators(data)
    
    # Calculate annual volatility (standard deviation of daily returns * sqrt(252))
    returns = data['Close'].pct_change().dropna()
    volatility = returns.std() * np.sqrt(252)
    
    # Combine data
    full_data = data.join(indicators_df)
    
    # 3. Prepare summary for report (latest values)
    latest = full_data.iloc[-1]
    prev = full_data.iloc[-2]
    
    summary = {
        'ticker': ticker,
        'date': latest.name.strftime('%Y-%m-%d'),
        'price': round(latest['Close'], 2),
        'rsi': round(latest['RSI'], 2),
        'macd': {
            'dif': round(latest['MACD_MACD'], 2),
            'dea': round(latest['MACD_Signal'], 2),
            'hist': round(latest['MACD_Histogram'], 2)
        },
        'sma': {
            'sma_20': round(latest['SMA_20'], 2),
            'sma_50': round(latest['SMA_50'], 2),
            'sma_200': round(latest['SMA_200'], 2)
        },
        'bollinger': {
            'upper': round(latest['BB_Upper'], 2),
            'middle': round(latest['BB_Middle'], 2),
            'lower': round(latest['BB_Lower'], 2),
            'percent_b': round(latest['BB_Percent_B'], 2)
        },
        'cci': round(latest['CCI'], 2),
        'atr': round(latest['ATR'], 2),
        'volatility': round(volatility * 100, 2), # Percentage
    }
    
    # 4. Save files
    # CSV for raw data
    full_data.to_csv(os.path.join(SCRIPT_DIR, f'technical_analysis_{ticker}_data.csv'))
    
    # JSON for summary
    with open(os.path.join(SCRIPT_DIR, f'technical_analysis_{ticker}_data.json'), 'w') as f:
        json.dump(summary, f, indent=4)
        
    print(f"Analysis for {ticker} completed.")
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    analyze_tsla()
