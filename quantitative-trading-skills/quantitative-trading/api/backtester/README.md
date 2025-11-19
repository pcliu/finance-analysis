# Backtester API

**Use when:** you already generated signals (e.g., from `api.strategies`) and want a quick performance readout.

## Main Call
- `backtest_strategy(data, strategy_name, strategy_params=None, initial_capital=100_000)` – runs the chosen strategy on historical OHLCV data and returns:
  - `signals`: enriched DataFrame with indicator columns
  - `trades`: executed orders
  - `performance`: total/annualized return, Sharpe, Sortino, max drawdown, win rate, etc.

```python
from api.backtester import backtest_strategy
from api.data_fetcher import fetch_stock_data

data = fetch_stock_data('AAPL', period='2y')
results = backtest_strategy(
    data=data,
    strategy_name='moving_average_crossover',
    strategy_params={'fast_window': 20, 'slow_window': 50},
    initial_capital=50_000,
)
print(results['performance']['total_return'], results['performance']['sharpe_ratio'])
```

## Tips
- Supported strategy names match helpers in `api.strategies` (e.g., `moving_average_crossover`, `rsi_mean_reversion`).
- Input data must include `Close`, `High`, `Low`, and `Volume` columns produced by the fetcher.
- Backtests assume simple long/short flipping; for portfolio or multi-asset tests, run multiple assets separately and aggregate results yourself.
