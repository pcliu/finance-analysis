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
> - **Scripts: `workspace/YYYY-MM-DD/HHMMSS/analyze_*.py`** ← 脚本本身也放在此目录！
> - Output: `workspace/YYYY-MM-DD/HHMMSS/*.json`, `*.csv`, `*.png`
> - **📋 MUST generate `analysis_report.md`** - 每次分析必须生成分析报告便于回顾
> 
> **🚨 注意：创建脚本时，必须先确定 output_dir，再将脚本文件写入该目录！**
> 
> ```python
> from datetime import datetime
> import os
> 
> # 1. FIRST: Generate date-time based output directory
> now = datetime.now()
> output_dir = f"workspace/{now.strftime('%Y-%m-%d')}/{now.strftime('%H%M%S')}"
> os.makedirs(output_dir, exist_ok=True)
> 
> # 2. Script file should be saved AS: {output_dir}/analyze_xxx.py
> #    NOT in workspace/ root!
> ```


> **📋 Analysis Report Templates**
> 
> 每次分析完成后，必须在输出目录生成 `analysis_report.md` 报告。
> 
> 请根据任务类型选择合适的模板：
> 1. **技术分析 (Technical Analysis)**: [`references/report_templates/technical_analysis.md`](references/report_templates/technical_analysis.md)
> 2. **持仓调整 (Portfolio Adjustment)**: [`references/report_templates/portfolio_adjustment.md`](references/report_templates/portfolio_adjustment.md)
> 3. **策略信号分析 (Strategy Signal Analysis)**: [`references/report_templates/strategy_signal_analysis.md`](references/report_templates/strategy_signal_analysis.md)
> 4. **组合分析 (Portfolio Analysis)**: [`references/report_templates/portfolio_analysis.md`](references/report_templates/portfolio_analysis.md)
> 5. **风险管理评估 (Risk Assessment)**: [`references/report_templates/risk_assessment.md`](references/report_templates/risk_assessment.md)
> 
> *注：若任务类型不属于上述任何一类，请根据实际分析内容**自由撰写**结构清晰的分析报告。*
> 
> **👉 更多详情与扩展:** [`references/report_templates/README.md`](references/report_templates/README.md)


## Quick Start

```python
import sys
sys.path.append('quantitative-trading-skills/quantitative-trading')

from scripts import fetch_stock_data, calculate_rsi, calculate_sma

# Fetch and analyze stock
data = fetch_stock_data('AAPL', period='6mo')
rsi = calculate_rsi(data)['RSI']
sma_20 = calculate_sma(data, window=20)['SMA']

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
> - **ALL** indicator functions return `pd.DataFrame`.
> - Single-value indicators (RSI, SMA) return a DataFrame with a single column (e.g., `'RSI'`, `'SMA'`).
> - Multi-value indicators (MACD, Bollinger Bands) return a DataFrame with multiple columns.

```python
from scripts import calculate_rsi, calculate_sma, calculate_macd, calculate_bollinger_bands

rsi = calculate_rsi(data, window=14)        # Returns DataFrame with column 'RSI'
sma = calculate_sma(data, window=20)        # Returns DataFrame with column 'SMA'
macd = calculate_macd(data)                 # Returns DataFrame with columns 'MACD', 'Signal', 'Histogram'
bb = calculate_bollinger_bands(data)        # Returns DataFrame with columns 'Upper', 'Middle', 'Lower', ...

# Access values:
current_rsi = rsi['RSI'].iloc[-1]
macd_line = macd['MACD'].iloc[-1]
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

### Portfolio Analysis
```python
from scripts import PortfolioAnalyzer

pa = PortfolioAnalyzer()
# Optimization (Max Sharpe, Min Volatility, etc.)
opt_result = pa.optimize_portfolio(returns, method='sharpe')

# Efficient Frontier
ef_data = pa.calculate_efficient_frontier(returns)

# Correlation Matrix
corr = returns.corr()
```

### Portfolio Adjustment (持仓调整)

持仓调整分析的完整流程：

**流程步骤：**

1. **获取技术指标** - 对持仓和候选品种计算 RSI、MACD、SMA、布林带等
2. **历史复盘**（可选）- 对比历史建议与实际走势，计算准确率
3. **动态调整阈值** - 根据复盘准确率调整 RSI 超买/超卖阈值
4. **生成操作建议** - 基于技术指标生成减持/持有/建仓建议

**决策逻辑：**
- RSI ≥ 80：严重超买 → 建议减持
- RSI ≥ 70：超买 → 观察持有
- RSI < 40：超卖 → 可左侧建仓
- 按 RSI 升序排列候选品种（优先低估值）

**输出结构：**
```python
recommendations = {
    'sell': [{'ticker': 'xxx', 'action': '减持', 'reason': '...'}],
    'buy': [{'ticker': 'xxx', 'action': '可建仓', 'feasibility': '✅', 'reason': '...'}],
    'hold': [{'ticker': 'xxx', 'action': '持有', 'reason': '...'}],
}
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
result = {'ticker': 'AAPL', 'rsi': float(rsi['RSI'].iloc[-1])}

with open(f'{output_dir}/result.json', 'w') as f:
    json.dump(result, f, indent=2)

print(f"Results saved to: {output_dir}/")
```

## Detailed Documentation

- [API Reference](references/api_reference.md) - Complete function documentation
- [Workflow Guide](references/workflow_guide.md) - Advanced usage patterns
- [Workflow Guide](references/workflow_guide.md) - Advanced usage patterns
- [Report Templates](references/report_templates/README.md) - 📋 Standard report formats
- [Troubleshooting](references/troubleshooting.md) - Common issues and solutions
- [Troubleshooting](references/troubleshooting.md) - Common issues and solutions
