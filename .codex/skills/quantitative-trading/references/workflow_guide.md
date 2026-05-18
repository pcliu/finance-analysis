# Workflow Guide

quantitative-trading skill 的常用模式。

## 基本分析流程

```python
import sys, os
SKILL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../.codex/skills/quantitative-trading'))
sys.path.append(SKILL_DIR)

from scripts import fetch_stock_data
from scripts.indicators import TechnicalIndicators

def analyze(ticker, period='6mo'):
    data = fetch_stock_data(ticker, period=period)
    if data is None or data.empty:
        return None

    ti = TechnicalIndicators()
    rsi    = ti.calculate_rsi(data)
    sma_20 = ti.calculate_sma(data, window=20)
    sma_60 = ti.calculate_sma(data, window=60)

    return {
        'ticker': ticker,
        'price':  float(data['Close'].iloc[-1]),
        'rsi':    float(rsi.iloc[-1]),
        'trend':  'Bullish' if sma_20.iloc[-1] > sma_60.iloc[-1] else 'Bearish',
    }

print(analyze('510300.SH'))   # 沪深300 ETF
print(analyze('600519.SH'))   # 贵州茅台
```

---

## 多标的批量扫描

```python
from scripts import fetch_stock_data
from scripts.indicators import TechnicalIndicators

tickers = ['510300.SH', '510500.SH', '159915.SZ', '512660.SH']
ti = TechnicalIndicators()
results = {}

for ticker in tickers:
    data = fetch_stock_data(ticker, period='6mo')
    if data is None:
        continue
    bb = ti.calculate_bollinger_bands(data)
    results[ticker] = {
        'price':    data['Close'].iloc[-1],
        'rsi':      ti.calculate_rsi(data).iloc[-1],
        'bb_pct_b': bb['Percent_B'].iloc[-1],
    }
```

---

## 相关性分析

```python
from scripts import fetch_multiple_stocks
import pandas as pd

data = fetch_multiple_stocks(['510300.SH', '510500.SH', '159915.SZ'], period='1y')
returns = {k: v['Close'].pct_change().dropna() for k, v in data.items()}
corr_matrix = pd.DataFrame(returns).corr()
```

---

## Context 效率建议

```python
# ✅ 只导入需要的函数
from scripts import fetch_stock_data, calculate_rsi

# ✅ 提前过滤，减少数据量
data = fetch_stock_data('510300.SH', period='6mo')
recent = data.tail(60)

# ✅ 返回摘要而非完整 DataFrame
summary = {'price': recent['Close'].iloc[-1], 'rsi': calculate_rsi(recent)['RSI'].iloc[-1]}
```
