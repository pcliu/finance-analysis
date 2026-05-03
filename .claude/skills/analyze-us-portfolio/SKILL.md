---
name: analyze-us-portfolio
description: >
  Moomoo 美股账户每日持仓调整分析工作流。
  Use when user requests:
  - 美股持仓调整 / 调仓分析 / 每日调仓
  - Moomoo 账户组合再平衡或持仓审视
  - 技术面 + 舆情面综合分析（美股）
  - 对 Moomoo「USStocks」关注列表观察池进行筛查
user-invocable: true
---

通过 Moomoo OpenD API 自动获取账户持仓、资金、订单状态和关注列表，结合技术指标和舆情分析，对各标的给出今日明确的继续持有或调整建议，并对「USStocks」关注分组中尚未纳入组合的品种评估即时建仓可行性。

## 账户数据获取（自动化）

使用 `moomoo-trading` skill 自动拉取以下数据，**无需用户手动输入**：

```python
from scripts import get_account_info, get_positions, get_order_list
import moomoo as ft

# 账户资金
account = get_account_info(trading_env='REAL')

# 当前持仓
positions = get_positions(trading_env='REAL')

# 今日订单状态（用于复盘）
orders = get_order_list(trading_env='REAL')

# 关注列表观察池（动态读取，与 moomoo App 同步）
ctx = ft.OpenQuoteContext(host='127.0.0.1', port=11111)
ret, watchlist = ctx.get_user_security(group_name='USStocks')
ctx.close()
# watchlist 包含列：code, name, stock_type
```

> **注意：** 交易密码从项目根目录 `.env.local` 的 `MOOMOO_TRADE_PASSWORD` 读取，连接参数同样来自该文件。

## 底层 Skill 分工

| 场景 | 使用 Skill |
|------|-----------|
| 美股历史 K 线 + 技术指标 | `moomoo-trading`（Moomoo OpenD） |
| 美股实时行情 | `moomoo-trading` → `get_realtime_quote` |
| 账户持仓 / 资金 / 订单 | `moomoo-trading` → `get_positions` / `get_account_info` |
| 宏观/行业新闻、舆情打分 | `economic-sentiment` |

## 观察池

- **来源**：Moomoo App 中名为 `USStocks` 的自定义关注分组，通过 API 动态读取，无需维护本地文件
- **更新方式**：直接在 moomoo App 中增减关注列表，下次分析自动同步
- **要求**：每次分析必须对观察池中所有品种（排除当前已持仓）逐一评估建仓可行性

## 输出目录

```
workspace/us/YYYY-MM-DD/HHMMSS/
├── us_adjustment_report.md    # 主报告
├── us_indicators_data.json    # 各标的技术指标原始数据
├── us_account_data.json       # 账户快照（持仓、资金）
└── us_sentiment_data.json     # 舆情抓取原始数据
```

> **脚本内路径写法：**
> ```python
> SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
> # 所有输出保存到 SCRIPT_DIR
> ```

## 核心原则

1. **数据驱动**：必须计算并引用 RSI、布林带 (%B)、MACD、成交量/20 日均量等核心指标。
2. **自由推理**：不使用硬编码阈值。结合美股市场环境、板块轮动与实时舆情综合判断。
3. **全量覆盖**：必须对所有关注标的（当前持仓 + USStocks 关注列表全部品种）逐一进行技术 + 舆情诊断。
4. **订单安全**：下单前必须打印完整订单摘要（标的、方向、数量、价格、预估金额），并在 chat 中获得用户明确确认后方可执行。

## 分析维度

1. **复盘分析**：结合今日订单状态，对前 5 个交易日的调仓情况进行复盘。
2. **持仓诊断**：识别高风险（超买/背离）和低风险（稳健/超卖）品种。
3. **机会扫描**：评估观察池品种的建仓性价比。
4. **资金规划**：给出明确的买卖数量和资金变动建议，标注预估成本（USD）。
5. **舆情联动**：说明舆情与技术信号是否同向；若背离需降低仓位或延后执行。

## 报告形式

- 不使用预定义模板，根据分析结果自由构建结构清晰的 Markdown 报告。
- 必须包含**"账户快照"**章节：总资产、持仓市值、可用资金（USD）。
- 必须包含**"全市场扫描"**章节，对未入选/未交易品种详尽点评并说明落选原因。
- 必须包含**"舆情快照"**章节：关键词情绪结论 + 重要新闻标题。
- 报告和 JSON 数据文件统一存入 `workspace/us/YYYY-MM-DD/HHMMSS/`。
