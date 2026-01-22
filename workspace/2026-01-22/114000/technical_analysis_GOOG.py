import sys
import os
import json
import pandas as pd
import numpy as np

# Setup path to import from skills
# Current path: workspace/2026-01-22/114000/technical_analysis_GOOG.py
# Skill path: .agent/skills/quantitative-trading/
SKILL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../.agent/skills/quantitative-trading'))
if SKILL_DIR not in sys.path:
    sys.path.append(SKILL_DIR)

from scripts.data_fetcher import DataFetcher
from scripts.indicators import TechnicalIndicators
from scripts.utils import make_serializable

def main():
    ticker = 'GOOG'
    print(f"Starting analysis for {ticker}...")

    # 1. Fetch Data
    fetcher = DataFetcher()
    # Fetch enough data for slow indicators (e.g. SMA 200)
    data = fetcher.fetch_stock_data(ticker, period='2y')
    
    if data is None or data.empty:
        print(f"Error: No data found for {ticker}.")
        sys.exit(1)

    print(f"Fetched {len(data)} rows of data.")

    # 2. Calculate Indicators
    ti = TechnicalIndicators()
    print("Calculating indicators...")
    indicators = ti.calculate_all_indicators(data)
    
    # Merge data
    full_df = data.join(indicators)
    
    # 3. Calculate Volatility (Annualized)
    # Annualized Volatility based on last 1 year of daily returns
    full_df['Returns'] = full_df['Close'].pct_change()
    # Calculate volatility over the last 252 trading days (approx 1 year) window, taking the last value
    # Or just standard deviation of the last year's returns * sqrt(252)
    last_year_data = full_df.tail(252)
    volatility = last_year_data['Returns'].std() * np.sqrt(252)

    # 4. Extract latest values for the report
    latest = full_df.iloc[-1]
    
    results = {
        "ticker": ticker,
        "date": str(latest.name.date()),
        "price": latest['Close'],
        "rsi": latest['RSI'],
        "cci": latest['CCI'],
        "macd": latest['MACD_MACD'],
        "macd_signal": latest['MACD_Signal'],
        "macd_hist": latest['MACD_Histogram'],
        "sma_20": latest['SMA_20'],
        "sma_50": latest['SMA_50'],
        "sma_200": latest['SMA_200'],
        "bb_upper": latest['BB_Upper'],
        "bb_middle": latest['BB_Middle'],
        "bb_lower": latest['BB_Lower'],
        "bb_percent_b": latest['BB_Percent_B'],
        "atr": latest['ATR'],
        "volatility": volatility,
        "obv": latest['OBV'],
        # Add a few previous days for context (e.g. is RSI rising or falling?)
        "prev_rsi": full_df.iloc[-2]['RSI'],
        "prev_price": full_df.iloc[-2]['Close']
    }
    
    # Save to JSON
    output_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(output_dir, f'technical_analysis_{ticker}_data.json')
    
    try:
        clean_results = make_serializable(results)
        with open(output_file, 'w') as f:
            json.dump(clean_results, f, indent=4)
        print(f"Analysis complete. Data saved to {output_file}")
        print(json.dumps(clean_results, indent=2))
    except Exception as e:
        print(f"Error saving data: {e}")
        # Fallback if make_serializable fails or other issues
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
