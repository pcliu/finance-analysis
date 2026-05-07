#!/usr/bin/env python3
"""Fetch account data, positions, orders, and watchlist from Moomoo OpenD."""
import sys, os, json
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../../.claude/skills/moomoo-trading'))
sys.path.insert(0, SKILL_DIR)

from scripts import get_account_info, get_positions, get_order_list, make_serializable
import moomoo as ft

# Load env
from dotenv import load_dotenv
load_dotenv(os.path.join(SCRIPT_DIR, '../../../../.env.local'))

def main():
    results = {}

    # 1. Account info
    print("Fetching account info...")
    account = get_account_info(trading_env='REAL')
    results['account'] = make_serializable(account)
    print(f"  Account: {account}")

    # 2. Positions
    print("Fetching positions...")
    positions = get_positions(trading_env='REAL')
    results['positions'] = make_serializable(positions)
    if hasattr(positions, 'to_dict'):
        print(f"  Positions ({len(positions)} holdings):")
        for _, row in positions.iterrows():
            print(f"    {row.get('code','?')} qty={row.get('qty','?')} cost={row.get('cost_price','?')} nominal={row.get('nominal_price','?')}")

    # 3. Orders today
    print("Fetching orders...")
    orders = get_order_list(trading_env='REAL')
    results['orders'] = make_serializable(orders)
    if hasattr(orders, 'to_dict'):
        print(f"  Orders ({len(orders)} today)")

    # 4. Watchlist
    print("Fetching USStocks watchlist...")
    ctx = ft.OpenQuoteContext(host='127.0.0.1', port=11111)
    ret, watchlist = ctx.get_user_security(group_name='USStocks')
    ctx.close()
    if ret == ft.RET_OK:
        results['watchlist'] = make_serializable(watchlist)
        print(f"  Watchlist ({len(watchlist)} items):")
        for _, row in watchlist.iterrows():
            print(f"    {row.get('code','?')} {row.get('name','?')}")
    else:
        print(f"  Watchlist error: {watchlist}")
        results['watchlist'] = []

    results['fetch_time'] = datetime.now().isoformat()

    # Save
    out_path = os.path.join(SCRIPT_DIR, 'us_account_data.json')
    with open(out_path, 'w') as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    print(f"\nSaved to {out_path}")
    return results

if __name__ == '__main__':
    main()
