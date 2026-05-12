"""
US Portfolio Analysis — Full Data Fetch
Date: 2026-05-11
"""

import sys
import os
import json
import moomoo as ft
from datetime import datetime

SKILL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../.claude/skills/moomoo-trading'))
sys.path.insert(0, SKILL_DIR)

from scripts import (
    get_account_info, get_positions, get_order_list,
    get_realtime_quote, get_us_session, get_kline_data, calculate_all,
    MoomooConnection, make_serializable,
)
from scripts.indicators import calculate_sma

OUT_DIR = os.path.dirname(os.path.abspath(__file__))


def get_watchlist():
    with MoomooConnection.quote_ctx() as ctx:
        ret, data = ctx.get_user_security(group_name='USStocks')
        if ret != ft.RET_OK:
            raise RuntimeError(f'get_user_security failed: {data}')
        return data[['code', 'name', 'stock_type']].to_dict('records')


def fetch_indicators(code, count=120):
    try:
        df = get_kline_data(code, count=count)
        if df is None or df.empty or len(df) < 20:
            return None
        ind = calculate_all(df)
        last = ind.iloc[-1]
        sma20_val = float(calculate_sma(df, 20)['SMA'].iloc[-1])
        sma50_val = float(calculate_sma(df, 50)['SMA'].iloc[-1])

        def safe(v):
            try:
                f = float(v)
                return None if (f != f) else round(f, 4)
            except:
                return None

        return {
            'last_close': safe(last.get('Close')),
            'last_date': str(ind.index[-1]),
            'rsi14': safe(last.get('RSI')),
            'macd': safe(last.get('MACD')),
            'macd_signal': safe(last.get('Signal')),
            'macd_hist': safe(last.get('Histogram')),
            'bb_upper': safe(last.get('Upper')),
            'bb_middle': safe(last.get('Middle')),
            'bb_lower': safe(last.get('Lower')),
            'bb_pct_b': safe(last.get('%B')),
            'sma20': round(sma20_val, 2),
            'sma50': round(sma50_val, 2),
            'atr14': safe(last.get('ATR')),
            'volume': int(df['Volume'].iloc[-1]),
            'vol_ma20': round(float(df['Volume'].tail(20).mean()), 0),
            'vol_ratio': round(float(df['Volume'].iloc[-1]) / float(df['Volume'].tail(20).mean()), 2),
        }
    except Exception as e:
        import traceback
        return {'error': str(e), 'traceback': traceback.format_exc()}


def main():
    # ── 当前时段 ──
    session_info = get_us_session()
    print(f"=== 当前美股时段 ===")
    print(f"  {session_info['note']}")
    print(f"  ET: {session_info['et_time']}")
    print(f"  是否交易日: {session_info['is_weekday']}")

    # ── 账户 ──
    print('\n=== Fetching account data ===')
    account = get_account_info(trading_env='REAL')
    investable = account.get('total_assets', 0) - account.get('market_val', 0)
    print(f"  Total assets: ${account.get('total_assets', 0):,.2f}")
    print(f"  Market val:   ${account.get('market_val', 0):,.2f}")
    print(f"  Investable:   ${investable:,.2f}")

    # ── 持仓 ──
    print('\n=== Fetching positions ===')
    positions_df = get_positions(trading_env='REAL')
    positions = positions_df.to_dict('records') if not positions_df.empty else []
    for p in positions:
        print(f"  {p.get('code')} qty={p.get('qty')} cost={p.get('cost_price')}")

    # ── 订单 ──
    print('\n=== Fetching today orders ===')
    try:
        orders_df = get_order_list(trading_env='REAL')
        orders = orders_df.to_dict('records') if not orders_df.empty else []
    except Exception as e:
        orders = []
    print(f"  Orders today: {len(orders)}")

    # ── 关注列表 ──
    print('\n=== Fetching USStocks watchlist ===')
    watchlist = get_watchlist()
    for w in watchlist:
        print(f"  {w['code']} {w['name']}")

    # ── 实时行情（含时段标注）──
    position_codes = [p['code'] for p in positions]
    watchlist_codes = [w['code'] for w in watchlist]
    all_codes = list(dict.fromkeys(position_codes + watchlist_codes))
    print(f'\n=== Fetching real-time quotes ({session_info["session"]}) ===')
    quotes_df = get_realtime_quote(all_codes)
    quotes = quotes_df.to_dict('records') if not quotes_df.empty else []
    for q in quotes:
        print(f"  {q.get('code'):12s}  last={q.get('last_price'):>8.2f}"
              f"  prev_close={q.get('prev_close_price'):>8.2f}"
              f"  session={q.get('session')}  et={q.get('et_time')}")

    # ── 技术指标 ──
    print('\n=== Calculating technical indicators ===')
    indicators = {}
    for code in all_codes:
        print(f"  {code}...", end=' ', flush=True)
        ind = fetch_indicators(code)
        indicators[code] = ind
        if ind and 'error' not in ind:
            print(f"RSI={ind.get('rsi14')}  %B={ind.get('bb_pct_b')}  vol_ratio={ind.get('vol_ratio')}")
        else:
            print(f"ERROR: {ind.get('error') if ind else 'None'}")

    # ── 保存 ──
    account_data = {
        'fetch_time': datetime.now().isoformat(),
        'session': session_info,
        'account': make_serializable(account),
        'investable_amount': investable,
        'positions': make_serializable(positions),
        'orders': make_serializable(orders),
        'watchlist': watchlist,
        'quotes': make_serializable(quotes),
    }
    with open(os.path.join(OUT_DIR, 'us_account_data.json'), 'w') as f:
        json.dump(account_data, f, indent=2, ensure_ascii=False, default=str)

    with open(os.path.join(OUT_DIR, 'us_indicators_data.json'), 'w') as f:
        json.dump(make_serializable(indicators), f, indent=2, ensure_ascii=False, default=str)

    print('\nSaved us_account_data.json + us_indicators_data.json')
    return account_data, indicators


if __name__ == '__main__':
    main()
