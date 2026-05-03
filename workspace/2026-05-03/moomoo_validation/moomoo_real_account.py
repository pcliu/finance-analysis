import sys, os, json
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
HOST, PORT = '127.0.0.1', 11111

import moomoo as ft

print("=" * 55)
print("  Moomoo 真实账户信息查询")
print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 55)

ctx = ft.OpenSecTradeContext(
    filter_trdmarket=ft.TrdMarket.US,
    host=HOST, port=PORT,
    security_firm=ft.SecurityFirm.FUTUSG
)

# ── 账户资金 ────────────────────────────────────────────────
print("\n[账户资金]")
ret, data = ctx.accinfo_query(trd_env=ft.TrdEnv.REAL)
if ret == ft.RET_OK:
    row = data.iloc[0]
    print(data.T.to_string())
else:
    print(f"  ❌ 查询失败: {data}")

# ── 当前持仓 ────────────────────────────────────────────────
print("\n[当前持仓]")
ret, data = ctx.position_list_query(trd_env=ft.TrdEnv.REAL)
if ret == ft.RET_OK:
    if len(data) == 0:
        print("  (无持仓)")
    else:
        cols = ['code', 'stock_name', 'qty', 'can_sell_qty', 'cost_price', 'market_val', 'pl_ratio']
        available = [c for c in cols if c in data.columns]
        print(data[available].to_string(index=False))
else:
    print(f"  ❌ 查询失败: {data}")

# ── 今日订单 ────────────────────────────────────────────────
print("\n[今日订单]")
ret, data = ctx.order_list_query(trd_env=ft.TrdEnv.REAL)
if ret == ft.RET_OK:
    if len(data) == 0:
        print("  (今日无订单)")
    else:
        cols = ['code', 'trd_side', 'order_type', 'order_status', 'qty', 'price', 'create_time']
        available = [c for c in cols if c in data.columns]
        print(data[available].to_string(index=False))
else:
    print(f"  ❌ 查询失败: {data}")

ctx.close()
print("\n" + "=" * 55)
