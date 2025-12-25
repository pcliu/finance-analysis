---
name: quantitative-trading
description: >
  Quantitative trading toolkit for stock analysis with yfinance (global) and tushare (China/HK).
  Use when users request:
  - Stock data fetching (historical/real-time prices, volume, dividends)
  - Technical indicators (RSI, MACD, SMA, EMA, Bollinger Bands, ATR, Stochastic)
  - Trading strategies (moving average crossover, mean reversion, momentum)
  - Portfolio optimization, correlation analysis, and efficient frontier
  - Backtesting trading strategies with historical data
  - Risk assessment (Sharpe ratio, VaR, CVaR, maximum drawdown, Sortino ratio)
version: 1.0.0
dependencies:
  - python>=3.8
  - yfinance
  - tushare
  - pandas>=1.5.0
  - numpy>=1.20.0
  - matplotlib>=3.5.0
  - scipy>=1.8.0
---

# Quantitative Trading Skill

A toolkit for quantitative trading analysis using yfinance (global) and tushare (China/HK).

## Quick Start

```python
import sys
sys.path.append('quantitative-trading-skills/quantitative-trading')

from scripts import fetch_stock_data, calculate_rsi, calculate_sma

# Fetch and analyze stock
data = fetch_stock_data('AAPL', period='6mo')
rsi = calculate_rsi(data)
sma_20 = calculate_sma(data, window=20)

print(f"Price: ${data['Close'].iloc[-1]:.2f}")
print(f"RSI: {rsi.iloc[-1]:.2f}")
```

## Environment Setup

**Use `finance-analysis` environment:**

```bash
ENV_PYTHON=/opt/homebrew/Caskroom/miniforge/base/envs/finance-analysis/bin/python
ENV_PIP=/opt/homebrew/Caskroom/miniforge/base/envs/finance-analysis/bin/pip

$ENV_PIP install yfinance tushare pandas numpy matplotlib scipy
$ENV_PYTHON your_script.py
```

**Tushare (China/HK):** Set `TUSHARE_TOKEN` environment variable.

## Directory Structure

```
quantitative-trading/
├── SKILL.md              # This file
├── references/           # 📚 Detailed documentation
│   ├── api_reference.md
│   ├── workflow_guide.md
│   └── troubleshooting.md
├── scripts/              # 💻 Core implementation
│   ├── __init__.py       # Unified exports
│   ├── data_fetcher.py
│   ├── indicators.py
│   ├── strategies.py
│   ├── backtester.py
│   ├── portfolio_analyzer.py
│   └── risk_manager.py
├── workflows/            # 🔄 Reusable workflows
│   ├── analyze_and_save.py
│   └── compare_stocks.py
├── examples/             # 📝 Usage examples
└── workspace/            # 📂 Output directory
```

## Core Modules

### Data Fetching
```python
from scripts import fetch_stock_data, fetch_multiple_stocks, get_company_info

data = fetch_stock_data('AAPL', period='1y')
data_dict = fetch_multiple_stocks(['AAPL', 'GOOGL'], period='1y')
info = get_company_info('AAPL')
```

### Technical Indicators
```python
from scripts import calculate_rsi, calculate_sma, calculate_macd, calculate_bollinger_bands

rsi = calculate_rsi(data, period=14)
sma = calculate_sma(data, window=20)
macd = calculate_macd(data)
bb = calculate_bollinger_bands(data)
```

### Trading Strategies
```python
from scripts import moving_average_crossover, rsi_mean_reversion

signals = moving_average_crossover(data, fast_window=20, slow_window=50)
signals = rsi_mean_reversion(data, oversold=30, overbought=70)
```

### Risk Analysis
```python
from scripts import calculate_var, calculate_max_drawdown

var = calculate_var(returns, confidence_level=0.95)
drawdown = calculate_max_drawdown(data)
```

### Workflows
```python
from workflows import analyze_and_save, compare_stocks

result = analyze_and_save('AAPL', period='1y')
comparison = compare_stocks(['AAPL', 'GOOGL', 'MSFT'])
```

## Usage Guidelines

1. **Create Python scripts** that import from `scripts` module
2. **Filter data early** to reduce context size
3. **Return summaries** not full datasets
4. **Save results** to `workspace/` directory

## Detailed Documentation

- [API Reference](references/api_reference.md) - Complete function documentation
- [Workflow Guide](references/workflow_guide.md) - Advanced usage patterns
- [Troubleshooting](references/troubleshooting.md) - Common issues and solutions
