import os
import sys
import pandas as pd
import numpy as np
import json
from datetime import datetime

# Adjust path to include the skill scripts
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_PATH = '/Users/liupengcheng/Documents/Code/finance-analysis/.agent/skills/quantitative-trading'
if SKILL_PATH not in sys.path:
    sys.path.append(SKILL_PATH)

from scripts import DataFetcher, calculate_rsi, calculate_sma, calculate_macd, calculate_bollinger_bands

def main():
    fetcher = DataFetcher()
    
    # 1. Define Candidates from ETFs.csv
    etf_list_path = '/Users/liupengcheng/Documents/Code/finance-analysis/workspace/ETFs.csv'
    etf_df = pd.read_csv(etf_list_path)
    # The CSV has columns: "ETF 名称", "代码"
    ticker_to_name = dict(zip(etf_df['代码'].astype(str), etf_df['ETF 名称']))
    all_tickers = etf_df['代码'].astype(str).tolist()
    
    # 2. Define Current Portfolio (from images/previous script)
    portfolio = {
        '510150': {'quantity': 5000, 'cost': 0.5751},
        '510880': {'quantity': 1000, 'cost': 3.2055},
        '512660': {'quantity': 3000, 'cost': 1.5312},
        '513180': {'quantity': 800, 'cost': 0.7686},
        '513630': {'quantity': 500, 'cost': 1.6180},
        '515050': {'quantity': 1000, 'cost': 2.3200},
        '515070': {'quantity': 400, 'cost': 1.9388},
        '588000': {'quantity': 2000, 'cost': 0.9502},
        '159241': {'quantity': 3000, 'cost': 1.5392},
        '159770': {'quantity': 700, 'cost': 1.0407},
        '159830': {'quantity': 400, 'cost': 9.7220},
        '161226': {'quantity': 300, 'cost': 2.1530},
    }
    
    holding_tickers = list(portfolio.keys())
    non_holding_tickers = [t for t in all_tickers if t not in holding_tickers]
    
    print("Fetching data and calculating indicators for all ETFs...")
    analysis_results = []
    
    for ticker in all_tickers:
        name = ticker_to_name.get(ticker, "Unknown")
        try:
            data = fetcher.fetch_stock_data(ticker, period='6mo', market='cn')
            if data is None or data.empty:
                print(f"Failed to fetch data for {ticker}")
                continue
            
            # Calculate Indicators
            rsi_df = calculate_rsi(data)
            rsi = rsi_df['RSI'].iloc[-1]
            
            macd_df = calculate_macd(data)
            macd_hist = macd_df['Histogram'].iloc[-1]
            macd_signal = macd_df['MACD'].iloc[-1]
            
            sma20_df = calculate_sma(data, window=20)
            sma20 = sma20_df['SMA'].iloc[-1]
            
            bb_df = calculate_bollinger_bands(data)
            bb_upper = bb_df['Upper'].iloc[-1]
            bb_lower = bb_df['Lower'].iloc[-1]
            
            current_price = data['Close'].iloc[-1]
            at_cost = portfolio.get(ticker, {}).get('cost', 0)
            profit_pct = ((current_price / at_cost - 1) * 100) if at_cost > 0 else 0
            
            # Record results
            item = {
                'ticker': ticker,
                'name': name,
                'holding': ticker in holding_tickers,
                'price': float(current_price),
                'cost': float(at_cost),
                'profit_pct': float(profit_pct),
                'rsi': float(rsi),
                'macd_hist': float(macd_hist),
                'sma20': float(sma20),
                'bb_upper': float(bb_upper),
                'bb_lower': float(bb_lower),
                'trend': 'Up' if current_price > sma20 else 'Down'
            }
            analysis_results.append(item)
        except Exception as e:
            print(f"Error analyzing {ticker}: {e}")

    # 3. Generate Recommendations
    recommendations = {
        'holdings': [],
        'non_holdings': []
    }
    
    for res in analysis_results:
        ticker = res['ticker']
        rsi = res['rsi']
        price = res['price']
        sma20 = res['sma20']
        macd_hist = res['macd_hist']
        
        advice = ""
        action = "Hold"
        
        # Logic for holdings
        if res['holding']:
            if rsi > 75:
                action = "Reduce"
                advice = "RSI severely overbought (>75). Recommend reducing position to lock in profit."
            elif rsi > 70:
                action = "Watch/Reduce"
                advice = "RSI overbought (>70). Monitor for trend reversal."
            elif rsi < 30:
                action = "Buy/Hold"
                advice = "RSI oversold (<30). Fundamental remains strong, can hold or add."
            elif price < sma20 * 0.95:
                action = "Hold/Add"
                advice = "Price significantly below SMA20. Potential rebound play."
            else:
                action = "Hold"
                advice = "Indicators stable. Maintain current position."
            
            res['action'] = action
            res['advice'] = advice
            recommendations['holdings'].append(res)
            
        else:
            # Logic for non-holdings
            feasibility = "Low"
            if rsi < 40 and macd_hist > 0:
                feasibility = "High"
                advice = "RSI is low (<40) and MACD histogram turning positive. Good entry window."
            elif rsi < 45:
                feasibility = "Medium"
                advice = "RSI indicates reasonable valuation. Consider entry if trend improves."
            else:
                feasibility = "Low"
                advice = "RSI high or momentum weak. Not recommended for immediate entry."
            
            res['feasibility'] = feasibility
            res['advice'] = advice
            recommendations['non_holdings'].append(res)

    # 4. Filter and Save Output
    output_path = os.path.join(SCRIPT_DIR, 'portfolio_adjustment_data.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(recommendations, f, ensure_ascii=False, indent=4)
    
    print(f"Analysis complete. Data saved to {output_path}")

if __name__ == "__main__":
    main()
