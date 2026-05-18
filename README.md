# Finance Analysis Skills

面向 AI Agent 的个人投研与交易辅助技能库。项目通过 Codex Skills 组织能力，由 Agent 按任务读取对应 `SKILL.md`，生成一次性分析脚本，拉取行情/账户/舆情数据，并把报告与原始数据沉淀到 `workspace/`。

本项目用于研究、复盘和辅助决策，不构成投资建议。

## 核心能力

- A 股 / ETF / 港股历史行情与实时行情获取
- 美股 / 港股 / 新加坡市场 Moomoo OpenD 行情、账户和订单查询
- RSI、MACD、SMA/EMA、布林带、ATR、Stochastic 等技术指标
- A 股账户每日调仓分析工作流
- Moomoo 美股账户每日调仓分析工作流
- 宏观、行业、个股新闻和简单舆情辅助分析
- 每次分析生成可追溯的脚本、JSON 数据和 Markdown 报告

## 目录结构

```text
finance-analysis/
├── README.md
├── AGENTS.md
├── .codex/
│   └── skills/
│       ├── analyze-astock-portfolio/   # A 股每日持仓调整工作流
│       ├── analyze-us-portfolio/       # Moomoo 美股账户调仓工作流
│       ├── economic-sentiment/         # 新闻/舆情信息采集
│       ├── moomoo-trading/             # Moomoo OpenD 行情、账户、下单工具
│       └── quantitative-trading/       # A 股/港股行情与技术指标原语
├── workspace/
│   ├── ETFs.csv                        # A 股 ETF 观察池
│   ├── YYYY-MM-DD/HHMMSS/              # A 股/专题分析历史产物
│   └── us/YYYY-MM-DD/HHMMSS/           # 美股账户分析历史产物
├── test_akshare.py
└── test_economic_sentiment.py
```

`.codex/skills` 是当前技能主目录。`AGENTS.md` 是 Codex 进入项目时的项目级指令。`workspace/` 是运行产物目录，里面的脚本和报告是一次分析的快照，便于复盘当时使用的数据、指标和结论。

## 技能分工

| 技能 | 用途 | 主要数据源 |
| --- | --- | --- |
| `quantitative-trading` | A 股 / 港股历史行情、A 股实时行情、技术指标计算 | Tushare、AkShare |
| `moomoo-trading` | Moomoo 行情、K 线、账户、订单、下单工具 | Moomoo OpenD |
| `economic-sentiment` | 市场新闻、热点、宏观事件、简单情绪判断 | AkShare、Web 搜索 |
| `analyze-astock-portfolio` | A 股账户每日持仓诊断与调仓建议 | 用户截图、`workspace/ETFs.csv`、行情和舆情技能 |
| `analyze-us-portfolio` | Moomoo 美股账户自动调仓分析 | Moomoo 账户、`USStocks` 关注列表、行情和舆情技能 |

## 环境准备

推荐使用独立 Conda 环境：

```bash
conda create -n finance-analysis python=3.10 -y
conda activate finance-analysis
pip install pandas numpy matplotlib scipy tushare akshare moomoo-api python-dotenv
```

A 股 / 港股历史行情需要 Tushare Token：

```bash
export TUSHARE_TOKEN="your-token-here"
```

也可以放在本地 `.env.local`，但不要提交到 Git。

Moomoo 相关能力需要本机启动 OpenD，默认连接：

```text
host: 127.0.0.1
port: 11111
```

`.env.local` 可包含：

```bash
TUSHARE_TOKEN="your-token-here"
MOOMOO_HOST="127.0.0.1"
MOOMOO_PORT="11111"
MOOMOO_TRADE_PASSWORD="your-trade-password"
```

## 使用方式

这个仓库主要由 AI Agent 调用，不是命令行应用。典型请求示例：

```text
帮我分析一下 510150 消费 ETF 的技术指标
```

```text
根据我的 A 股持仓截图做一次今日调仓分析
```

```text
帮我做一次 Moomoo 美股账户调仓分析
```

```text
查询 US.NVDA、US.AMD、US.GOOG 的实时行情和 RSI/MACD
```

Agent 会按任务选择对应技能，生成脚本到 `workspace/YYYY-MM-DD/HHMMSS/` 或 `workspace/us/YYYY-MM-DD/HHMMSS/`，运行后保存数据与报告。

## 工作流说明

### A 股账户分析

`analyze-astock-portfolio` 需要用户提供账户截图，因为当前没有 A 股券商账户 API。分析时会读取：

- 截图中的持仓、成本、市值、盈亏、总资产和可用资金
- `workspace/ETFs.csv` 中的 ETF 观察池
- Tushare / AkShare 的历史行情、实时行情和技术指标
- AkShare / Web 搜索得到的宏观与行业舆情

输出目录：

```text
workspace/YYYY-MM-DD/HHMMSS/
```

或技能要求的新格式：

```text
workspace/astock/YYYY-MM-DD/HHMMSS/
```

### 美股账户分析

`analyze-us-portfolio` 通过 Moomoo OpenD 自动获取：

- 账户资产、现金、持仓
- 今日订单记录
- Moomoo App 中 `USStocks` 分组的关注列表
- 实时行情和历史 K 线

输出目录：

```text
workspace/us/YYYY-MM-DD/HHMMSS/
```

常见文件：

```text
us_adjustment_report.md
us_account_data.json
us_indicators_data.json
us_sentiment_data.json
order_results.json
```

## 交易安全规则

`moomoo-trading` 支持订单相关操作，但默认应优先用于查询和模拟。真实交易必须遵守：

1. 下单前先展示完整订单摘要：标的、方向、数量、价格、订单类型、预估金额。
2. 必须在聊天中获得用户明确确认后，才能调用真实交易接口。
3. 默认使用 `trading_env='SIMULATE'`；真实交易才使用 `trading_env='REAL'`。
4. 每次订单尝试都应保存到 `workspace/` 的 JSON 文件，便于审计和复盘。

## 数据与密钥

- `.env.local` 已被 `.gitignore` 忽略，用于保存本地密钥和连接参数。
- 不要把 Tushare Token、Moomoo 交易密码、账户快照或订单明细提交到公共仓库。
- `workspace/` 中可能包含账户资产、订单结果和持仓信息，提交前请确认是否适合入库。

## 快速自检

语法检查：

```bash
python3 -m compileall -q .codex/skills test_akshare.py test_economic_sentiment.py
```

测试 AkShare 新闻接口：

```bash
python test_economic_sentiment.py
```

Moomoo 能力依赖 OpenD，运行前请确认 OpenD 已启动并登录。

## 详细文档

- [A 股调仓工作流](.codex/skills/analyze-astock-portfolio/SKILL.md)
- [美股调仓工作流](.codex/skills/analyze-us-portfolio/SKILL.md)
- [Moomoo 交易工具](.codex/skills/moomoo-trading/SKILL.md)
- [Moomoo API 参考](.codex/skills/moomoo-trading/references/api_reference.md)
- [A 股/港股量化工具](.codex/skills/quantitative-trading/SKILL.md)
- [量化工具 API 参考](.codex/skills/quantitative-trading/references/api_reference.md)
- [新闻舆情工具](.codex/skills/economic-sentiment/SKILL.md)

## License

MIT
