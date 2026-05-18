# Finance Analysis Codex Instructions

This repository stores Codex-native project skills in `.codex/skills/*/SKILL.md`.

When a user asks for finance analysis, portfolio review, Moomoo account data, market sentiment, A-share analysis, ETF screening, or trading-related workflows:

1. Inspect the relevant `.codex/skills/*/SKILL.md` before acting.
2. Select skills by their frontmatter `name` and `description`.
3. Load bundled `scripts/` and `references/` only when needed.
4. Treat `.codex/skills` as the canonical skill source for this branch.
5. Keep generated scripts and outputs under the workspace paths required by each skill.
6. Never place real orders without explicit user confirmation in the chat.

Skill map:

- `moomoo-trading`: Moomoo OpenD market data, account data, positions, orders, and execution safety.
- `quantitative-trading`: A-share, ETF, index, and HK market data plus technical indicators.
- `analyze-us-portfolio`: US portfolio review using Moomoo account data plus sentiment.
- `analyze-astock-portfolio`: A-share/ETF portfolio review using screenshots, ETF watchlist, indicators, and sentiment.
- `economic-sentiment`: Current market news, macro context, sentiment, and risk events.
