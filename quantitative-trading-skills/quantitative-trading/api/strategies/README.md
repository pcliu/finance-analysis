# Strategies API

**Use when:** you want ready-made trading signals without reimplementing indicator math.

## Available Signals
- `moving_average_crossover(data, fast_window=20, slow_window=50)` – adds fast/slow MAs plus `Buy_Signal`/`Sell_Signal` columns for golden/death crosses.
- `rsi_mean_reversion(data, oversold=30, overbought=70, window=14)` – appends RSI and boolean signal columns when RSI exits extreme zones.

```python
from api.strategies import moving_average_crossover
from api.data_fetcher import fetch_stock_data

data = fetch_stock_data('MSFT', period='1y')
signals = moving_average_crossover(data, fast_window=20, slow_window=50)
print(signals[['Buy_Signal', 'Sell_Signal']].tail())
```

## Tips
- Pair signals with risk tools (position sizing, stop levels) before placing trades.
- Filter signals with confirmation (volume spike, broader trend, etc.) to reduce noise.
- For lower latency, evaluate signals on sliced data (`signals.tail(90)`) and share only summaries back to the model.
