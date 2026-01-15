# [标的代码] 策略信号分析报告
**分析日期**: YYYY-MM-DD (数据截止 YYYY-MM-DD)

## 1. 综合信号建议
*   **当前价格**: [Price]
*   **综合评级**: **[BUY / SELL / HOLD]** (Consensus Score: [Score])
    *   *解读*: [如：综合得分为 0.8，多数策略发出买入信号，建议积极关注。]

## 2. 策略详细表现
| 策略名称                      | 信号状态        | 信号日期 | 描述                       |
| :---------------------------- | :-------------- | :------- | :------------------------- |
| **均线交叉 (MA Crossover)**   | [BUY/SELL/NONE] | [Date]   | [如：短期均线上穿长期均线] |
| **MACD 策略**                 | [BUY/SELL/NONE] | [Date]   | [如：DIF 上穿 DEA]         |
| **RSI 均值回归**              | [BUY/SELL/NONE] | [Date]   | [如：RSI 超卖反弹]         |
| **布林带突破**                | [BUY/SELL/NONE] | [Date]   | [如：触及下轨反弹]         |
| **动量突破**                  | [BUY/SELL/NONE] | [Date]   | [如：放量突破]             |
| **随机指标 (Stochastic)**     | [BUY/SELL/NONE] | [Date]   | [如：K线下穿D线]           |
| **均值回归 (Mean Reversion)** | [BUY/SELL/NONE] | [Date]   | [如：价格偏离均线过大回归] |

## 3. 核心指标概览
*   **RSI (14)**: [Value]
*   **MACD**: [Value] (Signal: [Value])
*   **市场趋势**: [如：多头排列 / 震荡 / 空头排列]

## 4. 近期信号追踪
[列出最近 5 个交易日内触发的重要信号，用于辅助判断时机]

*   **YYYY-MM-DD**: [策略名] 发出 [信号]
*   ...

## 5. 📊 生成文件
*   **完整报告**: `workspace/.../analysis_report.md`
*   **信号数据**: `workspace/.../analysis_result.json`
*   **分析脚本**: `workspace/.../analyze_[ticker].py`
