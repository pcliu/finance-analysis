
import sys
import os
import json
import pandas as pd
from datetime import datetime

# Add skill path
sys.path.append('/Users/liupengcheng/Documents/Code/finance-analysis/.agent/skills/quantitative-trading')

from scripts import fetch_stock_data, calculate_rsi, calculate_sma, calculate_macd, calculate_bollinger_bands, moving_average_crossover, TechnicalIndicators

# Initialize indicators
indicators = TechnicalIndicators()

def analyze_ticker(ticker):
    print(f"Analyzing {ticker}...")
    try:
        # Fetch data
        data = fetch_stock_data(ticker, period='1y')
        if data.empty:
            print(f"Error: No data found for {ticker}")
            return None

        # Calculate indicators
        rsi = calculate_rsi(data, window=14)
        sma_20 = calculate_sma(data, window=20)
        sma_50 = calculate_sma(data, window=50)
        sma_200 = calculate_sma(data, window=200)
        macd = calculate_macd(data)
        bb = calculate_bollinger_bands(data)
        atr = indicators.calculate_atr(data)
        
        # Strategy Signals
        ma_cross = moving_average_crossover(data, fast_window=20, slow_window=50)

        # Get latest values
        last_price = data['Close'].iloc[-1]
        last_date = data.index[-1].strftime('%Y-%m-%d')
        
        last_rsi = rsi['RSI'].iloc[-1]
        last_sma_20 = sma_20['SMA'].iloc[-1]
        last_sma_50 = sma_50['SMA'].iloc[-1]
        last_sma_200 = sma_200['SMA'].iloc[-1]
        
        last_macd = macd['MACD'].iloc[-1]
        last_signal = macd['Signal'].iloc[-1]
        last_hist = macd['Histogram'].iloc[-1]
        
        last_upper = bb['Upper'].iloc[-1]
        last_middle = bb['Middle'].iloc[-1]
        last_lower = bb['Lower'].iloc[-1]
        
        last_atr = atr['ATR'].iloc[-1]

        # Determine Trend
        trend = "Neutral"
        if last_price > last_sma_20 > last_sma_50:
            trend = "Bullish"
        elif last_price < last_sma_20 < last_sma_50:
            trend = "Bearish"

        # Signal Interpretation
        rsi_signal = "Neutral"
        if last_rsi > 70:
            rsi_signal = "Overbought"
        elif last_rsi < 30:
            rsi_signal = "Oversold"
            
        macd_signal = "Neutral"
        if last_macd > last_signal:
            macd_signal = "Bullish (MACD > Signal)"
        else:
            macd_signal = "Bearish (MACD < Signal)"

        return {
            "ticker": str(ticker),
            "date": str(last_date),
            "px_close": float(last_price),
            "rsi": float(last_rsi),
            "rsi_signal": str(rsi_signal),
            "sma_20": float(last_sma_20),
            "sma_50": float(last_sma_50),
            "sma_200": float(last_sma_200),
            "macd": float(last_macd),
            "macd_signal_line": float(last_signal),
            "macd_hist": float(last_hist),
            "macd_interpretation": str(macd_signal),
            "bb_upper": float(last_upper),
            "bb_middle": float(last_middle),
            "bb_lower": float(last_lower),
            "atr": float(last_atr),
            "trend": str(trend),
            "ma_cross_signal": int(ma_cross['Signal'].iloc[-1]) if not ma_cross.empty else 0
        }

    except Exception as e:
        print(f"Error analyzing {ticker}: {e}")
        return None

def main():
    tickers = ['IAU', 'SLV']
    results = {}
    
    for ticker in tickers:
        result = analyze_ticker(ticker)
        if result:
            results[ticker] = result
            
    # Output JSON
    output_file = os.path.join(os.path.dirname(__file__), 'technical_analysis_IAU_SLV_data.json')
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=4)
        
    print(f"\nAnalysis results saved to {output_file}")
    
    # Print summary for Agent
    print("\n=== SUMMARY FOR AGENT ===")
    for ticker, res in results.items():
        print(f"\n--- {ticker} ---")
        print(f"Date: {res['date']}")
        print(f"Price: {res['px_close']:.2f}")
        print(f"Trend: {res['trend']}")
        print(f"RSI: {res['rsi']:.2f} ({res['rsi_signal']})")
        print(f"MACD: {res['macd']:.4f}, Signal: {res['macd_signal_line']:.4f}, Hist: {res['macd_hist']:.4f} ({res['macd_interpretation']})")
        print(f"BB: Upper={res['bb_upper']:.2f}, Lower={res['bb_lower']:.2f}")
        print(f"SMA: 20={res['sma_20']:.2f}, 50={res['sma_50']:.2f}, 200={res['sma_200']:.2f}")
        print(f"ATR: {res['atr']:.4f}")

if __name__ == "__main__":
    main()
