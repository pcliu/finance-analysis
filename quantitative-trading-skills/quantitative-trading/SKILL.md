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
  - Multiple stock comparison and sector analysis
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

A comprehensive toolkit for quantitative trading analysis and strategy development using Python's yfinance package for global markets and tushare for China/Hong Kong coverage, alongside other financial analysis libraries.

## Quick Start Examples

### Example 1: Basic Stock Analysis
```python
import sys
sys.path.append('quantitative-trading-skills/quantitative-trading')

from api.data_fetcher import fetch_stock_data
from api.indicators import calculate_rsi, calculate_sma

# Analyze Apple's stock
if __name__ == "__main__":
    data = fetch_stock_data('AAPL', period='6mo')
    rsi = calculate_rsi(data)
    sma_20 = calculate_sma(data, window=20)
    sma_50 = calculate_sma(data, window=50)

    print(f"Current Price: ${data['Close'].iloc[-1]:.2f}")
    print(f"RSI: {rsi.iloc[-1]:.2f}")
    print(f"Trend: {'Bullish' if sma_20.iloc[-1] > sma_50.iloc[-1] else 'Bearish'}")
```

### Example 2: RSI Mean Reversion Strategy
```python
import sys
sys.path.append('quantitative-trading-skills/quantitative-trading')

from api.data_fetcher import fetch_stock_data
from api.indicators import calculate_rsi
from api.strategies import rsi_mean_reversion

# Generate buy/sell signals
if __name__ == "__main__":
    data = fetch_stock_data('AAPL', period='1y')
    signals = rsi_mean_reversion(data, oversold=30, overbought=70)

    buy_signals = signals[signals['Buy_Signal'] == True]
    sell_signals = signals[signals['Sell_Signal'] == True]

    print(f"Buy signals in last 30 days: {len(buy_signals.tail(30))}")
    print(f"Sell signals in last 30 days: {len(sell_signals.tail(30))}")
```

### Example 3: Portfolio Risk Analysis
```python
import sys
sys.path.append('quantitative-trading-skills/quantitative-trading')

from api.data_fetcher import fetch_multiple_stocks
from api.risk import calculate_portfolio_metrics, calculate_var

# Analyze a portfolio of tech stocks
tickers = ['AAPL', 'GOOGL', 'MSFT', 'AMZN']
prices = fetch_multiple_stocks(tickers, period='1y')

returns = {ticker: prices[ticker]['Close'].pct_change().dropna() for ticker in tickers}
weights = [0.25, 0.25, 0.25, 0.25]  # Equal weight

metrics = calculate_portfolio_metrics(returns, weights)
portfolio_var = calculate_var(returns, weights, confidence_level=0.95)

print(f"Portfolio Sharpe Ratio: {metrics['sharpe_ratio']:.3f}")
print(f"Portfolio VaR (95%): {portfolio_var:.3f}")
```

## Environment Setup

### Runtime Environment

**This skill must be run with the `finance-analysis` environment interpreter.**

> ⚠️ **Claude Code note:** The hosted workspace does not expose the `conda` CLI, so you cannot run `conda activate`. Always invoke the interpreter and `pip` inside the environment directly:
>
> ```bash
> ENV_PYTHON=/opt/homebrew/Caskroom/miniforge/base/envs/finance-analysis/bin/python
> ENV_PIP=/opt/homebrew/Caskroom/miniforge/base/envs/finance-analysis/bin/pip
>
> # Installing / upgrading packages
> $ENV_PIP install -U yfinance tushare pandas numpy matplotlib scipy
>
> # Running your scripts
> $ENV_PYTHON my_analysis.py
> ```
>
> If you are working on your own machine with conda available, you may still run:
>
> ```bash
> conda activate finance-analysis
> pip install -U yfinance tushare pandas numpy matplotlib scipy
> ```

### Required Dependencies

Install the following Python packages in the `finance-analysis` environment using the paths above. On Claude Code:

```bash
ENV_PIP=/opt/homebrew/Caskroom/miniforge/base/envs/finance-analysis/bin/pip
$ENV_PIP install yfinance tushare pandas numpy matplotlib scipy
```

On a local machine with conda available:

```bash
conda activate finance-analysis
pip install yfinance tushare pandas numpy matplotlib scipy
```

### Dependency List

