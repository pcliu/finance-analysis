# Portfolio API

**Use when:** you need multi-asset data prep, optimization, or metrics without redoing math.

## Key Helpers
- `create_portfolio_data(tickers, period='1y')` – fetches prices, aligns dates, and returns a dict with `prices`, `returns`, `tickers`, and equal weights.
- `calculate_portfolio_metrics(returns, weights=None)` – annualized return/vol, Sharpe, Sortino, max drawdown, VaR/CVaR, etc.
- `optimize_portfolio(returns, optimization_method='sharpe', target_return=None)` – SLSQP-based optimizer (modes: `sharpe`, `min_volatility`, `target_return`, `risk_parity`).

```python
from api.portfolio import create_portfolio_data, calculate_portfolio_metrics, optimize_portfolio

portfolio = create_portfolio_data(['AAPL', 'GOOGL', 'MSFT'], period='2y')
metrics = calculate_portfolio_metrics(portfolio['returns'])
optimal = optimize_portfolio(portfolio['returns'], optimization_method='sharpe')
print(metrics['sharpe_ratio'], optimal['weights'])
```

## Tips
- Always drop NA rows after fetching (`returns = portfolio['returns'].dropna()`) before passing to optimizers.
- Supply explicit weights to `calculate_portfolio_metrics` if you are not using the equal-weight default.
- For target-return optimization, set `target_return` in daily units (same frequency as `returns`).
