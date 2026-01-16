import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime

# Adjust path to include the skill scripts
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_PATH = '/Users/liupengcheng/Documents/Code/finance-analysis/.agent/skills/quantitative-trading'
if SKILL_PATH not in sys.path:
    sys.path.append(SKILL_PATH)

from scripts import DataFetcher, calculate_rsi, calculate_sma, calculate_macd

def main():
    fetcher = DataFetcher()
    
    # 1. Define Candidates from ETFs.csv
    etf_list_path = '/Users/liupengcheng/Documents/Code/finance-analysis/workspace/ETFs.csv'
    etf_df = pd.read_csv(etf_list_path)
    all_tickers = etf_df['代码'].astype(str).tolist()
    
    # 2. Define Current Portfolio (from images)
    portfolio = {
        '510150': {'name': '消费 ETF', 'quantity': 5000, 'cost': 0.5751},
        '510880': {'name': '红利 ETF', 'quantity': 1000, 'cost': 3.2055},
        '512660': {'name': '军工 ETF', 'quantity': 3000, 'cost': 1.5312},
        '513180': {'name': '恒指科技', 'quantity': 800, 'cost': 0.7686},
        '513630': {'name': '香港红利', 'quantity': 500, 'cost': 1.6180},
        '515050': {'name': '5GETF', 'quantity': 1000, 'cost': 2.3200},
        '515070': {'name': 'AI智能', 'quantity': 400, 'cost': 1.9388},
        '588000': {'name': '科创 50', 'quantity': 2000, 'cost': 0.9502},
        '159241': {'name': '航空 TH', 'quantity': 3000, 'cost': 1.5392},
        '159770': {'name': '机器人 AI', 'quantity': 700, 'cost': 1.0407},
        '159830': {'name': '上海金', 'quantity': 400, 'cost': 9.7220},
        '161226': {'name': '白银基金', 'quantity': 300, 'cost': 2.1530},
    }
    
    # 3. Fetch Data and Calculate Indicators
    print("Fetching data and calculating indicators...")
    results = {}
    for ticker in all_tickers:
        data = fetcher.fetch_stock_data(ticker, period='6mo', market='cn')
        if data is not None and not data.empty:
            rsi = calculate_rsi(data)['RSI'].iloc[-1]
            macd = calculate_macd(data)
            sma20 = calculate_sma(data, window=20)['SMA'].iloc[-1]
            current_price = data['Close'].iloc[-1]
            prev_price = data['Close'].iloc[-2]
            change = (current_price / prev_price - 1) * 100
            
            # Historical prices for review (Jan 7, 9, 12, 13, 14, 15)
            # Find closest trading days
            dates = {
                '2026-01-07': '2026-01-07',
                '2026-01-09': '2026-01-09',
                '2026-01-12': '2026-01-12',
                '2026-01-13': '2026-01-13',
                '2026-01-14': '2026-01-14',
                '2026-01-15': '2026-01-15'
            }
            hist_prices = {}
            for label, d_str in dates.items():
                try:
                    d_ts = pd.to_datetime(d_str)
                    if d_ts in data.index:
                        hist_prices[label] = data.loc[d_ts, 'Close']
                    else:
                        # Find nearest before
                        idx = data.index.get_indexer([d_ts], method='ffill')[0]
                        if idx != -1:
                            hist_prices[label] = data.iloc[idx]['Close']
                except:
                    pass

            results[ticker] = {
                'price': current_price,
                'change': change,
                'rsi': rsi,
                'sma20': sma20,
                'macd_hist': macd['Histogram'].iloc[-1],
                'hist_prices': hist_prices
            }

    # 4. Save analysis results
    import json
    with open(os.path.join(SCRIPT_DIR, 'backtest_review_data.json'), 'w') as f:
        json.dump(results, f, indent=4)
    
    print(f"Analysis complete. Data saved to {SCRIPT_DIR}/backtest_review_data.json")

if __name__ == "__main__":
    main()