- **yfinance** - Yahoo Finance data fetching
- **tushare** - Mainland China & Hong Kong market data (requires `TUSHARE_TOKEN`)
- **pandas** - Data manipulation and analysis
- **numpy** - Numerical computing
- **matplotlib** - Data visualization
- **scipy** - Scientific computing (for portfolio optimization)

### Verification

To verify the environment is set up correctly:

```python
import sys
import yfinance as yf
import tushare as ts
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize

print("All dependencies installed successfully!")
print(f"Python version: {sys.version}")
print(f"yfinance version: {yf.__version__}")
print(f"tushare version: {ts.__version__}")
print(f"pandas version: {pd.__version__}")
print(f"numpy version: {np.__version__}")
```

**Important**: Always run your scripts with the `finance-analysis` interpreter (`/opt/homebrew/Caskroom/miniforge/base/envs/finance-analysis/bin/python` inside Claude Code) so all required packages are available.

### Tushare Token (China/HK Data)

Tushare requires an API token. Create a free account at [tushare.pro](https://tushare.pro/register) and set the token before running scripts:

```bash
export TUSHARE_TOKEN="your-token-here"        # Linux / macOS
setx TUSHARE_TOKEN "your-token-here"          # Windows PowerShell
```

Without this variable the China/HK data provider will not initialize.

## Core Capabilities

### Data Acquisition
- **Stock Data**: Fetch real-time and historical stock data using yfinance (global) or tushare (China/HK)
- **Market Indices**: Analyze major indices (S&P 500, NASDAQ, etc.)
- **Company Information**: Get fundamental data and company financials
- **Multiple Tickers**: Batch process multiple stocks simultaneously

### Technical Indicators
- **Moving Averages**: SMA, EMA, Bollinger Bands
- **Momentum Indicators**: RSI, MACD, Stochastic Oscillator
- **Volatility Indicators**: ATR, VIX, Standard Deviation
- **Volume Indicators**: OBV, Volume Moving Averages
- **Trend Indicators**: ADX, Aroon, Parabolic SAR

### Analysis Tools
- **Statistical Analysis**: Returns, volatility, correlation analysis
- **Risk Metrics**: Sharpe ratio, Sortino ratio, maximum drawdown
- **Portfolio Analysis**: Optimization, diversification metrics
- **Backtesting**: Strategy testing with historical data

### Trading Strategies
- **Trend Following**: Moving average crossovers, momentum strategies
- **Mean Reversion**: RSI-based, Bollinger Band reversal strategies
- **Volatility Trading**: VIX-based, volatility targeting strategies
- **Arbitrage**: Statistical arbitrage, pairs trading opportunities

## API Structure (Code Execution Pattern)

This skill follows a **code execution pattern** where tools are presented as importable API functions, enabling:
- **Progressive Discovery**: Models can explore the filesystem to discover available tools
- **Context Efficiency**: Import only what you need, reducing token usage
- **Data Processing**: Filter and transform data in code before returning to model
- **State Persistence**: Save intermediate results and reusable functions

### How Agents Should Use This Skill

**Important**: When using this skill, agents should **create Python script files locally** that import and call the API functions. The Python code handles control flow (loops, conditionals, error handling), while data processing logic is implemented in the underlying `scripts/` modules.

#### Workflow Pattern

1. **Create a Python script file** (e.g., `analysis.py` or `strategy_backtest.py`)
2. **Import API functions** from the `api/` directory
3. **Write control flow logic** in Python (loops, conditionals, error handling)
4. **Call API functions** which internally use the `scripts/` modules for data processing
5. **Execute the script** using `/opt/homebrew/Caskroom/miniforge/base/envs/finance-analysis/bin/python your_script.py`

#### Example: Creating a Script to Use the Skill

```python
# File: analyze_stock.py
# This script demonstrates how agents should use the skill

import sys
import os
# Add the skill directory to Python path
sys.path.append('quantitative-trading-skills/quantitative-trading')

# Import API functions (control flow layer)
from api.data_fetcher import fetch_stock_data, get_company_info
from api.indicators import calculate_rsi, calculate_sma, calculate_macd
from api.strategies import moving_average_crossover
from api.backtester import backtest_strategy

def analyze_stock(ticker: str, period: str = '1y'):
    """
    Example function showing how to use the skill APIs.
    This Python code handles control flow, while data processing
    happens in the underlying scripts/ modules.
    """
    try:
        # Fetch data using API (data processing in scripts/data_fetcher.py)
        print(f"Fetching data for {ticker}...")
        data = fetch_stock_data(ticker, period=period)
        
        if data is None or data.empty:
            print(f"Error: Could not fetch data for {ticker}")
            return None
        
        # Filter data (control flow in Python)
        recent_data = data.tail(60)  # Last 60 days
        
        # Calculate indicators using API (data processing in scripts/indicators.py)
        print("Calculating indicators...")
        rsi = calculate_rsi(recent_data)
        sma_20 = calculate_sma(recent_data, window=20)
        sma_50 = calculate_sma(recent_data, window=50)
        macd = calculate_macd(recent_data)
        
        # Extract summary (control flow in Python)
        summary = {
            'ticker': ticker,
            'current_price': float(recent_data['Close'].iloc[-1]),
            'rsi': float(rsi.iloc[-1]),
            'sma_20': float(sma_20.iloc[-1]),
            'sma_50': float(sma_50.iloc[-1]),
            'macd': float(macd['MACD'].iloc[-1]),
            'macd_signal': float(macd['Signal'].iloc[-1]),
        }
        
        # Generate signals using API (data processing in scripts/strategies.py)
        signals = moving_average_crossover(recent_data, fast_window=20, slow_window=50)
        buy_signals = signals[signals['Buy_Signal'] == True]
        sell_signals = signals[signals['Sell_Signal'] == True]
        
        summary['buy_signals'] = len(buy_signals)
        summary['sell_signals'] = len(sell_signals)
        
        return summary
        
    except Exception as e:
        print(f"Error analyzing {ticker}: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

# Control flow: Main execution
if __name__ == "__main__":
    ticker = 'AAPL'
    result = analyze_stock(ticker, period='6mo')
    
    if result:
        print(f"\nAnalysis Results for {ticker}:")
        print("=" * 50)
        for key, value in result.items():
            print(f"{key:20s}: {value}")
```

#### Architecture: Control Flow vs Data Flow

```
┌─────────────────────────────────────────┐
│  Agent-Created Python Script            │
│  (Control Flow: loops, conditionals)    │
│                                         │
│  - Import API functions                │
│  - Write control logic                 │
│  - Handle errors                       │
│  - Orchestrate workflow                │
└──────────────┬──────────────────────────┘
               │ calls
               ▼
┌─────────────────────────────────────────┐
│  API Layer (api/*.py)                  │
│  (Thin wrapper functions)             │
│                                         │
│  - Simple function interfaces          │
│  - Parameter validation                │
│  - Delegates to scripts/               │
└──────────────┬──────────────────────────┘
               │ delegates to
               ▼
┌─────────────────────────────────────────┐
│  Scripts Layer (scripts/*.py)          │
│  (Data Flow: data processing logic)     │
│                                         │
│  - Data fetching (yfinance)           │
│  - Indicator calculations              │
│  - Strategy implementations            │
│  - Backtesting engines                 │
│  - Portfolio optimization              │
└─────────────────────────────────────────┘
```

**Key Points**:
- **Control Flow**: Written by agents in Python scripts (loops, conditionals, error handling, workflow orchestration)
- **Data Flow**: Implemented in `scripts/` modules (data fetching, calculations, processing)
- **API Layer**: Provides clean function interfaces that agents can import and call
- **Separation of Concerns**: Agents focus on control logic, scripts handle data processing

### API Directory Structure

```
api/
├── data_fetcher/          # Stock data fetching functions
│   ├── fetch_stock_data.py
│   ├── fetch_multiple_stocks.py
│   ├── get_company_info.py
│   └── ...
├── indicators/            # Technical indicator calculations
│   ├── calculate_sma.py
│   ├── calculate_rsi.py
│   ├── calculate_macd.py
│   └── ...
├── strategies/           # Trading strategy implementations
│   ├── moving_average_crossover.py
│   └── rsi_mean_reversion.py
├── backtester/          # Backtesting functions
│   └── backtest_strategy.py
├── portfolio/            # Portfolio analysis
│   ├── create_portfolio_data.py
│   ├── optimize_portfolio.py
│   └── calculate_portfolio_metrics.py
└── risk/                # Risk management
    ├── calculate_var.py
    ├── calculate_cvar.py
    └── calculate_max_drawdown.py
```

### Getting Started with API

#### Step 1: Create a Python Script File

Agents should create a Python script file (e.g., `my_analysis.py`) in the workspace or project directory. This script will contain the control flow logic.

#### Step 2: Import API Functions

Import only the API functions you need:

```python
# In your Python script file
import sys
import os
sys.path.append('quantitative-trading-skills/quantitative-trading')

# Import only what you need (progressive discovery)
from api.data_fetcher import fetch_stock_data, get_company_info
from api.indicators import calculate_rsi, calculate_sma
from api.strategies import moving_average_crossover
```

#### Step 3: Write Control Flow Logic

Write Python code to orchestrate the workflow:

```python
# Control flow: loops, conditionals, error handling
tickers = ['AAPL', 'GOOGL', 'MSFT']
results = {}

for ticker in tickers:
    try:
        # Call API functions (data processing happens in scripts/)
        data = fetch_stock_data(ticker, period='1y')
        rsi = calculate_rsi(data)
        
        # Control flow: extract and store results
        results[ticker] = {
            'price': data['Close'].iloc[-1],
            'rsi': rsi.iloc[-1]
        }
    except Exception as e:
        print(f"Error processing {ticker}: {e}")
        results[ticker] = None

# Control flow: find best performer
best = max([(k, v) for k, v in results.items() if v], 
          key=lambda x: x[1]['rsi'])
print(f"Best RSI: {best[0]} with RSI {best[1]['rsi']:.2f}")
```

#### Progressive Discovery Pattern

Agents can discover available tools by exploring the filesystem:

```python
# Step 1: List available API modules
import os
api_dir = 'quantitative-trading-skills/quantitative-trading/api'
modules = [d for d in os.listdir(api_dir) 
           if os.path.isdir(os.path.join(api_dir, d)) and not d.startswith('_')]
print(f"Available modules: {modules}")

# Step 2: Check available functions in a module
import importlib
from api import data_fetcher
print(f"Available functions: {dir(data_fetcher)}")

# Step 3: Import and use
from api.data_fetcher import fetch_stock_data
data = fetch_stock_data('AAPL', period='1y')
```

#### Context-Efficient Usage

Filter and transform data before returning to model:

```python
from api.data_fetcher import fetch_stock_data_async
from api.indicators import calculate_rsi, calculate_sma

# Fetch data
data = await fetch_stock_data_async('AAPL', period='1y')

# Filter to recent data only (context efficient)
recent = data.tail(30)  # Last 30 days

# Calculate indicators
rsi = calculate_rsi(recent)
sma = calculate_sma(recent, window=20)

# Extract only latest values (not full series)
summary = {
    'current_price': recent['Close'].iloc[-1],
    'rsi': rsi.iloc[-1],
    'sma_20': sma.iloc[-1]
}
print(summary)  # Only summary, not full datasets
```

#### Using Reusable Skills

Save and reuse common analysis patterns:

```python
from skills.analyze_and_save import analyze_and_save
from skills.compare_stocks import compare_stocks

# Analyze and save results
result = analyze_and_save('AAPL', period='1y')
# Results saved to workspace/analysis_AAPL.json

# Compare multiple stocks
comparison = compare_stocks(['AAPL', 'GOOGL', 'MSFT'])
# Results saved to workspace/comparison_AAPL_GOOGL_MSFT.json
```

## Usage Guidelines

### Prerequisites

**⚠️ Important**: Before using this skill, ensure:
1. You're running commands with the `finance-analysis` interpreter (`/opt/homebrew/Caskroom/miniforge/base/envs/finance-analysis/bin/python` inside Claude Code, or `conda activate finance-analysis` on a local machine).
2. Packages were installed with the matching `pip` (`/opt/homebrew/Caskroom/miniforge/base/envs/finance-analysis/bin/pip`) so yfinance/tushare/pandas/etc. are available.
3. Required environment variables (e.g., `TUSHARE_TOKEN`) are configured before executing scripts.

### When to Use This Skill
1. **Stock Analysis**: When users need detailed analysis of specific stocks or sectors
2. **Technical Analysis**: When technical indicators and chart patterns are needed
3. **Strategy Development**: When developing or testing trading strategies
4. **Risk Assessment**: When evaluating investment risk and portfolio metrics
5. **Market Research**: When conducting broad market analysis or comparisons

### Analysis Workflow

**For Agents**: Follow this workflow when using the skill:

1. **Environment Check**: Confirm you're using `/opt/homebrew/Caskroom/miniforge/base/envs/finance-analysis/bin/python` (or have locally activated `finance-analysis`)
2. **Create Python Script**: Create a new Python script file (e.g., `analysis.py`) in your workspace
3. **Add Path Setup**: Add the skill directory to Python path in your script
4. **Progressive Discovery**: Explore `api/` directory to find relevant functions
5. **Selective Import**: Import only the functions needed for the task
6. **Write Control Flow**: Write Python code for loops, conditionals, error handling
7. **Call API Functions**: Call API functions which handle data processing via `scripts/`
8. **Data Processing**: Filter and transform data in your Python code (control flow)
9. **State Persistence**: Save intermediate results to files if needed
10. **Execute Script**: Run your Python script via `/opt/homebrew/Caskroom/miniforge/base/envs/finance-analysis/bin/python your_script.py`

**Example Workflow**:

```python
# File: my_analysis.py
import sys
sys.path.append('quantitative-trading-skills/quantitative-trading')

from api.data_fetcher import fetch_stock_data
from api.indicators import calculate_rsi

# Control flow: process multiple stocks
for ticker in ['AAPL', 'GOOGL']:
    data = fetch_stock_data(ticker, period='1y')  # Data processing in scripts/
    rsi = calculate_rsi(data)  # Data processing in scripts/
    print(f"{ticker}: RSI = {rsi.iloc[-1]:.2f}")  # Control flow in Python
```

Run with: `/opt/homebrew/Caskroom/miniforge/base/envs/finance-analysis/bin/python my_analysis.py`

### Best Practices

#### Control Flow vs Data Flow Separation

**Agents should**:
- ✅ **Create Python scripts** that import API functions
- ✅ **Write control flow logic** (loops, conditionals, error handling) in Python
- ✅ **Call API functions** which handle data processing internally
- ✅ **Focus on orchestration** and workflow logic

**Agents should NOT**:
- ❌ Try to modify `scripts/` modules directly (data processing layer)
- ❌ Call `scripts/` modules directly (use `api/` layer instead)
- ❌ Write data processing logic in agent scripts (use API functions)

**Example of Good Separation**:

```python
# ✅ Good: Control flow in agent script, data processing via API
import sys
sys.path.append('quantitative-trading-skills/quantitative-trading')

from api.data_fetcher import fetch_stock_data
from api.indicators import calculate_rsi

# Control flow: iterate over multiple stocks
for ticker in ['AAPL', 'GOOGL', 'MSFT']:
    # Data processing: handled by API -> scripts/
    data = fetch_stock_data(ticker, period='1y')
    rsi = calculate_rsi(data)
    
    # Control flow: conditional logic
    if rsi.iloc[-1] > 70:
        print(f"{ticker}: Overbought (RSI={rsi.iloc[-1]:.2f})")
    elif rsi.iloc[-1] < 30:
        print(f"{ticker}: Oversold (RSI={rsi.iloc[-1]:.2f})")
```

#### Context Efficiency
- **Import only what you need**: Don't import entire modules if you only need one function
- **Filter data early**: Use `.tail()`, `.head()`, or date filtering to reduce data size
- **Extract summaries**: Return only latest values or aggregated statistics, not full time series
- **Use workspace**: Save large datasets to `workspace/` directory instead of returning them

#### Code Execution Patterns
```python
# ✅ Good: Filter and summarize
data = await fetch_stock_data_async('AAPL', period='2y')
recent = data.tail(60)  # Only last 60 days
summary = {
    'current_price': recent['Close'].iloc[-1],
    'return': (recent['Close'].iloc[-1] / recent['Close'].iloc[0] - 1) * 100
}
print(summary)

# ❌ Avoid: Returning full datasets
data = await fetch_stock_data_async('AAPL', period='2y')
print(data)  # Too much data for context window
```

#### State Management
- Save intermediate results to `workspace/` directory
- Use reusable skills from `skills/` directory for common patterns
- Load saved results in subsequent executions to resume work

#### General Best Practices
- Always validate data quality and handle missing values appropriately
- Use multiple timeframes for comprehensive analysis (daily, weekly, monthly)
- Combine technical and fundamental analysis for better insights
- Consider transaction costs and slippage in backtesting
- Implement proper risk management techniques

## Available API Modules

Each module has its own README with detailed documentation. Agents can progressively discover and load only the modules needed for the task:

- **[Data Fetcher API](api/data_fetcher/)** - `api/data_fetcher/`
  - Fetch stock data, market indices, company information
  - Calculate correlation matrices

- **[Indicators API](api/indicators/)** - `api/indicators/`
  - Moving averages (SMA, EMA)
  - Momentum oscillators (RSI, MACD, Stochastic)
  - Volatility measures (Bollinger Bands, ATR)

- **[Strategies API](api/strategies/)** - `api/strategies/`
  - Moving average crossover signals
  - RSI mean reversion signals

- **[Backtester API](api/backtester/)** - `api/backtester/`
  - Backtest strategies with historical data
  - Performance metrics (Sharpe ratio, max drawdown, win rate)

- **[Portfolio API](api/portfolio/)** - `api/portfolio/`
  - Portfolio construction and optimization
  - Efficient frontier analysis

- **[Risk API](api/risk/)** - `api/risk/`
  - Value at Risk (VaR) and Conditional VaR (CVaR)
  - Maximum drawdown analysis

- **[Reusable Skills](skills/)** - `skills/`
  - Pre-built workflows: `analyze_and_save`, `compare_stocks`

### Progressive Discovery

Agents can explore available APIs by checking module directories:

```python
import os

# List available API modules
api_dir = 'quantitative-trading-skills/quantitative-trading/api'
modules = [d for d in os.listdir(api_dir)
           if os.path.isdir(os.path.join(api_dir, d)) and not d.startswith('_')]
print(f"Available modules: {modules}")
# Output: ['data_fetcher', 'indicators', 'strategies', 'backtester', 'portfolio', 'risk']

# Read specific module documentation (agent uses Read tool)
# For example: read file api/data_fetcher/README.md
```

## Example Analyses

### 1. Stock Trend Analysis
- Fetch historical price data
- Calculate moving averages (SMA 20, 50, 200)
- Identify trend direction and strength
- Provide buy/sell signals based on crossovers

### 2. Momentum Strategy
- Calculate RSI and MACD indicators
- Identify overbought/oversold conditions
- Generate trading signals based on momentum
- Backtest strategy performance

### 3. Portfolio Optimization
- Analyze correlation between multiple stocks
- Calculate efficient frontier
- Optimize portfolio weights based on risk-return
- Provide diversification recommendations

### 4. Risk Assessment
- Calculate volatility and beta values
- Assess maximum drawdown risk
- Compute Sharpe and Sortino ratios
- Provide risk management recommendations

## Data Sources
- **Yahoo Finance** (via yfinance): Real-time and historical market data
- **Company Financials**: Income statements, balance sheets, cash flows
- **Market Indices**: Major global indices and sector performance

## Example Analysis Workflows

See `examples/` directory for complete examples:
- `api_usage_example.py` - Demonstrates context-efficient API usage
- `progressive_discovery_example.py` - Shows how to discover tools progressively
- `basic_analysis.py` - Basic stock analysis workflow

## Workspace Directory

The `workspace/` directory is used for saving intermediate results and analysis outputs. Skills can save results here for persistence across sessions.

### Workspace Structure
- `workspace/analysis_*.json` - Individual stock analysis results
- `workspace/comparison_*.json` - Multi-stock comparison results
- `workspace/backtest_*.json` - Strategy backtest results
- `workspace/portfolio_*.json` - Portfolio optimization results
- `workspace/risk_*.json` - Risk assessment results

### Data Persistence Guidelines
- Results are automatically saved to `workspace/` for reuse across sessions
- Files are named with timestamps to avoid conflicts: `analysis_AAPL_20251112.json`
- Use `skills.analyze_and_save` for automatic saving of analysis results
- Use `skills.compare_stocks` for automatic saving of comparison results

### Example: Working with Saved Results
```python
import json
from api.data_fetcher import fetch_stock_data

# Save analysis to workspace
def analyze_and_save(ticker):
    data = fetch_stock_data(ticker, period='1y')
    summary = {
        'ticker': ticker,
        'current_price': float(data['Close'].iloc[-1]),
        'return_1y': float((data['Close'].iloc[-1] / data['Close'].iloc[0] - 1) * 100)
    }

    # Save to workspace
    with open(f'workspace/analysis_{ticker}.json', 'w') as f:
        json.dump(summary, f, indent=2)

    return summary

# Later, load saved results
with open('workspace/analysis_AAPL.json', 'r') as f:
    saved_analysis = json.load(f)
    print(f"Loaded: {saved_analysis}")
```

This skill provides a complete framework for quantitative analysis, from basic stock data fetching to advanced strategy development and backtesting, optimized for code execution environments with progressive discovery and context efficiency.

## Troubleshooting

### Common Issues and Solutions

**Issue**: `ImportError: No module named 'yfinance'` or other import errors
- **Solution**: Ensure you're using the `finance-analysis` interpreter:
  ```bash
  ENV_PYTHON=/opt/homebrew/Caskroom/miniforge/base/envs/finance-analysis/bin/python
  ENV_PIP=/opt/homebrew/Caskroom/miniforge/base/envs/finance-analysis/bin/pip
  $ENV_PIP install yfinance tushare pandas numpy matplotlib scipy
  $ENV_PYTHON -c "import yfinance; print('OK')"
  ```

**Issue**: `HTTP Error 404` or `ConnectionError` when fetching stock data
- **Solution**: Check internet connection and verify ticker symbol is correct. Some tickers may not be available on Yahoo Finance:
  ```python
  import yfinance as yf
  ticker = yf.Ticker('INVALID_TICKER')
  info = ticker.info  # Will fail if ticker doesn't exist
  ```

**Issue**: `KeyError: 'Close'` or missing columns in data
- **Solution**: Check if data was fetched successfully. Some tickers may have missing data:
  ```python
  if data is None or data.empty:
      print("No data returned. Check ticker symbol.")
  elif 'Close' not in data.columns:
      print("Missing required columns. Data may be corrupted.")
  ```

**Issue**: `RuntimeWarning: invalid value encountered` in calculations
- **Solution**: Check for NaN values in data before calculations:
  ```python
  if data.isnull().any().any():
      print("Data contains NaN values. Consider dropping or filling them.")
      data = data.dropna()  # or data = data.fillna(method='ffill')
  ```

**Issue**: Slow performance when fetching multiple stocks
- **Solution**: Use `fetch_multiple_stocks` instead of looping through individual `fetch_stock_data` calls

**Issue**: Memory issues with large datasets
- **Solution**: Filter data early and extract only needed columns:
  ```python
  # Instead of fetching all columns
  data = fetch_stock_data('AAPL', period='max')

  # Only fetch recent data and needed columns
  data = fetch_stock_data('AAPL', period='1y')[['Open', 'High', 'Low', 'Close', 'Volume']]
  ```

### Debugging Mode

Enable debug logging to see detailed information about data fetching and calculations:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from api.data_fetcher import fetch_stock_data

# Now you'll see debug messages
data = fetch_stock_data('AAPL', period='1y')
```

### Validation and Testing

Before running full analysis, validate your setup:

```python
# Validation script
def validate_setup():
    import sys
    sys.path.append('quantitative-trading-skills/quantitative-trading')

    try:
        from api.data_fetcher import fetch_stock_data
        from api.indicators import calculate_rsi

        # Test data fetching
        data = fetch_stock_data('AAPL', period='5d')
        assert not data.empty, "Data fetch failed"

        # Test indicator calculation
        rsi = calculate_rsi(data)
        assert not rsi.empty, "RSI calculation failed"

        print("✓ All tests passed!")
        return True
    except Exception as e:
        print(f"✗ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    validate_setup()
```

### Getting Help

If you encounter issues not covered here:
1. Check the `examples/` directory for working code samples
2. Review API function docstrings in `api/` directory
3. Verify dependencies with `/opt/homebrew/Caskroom/miniforge/base/envs/finance-analysis/bin/pip list | grep -E "(yfinance|pandas|numpy)"`
4. Confirm you're invoking `/opt/homebrew/Caskroom/miniforge/base/envs/finance-analysis/bin/python` (or have a locally activated `finance-analysis` environment)
