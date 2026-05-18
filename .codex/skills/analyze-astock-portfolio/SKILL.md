---
name: analyze-astock-portfolio
description: Daily A-share and ETF portfolio adjustment workflow for screenshot-based holdings, ETF watchlist scanning, technical indicators, sentiment review, risk diagnosis, and next-trading-day buy/sell/hold recommendations. Use when the user asks for A-share portfolio review, ETF rebalancing, A-stock daily adjustment analysis, holdings screenshot interpretation, or technical plus sentiment analysis for Chinese market positions.
---

# Analyze A-Stock Portfolio

Use this workflow to produce a daily A-share or ETF portfolio review from user-provided account screenshots, ETF watchlists, technical indicators, and sentiment.

## Required Skill Flow

1. Read the user's screenshot for holdings, position sizes, cost, market value, total assets, and available/redeemable funds.
2. Use `quantitative-trading` for A-share, ETF, and index data plus indicators.
3. Use `economic-sentiment` for macro, policy, industry, and market news context.
4. Review all current holdings and every symbol in the root `ETFs.csv` watchlist.

## Data Rules

- A-share account data cannot be fetched automatically. If the screenshot omits required fields, ask for the missing fields.
- Do not invent holdings, costs, quantities, or asset values.
- Calculate and cite RSI, Bollinger `%B`, MACD, volume versus 20-day average, and trend context where data allows.
- Use flexible judgment; do not hard-code simple thresholds such as "RSI > 80 means sell" without market context.
- Treat available deployable capital as total assets minus position market value when money-market funds are redeemable.
- Keep any single new allocation within CNY 10,000 unless the user explicitly changes this rule.

## Report Requirements

- Include a full-market scan section explaining why non-selected watchlist ETFs were excluded.
- Include a sentiment snapshot with important news titles and directional conclusion.
- Give concrete quantities and cash impact for any suggested trade.
- Do not execute trades; this workflow is analysis only.

## Output Convention

Save outputs under `workspace/astock/YYYY-MM-DD/HHMMSS/`:

- `astock_adjustment_report.md`
- `astock_indicators_data.json`
- `astock_sentiment_data.json`

Use `SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))` inside generated scripts.

## Resources

- `references/legacy-anthropic-skill.md`: full migrated legacy workflow; read if detailed report requirements or edge cases are needed.
