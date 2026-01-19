import sys
import os
import json
import pandas as pd
import numpy as np

# Fix path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
skill_path = os.path.join(project_root, '.agent', 'skills', 'quantitative-trading')
sys.path.append(skill_path)

try:
    from scripts.data_fetcher import DataFetcher
    from scripts.indicators import TechnicalIndicators
except ImportError as e:
    print(f"Error importing scripts: {e}")
    sys.exit(1)

# Initialize Fetcher and Calculator
fetcher = DataFetcher()
ti = TechnicalIndicators()

# Holdings
holdings = {
    '510150.SH': '消费ETF',
    '510880.SH': '红利ETF',
    '512660.SH': '军工ETF',
    '513180.SH': '恒指科技',
    '513630.SH': '香港红利',
    '515050.SH': '5GETF',
    '515070.SH': 'AI智能',
    '588000.SH': '科创50',
    '159241.SZ': '航空TH',
    '159770.SZ': '机器人AI',
    '159830.SZ': '上海金',
    '161226.SZ': '白银基金'
}

# Candidates
candidates = {
    '159352.SZ': 'A500ETF',
    '159326.SZ': '电网设备',
    '159516.SZ': '半导体设备',
    '518880.SH': '黄金ETF',
    '512400.SH': '有色金属'
}

all_tickers = {**holdings, **candidates}
tickers = list(all_tickers.keys())

# Fetch Data
print("Fetching data...")
try:
    # Use fetcher instance
    data_map = fetcher.fetch_multiple_stocks(tickers, period='3mo')
except Exception as e:
    print(f"Data fetch error: {e}")
    sys.exit(1)

results = []

for ticker, name in all_tickers.items():
    if ticker not in data_map or data_map[ticker].empty:
        continue
    
    df = data_map[ticker]
    
    # Calc indicators using class instance
    rsi = ti.calculate_rsi(df, window=14)
    rsi6 = ti.calculate_rsi(df, window=6) # Sensitive
    sma20 = ti.calculate_sma(df, window=20)
    sma60 = ti.calculate_sma(df, window=60)
    macd = ti.calculate_macd(df)
    bb = ti.calculate_bollinger_bands(df)
    
    curr = df['Close'].iloc[-1]
    prev = df['Close'].iloc[-2]
    chg = (curr - prev) / prev * 100
    
    r = {
        'code': ticker,
        'name': name,
        'price': float(curr),
        'change': float(chg),
        'rsi_14': float(rsi['RSI'].iloc[-1]),
        'rsi_6': float(rsi6['RSI'].iloc[-1]),
        'sma_20': float(sma20['SMA'].iloc[-1]),
        'sma_60': float(sma60['SMA'].iloc[-1]),
        'macd': float(macd['MACD'].iloc[-1]),
        'macd_sig': float(macd['Signal'].iloc[-1]),
        'macd_hist': float(macd['Histogram'].iloc[-1]),
        'bb_up': float(bb['Upper'].iloc[-1]),
        'bb_mid': float(bb['Middle'].iloc[-1]),
        'bb_low': float(bb['Lower'].iloc[-1]),
        'is_holding': ticker in holdings
    }
    
    # Simple strategy check
    # Buy signal: RSI < 30 (Oversold) or Golden Cross (MACD or SMA)
    # Sell signal: RSI > 70 (Overbought) or Death Cross
    
    signal = "HOLD"
    reason = ""
    
    # Check RSI
    if r['rsi_6'] < 20:
        signal = "STRONG BUY"
        reason += "RSI6 Extremely Oversold (<20); "
    elif r['rsi_6'] < 30:
        signal = "BUY"
        reason += "RSI6 Oversold (<30); "
    elif r['rsi_14'] > 80:
        signal = "STRONG SELL"
        reason += "RSI14 Extremely Overbought (>80); "
    elif r['rsi_14'] > 70:
        signal = "SELL"
        reason += "RSI14 Overbought (>70); "
        
    # Check Trends
    if curr > r['sma_20'] and curr > r['sma_60']:
        reason += "Above SMA20 & SMA60 (Bullish); "
    elif curr < r['sma_20'] and curr < r['sma_60']:
        reason += "Below SMA20 & SMA60 (Bearish); "
        
    r['signal'] = signal
    r['reason'] = reason
    
    results.append(r)

results.sort(key=lambda x: x['rsi_6'])
print(json.dumps(results, indent=2, ensure_ascii=False))
