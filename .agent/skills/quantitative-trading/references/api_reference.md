# API Reference

Complete API documentation for the quantitative-trading skill.

## Data Fetcher Module

### `scripts.data_fetcher.DataFetcher`

Core class for fetching market data from yfinance (global) or tushare (China/HK).

```python
from scripts.data_fetcher import DataFetcher

fetcher = DataFetcher(default_provider='auto', tushare_token=None)
```

#### Methods

##### `fetch_stock_data(ticker, start_date=None, end_date=None, period='1y', provider=None, market=None)`

Fetch historical stock data.

**Parameters:**
- `ticker` (str): Stock symbol (e.g., 'AAPL', '000001.SZ')
- `start_date` (str): Start date 'YYYY-MM-DD' (optional)
- `end_date` (str): End date 'YYYY-MM-DD' (optional)
- `period` (str): '1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'
- `provider` (str): 'yfinance', 'tushare', or 'auto'
- `market` (str): Market hint ('cn', 'hk', 'us')

**Returns:** `pd.DataFrame` with OHLCV and calculated fields (Returns, Volatility, etc.)

```python
data = fetcher.fetch_stock_data('AAPL', period='1y')
print(f"Current Price: ${data['Close'].iloc[-1]:.2f}")
```

##### `fetch_multiple_stocks(tickers, start_date=None, end_date=None, period='1y')`

Fetch data for multiple stocks.

```python
data_dict = fetcher.fetch_multiple_stocks(['AAPL', 'GOOGL', 'MSFT'], period='1y')
```

##### `get_company_info(ticker, provider=None, market=None)`

Get company fundamentals.

```python
info = fetcher.get_company_info('AAPL')
# Returns: Name, Sector, Industry, Market Cap, P/E Ratio, etc.
```

##### `calculate_correlation_matrix(tickers, period='1y')`

Calculate return correlation between stocks.

```python
corr = fetcher.calculate_correlation_matrix(['AAPL', 'GOOGL', 'MSFT'])
```

##### `fetch_realtime_quote(tickers, market=None)`

Unified real-time quote entry point for all markets. No Tushare permission needed.

**Parameters:**
- `tickers` (str or list): Single ticker or list (e.g., `'510150'`, `'AAPL'`, `['510150', 'AAPL']`)
- `market` (str): Market hint (`'cn'`, `'hk'`, `'us'`). Auto-detect if None.

**Returns:** `pd.DataFrame` with columns: 代码, 名称, 最新价, 涨跌额, 涨跌幅, 昨收, 今开, 最高, 最低, 成交量, 成交额

**Data Sources (auto-routed):**
- CN ETF → `ak.fund_etf_category_sina()` (AKShare/Sina Finance)
- CN Index → `ak.stock_zh_index_spot_sina()` (AKShare/Sina Finance)
- CN A-share → `ak.stock_zh_a_spot()` (AKShare/Sina Finance)
- US/Global → `yf.Ticker.fast_info` (yfinance, ~15-min delay)

```python
# Single ETF
quote = fetcher.fetch_realtime_quote('510150')
print(f"Latest: {quote['最新价'].iloc[0]}")

# US stock
quote_us = fetcher.fetch_realtime_quote('AAPL')

# Mixed: CN + US
quotes = fetcher.fetch_realtime_quote(['510150', 'AAPL', '512660'])
print(quotes)
```

---

## Indicators Module

### `scripts.indicators.TechnicalIndicators`

Technical analysis indicator calculations.

```python
from scripts.indicators import TechnicalIndicators

ti = TechnicalIndicators()
```

#### Methods

##### Moving Averages
```python
sma = ti.calculate_sma(data, window=20)      # Returns pd.Series
ema = ti.calculate_ema(data, window=20)      # Returns pd.Series
```

##### Momentum Indicators

> **⚠️ IMPORTANT:** These functions return `dict`, NOT DataFrame!

