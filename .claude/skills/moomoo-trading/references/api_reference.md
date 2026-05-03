# Moomoo Trading Skill — API Reference

## Connection

```python
MoomooConnection.check_health()         # → dict: connected, message
MoomooConnection.quote_ctx()            # context manager → OpenQuoteContext
MoomooConnection.trade_ctx(market)      # context manager → OpenSecTradeContext
```

---

## Data Fetching

### Real-time Quote
```python
get_realtime_quote(tickers)
# tickers: 'US.NVDA' or ['US.NVDA', 'US.AMD', 'HK.00700']
# Returns: DataFrame[code, name, last_price, open_price, high_price, low_price,
#                    prev_close_price, volume, turnover, change_val, change_rate, update_time]
```

### Historical K-lines
```python
get_kline_data(
    ticker,                        # 'US.NVDA'
    ktype=ft.KLType.K_DAY,         # K_DAY | K_WEEK | K_60M | K_30M | K_15M | K_5M | K_1M
    count=120,
    adjust_type=ft.AdjustType.FORWARD,
    start=None,                    # 'YYYY-MM-DD'
    end=None
)
# Returns: DataFrame[Open, High, Low, Close, Volume, Turnover] — DatetimeIndex
```

### Order Book
```python
get_order_book(ticker, num=10)
# Returns: dict{'bid': [[price, vol, orders], ...], 'ask': [...]}
```

---

## Technical Indicators

All accept OHLCV DataFrame (columns: Open, High, Low, Close, Volume).

```python
calculate_rsi(data, window=14)              # → DataFrame['RSI']
calculate_sma(data, window=20)              # → DataFrame['SMA']
calculate_ema(data, window=20)              # → DataFrame['EMA']
calculate_macd(data, fast=12, slow=26, signal=9)  # → DataFrame['MACD','Signal','Histogram']
calculate_bollinger_bands(data, window=20)  # → DataFrame['Upper','Middle','Lower','%B']
calculate_atr(data, window=14)              # → DataFrame['ATR']
calculate_stochastic(data, k_window=14)     # → DataFrame['K','D']
calculate_all(data)                         # → All indicators merged into one DataFrame
```

---

## Account

```python
get_account_info(trading_env='SIMULATE', market='US')
# → dict: total_assets, cash, market_val, frozen_cash, available_funds,
#         unrealized_pl, realized_pl, currency

get_positions(trading_env='SIMULATE', market='US', ticker=None)
# → DataFrame[code, stock_name, qty, can_sell_qty, cost_price,
#             market_val, nominal_price, pl_ratio, pl_val]

get_cash_info(trading_env='SIMULATE', market='US')
# → dict: cash, frozen_cash, available_funds, currency

print_account_summary(trading_env='SIMULATE', market='US')  # Formatted console output
```

---

## Orders

### Place Order
```python
place_order(
    ticker,                    # 'US.NVDA'
    direction,                 # 'BUY' or 'SELL'
    qty,                       # int > 0
    price,                     # float (ignored for MARKET orders)
    order_type='LIMIT',        # 'LIMIT' | 'MARKET' | 'STOP' | 'STOP_LIMIT'
    trading_env='SIMULATE',    # ⚠️ 'REAL' requires explicit user confirmation
)
# Always prints order summary before executing.
# → dict: success, order_id, status, ticker, direction, qty, price, message
```

### Manage Orders
```python
cancel_order(order_id, trading_env='SIMULATE', market='US')
modify_order(order_id, qty, price, trading_env='SIMULATE', market='US')
cancel_all_orders(trading_env='SIMULATE', market='US')

get_order_list(trading_env='SIMULATE', market='US', status_filter=None)
# status_filter: ['SUBMITTED', 'PART_FILLED', 'FILLED', 'CANCELLED', 'FAILED']

get_order_detail(order_id, trading_env='SIMULATE', market='US')
save_order_log(output_path)   # Save session audit log to JSON
```

---

## Utilities

```python
to_moomoo_code('NVDA', 'US')     # → 'US.NVDA'
to_moomoo_code('700', 'HK')      # → 'HK.00700'
parse_market_from_code('US.NVDA')  # → 'US'
strip_market_prefix('US.NVDA')     # → 'NVDA'
make_serializable(obj)             # Convert numpy/pandas → JSON-safe Python types
```

---

## Market Codes Quick Reference

| Ticker | Moomoo Code |
|--------|-------------|
| NVDA   | US.NVDA     |
| AMD    | US.AMD      |
| GOOG   | US.GOOG     |
| AAPL   | US.AAPL     |
| Tencent | HK.00700   |
| Alibaba HK | HK.09988 |
| DBS Bank | SG.D05   |
| UOB    | SG.U11      |

---

## KLType Reference

| Constant | Description |
|----------|-------------|
| `ft.KLType.K_1M` | 1-minute bars |
| `ft.KLType.K_5M` | 5-minute bars |
| `ft.KLType.K_15M` | 15-minute bars |
| `ft.KLType.K_30M` | 30-minute bars |
| `ft.KLType.K_60M` | 1-hour bars |
| `ft.KLType.K_DAY` | Daily bars (default) |
| `ft.KLType.K_WEEK` | Weekly bars |
| `ft.KLType.K_MON` | Monthly bars |
