# Workflow Guide

Advanced usage patterns for the quantitative-trading skill.

## Analysis Workflow Pattern

### Step-by-Step

1. **Create a Python script file** (e.g., `analysis.py`)
2. **Add path setup** at the top of your script
3. **Import from scripts** module
4. **Write control flow logic** (loops, conditionals, error handling)
5. **Execute** with the finance-analysis interpreter

### Example Script

```python
# File: analyze_stock.py
import sys
sys.path.append('.claude/skills/quantitative-trading')

from scripts import fetch_stock_data
from scripts.indicators import TechnicalIndicators

def analyze(ticker, period='1y'):
    # Fetch data
    data = fetch_stock_data(ticker, period=period)
    if data is None or data.empty:
        print(f"Error: No data for {ticker}")
        return None
    
    # Calculate indicators
    ti = TechnicalIndicators()
    rsi = ti.calculate_rsi(data)
    sma_20 = ti.calculate_sma(data, window=20)
    sma_50 = ti.calculate_sma(data, window=50)
    
    # Return summary (context efficient)
    return {
        'ticker': ticker,
        'price': float(data['Close'].iloc[-1]),
        'rsi': float(rsi.iloc[-1]),
        'trend': 'Bullish' if sma_20.iloc[-1] > sma_50.iloc[-1] else 'Bearish'
    }

if __name__ == "__main__":
    result = analyze('AAPL')
    print(result)
```

---

## Context Efficiency Tips

### Import Only What You Need

```python
# ✅ Good
from scripts import fetch_stock_data

# ❌ Avoid
from scripts import *
```

### Filter Data Early

```python
# ✅ Good - filter and summarize
data = fetch_stock_data('AAPL', period='2y')
recent = data.tail(60)  # Only last 60 days
summary = {
    'price': recent['Close'].iloc[-1],
    'return': (recent['Close'].iloc[-1] / recent['Close'].iloc[0] - 1) * 100
}
print(summary)

# ❌ Avoid - returning full datasets
print(data)  # Too much data for context window
```

### Save Large Results to Workspace

```python
import json

result = {'ticker': 'AAPL', 'data': large_analysis}

# Save to workspace
with open('workspace/analysis_AAPL.json', 'w') as f:
    json.dump(result, f, indent=2)
```

---

## Multi-Stock Analysis Pattern

```python
import sys
sys.path.append('.claude/skills/quantitative-trading')

from scripts import fetch_stock_data
from scripts.indicators import TechnicalIndicators

tickers = ['AAPL', 'GOOGL', 'MSFT', 'AMZN']
results = {}

ti = TechnicalIndicators()

for ticker in tickers:
    try:
        data = fetch_stock_data(ticker, period='1y')
        rsi = ti.calculate_rsi(data)
        
        results[ticker] = {
            'price': data['Close'].iloc[-1],
            'rsi': rsi.iloc[-1]
        }
    except Exception as e:
        results[ticker] = {'error': str(e)}

# Find best performer
best = max([(k, v) for k, v in results.items() if 'error' not in v], 
          key=lambda x: x[1]['rsi'])
print(f"Highest RSI: {best[0]} = {best[1]['rsi']:.2f}")
```

---

## Correlation Analysis Pattern

When analyzing correlations between assets, use pandas directly:

```python
from scripts import fetch_multiple_stocks

data = fetch_multiple_stocks(['510300.SH', '510500.SH', '159830.SZ'], period='1y')
returns = {k: v['Close'].pct_change().dropna() for k, v in data.items()}
import pandas as pd
corr_matrix = pd.DataFrame(returns).corr()
```

