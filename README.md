# Quantitative Trading Skills

量化交易智能体技能包 - 基于 Claude Code Skills 规范实现，通过 AI 智能体进行股票分析与投资建议。

## 项目简介

本项目是一个 **Claude Code Skills** 规范的量化交易技能包，设计用于通过 AI 智能体（如 Claude/Gemini）进行交互式量化分析。核心功能包括：

- 📊 **数据获取**: 支持全球市场 (yfinance) 和中国/香港市场 (tushare)
- 📈 **技术指标**: RSI、MACD、布林带、移动平均线、ATR 等
- 🎯 **交易策略**: 均线交叉、RSI 均值回归、动量策略
- 💼 **组合分析**: 投资组合优化、有效前沿、相关性分析
- ⚠️ **风险管理**: VaR、CVaR、最大回撤、夏普比率
- 🔄 **回测框架**: 历史策略回测

## 环境部署

### 1. 创建 Conda 环境

```bash
# 创建名为 finance-analysis 的 Python 环境
conda create -n finance-analysis python=3.10 -y

# 激活环境
conda activate finance-analysis
```

### 2. 安装依赖

```bash
# 安装核心依赖包
pip install yfinance tushare pandas numpy matplotlib scipy
```

### 3. 配置 Tushare（中国/香港市场）

如需分析中国/香港市场数据，请先在 [tushare.pro](https://tushare.pro/register) 注册并获取 Token，然后设置环境变量：

```bash
export TUSHARE_TOKEN="your-token-here"
```

## 快速开始

本项目设计为通过 AI 智能体进行交互。以下是一些示例问题：

### 📊 技术分析类

```
帮我分析一下 510150 消费ETF 的技术指标
```

```
请用 RSI 和 MACD 分析贵州茅台（600519）的买卖信号
```

### 💼 投资组合类

```
我目前持有以下 ETF，请帮我优化投资组合：
- 510150 消费ETF: 10000元
- 159915 创业板ETF: 8000元  
- 512660 军工ETF: 5000元
```

```
请分析我的持仓，给出具体的调仓建议，增量资金不超过 10000 元
```

### ⚠️ 风险评估类

```
请评估我当前投资组合的风险，计算 VaR 和最大回撤
```

### 🔄 策略回测类

```
帮我回测一下均线交叉策略在 510300 沪深300ETF 上的表现
```

### 🆚 对比分析类

```
对比分析 510150、159915、512660 这三只 ETF 的相关性和收益风险特征
```

## 目录结构

```
quantitative-trading-skills/
├── README.md                     # 本文件
└── quantitative-trading/         # Skills 核心目录
    ├── SKILL.md                  # 技能定义文件（Agent 入口）
    ├── scripts/                  # 核心 Python 模块
    │   ├── __init__.py           # 统一导出接口
    │   ├── data_fetcher.py       # 数据获取模块
    │   ├── indicators.py         # 技术指标计算
    │   ├── strategies.py         # 交易策略实现
    │   ├── backtester.py         # 回测框架
    │   ├── portfolio_analyzer.py # 投资组合分析
    │   └── risk_manager.py       # 风险管理工具
    ├── references/               # 参考文档
    │   ├── api_reference.md      # API 参考手册
    │   ├── workflow_guide.md     # 工作流指南
    │   ├── troubleshooting.md    # 问题排查
    │   └── report_templates/     # 分析报告模板
    ├── examples/                 # 示例代码（只读参考）
    └── workspace/                # 输出目录（自动生成）
```

## 工作原理

1. **技能发现**: AI 智能体通过读取 `quantitative-trading/SKILL.md` 了解可用能力
2. **任务理解**: 根据用户问题，智能体选择合适的分析模块
3. **脚本生成**: 智能体编写分析脚本并保存到 `workspace/YYYY-MM-DD/HHMMSS/`
4. **执行分析**: 运行脚本获取数据、计算指标、生成图表
5. **报告生成**: 基于预设模板生成结构化分析报告

## 核心模块说明

| 模块                    | 功能                                       |
| ----------------------- | ------------------------------------------ |
| `data_fetcher.py`       | 获取股票/ETF 历史数据、实时价格、公司信息  |
| `indicators.py`         | 计算 RSI、MACD、SMA、EMA、布林带等技术指标 |
| `strategies.py`         | 实现均线交叉、RSI 均值回归等交易策略       |
| `backtester.py`         | 策略历史回测与绩效分析                     |
| `portfolio_analyzer.py` | 投资组合优化、有效前沿计算                 |
| `risk_manager.py`       | VaR、CVaR、最大回撤、夏普比率等风险指标    |

## 分析报告类型

根据不同分析任务，智能体会自动选择相应的报告模板：

- **技术分析报告** - 单只股票/ETF 的技术指标分析
- **持仓调整报告** - 现有持仓的调仓建议
- **策略信号报告** - 交易策略信号分析
- **组合分析报告** - 投资组合优化建议
- **风险评估报告** - 风险指标评估与预警

## 注意事项

> ⚠️ **投资风险提示**
> 
> 本工具仅供学习和研究使用，分析结果不构成投资建议。投资有风险，入市需谨慎。

## 详细文档

- [SKILL.md](quantitative-trading/SKILL.md) - 技能定义与 Agent 使用指南
- [API 参考](quantitative-trading/references/api_reference.md) - 完整函数文档
- [工作流指南](quantitative-trading/references/workflow_guide.md) - 高级用法
- [报告模板](quantitative-trading/references/report_templates/README.md) - 报告格式说明
- [问题排查](quantitative-trading/references/troubleshooting.md) - 常见问题解决

## License

MIT
