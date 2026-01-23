import sys
import os
import pandas as pd
import numpy as np

# Robust Import
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../.agent/skills/quantitative-trading'))
sys.path.append(SKILL_DIR)

from scripts import fetch_stock_data, calculate_rsi, calculate_sma
from scripts.utils import make_serializable

def detect_divergence(price, rsi, window=60):
    """
    Simple divergence detection.
    Check if current price is higher than max price in past window (excl today),
    but current RSI is lower than RSI at that past price peak.
    """
    if len(price) < window + 1:
        return None
        
    current_price = price.iloc[-1]
    current_rsi = rsi.iloc[-1]
    
    # Look back window days (excluding today)
    past_price = price.iloc[-(window+1):-1]
    past_rsi = rsi.iloc[-(window+1):-1]
    
    # Find the index of the previous highest high
    # We use High price for peak detection usually, checking Close here for consistency with RSI usually calc on Close
    # But usually divergence is Price High vs RSI. Let's stick to Close for simplicity or High.
    # Standard: Compare Price Highs vs RSI Highs? Or Close vs RSI. 
    # Let's use Close to match RSI calculation base.
    
    max_price_idx = past_price.idxmax()
    max_price = past_price.max()
    rsi_at_max_price = past_rsi.loc[max_price_idx]
    
    divergence = False
    if current_price > max_price and current_rsi < rsi_at_max_price:
        divergence = True
        
    return {
        "divergence_detected": divergence,
        "current_price": current_price,
        "current_rsi": current_rsi,
        "past_peak_price": max_price,
        "past_peak_rsi": rsi_at_max_price,
        "peak_date": max_price_idx.strftime('%Y-%m-%d')
    }

def verify_breakout(ticker, name):
    print(f"Verifying Breakout for {name} ({ticker})...")
    
    try:
        data = fetch_stock_data(ticker, period='6mo')
        if data.empty:
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None
        
    # 1. Volume Analysis
    # Yahoo Finance Future data sometimes has 0 volume or delayed volume. Check if valid.
    volume = data['Volume']
    vol_sma20 = volume.rolling(window=20).mean()
    
    current_vol = volume.iloc[-1]
    avg_vol = vol_sma20.iloc[-1]
    
    vol_ratio = 0
    if avg_vol > 0:
        vol_ratio = current_vol / avg_vol
        
    # 2. RSI Divergence
    rsi = calculate_rsi(data)['RSI']
    div_check = detect_divergence(data['Close'], rsi)
    
    # 3. Candle Strength (Close position relative to today's range)
    high = data['High'].iloc[-1]
    low = data['Low'].iloc[-1]
    close = data['Close'].iloc[-1]
    open_p = data['Open'].iloc[-1]
    
    range_len = high - low
    if range_len == 0:
        range_len = 0.0001 # prevent div by zero
        
    close_position = (close - low) / range_len # 1.0 means closed at high
    body_size = abs(close - open_p)
    body_pct = body_size / range_len # % of candle that is body
    
    # 4. Bollinger Band Width (Expansion = Volatility breakout)
    # Manual calc for simplicity or use skill
    sma20 = data['Close'].rolling(window=20).mean()
    std20 = data['Close'].rolling(window=20).std()
    upper = sma20 + 2 * std20
    lower = sma20 - 2 * std20
    bandwidth = (upper - lower) / sma20
    prev_bandwidth = bandwidth.iloc[-2]
    bandwidth_expanding = bandwidth.iloc[-1] > prev_bandwidth

    analysis = {
        "ticker": ticker,
        "name": name,
        "date": data.index[-1].strftime('%Y-%m-%d'),
        "volume_analysis": {
            "current_volume": current_vol,
            "avg_volume_20d": avg_vol,
            "volume_ratio": vol_ratio,
            "is_high_volume": vol_ratio > 1.2, # Threshold for strong volume
            "volume_trend_comment": "Significant Volume" if vol_ratio > 1.2 else "Weak/Normal Volume"
        },
        "divergence_analysis": div_check,
        "candle_analysis": {
            "close_position": close_position, # > 0.8 is strong close
            "body_pct": body_pct, # > 0.5 indicates conviction
            "is_strong_close": close_position > 0.8
        },
        "volatility_analysis": {
            "bandwidth_expanding": bool(bandwidth_expanding),
            "comment": "Volatility Expanding" if bandwidth_expanding else "Volatility Contracting"
        }
    }
    
    return analysis

def main():
    tickers = {
        "GC=F": "Gold Futures",
        "SI=F": "Silver Futures"
    }
    
    results = {}
    for ticker, name in tickers.items():
        res = verify_breakout(ticker, name)
        if res:
            results[ticker] = res
            
    output_path = os.path.join(SCRIPT_DIR, "breakout_verification_data.json")
    with open(output_path, "w") as f:
        import json
        json.dump(make_serializable(results), f, indent=4)
    print(f"Verification complete. Saved to {output_path}")

if __name__ == "__main__":
    main()
