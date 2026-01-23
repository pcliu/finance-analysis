import sys
import os
import pandas as pd
import numpy as np
import json

# Add skill directory to path
SKILL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../.agent/skills/quantitative-trading'))
sys.path.append(SKILL_DIR)

from scripts import fetch_stock_data, calculate_rsi, calculate_bollinger_bands, calculate_macd, calculate_sma
from scripts.utils import make_serializable

# Configuration
HOLDINGS = {
    "510150": {"name": "消费ETF", "qty": 10000, "cost": 0.5721},
    "510880": {"name": "红利ETF", "qty": 5500, "cost": 3.0505},
    "512660": {"name": "军工ETF", "qty": 5000, "cost": 1.5264},
    "513180": {"name": "恒指科技", "qty": 800, "cost": 0.7686},
    "513630": {"name": "香港红利", "qty": 500, "cost": 1.6180},
    "515050": {"name": "5GETF", "qty": 1000, "cost": 2.3200},
    "515070": {"name": "AI智能", "qty": 400, "cost": 1.9388},
    "588000": {"name": "科创50", "qty": 1000, "cost": 0.3019},
    "159241": {"name": "航空 TH", "qty": 5000, "cost": 1.5292},
    "159770": {"name": "机器人 AI", "qty": 200, "cost": 0.7670}
}

CSV_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'ETFs.csv')

def load_etf_list():
    df = pd.read_csv(CSV_PATH)
    # Ensure code is string and 6 digits
    df['代码'] = df['代码'].astype(str).str.zfill(6)
    return df

def analyze_etf(ticker, name):
    print(f"Analyzing {ticker} - {name}...")
    try:
        # Fetch data (last 1 year to be safe for indicators)
        df = fetch_stock_data(ticker, period='1y')
        
        if df is None or len(df) < 50:
            print(f"Skipping {ticker}: Insufficient data")
            return None

        # Calculate Indicators
        # RSI
        df_rsi = calculate_rsi(df, window=6) # Sort term RSI
        rsi_val = df_rsi['RSI'].iloc[-1]
        
        # Bollinger Bands
        df_bb = calculate_bollinger_bands(df, window=20, num_std=2)
        bb_upper = df_bb['Upper'].iloc[-1]
        bb_lower = df_bb['Lower'].iloc[-1]
        current_price = df['Close'].iloc[-1]
        
        # Calculate %B: (Price - Lower) / (Upper - Lower)
        if bb_upper != bb_lower:
            pct_b = (current_price - bb_lower) / (bb_upper - bb_lower)
        else:
            pct_b = 0.5

        # MACD
        df_macd = calculate_macd(df)
        macd_hist = df_macd['Histogram'].iloc[-1]
        macd_line = df_macd['MACD'].iloc[-1]
        
        # SMA for trend
        df_sma20 = calculate_sma(df, window=20)
        sma20 = df_sma20['SMA'].iloc[-1]

        # Volume Analysis
        vol_avg_5 = df['Volume'].rolling(window=5).mean().iloc[-1]
        curr_vol = df['Volume'].iloc[-1]
        vol_ratio = curr_vol / vol_avg_5 if vol_avg_5 > 0 else 1.0

        # KDJ (Simple implementation since not in standard export list explicitly but useful)
        # Using KD from Stochastic tool if available, or manual. SKILL says calculate_stochastic is available.
        from scripts import calculate_stochastic
        df_kdj = calculate_stochastic(df, k_window=9, d_window=3)
        k_val = df_kdj['K'].iloc[-1]
        d_val = df_kdj['D'].iloc[-1]

        return {
            "ticker": ticker,
            "name": name,
            "price": current_price,
            "change_pct": (df['Close'].pct_change().iloc[-1]) * 100,
            "rsi_6": rsi_val,
            "pct_b": pct_b,
            "macd_hist": macd_hist,
            "macd_line": macd_line,
            "k_val": k_val,
            "d_val": d_val,
            "vol_ratio": vol_ratio,
            "sma20": sma20,
            "is_held": ticker in HOLDINGS,
            "cost": HOLDINGS[ticker]['cost'] if ticker in HOLDINGS else None,
            "qty": HOLDINGS[ticker]['qty'] if ticker in HOLDINGS else None
        }

    except Exception as e:
        print(f"Error analyzing {ticker}: {e}")
        return None

def main():
    etfs = load_etf_list()
    results = []

    for _, row in etfs.iterrows():
        ticker = row['代码']
        name = row['ETF 名称']
        
        # Override name if in holdings list (sometimes CSV names are slightly different)
        if ticker in HOLDINGS:
            name = HOLDINGS[ticker]['name']
            
        data = analyze_etf(ticker, name)
        if data:
            results.append(data)

    # Save Results
    clean_results = make_serializable(results)
    output_file = os.path.join(os.path.dirname(__file__), 'portfolio_adjustment_data.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(clean_results, f, indent=4, ensure_ascii=False)
    
    print(f"Analysis complete. Saved to {output_file}")

if __name__ == "__main__":
    main()
