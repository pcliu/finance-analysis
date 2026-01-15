#!/usr/bin/env python3
import sys
import os
import pandas as pd

# Add scripts directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'quantitative-trading-skills', 'quantitative-trading', 'scripts'))

from data_fetcher import DataFetcher
from indicators import TechnicalIndicators

def analyze():
    # Holdings (Ticker, Name, Shares)
    holdings = [
        ('510880', '红利ETF', 1000),
        ('513180', '恒指科技', 2400),
        ('513630', '香港红利', 500),
        ('588000', '科创50', 8000),
        ('159830', '上海金', 400),
        # ('159980', '有色ETF', 0), # Ignore 0 holding
        # ('RXL001', '日鑫利', 0), # Ignore 0 holding and likely non-standard ticker
    ]

    # Candidates
    candidates = [
        ('161226', '国投白银LOF'),
        ('159516', '半导体设备ETF'),
        ('515070', '人工智能AIETF'),
        ('515050', '5G通信ETF'),
        ('159770', '机器人ETF'),
    ]

    all_tickers = holdings + candidates
    
    fetcher = DataFetcher(default_provider='tushare') # Use Tushare for China market
    indicators = TechnicalIndicators()
    
    print(f"{'Ticker':<10} {'Name':<15} {'Price':<8} {'RSI':<6} {'Trend':<20} {'Vol(Ann)%':<10} {'Rec 1M %':<10}")
    print("-" * 90)

    for item in all_tickers:
        ticker = item[0]
        name = item[1]
        
        # Try different suffixes if needed, but DataFetcher should handle it.
        # However, for pure numbers, DataFetcher needs Tushare mapping.
        # Let's trust DataFetcher's auto logic or specify valid codes if known.
        # Tushare codes usually need suffix. DataFetcher attempts to normalize.
        
        data = fetcher.fetch_stock_data(ticker, period='6mo', market='cn')
        
        if data is None or data.empty:
            print(f"{ticker:<10} {name:<15} N/A")
            continue
            
        # Calculate Indicators
        try:
            rsi = indicators.calculate_rsi(data, window=14).iloc[-1]
            sma20 = indicators.calculate_sma(data, window=20).iloc[-1]
            sma60 = indicators.calculate_sma(data, window=60).iloc[-1]
        except Exception:
            rsi = 50
            sma20 = 0
            sma60 = 0
            
        current_price = data['Close'].iloc[-1]
        
        # Trend
        if current_price > sma20 and sma20 > sma60:
            trend = "Bullish"
        elif current_price < sma20 and sma20 < sma60:
            trend = "Bearish"
        elif current_price > sma20:
             trend = "Recov/Up"
        else:
             trend = "Weak/Down"
             
        # Volatility
        volatility = data['Volatility'].iloc[-1] * 100 if 'Volatility' in data.columns else 0
        
        # 1 Month Return
        cur_close = data['Close'].iloc[-1]
        prev_close_20 = data['Close'].iloc[-21] if len(data) > 20 else data['Close'].iloc[0]
        ret_1m = ((cur_close / prev_close_20) - 1) * 100
        
        print(f"{ticker:<10} {name:<15} {current_price:<8.3f} {rsi:<6.1f} {trend:<20} {volatility:<10.2f} {ret_1m:<10.2f}")

if __name__ == "__main__":
    analyze()
