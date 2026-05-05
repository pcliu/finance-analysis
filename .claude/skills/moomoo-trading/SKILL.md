---
name: moomoo-trading
description: >
  Moomoo OpenAPI trading toolkit — real-time market data, technical indicators,
  account management, and order execution via Moomoo OpenD.
  Use when users request:
  - Real-time or live quotes for US, HK, or SG stocks via Moomoo
  - Historical K-line data from Moomoo (more accurate than yfinance for HK/SG)
  - Account positions, cash balance, P&L via Moomoo
  - Placing, modifying, or cancelling orders (paper or real trading)
  - Order status tracking and fill confirmation
  - Full trade execution workflow: signal → confirm → order → track
  ALWAYS use this skill (not quantitative-trading) when the task involves
  actual order execution or when Moomoo account data is needed.
user-invocable: false
---

# Moomoo Trading Skill

Real-time market data, technical analysis, and order execution via Moomoo OpenAPI.

> **⚠️ PREREQUISITE: OpenD must be running**
>
> This skill requires the Moomoo OpenD gateway to be running locally.
> Default: `127.0.0.1:11111`
> If OpenD is not running, all functions will raise `ConnectionError`.
> Check status: `MoomooConnection.check_health()`

> **🔴 ORDER SAFETY RULES — NON-NEGOTIABLE**
>
> 1. **NEVER place a real order without explicit user confirmation in the chat**
> 2. **Default mode is SIMULATE (paper trading)** — real trading requires `trading_env='REAL'`
> 3. **Always print the full order summary** (ticker, direction, qty, price, estimated cost) before execution
> 4. **Always ask for confirmation** before calling `place_order()` in real mode
> 5. Log every order attempt (success or failure) to the workspace JSON

> **🕐 交易时段默认规则**
>
> 除非用户明确指定交易时段，所有美股订单默认覆盖**盘前 + 盘中 + 盘后**：
> - 订单类型：`ft.OrderType.NORMAL`（限价单）
> - 必须设置：`fill_outside_rth=True`
> - **禁止**在盘前/盘后使用 `ft.OrderType.MARKET`（API 不支持）
>
> ```python
> ret, data = ctx.place_order(
>     price=price,
>     qty=qty,
>     code=ticker,
>     trd_side=ft.TrdSide.BUY,
>     order_type=ft.OrderType.NORMAL,
>     trd_env=ft.TrdEnv.REAL,
>     time_in_force=ft.TimeInForce.DAY,
>     fill_outside_rth=True,   # 默认开启，覆盖盘前+盘中+盘后
> )
> ```

> **📁 File Generation Rules**
>
> - ALL generated scripts and output files → `workspace/YYYY-MM-DD/HHMMSS/`
> - Follow same naming as `quantitative-trading`:
>   - Scripts: `moomoo_{task_name}.py`
>   - Reports: `moomoo_{task_name}_report.md`
>   - Data:    `moomoo_{task_name}_data.json`
> - Scripts MUST use `SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))` for output paths

---

## Environment Setup

```bash
ENV_PYTHON=/usr/local/Caskroom/miniforge/base/envs/finance-analysis/bin/python
ENV_PIP=/usr/local/Caskroom/miniforge/base/envs/finance-analysis/bin/pip

$ENV_PIP install moomoo-api
```

## Quick Start

```python
import sys, os
SKILL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../.claude/skills/moomoo-trading'))
sys.path.append(SKILL_DIR)

from scripts import (
    get_realtime_quote, get_kline_data, get_order_book,
    get_positions, get_account_info,
    place_order, cancel_order, get_order_list,
    calculate_rsi, calculate_macd, calculate_bollinger_bands,
    make_serializable
)
import moomoo as ft

# 1. Real-time quote
quote = get_realtime_quote(['US.NVDA', 'US.AMD', 'US.GOOG'])

# 2. Historical K-line → technical indicators
kline = get_kline_data('US.NVDA', ktype=ft.KLType.K_DAY, count=120)
rsi   = calculate_rsi(kline)
macd  = calculate_macd(kline)
bb    = calculate_bollinger_bands(kline)

# 3. Account info (simulate mode by default)
positions = get_positions()
account   = get_account_info()

# 4. Place order — simulate mode safe by default
result = place_order(
    ticker='US.NVDA',
    direction='BUY',
    qty=10,
    price=198.50,
    order_type='LIMIT',
    trading_env='SIMULATE',   # Change to 'REAL' only after explicit user confirmation
)
```

---

## Market Code Format

Moomoo uses `{MARKET}.{TICKER}` format:

| Market | Format    | Example              |
|--------|-----------|----------------------|
| US     | `US.XXX`  | `US.NVDA`, `US.AAPL` |
| HK     | `HK.XXXX` | `HK.00700`           |
| SG     | `SG.XXX`  | `SG.D05`, `SG.U11`   |

Use `to_moomoo_code(ticker, market)` for auto-conversion:
```python
from scripts.utils import to_moomoo_code
to_moomoo_code('NVDA', 'US')   # → 'US.NVDA'
to_moomoo_code('700',  'HK')   # → 'HK.00700'
```

---

## Core Modules

### Data Fetching (`scripts/data_fetcher.py`)

```python
# Real-time snapshot
get_realtime_quote(tickers)                   # List of moomoo codes
get_order_book(ticker, num=10)                # Bid/ask depth

# Historical K-lines (returns OHLCV DataFrame compatible with indicators)
get_kline_data(ticker, ktype=KLType.K_DAY, count=120, adjust_type=AdjustType.FORWARD)
```

### Technical Indicators (`scripts/indicators.py`)

Identical API to `quantitative-trading` — all functions accept OHLCV DataFrames
from either yfinance or Moomoo K-line data:

```python
calculate_rsi(data, window=14)         # → DataFrame['RSI']
calculate_macd(data)                   # → DataFrame['MACD','Signal','Histogram']
calculate_bollinger_bands(data)        # → DataFrame['Upper','Middle','Lower','%B']
calculate_sma(data, window=20)         # → DataFrame['SMA']
calculate_ema(data, window=20)         # → DataFrame['EMA']
calculate_atr(data, window=14)         # → DataFrame['ATR']
calculate_stochastic(data)             # → DataFrame['K','D']
```

### Account Management (`scripts/account.py`)

```python
get_account_info(trading_env='SIMULATE')   # Cash, total assets, buying power
get_positions(trading_env='SIMULATE')      # Current holdings with unrealized P&L
get_cash_info(trading_env='SIMULATE')      # Cash balance breakdown
```

### Order Management (`scripts/order_manager.py`)

```python
# Place order — ALWAYS prints summary, SIMULATE by default
place_order(ticker, direction, qty, price,
            order_type='LIMIT',
            trading_env='SIMULATE')

# Query orders
get_order_list(trading_env='SIMULATE', status_filter=None)
get_order_detail(order_id, trading_env='SIMULATE')

# Modify / cancel
modify_order(order_id, qty, price, trading_env='SIMULATE')
cancel_order(order_id, trading_env='SIMULATE')
cancel_all_orders(trading_env='SIMULATE')
```

---

## Integration with Other Skills

Both `quantitative-trading` and `moomoo-trading` produce DataFrames with the same
column names (`Open`, `High`, `Low`, `Close`, `Volume`), so indicator functions
from either skill work on data from either source.

**Typical workflow orchestrated by `analyze-portfolio`:**
```
1. quantitative-trading  →  historical analysis, backtest, RSI/MACD signals
2. economic-sentiment    →  news sentiment
3. moomoo-trading        →  real-time quote, live positions → execute order
```

## References

- [Full API Reference](references/api_reference.md)
