---
name: analyze-us-portfolio
description: Daily Moomoo US portfolio adjustment workflow for real account positions, cash, recent orders, USStocks watchlist screening, technical indicators, news sentiment, risk review, and explicit hold/buy/sell recommendations. Use when the user asks for US stock portfolio review, Moomoo US account rebalancing, daily adjustment analysis, watchlist screening, or technical plus sentiment analysis for US holdings.
---

# Analyze US Portfolio

Use this workflow to produce a daily US portfolio review from Moomoo account data, technical signals, and market sentiment.

## Required Skill Flow

1. Use `moomoo-trading` for account info, positions, order status, live quotes, K-lines, indicators, and the Moomoo `USStocks` watchlist.
2. Use `economic-sentiment` for macro, industry, and ticker-specific news context.
3. Produce a clear Markdown report with concrete hold, buy, sell, or wait recommendations.

## Account Data

Read account data automatically through Moomoo OpenD; do not ask the user to type holdings manually unless OpenD is unavailable.

```python
from scripts import get_account_info, get_positions, get_order_list

account = get_account_info(trading_env="REAL", market="US")
positions = get_positions(trading_env="REAL", market="US")
orders = get_order_list(trading_env="REAL")
```

For watchlist scanning, read the Moomoo App group named `USStocks` through the quote API.

## Portfolio Rules

- Evaluate current holdings and every watchlist symbol not already held.
- Calculate and cite RSI, Bollinger `%B`, MACD, volume versus 20-day average, and trend context where data allows.
- Treat investable amount as `total_assets - market_val` because funds may be redeemable; do not equate cash with buying capacity.
- Keep recommendations explicit and executable, but do not place orders without separate user confirmation.
- Discuss sentiment and technical alignment; reduce confidence when they diverge.

## Output Convention

Save outputs under `workspace/us/YYYY-MM-DD/HHMMSS/`:

- `us_adjustment_report.md`
- `us_indicators_data.json`
- `us_account_data.json`
- `us_sentiment_data.json`

Use `SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))` inside generated scripts.

## Resources

- `references/legacy-anthropic-skill.md`: full migrated legacy workflow; read if detailed report requirements or edge cases are needed.
