#!/usr/bin/env python3
"""Fetch US account data: positions, account info, orders, and watchlist."""
import sys, os, json
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../../.claude/skills/moomoo-trading'))
sys.path.append(SKILL_DIR)

from dotenv import load_dotenv
load_dotenv(os.path.join(SCRIPT_DIR, '../../../../.env.local'))

from scripts import get_account_info, get_positions, get_order_list, make_serializable
import moomoo as ft

def main():
    result = {}

    # 1. Account info
    print("Fetching account info...")
    account = get_account_info(trading_env='REAL')
    result['account'] = make_serializable(account)
    print(f"Account: {account}")

    # 2. Positions
    print("\nFetching positions...")
    positions = get_positions(trading_env='REAL')
    result['positions'] = make_serializable(positions)
    print(f"Positions:\n{positions}")

    # 3. Today's orders
    print("\nFetching orders...")
    orders = get_order_list(trading_env='REAL')
    result['orders'] = make_serializable(orders)
    print(f"Orders:\n{orders}")

    # 4. USStocks watchlist
    print("\nFetching USStocks watchlist...")
    trade_pwd = os.environ.get('MOOMOO_TRADE_PASSWORD', '')
    host = os.environ.get('MOOMOO_HOST', '127.0.0.1')
    port = int(os.environ.get('MOOMOO_PORT', 11111))

    ctx = ft.OpenQuoteContext(host=host, port=port)
    ret, watchlist_data = ctx.get_user_security(group_name='USStocks')
    ctx.close()

    if ret == ft.RET_OK:
        result['watchlist'] = make_serializable(watchlist_data)
        print(f"Watchlist ({len(watchlist_data)} items):\n{watchlist_data}")
    else:
        print(f"Failed to get watchlist: {watchlist_data}")
        result['watchlist'] = []

    # Save
    out_path = os.path.join(SCRIPT_DIR, 'us_account_data.json')
    result['fetch_time'] = datetime.now().isoformat()
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\nSaved to {out_path}")
    return result

if __name__ == '__main__':
    main()
