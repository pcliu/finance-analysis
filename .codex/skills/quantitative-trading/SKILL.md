---
name: quantitative-trading
description: A-share and Hong Kong market quantitative analysis toolkit for historical prices, realtime A-share/ETF/index quotes, technical indicators, ETF screening, correlation analysis, and trading-signal research using Tushare and AKShare. Use for A-share, ETF, index, and HK historical analysis, RSI/MACD/SMA/EMA/Bollinger/ATR/Stochastic calculations, and non-account technical research. Use moomoo-trading instead for US realtime quotes, Moomoo account data, or order execution.
---

# Quantitative Trading

Use this skill for A-share, ETF, index, and HK historical market analysis. It provides bundled scripts for Tushare, AKShare, and technical indicators.

## Environment

Use the project Python environment:

```bash
/usr/local/Caskroom/miniforge/base/envs/finance-analysis/bin/python
```

Historical Tushare data requires `TUSHARE_TOKEN`. AKShare realtime quote helpers do not require the token.

## Quick Start

```python
import os
import sys

SKILL_DIR = os.path.abspath(".codex/skills/quantitative-trading")
sys.path.append(SKILL_DIR)

from scripts import (
    fetch_stock_data,
    fetch_multiple_stocks,
    fetch_realtime_quote,
    calculate_rsi,
    calculate_macd,
    calculate_bollinger_bands,
    calculate_atr,
    make_serializable,
)

data = fetch_stock_data("510300.SH", period="6mo")
rsi = calculate_rsi(data)["RSI"].iloc[-1]
```

Before `json.dump`, pass data through `make_serializable` to handle NumPy and pandas types.

## Common Tasks

- Fetch historical A-share, ETF, or index data with `fetch_stock_data`.
- Fetch multiple instruments with `fetch_multiple_stocks`.
- Fetch realtime A-share or ETF quotes with `fetch_realtime_quote`.
- Calculate RSI, MACD, Bollinger Bands, SMA, EMA, ATR, and Stochastic indicators.
- Use this skill as a data layer for `analyze-astock-portfolio`.

## Resources

- `scripts/`: reusable data fetchers, indicator helpers, and serialization utilities.
- `references/api_reference.md`: function-level API details.
- `references/workflow_guide.md`: recommended analysis workflow.
- `references/troubleshooting.md`: common dependency and data-source issues.
- `references/legacy-anthropic-skill.md`: full legacy instructions migrated from `.claude/skills/quantitative-trading/SKILL.md`.

## Output Convention

Save generated scripts and outputs under `workspace/YYYY-MM-DD/HHMMSS/`. Use `SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))` inside generated scripts so outputs stay with the script.
