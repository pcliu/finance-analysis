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

> **⚠️ IMPORTANT: File Generation Rules**
> 
> - **ALL generated scripts and output files MUST be saved to `workspace/YYYY-MM-DD/HHMMSS/`**
> - Use current date and time for directory structure (e.g., `workspace/2026-01-06/085012/`)
> - **NEVER create or modify files in `examples/`** - this directory is READ-ONLY reference
> - Scripts: `workspace/YYYY-MM-DD/HHMMSS/analyze_*.py`
> - Output: `workspace/YYYY-MM-DD/HHMMSS/*.json`, `*.csv`, `*.png`
> - **📋 MUST generate `analysis_report.md`** - 每次分析必须生成分析报告便于回顾
> 
> ```python
> from datetime import datetime
> import os
> 
> # Generate date-time based output directory
> now = datetime.now()
> output_dir = f"workspace/{now.strftime('%Y-%m-%d')}/{now.strftime('%H%M%S')}"
> os.makedirs(output_dir, exist_ok=True)
> ```

> **📋 Analysis Report Template (`analysis_report.md`)**
> 
> 每次分析完成后，必须在输出目录生成 `analysis_report.md` 报告，格式如下：
> 
> ```markdown
> # 投资分析报告
> 
> **生成时间**: YYYY-MM-DD HH:MM:SS
> 
> ## 1. 市场概况与持仓分析
> 
> [简要描述当前市场环境和持仓整体表现]
> 
> **现有持仓诊断：**
> 
> *   **标的1 (代码)**：当前价格、RSI、趋势状态、近期表现。**操作建议**。
> *   **标的2 (代码)**：...
> 
> ## 2. 关注标的分析
> 
> [如有新关注的标的，分析其技术指标和市场表现]
> 
> *   **标的A (代码)**：趋势强度、技术指标、建议。
> 
> ## 3. 具体操作建议
> 
> [策略总结，如："去弱留强，积极进攻"]
> 
> ### 减仓/卖出：
> | 代码 | 名称 | 操作 | 建议数量 | 理由 |
> | :--- | :--- | :--- | :--- | :--- |
> | **XXXXXX** | 名称 | 减持/清仓 | X 股 | 原因 |
> 
> ### 建仓/增持：
> | 代码 | 名称 | 操作 | 建议价格 | 建议数量 | 预估金额 | 理由 |
> | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
> | **XXXXXX** | 名称 | 建仓 | X.XX | X 股 | ~X 元 | 原因 |
> 
> ## 4. 调整后展望
> 
> *   **资金利用率**：调整前后对比
> *   **风格暴露**：组合风格变化
> *   **风险提示**：关键风险点和止损建议
> 
> ## 5. 生成文件
> - `analyze_*.py` - 分析脚本
> - `*.json` - 数据结果  
> - `*.png` - 图表
> 
> ---
> *注：以上分析基于技术指标与定量策略，仅供参考，不构成投资建议。*
> ```

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
├── scripts/              # 💻 Core implementation (import from here)
│   ├── __init__.py       # Unified exports
│   ├── data_fetcher.py
│   ├── indicators.py
│   ├── strategies.py
│   ├── backtester.py
│   ├── portfolio_analyzer.py
│   └── risk_manager.py
├── examples/             # 📝 READ-ONLY reference examples (do NOT modify)
└── workspace/            # 📂 ⬅️ ALL generated scripts & output go HERE
```

> **Note:** The `workspace/` directory is git-ignored. All intermediate results and generated scripts are stored here.

## Core Modules

### Data Fetching
```python
from scripts import fetch_stock_data, fetch_multiple_stocks, get_company_info

data = fetch_stock_data('AAPL', period='1y')
data_dict = fetch_multiple_stocks(['AAPL', 'GOOGL'], period='1y')
info = get_company_info('AAPL')
```

### Technical Indicators

> **⚠️ Return Types:**
> - `calculate_rsi`, `calculate_sma`, `calculate_ema` → `pd.Series`
> - `calculate_macd`, `calculate_bollinger_bands`, `calculate_stochastic` → `dict` (NOT DataFrame!)

```python
from scripts import calculate_rsi, calculate_sma, calculate_macd, calculate_bollinger_bands

rsi = calculate_rsi(data, window=14)        # Returns pd.Series
sma = calculate_sma(data, window=20)        # Returns pd.Series
macd = calculate_macd(data)                 # Returns dict: {'MACD': Series, 'Signal': Series, 'Histogram': Series}
bb = calculate_bollinger_bands(data)        # Returns dict: {'Upper': Series, 'Middle': Series, 'Lower': Series, ...}

# Access MACD values from dict:
macd_line = macd['MACD'].iloc[-1]
signal_line = macd['Signal'].iloc[-1]
```

### Trading Strategies
```python
from scripts import moving_average_crossover, rsi_mean_reversion

signals = moving_average_crossover(data, fast_window=20, slow_window=50)
signals = rsi_mean_reversion(data, oversold=30, overbought=70)
```

### Risk Analysis
```python
from scripts import RiskManager

rm = RiskManager()
var = rm.calculate_var(returns, confidence_level=0.95)
dd_metrics = rm.calculate_drawdown_metrics(returns, is_returns=True)  # Returns dict
risk_metrics = rm.calculate_risk_adjusted_metrics(returns)            # Returns dict with sharpe_ratio, etc.

# Access metrics:
max_drawdown = dd_metrics['max_drawdown']
sharpe_ratio = risk_metrics['sharpe_ratio']
```

## Usage Guidelines

1. **All generated files go to `workspace/YYYY-MM-DD/HHMMSS/`**:
   - Create date-time directory first: `workspace/2026-01-06/085012/`
   - Python scripts: `workspace/YYYY-MM-DD/HHMMSS/analyze_*.py`
   - Output data: `workspace/YYYY-MM-DD/HHMMSS/*.json`, `*.csv`
   - Charts/Reports: `workspace/YYYY-MM-DD/HHMMSS/*.png`, `*.md`
2. **Import from `scripts` module** for core functionality
3. **Filter data early** to reduce context size
4. **Return summaries** not full datasets

### Example Script Structure

```python
#!/usr/bin/env python3
"""Save this file to: workspace/YYYY-MM-DD/HHMMSS/my_analysis.py"""

import sys
import os
import json
from datetime import datetime

sys.path.insert(0, 'quantitative-trading-skills/quantitative-trading')

from scripts import fetch_stock_data, calculate_rsi

# Create date-time based output directory
now = datetime.now()
output_dir = f"workspace/{now.strftime('%Y-%m-%d')}/{now.strftime('%H%M%S')}"
os.makedirs(output_dir, exist_ok=True)

# Analysis code here...
data = fetch_stock_data('AAPL', period='3mo')
rsi = calculate_rsi(data)

# Save results to date-time directory
result = {'ticker': 'AAPL', 'rsi': float(rsi.iloc[-1])}
with open(f'{output_dir}/result.json', 'w') as f:
    json.dump(result, f, indent=2)

print(f"Results saved to: {output_dir}/")
```

## Detailed Documentation

- [API Reference](references/api_reference.md) - Complete function documentation
- [Workflow Guide](references/workflow_guide.md) - Advanced usage patterns
- [Troubleshooting](references/troubleshooting.md) - Common issues and solutions
