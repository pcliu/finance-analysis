# Quantitative Trading Skills

量化交易技能包 - 使用 yfinance（全球市场）和 tushare（中国/香港市场）进行股票分析。

## 功能特性

- 📊 **数据获取**: 实时和历史股票数据
- 📈 **技术指标**: RSI、MACD、布林带、移动平均线等
- 🎯 **交易策略**: 均线交叉、RSI 均值回归、动量策略
- 💼 **组合分析**: 投资组合优化、有效前沿
- ⚠️ **风险管理**: VaR、CVaR、最大回撤、夏普比率
- 🔄 **回测框架**: 历史策略回测

## 快速开始

```python
import sys
sys.path.append('quantitative-trading-skills/quantitative-trading')

from scripts import fetch_stock_data, calculate_rsi

data = fetch_stock_data('AAPL', period='6mo')
rsi = calculate_rsi(data)
print(f"Price: ${data['Close'].iloc[-1]:.2f}, RSI: {rsi.iloc[-1]:.2f}")
```

## 中国/香港市场

设置环境变量 `TUSHARE_TOKEN`（从 [tushare.pro](https://tushare.pro/register) 获取）：

```bash
export TUSHARE_TOKEN="your-token-here"
```

```python
data = fetch_stock_data('000001', provider='tushare', market='cn')
```

## 目录结构

```
quantitative-trading/
├── SKILL.md              # 技能定义
├── scripts/              # 核心实现
├── workflows/            # 可复用工作流
├── references/           # 详细文档
├── examples/             # 使用示例
└── workspace/            # 输出目录
```

详细文档请查看 [quantitative-trading/SKILL.md](quantitative-trading/SKILL.md)

## License

MIT
