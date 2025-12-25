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
sma = ti.calculate_sma(data, window=20)      # Simple Moving Average
ema = ti.calculate_ema(data, window=20)      # Exponential Moving Average
```

##### Momentum Indicators
```python
rsi = ti.calculate_rsi(data, period=14)      # Relative Strength Index (0-100)
macd = ti.calculate_macd(data)               # MACD, Signal, Histogram
stoch = ti.calculate_stochastic(data)        # %K, %D
```

##### Volatility Indicators
```python
bb = ti.calculate_bollinger_bands(data, window=20, num_std=2)  # Upper, Middle, Lower, Width
atr = ti.calculate_atr(data, period=14)      # Average True Range
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

##### `calculate_var(returns, confidence_level=0.95)`
Value at Risk calculation.

##### `calculate_cvar(returns, confidence_level=0.95)`
Conditional Value at Risk (Expected Shortfall).

##### `calculate_max_drawdown(data)`
Maximum drawdown from peak.

##### `calculate_sharpe_ratio(returns, risk_free_rate=0.02)`
Risk-adjusted return metric.

---

## Portfolio Module

### `scripts.portfolio_analyzer.PortfolioAnalyzer`

Portfolio optimization and analysis.

```python
from scripts.portfolio_analyzer import PortfolioAnalyzer

pa = PortfolioAnalyzer()
```

#### Methods

##### `optimize_portfolio(returns, method='sharpe')`
Find optimal portfolio weights.

##### `calculate_efficient_frontier(returns, num_portfolios=1000)`
Generate efficient frontier portfolios.
