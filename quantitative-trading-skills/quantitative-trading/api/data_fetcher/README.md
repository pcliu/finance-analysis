# Data Fetcher API

**Use when:** you need OHLCV data, company metadata, or quick stats inside the skill.  
The fetcher now auto-detects China & Hong Kong tickers and routes them through [tushare](https://github.com/waditu/tushare) for better accuracy; set `TUSHARE_TOKEN` in your environment to enable this data source.

## Key Calls
- `fetch_stock_data(ticker, period='1y', provider='auto', market=None)` – single ticker OHLCV with returns/vol columns.
- `fetch_multiple_stocks(tickers, period, provider)` – dict of DataFrames for batch lookups.
- `get_company_info(ticker, provider)` – sector, market cap, valuation ratios.
- `fetch_market_indices(indices, period, provider)` – major index snapshots (`^GSPC`, `^IXIC`, etc.).
- `calculate_correlation_matrix(tickers, period, provider)` – correlation of daily returns.
- `get_data_summary(ticker, period, provider)` – ready-made stats (total return, vol, drawdown, Sharpe).

```python
from api.data_fetcher import fetch_stock_data, get_data_summary

data = fetch_stock_data('AAPL', period='6mo')
summary = get_data_summary('AAPL', period='6mo')
print(summary['Current Price'], data['Close'].iloc[-1])

# Force tushare for a Shanghai listing
sh_data = fetch_stock_data('600519.SS', period='1y', provider='tushare', market='cn')
```

## Tips
- Prefer `fetch_multiple_stocks` instead of looping single-ticker calls.
- Slice/aggregate before returning (`recent = data.tail(60)`) to save context.
- Guard downstream code with `if data is None or data.empty`.
- Provide `market='cn'` or `market='hk'` plus `provider='tushare'` when the ticker format is ambiguous.

## Troubleshooting
- **Empty frame** → ticker unavailable or all-NaN period; adjust symbol/period/provider.
- **Network/timeout** → retry with shorter period or confirm connectivity (tushare has rate limits).
- **Tushare auth** → ensure `pip install tushare` and `TUSHARE_TOKEN` is exported before running.
