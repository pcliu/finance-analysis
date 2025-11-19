# Risk API

**Use when:** you need quick loss estimates or drawdown stats on return streams.

## Core Calls
- `calculate_var(returns, method='historical', confidence_level=0.95)` – tail loss at a confidence level (historical/parametric supported).
- `calculate_cvar(returns, confidence_level=0.95)` – average loss beyond VaR for heavier-tail view.
- `calculate_max_drawdown(returns)` – dict with drawdown depth, average depth, durations, and recovery timing.

```python
from api.data_fetcher import fetch_stock_data
from api.risk import calculate_var, calculate_cvar, calculate_max_drawdown

data = fetch_stock_data('QQQ', period='1y')
returns = data['Returns'].dropna()
drawdown = calculate_max_drawdown(returns)
print({
    'var95': calculate_var(returns, confidence_level=0.95),
    'cvar95': calculate_cvar(returns, confidence_level=0.95),
    'max_dd': drawdown['max_drawdown'],
    'duration': drawdown['max_drawdown_duration'],
})
```

## Tips
- Convert price series to returns before passing to these helpers (`data['Close'].pct_change().dropna()`).
- Use the same confidence level for VaR and CVaR to keep reports comparable.
- Report drawdown depth and duration together to give better risk context.
