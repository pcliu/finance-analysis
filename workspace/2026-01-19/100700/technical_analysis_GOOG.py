
import sys
import os
import pandas as pd
import numpy as np
import json

# Add skill path
sys.path.append('/Users/liupengcheng/Documents/Code/finance-analysis/.agent/skills/quantitative-trading')
from scripts.data_fetcher import DataFetcher
from scripts.indicators import TechnicalIndicators

def analyze_goog():
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    
    ticker = 'GOOG'
    fetcher = DataFetcher()
    data = fetcher.fetch_stock_data(ticker, period='1y')
    
    if data is None or data.empty:
        print("Failed to fetch data")
        return

    ti = TechnicalIndicators()
    indicators = ti.calculate_all_indicators(data)
    
    # Merge indicators with original data
    full_df = data.join(indicators)
    
    # Calculate Volatility (Annualized)
    full_df['Returns'] = full_df['Close'].pct_change()
    volatility = full_df['Returns'].std() * np.sqrt(252)
    
    # Get latest values
    latest = full_df.iloc[-1]
    
    # Handle NaN values for JSON serialization
    def safe_float(val):
        if pd.isna(val):
            return None
        return float(val)

    summary = {
        'date': str(latest.name),
        'price': safe_float(latest['Close']),
        'rsi': safe_float(latest['RSI']),
        'macd': safe_float(latest.get('MACD_MACD')),
        'macd_signal': safe_float(latest.get('MACD_Signal')),
        'macd_hist': safe_float(latest.get('MACD_Histogram')),
        'sma_20': safe_float(latest.get('SMA_20')),
        'sma_50': safe_float(latest.get('SMA_50')),
        'sma_200': safe_float(latest.get('SMA_200')),
        'bb_upper': safe_float(latest.get('BB_Upper')),
        'bb_middle': safe_float(latest.get('BB_Middle')),
        'bb_lower': safe_float(latest.get('BB_Lower')),
        'bb_percent_b': safe_float(latest.get('BB_Percent_B')),
        'cci': safe_float(latest.get('CCI')),
        'atr': safe_float(latest.get('ATR')),
        'volatility': safe_float(volatility)
    }
    
    print(json.dumps(summary, indent=2))
    
    # Save detailed data
    output_file = os.path.join(SCRIPT_DIR, f'technical_analysis_{ticker}_data.json')
    # Save last 30 days for reference in JSON
    full_df.tail(30).to_json(output_file, date_format='iso')
    print(f"Detailed data saved to {output_file}")

if __name__ == "__main__":
    analyze_goog()
