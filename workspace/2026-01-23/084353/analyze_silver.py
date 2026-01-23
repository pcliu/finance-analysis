import sys
import os
import pandas as pd
import numpy as np

# Add skill directory to path
SKILL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../.agent/skills/quantitative-trading'))
sys.path.append(SKILL_DIR)

from scripts import fetch_stock_data, calculate_rsi, calculate_bollinger_bands

def analyze_silver_live(price_now):
    ticker = "161226"
    print(f"Fetching data for {ticker}...")
    df = fetch_stock_data(ticker, period='3mo')
    
    if df is None:
        print("Error fetching data")
        return

    # Simulate today's candle based on user input
    last_date = df.index[-1]
    # If the last data point is not today (likely yesterday's close), append new row
    # If live data is already today, update it? 
    # Usually yfinance gives previous close until market close, or delayed.
    # We will assume we need to append or update last row.
    
    new_row = df.iloc[-1].copy()
    new_row['Close'] = price_now
    new_row['High'] = max(new_row['High'], price_now) # Conservative
    new_row['Low'] = min(new_row['Low'], price_now)
    
    # Check timestamps to see if we append
    # Simple hack: just append a "Live" row
    df_live = pd.concat([df, pd.DataFrame([new_row], index=[last_date + pd.Timedelta(days=1)])])

    # Calculate Indicators on new df
    df_rsi = calculate_rsi(df_live, window=6)
    rsi_val = df_rsi['RSI'].iloc[-1]
    
    df_bb = calculate_bollinger_bands(df_live, window=20, num_std=2)
    upper = df_bb['Upper'].iloc[-1]
    lower = df_bb['Lower'].iloc[-1]
    pct_b = (price_now - lower) / (upper - lower)
    
    print(f"--- Silver (161226) Live Analysis ---")
    print(f"Price: {price_now}")
    print(f"RSI(6): {rsi_val:.2f}")
    print(f"Bollinger Upper: {upper:.2f}")
    print(f"%B: {pct_b:.2f}")
    
    historical_max_rsi = df_rsi['RSI'].max()
    print(f"3-Month Max RSI: {historical_max_rsi:.2f}")

if __name__ == "__main__":
    analyze_silver_live(4.169)
