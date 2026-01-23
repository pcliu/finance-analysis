import sys
import os
import pandas as pd
import numpy as np

# Robust Import
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../.agent/skills/quantitative-trading'))
sys.path.append(SKILL_DIR)

from scripts import fetch_stock_data, calculate_rsi

def fetch_macro_data():
    """Fetch DXY and TNX for correlation analysis"""
    macros = {
        "DX-Y.NYB": "US Dollar Index",
        "^TNX": "10-Year Treasury Yield"
    }
    data = {}
    for ticker, name in macros.items():
        try:
            df = fetch_stock_data(ticker, period='6mo')
            if not df.empty:
                data[name] = df
        except:
            pass
    return data

def analyze_volume_climax(ticker, name):
    print(f"Analyzing Volume/Price Context for {name} ({ticker})...")
    
    # 1. Fetch 5 years to determine long-term position
    try:
        data = fetch_stock_data(ticker, period='5y')
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None
        
    if data.empty:
        return None
        
    # Calculate indicators
    rsi = calculate_rsi(data)['RSI']
    close = data['Close']
    volume = data['Volume']
    
    # Avoid div by zero in volume
    avg_vol = volume.rolling(window=20).mean().replace(0, 1) 
    vol_ratio = volume / avg_vol
    
    # 2. Identify similar historical days (High RSI + High Volume + Big Move)
    # Current condition
    curr_rsi = rsi.iloc[-1]
    curr_vol_ratio = vol_ratio.iloc[-1]
    curr_pct_change = data['Close'].pct_change().iloc[-1] * 100
    
    print(f"Current Status: RSI={curr_rsi:.1f}, VolRatio={curr_vol_ratio:.1f}x, Change={curr_pct_change:.1f}%")
    
    # Search for similar events
    # We look for days where data matches roughly current conditions
    # Logic: Previous days where RSI > 70 AND VolRatio > 2.0 (Lower threshold to find samples)
    mask = (rsi > 70) & (vol_ratio > 2.0) & (data.index < data.index[-1])
    similar_days = data[mask]
    
    history_analysis = []
    
    for date, row in similar_days.iterrows():
        # Get forward returns (1d, 5d, 20d)
        idx = data.index.get_loc(date)
        if idx + 20 >= len(data):
            continue
            
        price_t = close.iloc[idx]
        price_t1 = close.iloc[idx+1]
        price_t5 = close.iloc[idx+5]
        price_t20 = close.iloc[idx+20]
        
        ret_1d = (price_t1 - price_t) / price_t * 100
        ret_5d = (price_t5 - price_t) / price_t * 100
        ret_20d = (price_t20 - price_t) / price_t * 100
        
        history_analysis.append({
            "date": date.strftime('%Y-%m-%d'),
            "rsi": rsi.loc[date],
            "vol_ratio": vol_ratio.loc[date],
            "ret_1d": ret_1d,
            "ret_5d": ret_5d,
            "ret_20d": ret_20d
        })
        
    # 3. Analyze "Churn" (Distribution Sign)
    # Churn = High Volume but Price Stalling (Small body relative to range)
    # Determine the "Shadow" ratio of the recent candle
    high = data['High'].iloc[-1]
    low = data['Low'].iloc[-1]
    open_p = data['Open'].iloc[-1]
    close_p = data['Close'].iloc[-1]
    
    range_len = high - low
    upper_wick = high - max(open_p, close_p)
    wick_ratio = upper_wick / range_len if range_len > 0 else 0
    
    # 4. Long Term Context
    current_price = close.iloc[-1]
    max_price_5y = close.max()
    is_ath = current_price >= max_price_5y * 0.98
    
    # 5. Volatility expansion?
    # Use ATR or simple Range
    atr = (data['High'] - data['Low']).rolling(14).mean()
    curr_range = high - low
    range_expansion = curr_range / atr.iloc[-2] # vs yesterday's ATR
    
    return {
        "ticker": ticker,
        "is_ath": bool(is_ath),
        "wick_ratio": wick_ratio, # High wick ratio > 0.4 implies selling
        "range_expansion": range_expansion, # High expansion > 2.0 implies climax
        "history_samples": len(history_analysis),
        "history_avg_return_5d": np.mean([x['ret_5d'] for x in history_analysis]) if history_analysis else 0,
        "history_win_rate_5d": np.mean([1 if x['ret_5d'] > 0 else 0 for x in history_analysis]) if history_analysis else 0,
        "similar_events": sorted(history_analysis, key=lambda x: x['vol_ratio'], reverse=True)[:5] # Top 5 similar volume spikes
    }

def main():
    stock_tickers = {
        "GC=F": "Gold Futures",
        "SI=F": "Silver Futures"
    }
    
    # 1. Asset Analysis
    analysis_results = {}
    for t, n in stock_tickers.items():
        res = analyze_volume_climax(t, n)
        if res:
            analysis_results[t] = res
            
    # 2. Macro Check
    macros = fetch_macro_data()
    macro_trends = {}
    for name, df in macros.items():
        # Check 1 day and 5 day change
        curr = df['Close'].iloc[-1]
        prev = df['Close'].iloc[-2]
        prev5 = df['Close'].iloc[-6]
        macro_trends[name] = {
            "current": curr,
            "change_1d_pct": (curr - prev)/prev * 100,
            "change_5d_pct": (curr - prev5)/prev5 * 100
        }

    # Save
    import json
    from scripts.utils import make_serializable
    
    final_output = {
        "assets": analysis_results,
        "macro": macro_trends
    }
    
    output_path = os.path.join(SCRIPT_DIR, "distribution_check_data.json")
    with open(output_path, "w") as f:
        json.dump(make_serializable(final_output), f, indent=4)
        
    print(f"Done. Saved to {output_path}")

if __name__ == "__main__":
    main()
