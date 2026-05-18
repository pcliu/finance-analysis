---
name: moomoo-trading
description: Moomoo OpenAPI toolkit for live US/HK/SG market data, historical K-lines, technical indicators, real or simulated account queries, positions, cash, order status, and carefully controlled order execution through local Moomoo OpenD. Use when Codex needs Moomoo account data, realtime quotes, Moomoo watchlists, trade review, or any Moomoo order workflow. Always use this skill instead of quantitative-trading when actual account data or order execution is involved.
---

# Moomoo Trading

Use this skill for Moomoo OpenD workflows. OpenD must be running locally at `127.0.0.1:11111`.

## Safety Rules

- Never place a real order without explicit user confirmation in the chat.
- Default to `trading_env='SIMULATE'`; use `trading_env='REAL'` only when the user asks for real account data or explicitly confirms real trading.
- For real orders, show ticker, direction, quantity, price, estimated cost, order type, and trading environment before execution.
- For US extended-hours orders, use limit orders with `fill_outside_rth=True`; do not use market orders in premarket or after-hours sessions.
- Log every order attempt to the task output directory.

## Quick Start

Use the project Python environment:

```bash
/usr/local/Caskroom/miniforge/base/envs/finance-analysis/bin/python
```

Import bundled scripts from the skill directory:

```python
import os
import sys

SKILL_DIR = os.path.abspath(".codex/skills/moomoo-trading")
sys.path.append(SKILL_DIR)

from scripts import (
    MoomooConnection,
    get_account_info,
    get_positions,
    get_realtime_quote,
    get_kline_data,
    place_order,
    get_order_list,
    make_serializable,
)
```

## Common Tasks

- Check OpenD: `MoomooConnection.check_health()`
- Query real US account: `get_account_info(trading_env='REAL', market='US')`
- Query real US positions: `get_positions(trading_env='REAL', market='US')`
- Query live quotes: `get_realtime_quote(['US.NVDA', 'US.TSM'])`
- Query orders: `get_order_list(trading_env='REAL')`

## Resources

- `scripts/`: reusable Moomoo connection, account, market data, indicator, and order helpers.
- `references/api_reference.md`: detailed API reference.
- `references/legacy-anthropic-skill.md`: full legacy instructions migrated from `.claude/skills/moomoo-trading/SKILL.md`; read when a workflow needs details not covered here.

## Output Convention

Save generated scripts and outputs under `workspace/YYYY-MM-DD/HHMMSS/`. Use `SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))` inside generated scripts so data and reports are written beside the script.
