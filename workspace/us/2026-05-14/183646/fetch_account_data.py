"""
fetch_account_data.py — 获取美股账户快照：资金、持仓、订单、关注列表
输出: us_account_data.json
"""
import sys, os, json
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../../.claude/skills/moomoo-trading'))
sys.path.insert(0, SKILL_DIR)

from scripts import get_account_info, get_positions, get_order_list, make_serializable
import moomoo as ft

# ── 加载 .env.local ──────────────────────────────────────────────
from dotenv import load_dotenv
env_path = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../../.env.local'))
load_dotenv(env_path)
TRADE_PWD = os.environ.get('MOOMOO_TRADE_PASSWORD', '')

HOST = os.environ.get('MOOMOO_HOST', '127.0.0.1')
PORT = int(os.environ.get('MOOMOO_PORT', 11111))

# ── 1. 账户资金 ──────────────────────────────────────────────────
print("Fetching account info (REAL)...")
account = get_account_info(trading_env='REAL', market='US')
print(f"  Total assets: {account.get('total_assets', 0):,.2f} USD")
print(f"  Market val:   {account.get('market_val', 0):,.2f} USD")
print(f"  Cash:         {account.get('cash', 0):,.2f} USD")

# 可投资金额 = 总资产 - 股票持仓市值
investable = account.get('total_assets', 0) - account.get('market_val', 0)
account['investable_amount'] = investable
print(f"  Investable:   {investable:,.2f} USD (total_assets - market_val)")

# ── 2. 当前持仓 ──────────────────────────────────────────────────
print("\nFetching positions (REAL)...")
positions_df = get_positions(trading_env='REAL', market='US')
if not positions_df.empty:
    positions = positions_df.to_dict('records')
    print(f"  Found {len(positions)} positions:")
    for p in positions:
        print(f"    {p.get('code'):15s} qty={int(p.get('qty',0)):6d}  cost={p.get('cost_price',0):.2f}  nominal={p.get('nominal_price',0):.2f}")
else:
    positions = []
    print("  No open positions.")

# ── 3. 今日订单 ──────────────────────────────────────────────────
print("\nFetching today's orders (REAL)...")
orders_df = get_order_list(trading_env='REAL')
if orders_df is not None and not orders_df.empty:
    orders = orders_df.to_dict('records')
    print(f"  Found {len(orders)} orders today.")
else:
    orders = []
    print("  No orders today.")

# ── 4. USStocks 关注列表 ──────────────────────────────────────────
print("\nFetching USStocks watchlist...")
try:
    ctx = ft.OpenQuoteContext(host=HOST, port=PORT)
    ret, watchlist_df = ctx.get_user_security('USStocks')
    ctx.close()
    if ret == ft.RET_OK and watchlist_df is not None and not watchlist_df.empty:
        watchlist = watchlist_df[['code', 'name']].to_dict('records') if 'name' in watchlist_df.columns else watchlist_df[['code']].to_dict('records')
        print(f"  Found {len(watchlist)} symbols in USStocks:")
        for w in watchlist:
            print(f"    {w.get('code')}  {w.get('name','')}")
    else:
        watchlist = []
        print(f"  Warning: get_user_security returned ret={ret}")
except Exception as e:
    watchlist = []
    print(f"  Error fetching watchlist: {e}")

# ── 5. 保存 JSON ──────────────────────────────────────────────────
output = {
    'snapshot_time': datetime.now().isoformat(),
    'account': make_serializable(account),
    'positions': make_serializable(positions),
    'orders': make_serializable(orders),
    'watchlist': make_serializable(watchlist),
    'investable_amount': investable,
}

out_path = os.path.join(SCRIPT_DIR, 'us_account_data.json')
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\nSaved: {out_path}")
print(f"Snapshot time: {output['snapshot_time']}")
