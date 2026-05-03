---
name: quantitative-trading
description: >
  A 股和港股的历史行情获取与技术指标计算工具库（tushare 历史数据 + akshare 实时行情）。
  Use when users request:
  - A 股、港股、ETF、指数历史行情数据
  - A 股 / ETF / 指数实时行情（via AKShare/Sina Finance）
  - 技术指标计算（RSI、MACD、SMA、EMA、Bollinger Bands、ATR、Stochastic）
  - A 股标的相关性分析
  注意：美股和港股实时行情及交易请使用 moomoo-trading skill。
user-invocable: false
---

# Quantitative Trading Skill

A 股 / 港股历史行情获取和技术指标原语库，基于 tushare（历史数据）和 akshare（实时行情）。

## Environment Setup

```bash
ENV_PYTHON=/usr/local/Caskroom/miniforge/base/envs/finance-analysis/bin/python
ENV_PIP=/usr/local/Caskroom/miniforge/base/envs/finance-analysis/bin/pip

$ENV_PIP install tushare akshare pandas numpy matplotlib scipy
$ENV_PYTHON your_script.py
```

**Tushare Token：** 设置环境变量 `TUSHARE_TOKEN`（历史行情必须）。实时行情（`fetch_realtime_quote`）无需 Token。

## Quick Start

```python
import sys, os

SKILL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../.claude/skills/quantitative-trading'))
sys.path.append(SKILL_DIR)

from scripts import fetch_stock_data, calculate_rsi, calculate_atr
from scripts.utils import make_serializable

data = fetch_stock_data('510300.SH', period='6mo')  # 沪深300 ETF
results = {
    "price": data['Close'].iloc[-1],
    "rsi":   calculate_rsi(data)['RSI'].iloc[-1],
    "atr":   calculate_atr(data)['ATR'].iloc[-1],
}
print(make_serializable(results))
```

> **💾 JSON 序列化：** `numpy` 类型无法直接被 `json.dump` 序列化，必须先调用 `make_serializable`。

## Directory Structure

```
.claude/skills/quantitative-trading/
├── SKILL.md
├── references/
│   ├── api_reference.md
│   ├── workflow_guide.md
│   └── troubleshooting.md
└── scripts/
    ├── __init__.py       # Unified exports
    ├── utils.py          # make_serializable, etc.
    ├── data_fetcher.py   # tushare + akshare
    └── indicators.py
```

## Core Modules

### Data Fetching

```python
from scripts import fetch_stock_data, fetch_multiple_stocks, get_company_info, fetch_realtime_quote

# 历史数据（tushare，需要 TUSHARE_TOKEN）
data      = fetch_stock_data('510300.SH', period='1y')       # ETF
data      = fetch_stock_data('000001.SH', period='1y')       # 上证指数
data_dict = fetch_multiple_stocks(['510300.SH', '510500.SH'], period='1y')
info      = get_company_info('600519.SH')                    # 公司基本信息

# 实时行情（AKShare/Sina，无需 Token）
quote  = fetch_realtime_quote('510150')                      # CN ETF
quote  = fetch_realtime_quote('000001')                      # A 股
quotes = fetch_realtime_quote(['510150', '510300', '512660'])
# 返回列：代码, 名称, 最新价, 涨跌额, 涨跌幅, 昨收, 今开, 最高, 最低, 成交量, 成交额
```

### Technical Indicators

所有指标函数返回 `pd.DataFrame`，单值指标返回单列，多值指标返回多列。

```python
from scripts import (
    calculate_rsi, calculate_sma, calculate_ema, calculate_macd,
    calculate_bollinger_bands, calculate_atr, calculate_adx,
    calculate_stochastic, calculate_williams_r, calculate_cci, calculate_obv
)

rsi  = calculate_rsi(data, window=14)    # DataFrame['RSI']
macd = calculate_macd(data)              # DataFrame['MACD', 'Signal', 'Histogram']
bb   = calculate_bollinger_bands(data)   # DataFrame['Upper', 'Middle', 'Lower', '%B']
```

## References

- [API Reference](references/api_reference.md)
- [Workflow Guide](references/workflow_guide.md)
- [Troubleshooting](references/troubleshooting.md)
