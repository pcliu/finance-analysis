"""
data_fetcher.py — Market Data via Moomoo OpenD

Fetches real-time quotes, historical K-lines, and order book data.
All historical data is returned as OHLCV DataFrames compatible with
the quantitative-trading indicators module (same column names).
"""

import pandas as pd
import moomoo as ft
from datetime import datetime, time
import pytz
from .connection import MoomooConnection, require_opend
from .utils import to_moomoo_code, parse_market_from_code


# ── US Session Detection ──────────────────────────────────────────────────────

_ET = pytz.timezone('America/New_York')

# Session boundaries in ET (hour, minute)
_SESSION_BOUNDS = [
    (time(4, 0),  time(9, 30),  'Pre-Market'),
    (time(9, 30),  time(16, 0),  'RTH'),
    (time(16, 0),  time(20, 0),  'After-Hours'),
]


def get_us_session(dt_utc: datetime = None) -> dict:
    """
    Return the current US equity trading session based on ET time.

    Args:
        dt_utc: UTC datetime to evaluate (defaults to now).

    Returns:
        dict with keys:
            session      – 'Pre-Market' | 'RTH' | 'After-Hours' | 'Overnight'
            et_time      – current ET datetime string (HH:MM:SS)
            is_weekday   – bool, False on Saturday/Sunday
            note         – human-readable label for reports
    """
    if dt_utc is None:
        dt_utc = datetime.now(pytz.utc)
    elif dt_utc.tzinfo is None:
        dt_utc = pytz.utc.localize(dt_utc)

    et_now = dt_utc.astimezone(_ET)
    et_t = et_now.time()
    weekday = et_now.weekday()  # 0=Mon … 6=Sun

    is_weekday = weekday < 5

    session = 'Overnight'
    for start, end, name in _SESSION_BOUNDS:
        if start <= et_t < end:
            session = name
            break

    labels = {
        'Pre-Market':  '盘前 (Pre-Market 04:00–09:30 ET)',
        'RTH':         '盘中 (RTH 09:30–16:00 ET)',
        'After-Hours': '盘后 (After-Hours 16:00–20:00 ET)',
        'Overnight':   '夜盘 (Overnight 20:00–04:00 ET)',
    }

    return {
        'session':    session,
        'et_time':    et_now.strftime('%Y-%m-%d %H:%M:%S ET'),
        'is_weekday': is_weekday,
        'note':       labels[session] if is_weekday else f'非交易日 ({et_now.strftime("%A")}) — 价格为最近一个夜盘/盘后延续',
    }


# ── Real-time Data ────────────────────────────────────────────────────────────

@require_opend
def get_realtime_quote(tickers) -> pd.DataFrame:
    """
    Get real-time market snapshot for one or more tickers.

    ⚠️ IMPORTANT — `last_price` semantics for US equities:
        Moomoo's `last_price` field reflects the most recent **RTH** trade only.
        During Pre-Market / After-Hours / Overnight, `last_price` does NOT change
        and is NOT the current tradeable price. Always use `current_price`
        (added below) for decision-making — it picks the right session's price
        automatically.

    Returns (US equities) augmented columns:
        - last_price         : last RTH trade (stale outside RTH)
        - pre_price          : Pre-Market last trade
        - after_price        : After-Hours last trade
        - overnight_price    : Overnight last trade
        - pre_change_rate / after_change_rate / overnight_change_rate
        - current_price      : ⭐ session-aware "use this" price
                               (pre_price in Pre-Market, last_price in RTH,
                                after_price in After-Hours, overnight_price in Overnight)
        - current_change_rate: change_rate matching current_price
        - current_price_source: which field current_price came from
        - session, et_time, session_note: from get_us_session()
    """
    if isinstance(tickers, str):
        tickers = [tickers]

    session_info = get_us_session()

    with MoomooConnection.quote_ctx() as ctx:
        ret, data = ctx.get_market_snapshot(tickers)
        if ret != ft.RET_OK:
            raise RuntimeError(f'get_market_snapshot failed: {data}')

    cols = [
        'code', 'name', 'last_price', 'open_price', 'high_price', 'low_price',
        'prev_close_price', 'volume', 'turnover', 'price_spread',
        'change_val', 'change_rate', 'update_time',
        # Extended-hours fields (US equities)
        'pre_price', 'pre_change_val', 'pre_change_rate', 'pre_volume',
        'pre_high_price', 'pre_low_price',
        'after_price', 'after_change_val', 'after_change_rate',
        'after_high_price', 'after_low_price', 'after_volume', 'after_turnover',
        'overnight_price', 'overnight_change_val', 'overnight_change_rate',
        'overnight_high_price', 'overnight_low_price', 'overnight_volume',
    ]
    available = [c for c in cols if c in data.columns]
    df = data[available].reset_index(drop=True)

    df['session']      = session_info['session']
    df['et_time']      = session_info['et_time']
    df['session_note'] = session_info['note']

    # ── Session-aware current price selection ────────────────────────
    # Maps the current ET session to the correct price field.
    session_to_field = {
        'Pre-Market':  ('pre_price',       'pre_change_rate'),
        'RTH':         ('last_price',      'change_rate'),
        'After-Hours': ('after_price',     'after_change_rate'),
        'Overnight':   ('overnight_price', 'overnight_change_rate'),
    }
    price_field, change_field = session_to_field.get(
        session_info['session'], ('last_price', 'change_rate')
    )

    def _pick_current(row):
        # Prefer the session's price; fall back to last_price if missing/zero
        # (e.g. illiquid tickers with no extended-hours trades).
        if price_field in row.index:
            v = row[price_field]
            if v is not None and not pd.isna(v) and float(v) > 0:
                return pd.Series({
                    'current_price':         float(v),
                    'current_change_rate':   float(row[change_field]) if change_field in row.index and not pd.isna(row[change_field]) else 0.0,
                    'current_price_source':  price_field,
                })
        return pd.Series({
            'current_price':         float(row['last_price']) if 'last_price' in row.index else 0.0,
            'current_change_rate':   float(row['change_rate']) if 'change_rate' in row.index else 0.0,
            'current_price_source':  'last_price (fallback)',
        })

    if not df.empty:
        df = pd.concat([df, df.apply(_pick_current, axis=1)], axis=1)

    return df


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
    adjust_type=ft.AuType.QFQ,
    start: str = None,
    end: str = None,
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
    # Without an explicit end date, OpenD returns only its local cache (may be months stale).
    # Always pass end=today so the request goes to the server and returns current data.
    from datetime import date, timedelta
    if end is None:
        end = date.today().strftime('%Y-%m-%d')
    if start is None:
        # Use 2x buffer to ensure recent days are not truncated by max_count.
        # count=120 trading days needs ~170 cal days, but a tight window risks
        # the API filling max_count from the start and cutting off recent bars.
        # Use 2.5x to guarantee the last bars are always the most recent ones.
        buffer_days = max(int(count * 2.5), 250)
        start = (date.today() - timedelta(days=buffer_days)).strftime('%Y-%m-%d')

    with MoomooConnection.quote_ctx() as ctx:
        ret, data, _ = ctx.request_history_kline(
            ticker,
            start=start,
            end=end,
            ktype=ktype,
            autype=adjust_type,
            max_count=count,
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
    adjust_type=ft.AuType.QFQ
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
