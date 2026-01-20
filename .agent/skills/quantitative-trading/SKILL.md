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
> - **ALL generated scripts and output files MUST be saved to the project root `workspace/YYYY-MM-DD/HHMMSS/`**
> - Use current date and time for directory structure (e.g., `workspace/2026-01-06/085012/`)
> - **NEVER create or modify files in `examples/`** - this directory is READ-ONLY reference
> 
> **🏷️ 文件命名规范（按任务类型）：**
> 
> | 任务类型 | 脚本命名 | 报告命名 | 数据文件命名 |
> |:---|:---|:---|:---|
> | 持仓调整/再平衡 | `portfolio_adjustment.py` | `portfolio_adjustment_report.md` | `portfolio_adjustment_data.json` |
> | 技术分析 | `technical_analysis_{ticker}.py` | `technical_analysis_{ticker}_report.md` | `technical_analysis_{ticker}_data.json` |
> | 策略信号分析 | `strategy_signal_{ticker}.py` | `strategy_signal_{ticker}_report.md` | `strategy_signal_{ticker}_data.json` |
> | 组合优化 (Portfolio Optimization) | `portfolio_optimization.py` | `portfolio_optimization_report.md` | `portfolio_optimization_data.json` |
> | 风险管理评估 | `risk_assessment.py` | `risk_assessment_report.md` | `risk_assessment_data.json` |
> | 复盘/回测 | `backtest_review.py` | `backtest_review_report.md` | `backtest_review_data.json` |
> | **自定义任务** | `{task_name}.py` | `{task_name}_report.md` | `{task_name}_data.json` |
> 
> *注：*
> - *`{ticker}` 替换为实际代码，如 `510150`*
> - *若任务不属于上述预定义类型，使用简洁的英文描述命名，如 `etf_screening.py`、`correlation_analysis.py`*
> 
> **🚨 关键规则：脚本与输出必须在同一目录！**
> 
> **Agent 必须遵循的工作流程：**
> 1. **先确定目录**：根据当前时间在项目根目录生成目录名（如 `workspace/2026-01-15/091459/`）
> 2. **写入脚本**：使用 `write_to_file` 将脚本保存到该目录
> 3. **脚本内部使用 `__file__`**：脚本运行时用 `os.path.dirname(__file__)` 获取输出路径
> 
> ```python
> import os
> SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
> # 所有输出保存到 SCRIPT_DIR，不再调用 datetime.now()
> ```
> 
> **💾 数据序列化 (JSON)**
> 
> `numpy` 类型 (int64, float64 等) 无法直接被 `json.dump` 序列化。
> **必须** 引入 `scripts.utils` 并使用 `make_serializable` 工具：
> 
> ```python
> from scripts.utils import make_serializable
> 
> # ... 计算结果 ...
> results = { ... }
> 
> # 序列化处理
> clean_results = make_serializable(results)
> 
> with open(os.path.join(SCRIPT_DIR, 'output.json'), 'w') as f:
>     json.dump(clean_results, f, indent=4)
> ```


> **📋 Analysis Report Templates**
> 
> 每次分析完成后，必须在输出目录生成对应任务类型的报告（如 `portfolio_adjustment_report.md`）。
> 
> 请根据任务类型选择合适的模板：
> 1. **技术分析 (Technical Analysis)**: [`references/report_templates/technical_analysis.md`](references/report_templates/technical_analysis.md)
> 2. **策略信号分析 (Strategy Signal Analysis)**: [`references/report_templates/strategy_signal_analysis.md`](references/report_templates/strategy_signal_analysis.md)
> 3. **组合优化 (Portfolio Optimization)**: [`references/report_templates/portfolio_optimization.md`](references/report_templates/portfolio_optimization.md)
> 4. **风险管理评估 (Risk Assessment)**: [`references/report_templates/risk_assessment.md`](references/report_templates/risk_assessment.md)
> 
> *注：若任务类型不属于上述任何一类，请根据实际分析内容**自由撰写**结构清晰的分析报告。*
> 
> **👉 更多详情与扩展:** [`references/report_templates/README.md`](references/report_templates/README.md)


