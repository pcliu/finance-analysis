"""
data_fetcher.py — Market Data via Moomoo OpenD

Fetches real-time quotes, historical K-lines, and order book data.
All historical data is returned as OHLCV DataFrames compatible with
the quantitative-trading indicators module (same column names).
"""

import pandas as pd
import moomoo as ft
from .connection import MoomooConnection, require_opend
from .utils import to_moomoo_code, parse_market_from_code


# ── Real-time Data ────────────────────────────────────────────────────────────

@require_opend
def get_realtime_quote(tickers) -> pd.DataFrame:
    """
    Get real-time market snapshot for one or more tickers.

    Args:
        tickers: str or list of Moomoo-format codes, e.g. 'US.NVDA' or ['US.NVDA', 'HK.00700']

    Returns:
        pd.DataFrame with columns:
            code, name, last_price, open_price, high_price, low_price,
            prev_close_price, volume, turnover, price_spread,
            change_val, change_rate (%), update_time
    """
    if isinstance(tickers, str):
        tickers = [tickers]

    with MoomooConnection.quote_ctx() as ctx:
        ret, data = ctx.get_market_snapshot(tickers)
        if ret != ft.RET_OK:
            raise RuntimeError(f'get_market_snapshot failed: {data}')

    cols = [
        'code', 'name', 'last_price', 'open_price', 'high_price', 'low_price',
        'prev_close_price', 'volume', 'turnover', 'price_spread',
        'change_val', 'change_rate', 'update_time'
    ]
    available = [c for c in cols if c in data.columns]
    return data[available].reset_index(drop=True)


@require_opend
def get_order_book(ticker: str, num: int = 10) -> dict:
    """
    Get order book (bid/ask depth) for a ticker.

    Args:
        ticker: Moomoo code, e.g. 'US.NVDA'
        num:    Number of bid/ask levels to return (max 10)

    Returns:
        dict with keys:
            'bid': list of [price, volume, num_orders]
            'ask': list of [price, volume, num_orders]
    """
    with MoomooConnection.quote_ctx() as ctx:
        ret, data = ctx.get_order_book(ticker, num=num)
        if ret != ft.RET_OK:
            raise RuntimeError(f'get_order_book failed: {data}')

    return {
        'bid': data.get('Bid', []),
        'ask': data.get('Ask', [])
    }


# ── Historical K-line Data ────────────────────────────────────────────────────

@require_opend
def get_kline_data(
    ticker: str,
    ktype=ft.KLType.K_DAY,
    count: int = 120,
    adjust_type=ft.AdjustType.FORWARD,
    start: str = None,
    end: str = None
) -> pd.DataFrame:
    """
    Fetch historical K-line (OHLCV) data from Moomoo.

    Returns a DataFrame compatible with quantitative-trading indicators:
    columns are Open, High, Low, Close, Volume (capitalised).

    Args:
        ticker:      Moomoo code, e.g. 'US.NVDA'
        ktype:       ft.KLType.K_DAY | K_WEEK | K_MON | K_60M | K_30M | K_15M | K_5M | K_1M
        count:       Number of bars to fetch (most recent if no start/end given)
        adjust_type: ft.AdjustType.FORWARD (前复权) | NONE | BACKWARD
        start:       'YYYY-MM-DD' (optional)
        end:         'YYYY-MM-DD' (optional)

    Returns:
        pd.DataFrame indexed by datetime with columns:
            Open, High, Low, Close, Volume, Turnover, pe_ratio, turnover_rate
    """
    with MoomooConnection.quote_ctx() as ctx:
        if start and end:
            ret, data, _ = ctx.request_history_kline(
                ticker,
                start=start,
                end=end,
                ktype=ktype,
                autype=adjust_type,
                max_count=count
            )
        else:
            ret, data, _ = ctx.request_history_kline(
                ticker,
                ktype=ktype,
                autype=adjust_type,
                max_count=count
            )

        if ret != ft.RET_OK:
            raise RuntimeError(f'request_history_kline failed for {ticker}: {data}')

    # Normalise column names to match quantitative-trading format
    rename_map = {
        'open':   'Open',
        'high':   'High',
        'low':    'Low',
        'close':  'Close',
        'volume': 'Volume',
        'turnover': 'Turnover',
        'time_key': 'Date'
    }
    data = data.rename(columns=rename_map)

    # Set datetime index
    if 'Date' in data.columns:
        data['Date'] = pd.to_datetime(data['Date'])
        data = data.set_index('Date').sort_index()

    return data


@require_opend
def get_multiple_klines(
    tickers: list,
    ktype=ft.KLType.K_DAY,
    count: int = 120,
    adjust_type=ft.AdjustType.FORWARD
) -> dict:
    """
    Fetch K-line data for multiple tickers.

    Returns:
        dict mapping ticker → pd.DataFrame (same format as get_kline_data)
    """
    result = {}
    for ticker in tickers:
        try:
            result[ticker] = get_kline_data(ticker, ktype=ktype, count=count, adjust_type=adjust_type)
        except Exception as e:
            print(f'Warning: failed to fetch {ticker}: {e}')
            result[ticker] = None
    return result


# ── Broker / Market Info ──────────────────────────────────────────────────────

@require_opend
def get_stock_basicinfo(tickers: list) -> pd.DataFrame:
    """Get basic stock info (name, lot size, stock type, etc.)."""
    market = parse_market_from_code(tickers[0]) if tickers else ft.Market.US
    with MoomooConnection.quote_ctx() as ctx:
        ret, data = ctx.get_stock_basicinfo(market, ft.SecurityType.STOCK, tickers)
        if ret != ft.RET_OK:
            raise RuntimeError(f'get_stock_basicinfo failed: {data}')
    return data
