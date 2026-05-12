"""
US Portfolio Analysis — Full Data Fetch
Date: 2026-05-11
"""

import sys
import os
import json
import moomoo as ft
from datetime import datetime, date

SKILL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../.claude/skills/moomoo-trading'))
sys.path.insert(0, SKILL_DIR)

from scripts import (
    get_account_info, get_positions, get_order_list,
    get_realtime_quote, get_kline_data, calculate_all,
    MoomooConnection, make_serializable,
)

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
        # Calculate SMA20 and SMA50 separately since calculate_all uses same column name
        from scripts.indicators import calculate_sma
        sma20_df = calculate_sma(df, 20)
        sma50_df = calculate_sma(df, 50)
        sma20_val = float(sma20_df['SMA'].iloc[-1])
        sma50_val = float(sma50_df['SMA'].iloc[-1])
        def safe(v):
            try:
                f = float(v)
                return None if (f != f) else round(f, 4)  # nan check
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
    print('=== Fetching account data ===')
    account = get_account_info(trading_env='REAL')
    print(f"Total assets: ${account.get('total_assets', 0):,.2f}")
    print(f"Market val:   ${account.get('market_val', 0):,.2f}")
    investable = account.get('total_assets', 0) - account.get('market_val', 0)
    print(f"Investable:   ${investable:,.2f}")

    print('\n=== Fetching positions ===')
    positions_df = get_positions(trading_env='REAL')
    positions = positions_df.to_dict('records') if not positions_df.empty else []
    print(f"Positions: {len(positions)}")
    for p in positions:
        print(f"  {p.get('code')} qty={p.get('qty')} cost={p.get('cost_price')}")

    print('\n=== Fetching today orders ===')
    try:
        orders_df = get_order_list(trading_env='REAL')
        orders = orders_df.to_dict('records') if not orders_df.empty else []
    except Exception as e:
        print(f'Order fetch error: {e}')
        orders = []
    print(f"Orders today: {len(orders)}")

    print('\n=== Fetching USStocks watchlist ===')
    watchlist = get_watchlist()
    print(f"Watchlist items: {len(watchlist)}")
    for w in watchlist:
        print(f"  {w['code']} {w['name']}")

    # Collect all codes
    position_codes = [p['code'] for p in positions]
    watchlist_codes = [w['code'] for w in watchlist]
    all_codes = list(dict.fromkeys(position_codes + watchlist_codes))  # deduplicate preserving order
    print(f'\nAll codes to analyze ({len(all_codes)}): {all_codes}')

    print('\n=== Fetching real-time quotes ===')
    quotes_df = get_realtime_quote(all_codes)
    quotes = quotes_df.to_dict('records') if not quotes_df.empty else []
    for q in quotes:
        print(f"  {q.get('code')} last={q.get('last_price')} updated={q.get('update_time')}")

    print('\n=== Calculating technical indicators ===')
    indicators = {}
    for code in all_codes:
        print(f"  {code}...", end=' ')
        ind = fetch_indicators(code)
        indicators[code] = ind
        if ind and 'error' not in ind:
            print(f"RSI={ind.get('rsi14')} %B={ind.get('bb_pct_b')} vol_ratio={ind.get('vol_ratio')}")
        else:
            print(f"ERROR: {ind}")

    # Save account data
    account_data = {
        'fetch_time': datetime.now().isoformat(),
        'account': make_serializable(account),
        'investable_amount': investable,
        'positions': make_serializable(positions),
        'orders': make_serializable(orders),
        'watchlist': watchlist,
        'quotes': make_serializable(quotes),
    }
    with open(os.path.join(OUT_DIR, 'us_account_data.json'), 'w') as f:
        json.dump(account_data, f, indent=2, ensure_ascii=False, default=str)
    print('\nSaved us_account_data.json')

    # Save indicators data
    with open(os.path.join(OUT_DIR, 'us_indicators_data.json'), 'w') as f:
        json.dump(make_serializable(indicators), f, indent=2, ensure_ascii=False, default=str)
    print('Saved us_indicators_data.json')

    print('\n=== Done ===')
    return account_data, indicators


if __name__ == '__main__':
    main()
