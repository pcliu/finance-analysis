# API Reference

A 股 / 港股行情获取与技术指标的完整 API 文档。

## Data Fetcher Module

### `scripts.data_fetcher.DataFetcher`

A 股、港股、ETF、指数历史与实时行情获取。数据源：tushare（历史）+ akshare（实时）。

```python
from scripts.data_fetcher import DataFetcher

fetcher = DataFetcher(tushare_token=None)  # Token 从 TUSHARE_TOKEN 环境变量读取
```

#### Methods

##### `fetch_stock_data(ticker, start_date=None, end_date=None, period='1y', market=None)`

获取历史 K 线数据（tushare）。

**Parameters:**
- `ticker` (str): 代码，如 `'510300.SH'`、`'000001.SH'`、`'600519'`、`'00700.HK'`
- `start_date` (str): 开始日期 `'YYYY-MM-DD'`（可选）
- `end_date` (str): 结束日期 `'YYYY-MM-DD'`（可选）
- `period` (str): `'1d'`、`'5d'`、`'1mo'`、`'3mo'`、`'6mo'`、`'1y'`、`'2y'`、`'5y'`、`'max'`
- `market` (str): 市场提示 `'cn'`、`'hk'`（可选，自动识别）

**Returns:** `pd.DataFrame` — OHLCV + Returns / Volatility / Cumulative_Returns

```python
data = fetcher.fetch_stock_data('510300.SH', period='1y')   # 沪深300 ETF
data = fetcher.fetch_stock_data('000001.SH', period='6mo')  # 上证指数
data = fetcher.fetch_stock_data('00700', market='hk')       # 腾讯（港股）
```

##### `fetch_multiple_stocks(tickers, start_date=None, end_date=None, period='1y', market=None)`

批量获取历史数据。

```python
data_dict = fetcher.fetch_multiple_stocks(['510300.SH', '510500.SH', '159915.SZ'], period='1y')
```

##### `get_company_info(ticker, market=None)`

获取公司/基金基本信息（tushare）。

```python
info = fetcher.get_company_info('600519.SH')  # 贵州茅台
# Returns: Name, Sector, Industry, Market, Market Cap, P/E Ratio, P/B Ratio, EPS, etc.
```

##### `calculate_correlation_matrix(tickers, period='1y', market=None)`

计算多标的收益率相关矩阵。

```python
corr = fetcher.calculate_correlation_matrix(['510300.SH', '510500.SH', '159915.SZ'])
```

##### `fetch_realtime_quote(tickers, market=None)`

A 股 / ETF / 指数实时行情（AKShare/Sina，无需 Token）。

**Parameters:**
- `tickers` (str or list): 单个或多个代码，如 `'510150'`、`['510150', '510300', '000001']`
- `market` (str): 市场提示 `'cn'`（可选）

**Returns:** `pd.DataFrame` — 代码, 名称, 最新价, 涨跌额, 涨跌幅, 昨收, 今开, 最高, 最低, 成交量, 成交额

**数据路由：**
- ETF → `ak.fund_etf_category_sina()`
- 指数 → `ak.stock_zh_index_spot_sina()`
- A 股 → `ak.stock_zh_a_spot()`

```python
quote  = fetcher.fetch_realtime_quote('510150')                        # 单个 ETF
quotes = fetcher.fetch_realtime_quote(['510150', '510300', '000001'])   # 批量
print(quotes[['代码', '名称', '最新价', '涨跌幅']])
```

---

## Indicators Module

### `scripts.indicators.TechnicalIndicators`

技术指标计算，所有方法通过 `__init__.py` 的 convenience 函数暴露。

```python
from scripts.indicators import TechnicalIndicators
ti = TechnicalIndicators()
```

#### Methods

##### Moving Averages
```python
sma = ti.calculate_sma(data, window=20)   # Returns pd.Series
ema = ti.calculate_ema(data, window=20)   # Returns pd.Series
```

##### Momentum Indicators

> **⚠️** `calculate_macd` 和 `calculate_stochastic` 返回 `dict`，不是 DataFrame。

```python
rsi  = ti.calculate_rsi(data, window=14)   # pd.Series
macd = ti.calculate_macd(data)             # dict: 'MACD', 'Signal', 'Histogram'
stoch = ti.calculate_stochastic(data)      # dict: '%K', '%D'
```

##### Volatility Indicators

> **⚠️** `calculate_bollinger_bands` 返回 `dict`，不是 DataFrame。

```python
bb  = ti.calculate_bollinger_bands(data, window=20, num_std=2)
# dict: 'Upper', 'Middle', 'Lower', 'Bandwidth', 'Percent_B'

atr = ti.calculate_atr(data, window=14)    # pd.Series
adx = ti.calculate_adx(data, window=14)    # pd.Series
```
