# Indicators API

**Use when:** you already have price data and just need fast indicator calculations.

## Quick Reference
- `calculate_sma(data, window=20)` / `calculate_ema(data, span=20)` – moving averages on any column (default `Close`).
- `calculate_rsi(data, window=14)` – momentum oscillator (0-100) for overbought/oversold checks.
- `calculate_macd(data, fast=12, slow=26, signal=9)` – returns MACD/Signal/Histogram columns.
- `calculate_bollinger_bands(data, window=20, num_std=2)` – upper/middle/lower bands plus bandwidth stats.
- `calculate_atr(data, window=14)` – volatility proxy for stop placement or sizing.
- `calculate_stochastic(data, k_window=14, d_window=3)` – %K/%D series for range trading.

```python
from api.indicators import calculate_rsi, calculate_bollinger_bands
from api.data_fetcher import fetch_stock_data

data = fetch_stock_data('TSLA', period='6mo')
rsi = calculate_rsi(data)
bb = calculate_bollinger_bands(data)
print({'rsi': rsi.iloc[-1], 'upper': bb['Upper'].iloc[-1]})
```

## Tips
- Drop NA rows before sharing indicator output to keep context lean (`indicator.dropna().tail(5)`).
- Tune windows to your timeframe: 5-10 (scalps), 14-20 (swing), 50+ (trend).
- Combine indicators for confirmation (e.g., RSI < 30 AND price near lower Bollinger band).
