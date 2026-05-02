# Troubleshooting Guide

Common issues and solutions for the quantitative-trading skill.

## Import Errors

### `ImportError: No module named 'yfinance'`

**Solution:** Use the `finance-analysis` environment interpreter:

```bash
ENV_PYTHON=/opt/homebrew/Caskroom/miniforge/base/envs/finance-analysis/bin/python
ENV_PIP=/opt/homebrew/Caskroom/miniforge/base/envs/finance-analysis/bin/pip

$ENV_PIP install yfinance tushare pandas numpy matplotlib scipy
$ENV_PYTHON -c "import yfinance; print('OK')"
```

---

## Data Fetching Issues

### `HTTP Error 404` or `ConnectionError`

- Check internet connection
- Verify ticker symbol is correct
- Some tickers may not be available on Yahoo Finance

```python
import yfinance as yf
ticker = yf.Ticker('AAPL')
info = ticker.info  # Will fail if ticker doesn't exist
```

### `KeyError: 'Close'` or missing columns

Check if data was fetched successfully:

```python
if data is None or data.empty:
    print("No data returned. Check ticker symbol.")
elif 'Close' not in data.columns:
    print("Missing required columns.")
```

---

## Calculation Warnings

### `RuntimeWarning: invalid value encountered`

Check for NaN values before calculations:

```python
if data.isnull().any().any():
    print("Data contains NaN values.")
    data = data.dropna()  # or data = data.fillna(method='ffill')
```

---

## Performance Issues

### Slow when fetching multiple stocks

Use `fetch_multiple_stocks` instead of looping:

```python
# ❌ Slow
for ticker in tickers:
    data = fetch_stock_data(ticker)

# ✅ Fast
data_dict = fetcher.fetch_multiple_stocks(tickers, period='1y')
```

### Memory issues with large datasets

Filter data early:

```python
# Only fetch recent data and needed columns
data = fetch_stock_data('AAPL', period='1y')[['Open', 'High', 'Low', 'Close', 'Volume']]
```

---

## Tushare Issues

### Tushare token not working

1. Register at [tushare.pro](https://tushare.pro/register)
2. Get your token from user center
3. Set environment variable:

```bash
export TUSHARE_TOKEN="your-token-here"
```

### Ticker cannot be mapped

Provide market hint:

```python
data = fetch_stock_data('000001', provider='tushare', market='cn')
```
