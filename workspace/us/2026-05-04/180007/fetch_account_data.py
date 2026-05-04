import sys, os, json
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../../.claude/skills/moomoo-trading'))
sys.path.append(SKILL_DIR)

from dotenv import load_dotenv
load_dotenv(os.path.join(SCRIPT_DIR, '../../../../.env.local'))

from scripts import get_account_info, get_positions, get_order_list, make_serializable
import moomoo as ft

# Account info
account = get_account_info(trading_env='REAL')
print("=== ACCOUNT ===")
print(json.dumps(make_serializable(account), ensure_ascii=False, indent=2))

# Positions
positions = get_positions(trading_env='REAL')
print("=== POSITIONS ===")
print(json.dumps(make_serializable(positions), ensure_ascii=False, indent=2))

# Today's orders
orders = get_order_list(trading_env='REAL')
print("=== ORDERS ===")
print(json.dumps(make_serializable(orders), ensure_ascii=False, indent=2))

# USStocks watchlist
MOOMOO_HOST = os.getenv('MOOMOO_HOST', '127.0.0.1')
MOOMOO_PORT = int(os.getenv('MOOMOO_PORT', '11111'))
ctx = ft.OpenQuoteContext(host=MOOMOO_HOST, port=MOOMOO_PORT)
ret, watchlist = ctx.get_user_security(group_name='USStocks')
ctx.close()
if ret == ft.RET_OK:
    print("=== WATCHLIST ===")
    print(json.dumps(make_serializable(watchlist), ensure_ascii=False, indent=2))
else:
    print(f"=== WATCHLIST ERROR: {watchlist} ===")
