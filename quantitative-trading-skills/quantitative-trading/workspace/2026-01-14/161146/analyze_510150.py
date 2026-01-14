#!/usr/bin/env python3
import sys
import os
import json
import pandas as pd
from datetime import datetime

# Add project root to path
sys.path.insert(0, '/Users/liupengcheng/Documents/Code/finance-analysis/quantitative-trading-skills/quantitative-trading')

from scripts import DataFetcher, TechnicalIndicators

def main():
    ticker = '510150.SH'
    output_dir = 'workspace/2026-01-14/161146'
    os.makedirs(output_dir, exist_ok=True)

    fetcher = DataFetcher()
    tech = TechnicalIndicators()

    print(f"Fetching data for {ticker}...")
    data = fetcher.fetch_stock_data(ticker, period='1y')

    if data is None or data.empty:
        print(f"Failed to fetch data for {ticker}")
        return

    print("Calculating all indicators...")
    indicators_df = tech.calculate_all_indicators(data)
    
    # Combine with original data
    final_df = data.join(indicators_df)
    
    # Get the latest row
    latest = final_df.iloc[-1]
    
    # Prepare indicator summary for the report
    summary = {
        "Ticker": ticker,
        "Date": latest.name.strftime('%Y-%m-%d'),
        "Price": round(latest['Close'], 3),
        "Indicators": {
            "Trend": {
                "SMA_20": round(latest['SMA_20'], 3),
                "SMA_50": round(latest['SMA_50'], 3),
                "SMA_200": round(latest['SMA_200'], 3),
                "EMA_12": round(latest['EMA_12'], 3),
                "EMA_26": round(latest['EMA_26'], 3),
                "Bollinger": {
                    "Upper": round(latest['BB_Upper'], 3),
                    "Middle": round(latest['BB_Middle'], 3),
                    "Lower": round(latest['BB_Lower'], 3)
                }
            },
            "Momentum": {
                "RSI": round(latest['RSI'], 2),
                "MACD": round(latest['MACD_MACD'], 4),
                "MACD_Signal": round(latest['MACD_Signal'], 4),
                "MACD_Hist": round(latest['MACD_Histogram'], 4),
                "Stochastic_K": round(latest['Stoch_K'], 2),
                "Stochastic_D": round(latest['Stoch_D'], 2),
                "CCI": round(latest['CCI'], 2),
                "Williams_R": round(latest['Williams_R'], 2)
            },
            "Volatility": {
                "ATR": round(latest['ATR'], 4)
            },
            "Volume": {
                "Volume": int(latest['Volume']),
                "Volume_SMA": int(latest['Volume_SMA']),
                "OBV": int(latest['OBV'])
            }
        }
    }

    # Save summary to JSON
    with open(f"{output_dir}/analysis_result.json", 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    # Save full data to CSV (optional, but good practice)
    final_df.to_csv(f"{output_dir}/technical_analysis.csv")

    print(f"Analysis completed. Results saved to {output_dir}/")

if __name__ == "__main__":
    main()
