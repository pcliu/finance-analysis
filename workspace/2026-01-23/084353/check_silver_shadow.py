import sys
import os
import pandas as pd

SKILL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../.agent/skills/quantitative-trading'))
sys.path.append(SKILL_DIR)

from scripts import fetch_stock_data

def check_silver_intraday():
    ticker = "161226"
    print(f"Fetching latest data for {ticker}...")
    df = fetch_stock_data(ticker, period='5d')
    if df is not None:
        print(df.tail(1))
        
        last = df.iloc[-1]
        op = last['Open']
        hi = last['High']
        lo = last['Low']
        cl = last['Close']
        vol = last['Volume']
        
        # Upper shadow calc
        body_top = max(op, cl)
        upper_shadow = hi - body_top
        shadow_ratio = upper_shadow / (hi - lo) if (hi - lo) > 0 else 0
        
        print(f"\nAnalysis:")
        print(f"High: {hi}, Close: {cl}")
        print(f"Upper Shadow: {upper_shadow:.4f}")
        print(f"Shadow/Range Ratio: {shadow_ratio:.2%}")
        print(f"Volume: {vol}")

if __name__ == "__main__":
    check_silver_intraday()
