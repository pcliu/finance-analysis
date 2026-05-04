---
name: analyze-us-portfolio
description: >
  Daily portfolio adjustment workflow for US stock trading.
  Use when user requests:
  - 美股持仓调整 / 建仓分析 / 每日调仓
  - US stock/ETF portfolio rebalancing or position review
  - 技术面 + 舆情面综合分析（美股）
  - Entry analysis for new US stock positions
user-invocable: true
---

基于最新收盘数据和当前美股持仓结构，对各标的给出明确的建仓、持有或减仓建议。结合技术指标、市场舆情、财报日历和宏观环境（美联储利率、美元指数等）综合判断。对自选池中尚未建仓的标的评估即时建仓可行性。

## 数据源与工具
- **技术面**：使用 `quantitative-trading` 技能，通过 yfinance 获取 6 个月以上日线，计算 RSI、布林%B、MACD、成交量/20 日均量、ATR 等。
- **实时行情与账户**：使用 `moomoo-trading` 技能获取美股实时报价、账户持仓及可用资金。
- **舆情面**：使用 `economic-sentiment` 技能，通过 web search 抓取个股最新新闻、分析师评级变动、行业动态，进行情绪打分（bullish/neutral/bearish）。
- **宏观环境**：关注美联储利率决议、非农/CPI 数据、VIX 指数，通过 web search 获取最新动态。

## 核心原则 (Core Principles)

1. **数据驱动**：必须计算并引用 RSI、布林带 (%B)、MACD、ATR、成交量比等核心指标。
2. **自由推理**：不使用硬编码阈值。结合市场风格（risk-on/risk-off）、板块轮动、财报周期与实时舆情综合判断。
3. **全量覆盖**：对所有关注标的（当前持仓 + 自选池）逐一进行技术+舆情诊断。
   - 即使无交易建议，也须记录技术状态（RSI、布林带位置、趋势看法）。
   - 每个标的补充一句舆情结论（如"Bullish — Blackwell GPU demand exceeds supply"）。
4. **财报意识**：每次分析必须标注各标的的下一个财报日，财报前后风险敞口需特别说明。

## 分析维度 (Analysis Dimensions)

1. **持仓诊断**：识别高风险（超买/接近财报/技术背离）和低风险（健康整理/超卖支撑）品种。
2. **机会扫描**：评估自选池中未持仓标的的建仓性价比，给出入场评分。
3. **资金规划**：
   - 单笔风险 ≤ 总资金 1.5%；止损 = 当前价 − 2×ATR。
   - 单笔仓位 ≤ 总资金 35%。
   - 给出明确的建议股数、仓位金额、止损位、目标位和盈亏比。
4. **舆情联动**：技术与舆情信号是否同向；若背离需降低仓位或延后执行。
5. **宏观联动**：美联储政策、美元走势、VIX 是否对当前操作构成系统性风险。

## 流程要求 (Process Requirements)

1. **前置分析**：宏观环境扫描（Fed、VIX、板块轮动）→ 形成整体市场判断。
2. **复盘分析**：对前 5 个交易日的操作进行复盘，评估调整效果与风险变化。
3. **舆情扫描**：逐一搜索各标的最新新闻、分析师观点、财报预期。
4. **技术分析**：逐一计算各标的技术指标并打分。
5. **综合决策**：整合技术、舆情、财报风险、资金约束，输出可执行计划。

## 报告形式 (Reporting)

- **不使用预定义模板**，根据分析结果自由构建结构清晰、逻辑严密的 Markdown 报告（英文或中文均可）。
- 报告必须包含**"Market Scan / 全市场扫描"**章节，对未入选品种详尽点评。
- 报告单独列出**"Sentiment Snapshot / 舆情快照"**章节：各标的情绪结论与重要新闻标题。
- 报告包含**"Capital Allocation / 资金配置"**汇总表：各仓位金额、止损位、目标位、盈亏比。
- 输出位置：`workspace/YYYY-MM-DD/HHMMSS/us_portfolio_report.md`，原始指标/舆情 JSON 一并存档。
