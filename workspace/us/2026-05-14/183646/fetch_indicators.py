"""
fetch_indicators.py — 实时行情 + 技术指标（RSI/MACD/BB/SMA/ATR/成交量）
修复：使用 start='2025-01-01' end=today 获取足够历史数据，绕开 max_count 只返回首批问题
输出: us_indicators_data.json
"""
import sys, os, json
import pandas as pd
from datetime import datetime, date

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../../.claude/skills/moomoo-trading'))
sys.path.insert(0, SKILL_DIR)

from scripts import (
    get_realtime_quote,
    calculate_rsi, calculate_macd, calculate_bollinger_bands,
    calculate_sma, calculate_ema, calculate_atr,
    make_serializable
)
from scripts.connection import MoomooConnection
import moomoo as ft

TICKERS = [
    'US.HIMS', 'US.PLTR', 'US.CRCL', 'US.RKLB',
    'US.AMD', 'US.TSLA', 'US.SLV', 'US.GOOG',
    'US.IAU', 'US.TSM', 'US.NVDA'
]

TODAY = date.today().strftime('%Y-%m-%d')
START = '2025-01-01'   # ~340 cal days → ~240 trading days, sufficient for SMA50+


def fetch_kline_recent(ticker: str, start: str, end: str, count: int = 500) -> pd.DataFrame:
    """Fetch kline with explicit start/end to get the most recent bars."""
    with MoomooConnection.quote_ctx() as ctx:
        ret, data, _ = ctx.request_history_kline(
            ticker,
            start=start,
            end=end,
            ktype=ft.KLType.K_DAY,
            autype=ft.AuType.QFQ,
            max_count=count,
        )
    if ret != ft.RET_OK:
        raise RuntimeError(f'request_history_kline failed for {ticker}: {data}')
    if data is None or data.empty:
        return pd.DataFrame()

    # Normalise columns to match indicator functions
    col_map = {
        'open':   'Open', 'high': 'High', 'low': 'Low',
        'close':  'Close', 'volume': 'Volume', 'turnover': 'Turnover',
    }
    data = data.rename(columns=col_map)
    data['Date'] = pd.to_datetime(data['time_key'])
    data = data.set_index('Date').sort_index()
    return data


# ── 实时行情 ──────────────────────────────────────────────────────
print("Fetching realtime quotes...")
quotes = get_realtime_quote(TICKERS)
quote_map = {}
if quotes is not None and not quotes.empty:
    for _, row in quotes.iterrows():
        code = row.get('code', '')
        quote_map[code] = {
            'last_price':       float(row.get('last_price', 0)),
            'prev_close_price': float(row.get('prev_close_price', 0)),
            'open_price':       float(row.get('open_price', 0)),
            'high_price':       float(row.get('high_price', 0)),
            'low_price':        float(row.get('low_price', 0)),
            'volume':           float(row.get('volume', 0)),
            'update_time':      str(row.get('update_time', '')),
            'change_rate':      float(row.get('change_rate', 0)),
        }
        print(f"  {code:12s} last={quote_map[code]['last_price']:.3f}  "
              f"chg={quote_map[code]['change_rate']:.2f}%  "
              f"updated={quote_map[code]['update_time']}")

# ── 技术指标 ─────────────────────────────────────────────────────
indicators_data = {}

for ticker in TICKERS:
    print(f"\nProcessing {ticker}...")
    try:
        kline = fetch_kline_recent(ticker, start=START, end=TODAY)
        if kline is None or kline.empty:
            print(f"  Warning: no kline data for {ticker}")
            indicators_data[ticker] = {'error': 'no kline data'}
            continue

        latest_date = str(kline.index[-1].date())
        print(f"  K-line: {len(kline)} bars  {kline.index[0].date()} → {latest_date}")

        # 数据新鲜度校验（> 5 个交易日警告）
        from pandas.tseries.offsets import BDay
        last_bar_date = kline.index[-1].date()
        business_days_gap = len(pd.bdate_range(str(last_bar_date), TODAY)) - 1
        stale = business_days_gap > 5
        if stale:
            print(f"  ⚠️  DATA STALE: latest bar {latest_date}, gap={business_days_gap} bdays")

        rsi   = calculate_rsi(kline, window=14)
        macd  = calculate_macd(kline)
        bb    = calculate_bollinger_bands(kline)
        sma20 = calculate_sma(kline, window=20)
        sma50 = calculate_sma(kline, window=50)
        atr   = calculate_atr(kline, window=14)

        vol_series = kline['Volume'] if 'Volume' in kline.columns else None
        vol_20avg  = float(vol_series.tail(20).mean()) if vol_series is not None else 0
        vol_latest = float(vol_series.iloc[-1])        if vol_series is not None else 0
        vol_ratio  = vol_latest / vol_20avg if vol_20avg > 0 else 1.0

        close_latest = float(kline['Close'].iloc[-1])

        def last_val(df, col):
            if df is not None and not df.empty and col in df.columns:
                v = df[col].dropna()
                return float(v.iloc[-1]) if len(v) > 0 else None
            return None

        result = {
            'ticker':       ticker,
            'close':        close_latest,
            'latest_date':  latest_date,
            'stale':        stale,
            'stale_gap_bdays': business_days_gap,
            'quote':        quote_map.get(ticker, {}),
            'rsi14':        last_val(rsi, 'RSI'),
            'macd':         last_val(macd, 'MACD'),
            'macd_signal':  last_val(macd, 'Signal'),
            'macd_hist':    last_val(macd, 'Histogram'),
            'bb_upper':     last_val(bb, 'Upper'),
            'bb_middle':    last_val(bb, 'Middle'),
            'bb_lower':     last_val(bb, 'Lower'),
            'bb_pct_b':     last_val(bb, '%B'),
            'sma20':        last_val(sma20, 'SMA'),
            'sma50':        last_val(sma50, 'SMA'),
            'atr14':        last_val(atr, 'ATR'),
            'vol_latest':   vol_latest,
            'vol_20avg':    vol_20avg,
            'vol_ratio':    vol_ratio,
            'above_sma20':  close_latest > (last_val(sma20, 'SMA') or 0),
            'above_sma50':  close_latest > (last_val(sma50, 'SMA') or 0),
        }
        indicators_data[ticker] = result

        print(f"  RSI={result['rsi14']:.1f}  %B={result['bb_pct_b']:.2f}  "
              f"MACD_hist={result['macd_hist']:.4f}  vol_ratio={vol_ratio:.2f}x  "
              f"above_SMA20={'Y' if result['above_sma20'] else 'N'}  "
              f"above_SMA50={'Y' if result['above_sma50'] else 'N'}")

    except Exception as e:
        import traceback
        print(f"  Error: {e}")
        traceback.print_exc()
        indicators_data[ticker] = {'error': str(e)}

# ── 保存 ─────────────────────────────────────────────────────────
output = {
    'fetch_time': datetime.now().isoformat(),
    'tickers': TICKERS,
    'indicators': make_serializable(indicators_data),
}

out_path = os.path.join(SCRIPT_DIR, 'us_indicators_data.json')
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\nSaved: {out_path}")