```python
# RSI - Returns pd.Series
rsi = ti.calculate_rsi(data, window=14)      # ⚠️ Parameter is 'window', NOT 'period'!

# MACD - Returns dict with 'MACD', 'Signal', 'Histogram' keys
macd = ti.calculate_macd(data)               # Returns dict, NOT DataFrame!
macd_line = macd['MACD'].iloc[-1]            # Access via dict keys
signal = macd['Signal'].iloc[-1]

# Stochastic - Returns dict with '%K', '%D' keys  
stoch = ti.calculate_stochastic(data)        # Returns dict
k_value = stoch['%K'].iloc[-1]
```

##### Volatility Indicators

> **⚠️ IMPORTANT:** Bollinger Bands returns `dict`, NOT DataFrame!

```python
# Bollinger Bands - Returns dict with 'Upper', 'Middle', 'Lower', 'Bandwidth', 'Percent_B' keys
bb = ti.calculate_bollinger_bands(data, window=20, num_std=2)
bb_upper = bb['Upper'].iloc[-1]              # Access via dict keys
bb_lower = bb['Lower'].iloc[-1]

# ATR - Returns pd.Series
atr = ti.calculate_atr(data, window=14)      # ⚠️ Parameter is 'window', NOT 'period'!
```

---

## Strategies Module

### `scripts.strategies.TradingStrategies`

Pre-built trading strategy signals.

```python
from scripts.strategies import TradingStrategies

ts = TradingStrategies()
```

#### Methods

##### `moving_average_crossover(data, fast_window=20, slow_window=50)`

Generate signals on MA crossovers.

```python
signals = ts.moving_average_crossover(data, fast_window=20, slow_window=50)
# Returns DataFrame with Buy_Signal, Sell_Signal columns
```

##### `rsi_mean_reversion(data, oversold=30, overbought=70)`

Generate signals on RSI extremes.

```python
signals = ts.rsi_mean_reversion(data, oversold=30, overbought=70)
```

---

## Backtester Module

### `scripts.backtester.Backtester`

Backtest trading strategies with historical data.

```python
from scripts.backtester import Backtester

bt = Backtester(initial_capital=100000)
results = bt.backtest(data, signals)
```

**Results include:**
- Total Return (%)
- Sharpe Ratio
- Max Drawdown (%)
- Win Rate (%)
- Number of Trades

---

## Risk Module

### `scripts.risk_manager.RiskManager`

Portfolio risk assessment tools.

```python
from scripts.risk_manager import RiskManager

rm = RiskManager()
```

#### Methods

##### `calculate_var(returns, method='historical', confidence_level=0.95)`
Value at Risk calculation.

##### `calculate_cvar(returns, var=None, confidence_level=0.95)`
Conditional Value at Risk (Expected Shortfall).

##### `calculate_drawdown_metrics(series, is_returns=True)`

> **⚠️ Note:** This replaces `calculate_max_drawdown`. Returns a dict!

```python
dd_metrics = rm.calculate_drawdown_metrics(returns, is_returns=True)
# Returns dict with keys:
# - 'max_drawdown'
# - 'avg_drawdown'
# - 'max_drawdown_duration'
# - 'current_drawdown'
max_dd = dd_metrics['max_drawdown']
```

##### `calculate_risk_adjusted_metrics(returns, benchmark_returns=None, risk_free_rate=0.02)`

> **⚠️ Note:** This replaces `calculate_sharpe_ratio`. Returns a dict!

```python
risk_metrics = rm.calculate_risk_adjusted_metrics(returns)
# Returns dict with keys:
# - 'sharpe_ratio'
# - 'sortino_ratio'
# - 'calmar_ratio'
# - 'volatility'
# - 'downside_volatility'
sharpe = risk_metrics['sharpe_ratio']
```

---

## Portfolio Module

### `scripts.portfolio_optimization.PortfolioAnalyzer`

Portfolio optimization and analysis.

```python
from scripts.portfolio_optimization import PortfolioAnalyzer

pa = PortfolioAnalyzer()
```

#### Methods

##### `optimize_portfolio(returns, method='sharpe')`
Find optimal portfolio weights.

##### `calculate_efficient_frontier(returns, num_portfolios=1000)`
Generate efficient frontier portfolios.
