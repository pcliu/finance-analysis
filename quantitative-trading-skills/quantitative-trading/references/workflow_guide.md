# Workflow Guide

Advanced usage patterns and workflows for the quantitative-trading skill.

> **⚠️ IMPORTANT: All generated files go to `workspace/`**
> 
> - Scripts: `workspace/analyze_*.py`
> - Output: `workspace/*.json`, `workspace/*.csv`, `workspace/*.png`
> - **NEVER** create files in `examples/` (read-only reference)

## Environment Setup

### Runtime Environment

This skill requires the `finance-analysis` conda environment.

**Claude Code / Hosted environment:**
```bash
ENV_PYTHON=/opt/homebrew/Caskroom/miniforge/base/envs/finance-analysis/bin/python
ENV_PIP=/opt/homebrew/Caskroom/miniforge/base/envs/finance-analysis/bin/pip

$ENV_PIP install -U yfinance tushare pandas numpy matplotlib scipy
$ENV_PYTHON your_script.py
```

**Local machine with conda:**
```bash
conda activate finance-analysis
pip install -U yfinance tushare pandas numpy matplotlib scipy
python your_script.py
```

---

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
sys.path.append('quantitative-trading-skills/quantitative-trading')

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

## Reusable Workflows

### analyze_and_save

```python
from workflows import analyze_and_save

# Analyze and auto-save to workspace
result = analyze_and_save('AAPL', period='1y')
# Saved to: workspace/analysis_AAPL.json
```

### compare_stocks

```python
from workflows import compare_stocks

# Compare multiple stocks
comparison = compare_stocks(['AAPL', 'GOOGL', 'MSFT'])
# Saved to: workspace/comparison_AAPL_GOOGL_MSFT.json
```

---

## Multi-Stock Analysis Pattern

```python
import sys
sys.path.append('quantitative-trading-skills/quantitative-trading')

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
