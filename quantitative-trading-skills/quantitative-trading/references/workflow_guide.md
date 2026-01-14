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

---

## Portfolio Analysis Pattern

When performing portfolio analysis (diversification and optimization):

1. **Use `PortfolioAnalyzer` class** for correlation and optimization.
2. **Handle Risky Assets vs Cash**: Always calculate metrics for the risky part (ETFs/Stocks) and separately account for cash holdings to show total portfolio risk.
3. **Save Multiple Outputs**: Portfolio analysis usually requires a JSON for data and PNGs for visualization (Efficient Frontier, Correlation Matrix).

### Example Pattern

```python
from scripts import PortfolioAnalyzer

# 1. Fetch data for multiple tickers
pa = PortfolioAnalyzer()
tickers = ['510300.SH', '510500.SH', '159830.SZ']
price_data = pa.create_portfolio_data(tickers, period='1y')
returns = pa.calculate_returns(price_data)

# 2. Portfolio Optimization (Max Sharpe)
opt_result = pa.optimize_portfolio(returns, optimization_method='sharpe')

# 3. Correlation Matrix
corr_matrix = returns.corr()

# 4. Save results to workspace
# [See example script in SKILL.md for directory structure]
```

---

## Risk Management Assessment Pattern

For deep risk dives (Stress Testing, VaR, Risk Contribution):

1. **Use `RiskManager` class** for quantitative risk metrics.
2. **Component Risk Analysis**: Calculate `portfolio_risk_contribution` to identify which individual assets are driving the portfolio's overall volatility.
3. **Stress Scenarios**: Run `stress_testing` with various scenarios (Market Crash, Volatility Spike) to understand potential losses in tail events.
4. **Visualizations**: Always generate at least:
   - `risk_contribution.png`: To visualize where risk is concentrated.
   - `correlation_matrix.png`: To visualize diversification or lack thereof.

### Example Pattern

```python
from scripts import RiskManager, DataFetcher

rm = RiskManager()
fetcher = DataFetcher()

# 1. Prepare Returns (including risky and cash allocation)
returns_df = fetcher.fetch_multiple_stocks(tickers, period='1y')
portfolio_returns = (returns_df * weights).sum(axis=1)

# 2. Generate Full Risk Report
report = rm.generate_risk_report(portfolio_returns, weights=weights, returns=returns_df)

# 3. Component Risk Contribution
risk_contrib = rm.portfolio_risk_contribution(returns_df, weights)

# 4. Stress Testing
stress_results = rm.stress_testing(portfolio_returns)
```

> **👉 Tip:** Use the [Risk Assessment](./report_templates/risk_assessment.md) template for documenting these findings.
