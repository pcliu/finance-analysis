---
name: economic-sentiment
description: Finance and macro news monitoring skill for realtime market intelligence, economic sentiment, hot topics, policy updates, industry news, risk events, geopolitical context, and social sentiment that supports portfolio and quantitative trading decisions. Use when Codex needs current market news, sentiment analysis, topical explanations for price moves, macro policy context, or risk-event monitoring.
---

# Economic Sentiment

Use this skill to gather timely news and sentiment context that complements technical and portfolio analysis.

## Scope

- Market news and ticker or sector catalysts.
- Macro policy, central bank, inflation, employment, and growth updates.
- Industry-specific news and hot topics.
- Risk events, geopolitical shocks, and regulatory changes.
- Sentiment summaries for portfolio decisions.

This skill is for information gathering and concise synthesis, not deep fundamental research or backtesting.

## Data Sources

Prefer current web search when the user asks about latest, today, recent, or market-moving events. Use AkShare when available for Chinese financial news:

```python
import akshare as ak

stock_news = ak.stock_news_em(symbol="芯片")
economic_news = ak.news_economic_baidu()
cctv_news = ak.news_cctv()
```

When browsing, cite sources and compare dates because news and market context are time-sensitive.

## Output Guidance

- Summarize the key catalysts and whether sentiment is positive, negative, or mixed.
- Separate confirmed facts from inference.
- Call out whether sentiment aligns or conflicts with technical signals when used with portfolio skills.
- Keep raw headlines or source snippets in the task output data when generating a report.

## Resources

- `references/examples.md`: migrated examples for common news and sentiment workflows.
- `references/legacy-anthropic-skill.md`: full migrated legacy instructions; read if a workflow needs more source-specific detail.
