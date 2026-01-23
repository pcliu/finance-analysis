import sys
import os
import pandas as pd
import numpy as np

# Robust Import: Use absolute path relative to this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../.agent/skills/quantitative-trading'))
sys.path.append(SKILL_DIR)

from scripts import fetch_stock_data, calculate_rsi, calculate_sma, calculate_macd, calculate_bollinger_bands
from scripts.utils import make_serializable

def analyze_breakout(ticker, name):
    print(f"Analyzing {name} ({ticker})...")
    
    # Fetch 1 year of data for trend and breakout analysis
    try:
        data = fetch_stock_data(ticker, period='1y')
        if data.empty:
            print(f"No data found for {ticker}")
            return None
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None

    # Calculate indicators
    rsi = calculate_rsi(data)['RSI']
    sma20 = calculate_sma(data, window=20)['SMA']
    sma50 = calculate_sma(data, window=50)['SMA']
    sma200 = calculate_sma(data, window=200)['SMA']
    macd = calculate_macd(data)
    bb = calculate_bollinger_bands(data)

    current_price = data['Close'].iloc[-1]
    prev_price = data['Close'].iloc[-2]
    
    # Calculate 60-day resistance (local high)
    recent_high = data['High'].iloc[-60:-1].max()
    
    # Breakout conditions
    is_above_sma20 = current_price > sma20.iloc[-1]
    is_above_sma50 = current_price > sma50.iloc[-1]
    is_above_sma200 = current_price > sma200.iloc[-1]
    
    # Price breakout of resistance
    price_breakout = current_price > recent_high
    
    # Bollinger Band breakout (Price above Upper Band)
    bb_breakout = current_price > bb['Upper'].iloc[-1]
    
    # RSI Trend
    current_rsi = rsi.iloc[-1]
    rsi_rising = current_rsi > rsi.iloc[-2]
    
    # MACD Signal
    macd_hist = macd['Histogram'].iloc[-1]
    macd_cross_up = (macd_hist > 0 and macd['Histogram'].iloc[-2] <= 0) or (macd_hist > macd['Histogram'].iloc[-2] and macd_hist < 0)
    
    analysis = {
        "ticker": ticker,
        "name": name,
        "current_price": current_price,
        "prev_price": prev_price,
        "change_pct": (current_price - prev_price) / prev_price * 100,
        "sma20": sma20.iloc[-1],
        "sma50": sma50.iloc[-1],
        "sma200": sma200.iloc[-1],
        "rsi": current_rsi,
        "macd_hist": macd_hist,
        "upper_bb": bb['Upper'].iloc[-1],
        "lower_bb": bb['Lower'].iloc[-1],
        "recent_high_60d": recent_high,
        "is_above_sma20": bool(is_above_sma20),
        "is_above_sma50": bool(is_above_sma50),
        "is_above_sma200": bool(is_above_sma200),
        "price_breakout": bool(price_breakout),
        "bb_breakout": bool(bb_breakout),
        "rsi_rising": bool(rsi_rising),
        "macd_cross_up": bool(macd_cross_up),
        "analysis_date": data.index[-1].strftime('%Y-%m-%d')
    }
    
    return analysis

def main():
    tickers = {
        "GC=F": "Gold Futures (GC)",
        "SI=F": "Silver Futures (SI)"
    }
    
    results = {}
    for ticker, name in tickers.items():
        analysis = analyze_breakout(ticker, name)
        if analysis:
            results[ticker] = analysis
            
    # Save results
    import json
    output_path = os.path.join(SCRIPT_DIR, "gold_silver_breakout_data.json")
    with open(output_path, "w") as f:
        json.dump(make_serializable(results), f, indent=4)
    
    print(f"Analysis complete. Results saved to {output_path}")

if __name__ == "__main__":
    main()
