import sys
import os
import json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../../.claude/skills/moomoo-trading'))
sys.path.append(SKILL_DIR)

from scripts import (
    get_positions, get_account_info, get_order_list,
    get_realtime_quote, make_serializable
)
import moomoo as ft
from dotenv import load_dotenv

load_dotenv(os.path.join(SCRIPT_DIR, '../../../../.env.local'))

# 1. Account info
print("=== Account Info ===")
account = get_account_info(trading_env='REAL')
print(account)

# 2. Positions
print("\n=== Positions ===")
positions = get_positions(trading_env='REAL')
print(positions)

# 3. Today's orders
print("\n=== Orders ===")
orders = get_order_list(trading_env='REAL')
print(orders)

# 4. USStocks watchlist
print("\n=== USStocks Watchlist ===")
host = os.getenv('MOOMOO_HOST', '127.0.0.1')
port = int(os.getenv('MOOMOO_PORT', '11111'))
ctx = ft.OpenQuoteContext(host=host, port=port)
ret, watchlist = ctx.get_user_security(group_name='USStocks')
ctx.close()
if ret == ft.RET_OK:
    print(watchlist)
else:
    print(f"Error: {watchlist}")

# Save all data
data = {
    'account': make_serializable(account),
    'positions': make_serializable(positions),
    'orders': make_serializable(orders),
    'watchlist': make_serializable(watchlist) if ret == ft.RET_OK else []
}

out_path = os.path.join(SCRIPT_DIR, 'us_account_data.json')
with open(out_path, 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f"\nSaved to {out_path}")
