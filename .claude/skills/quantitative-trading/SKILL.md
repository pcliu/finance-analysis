---
name: quantitative-trading
description: >
  Quantitative trading toolkit for stock analysis with yfinance (global), tushare (China/HK) and akshare (real-time).
  Use when users request:
  - Stock data fetching (historical prices, volume, dividends)
  - Real-time quotes for A-share, ETF, and Index (via AKShare/Sina Finance)
  - Technical indicators (RSI, MACD, SMA, EMA, Bollinger Bands, ATR, Stochastic)
  - Correlation analysis between stocks
user-invocable: false
---

# Quantitative Trading Skill

Data fetching and technical indicator primitives for quantitative analysis.

## Environment Setup

```bash
ENV_PYTHON=/usr/local/Caskroom/miniforge/base/envs/finance-analysis/bin/python
ENV_PIP=/usr/local/Caskroom/miniforge/base/envs/finance-analysis/bin/pip

$ENV_PIP install yfinance tushare pandas numpy matplotlib scipy
$ENV_PYTHON your_script.py
```

**Tushare (China/HK):** Set `TUSHARE_TOKEN` environment variable.

## Quick Start

```python
import sys, os

SKILL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../.claude/skills/quantitative-trading'))
sys.path.append(SKILL_DIR)

from scripts import fetch_stock_data, calculate_rsi, calculate_atr
from scripts.utils import make_serializable

data = fetch_stock_data('AAPL', period='6mo')
results = {
    "price": data['Close'].iloc[-1],
    "rsi":   calculate_rsi(data)['RSI'].iloc[-1],
    "atr":   calculate_atr(data)['ATR'].iloc[-1],
}
print(make_serializable(results))
```

> **💾 JSON 序列化：** `numpy` 类型无法直接被 `json.dump` 序列化，必须先调用 `make_serializable`。

## Directory Structure

```
.claude/skills/quantitative-trading/
├── SKILL.md
├── references/
│   ├── api_reference.md
│   ├── workflow_guide.md
│   └── troubleshooting.md
└── scripts/
    ├── __init__.py       # Unified exports
    ├── utils.py          # make_serializable, etc.
    ├── data_fetcher.py
    └── indicators.py
```

## Core Modules

### Data Fetching

```python
from scripts import fetch_stock_data, fetch_multiple_stocks, get_company_info, fetch_realtime_quote

data      = fetch_stock_data('AAPL', period='1y')
data_dict = fetch_multiple_stocks(['AAPL', 'GOOGL'], period='1y')
info      = get_company_info('AAPL')

# Real-time quotes — CN: AKShare/Sina | US/Global: yfinance
quote  = fetch_realtime_quote('510150')                       # CN ETF
quotes = fetch_realtime_quote(['510150', 'AAPL', '512660'])   # Mixed
# Returns: 代码, 名称, 最新价, 涨跌额, 涨跌幅, 昨收, 今开, 最高, 最低, 成交量, 成交额
```

### Technical Indicators

All indicator functions return `pd.DataFrame`. Single-value indicators return one column; multi-value return multiple.

```python
from scripts import (
    calculate_rsi, calculate_sma, calculate_ema, calculate_macd,
    calculate_bollinger_bands, calculate_atr, calculate_adx,
    calculate_stochastic, calculate_williams_r, calculate_cci, calculate_obv
)

rsi  = calculate_rsi(data, window=14)    # DataFrame['RSI']
macd = calculate_macd(data)              # DataFrame['MACD', 'Signal', 'Histogram']
bb   = calculate_bollinger_bands(data)   # DataFrame['Upper', 'Middle', 'Lower', '%B']
```

## References

- [API Reference](references/api_reference.md)
- [Workflow Guide](references/workflow_guide.md)
- [Troubleshooting](references/troubleshooting.md)
