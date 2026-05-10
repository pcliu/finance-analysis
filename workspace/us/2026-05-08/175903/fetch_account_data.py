"""
Step 1: Fetch all account data from Moomoo OpenD
- Account info (REAL)
- Positions (REAL)
- Orders today (REAL)
- USStocks watchlist
- Realtime quotes for all symbols
"""

import sys
import os
import json
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../../.claude/skills/moomoo-trading'))
sys.path.insert(0, SKILL_DIR)

from scripts import (
    get_account_info, get_positions, get_order_list,
    get_realtime_quote, MoomooConnection, make_serializable
)
import moomoo as ft

print("=== Step 1: Account Info ===")
account = get_account_info(trading_env='REAL', market='US')
print(json.dumps(account, indent=2, default=make_serializable))

print("\n=== Step 2: Positions ===")
positions = get_positions(trading_env='REAL', market='US')
print(positions.to_string())
positions_data = positions.to_dict(orient='records')

print("\n=== Step 3: Today's Orders ===")
orders = get_order_list(trading_env='REAL', market='US')
if hasattr(orders, 'to_dict'):
    orders_data = orders.to_dict(orient='records')
    print(orders.to_string())
else:
    orders_data = []
    print("No orders or error")

print("\n=== Step 4: USStocks Watchlist ===")
with MoomooConnection.quote_ctx() as ctx:
    ret, watchlist_df = ctx.get_user_security(group_name='USStocks')
    if ret == ft.RET_OK:
        print(watchlist_df.to_string())
        watchlist_data = watchlist_df.to_dict(orient='records')
    else:
        print(f"Failed to get watchlist: {watchlist_df}")
        watchlist_data = []

print("\n=== Step 5: Realtime Quotes ===")
# Collect all symbols: positions + watchlist
position_codes = [p['code'] for p in positions_data if 'code' in p]
watchlist_codes = [w['code'] for w in watchlist_data if 'code' in w]
all_codes = list(set(position_codes + watchlist_codes))
print(f"All codes to quote: {all_codes}")

quotes_data = []
if all_codes:
    quotes_df = get_realtime_quote(all_codes)
    print(quotes_df.to_string())
    quotes_data = quotes_df.to_dict(orient='records')

# Save everything
output = {
    'timestamp': datetime.now().isoformat(),
    'account': account,
    'positions': positions_data,
    'orders': orders_data,
    'watchlist': watchlist_data,
    'realtime_quotes': quotes_data,
    'all_codes': all_codes,
}

out_path = os.path.join(SCRIPT_DIR, 'us_account_data.json')
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, default=make_serializable, ensure_ascii=False)

print(f"\n✓ Saved to {out_path}")