## Quick Start

```python
import sys
import os

# Robust Import: Use absolute path relative to this script
# Assuming script is in workspace/YYYY-MM-DD/HHMMSS/
SKILL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../.agent/skills/quantitative-trading'))
sys.path.append(SKILL_DIR)

from scripts import fetch_stock_data, calculate_rsi, calculate_sma, calculate_atr
from scripts.utils import make_serializable

# Fetch and analyze stock
data = fetch_stock_data('AAPL', period='6mo')
rsi = calculate_rsi(data)['RSI']
atr = calculate_atr(data)['ATR']

# Prepare results safe for JSON
results = {
    "price": data['Close'].iloc[-1],
    "rsi": rsi.iloc[-1],
    "atr": atr.iloc[-1]
}
print(make_serializable(results))
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
.agent/skills/quantitative-trading/
├── SKILL.md              # This file
├── references/           # 📚 Detailed documentation
│   ├── api_reference.md
│   ├── workflow_guide.md
│   └── troubleshooting.md
├── scripts/              # 💻 Core implementation (import from here)
│   ├── __init__.py       # Unified exports
│   ├── utils.py          # 🛠 Utilities (serialization, etc.)
│   ├── data_fetcher.py
│   ├── indicators.py
│   ├── strategies.py
│   ├── backtester.py
│   ├── portfolio_analyzer.py
│   └── risk_manager.py
└── examples/             # 📝 READ-ONLY reference examples (do NOT modify)
workspace/                # 📂 ⬅️ ALL generated scripts & output go HERE (Project Root)
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
> - Single-value indicators (RSI, SMA, ATR) return a DataFrame with a single column.
> - Multi-value indicators (MACD, Bollinger Bands) return a DataFrame with multiple columns.

```python
from scripts import (
    calculate_rsi, calculate_sma, calculate_macd, calculate_bollinger_bands,
    calculate_atr, calculate_adx, calculate_stochastic, calculate_williams_r
)

rsi = calculate_rsi(data, window=14)        # Returns DataFrame with column 'RSI'
sma = calculate_sma(data, window=20)        # Returns DataFrame with column 'SMA'
atr = calculate_atr(data, window=14)        # Returns DataFrame with column 'ATR'
macd = calculate_macd(data)                 # Returns DataFrame with columns 'MACD', 'Signal', 'Histogram'
bb = calculate_bollinger_bands(data)        # Returns DataFrame with columns 'Upper', 'Middle', 'Lower', ...
stoch = calculate_stochastic(data)          # Returns DataFrame with columns 'K', 'D'

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

### Portfolio Optimization (组合优化)
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

**核心原则：**
- **数据驱动**：必须计算并引用 RSI、布林带 (%B)、MACD、成交量等核心指标。
- **自由推理**：不要使用硬编码的阈值（如 >80）。请利用你的金融知识，结合当前市场环境（震荡/趋势）、个股特性（蓝筹/妖股）进行综合判断。
- **报告自由度**：**不使用预定义模板**。请根据分析结果的丰富程度，自由构建结构清晰、逻辑严密的 Markdown 报告。

**建议分析维度：**
1. **持仓诊断**：识别高风险（超买/背离）和低风险（稳健/超卖）品种。
2. **机会扫描**：评估非持仓品种的建仓性价比。
3. **资金规划**：给出明确的买卖数量和资金变动建议。

## Usage Guidelines

1. **Import from `scripts` module** for core functionality
2. **Filter data early** to reduce context size
3. **Return summaries** not full datasets
4. See [API Reference](references/api_reference.md) for detailed function signatures

## References

- [API Reference](references/api_reference.md) - Function documentation
- [Workflow Guide](references/workflow_guide.md) - Advanced patterns
- [Report Templates](references/report_templates/README.md) - Report formats
- [Troubleshooting](references/troubleshooting.md) - Common issues
