import sys, os, json
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../../.claude/skills/moomoo-trading'))
sys.path.append(SKILL_DIR)

from dotenv import load_dotenv
load_dotenv(os.path.join(SCRIPT_DIR, '../../../../.env.local'))

from scripts import cancel_order, make_serializable
from scripts.connection import MoomooConnection, require_opend
from scripts.utils import resolve_trd_env, resolve_trd_market
import moomoo as ft

ORDERS_TO_CANCEL = [
    {"order_id": "FS1C775F6A9F127000", "ticker": "US.NVDA"},
    {"order_id": "FS1C775F6AFED27000", "ticker": "US.IAU"},
]

NEW_ORDERS = [
    {"ticker": "US.NVDA", "qty": 5, "price": 198.45},
    {"ticker": "US.IAU",  "qty": 5, "price": 86.72},
]

results = {"cancelled": [], "resubmitted": []}

# Step 1: 撤销原单
print("=== Step 1: 撤销原 RTH 订单 ===")
for o in ORDERS_TO_CANCEL:
    r = cancel_order(o["order_id"], trading_env="REAL", market="US")
    results["cancelled"].append(r)

# Step 2: 重新提交盘前单（fill_outside_rth=True）
print("\n=== Step 2: 重新提交盘前订单（fill_outside_rth=True）===")
env = resolve_trd_env("REAL")
trd_market = resolve_trd_market("US")

for o in NEW_ORDERS:
    print(f"\n>>> 提交盘前限价单: BUY {o['qty']} x {o['ticker']} @ ${o['price']}")
    with MoomooConnection.trade_ctx(market=trd_market) as ctx:
        ret, data = ctx.place_order(
            price=float(o["price"]),
            qty=o["qty"],
            code=o["ticker"],
            trd_side=ft.TrdSide.BUY,
            order_type=ft.OrderType.NORMAL,
            trd_env=env,
            fill_outside_rth=True,   # 允许盘前/盘后成交
        )
    if ret == ft.RET_OK:
        order_id = str(data["order_id"].iloc[0])
        print(f"    ✅ 下单成功 order_id={order_id}")
        results["resubmitted"].append({
            "success": True, "ticker": o["ticker"],
            "qty": o["qty"], "price": o["price"],
            "order_id": order_id, "fill_outside_rth": True,
        })
    else:
        print(f"    ❌ 下单失败: {data}")
        results["resubmitted"].append({
            "success": False, "ticker": o["ticker"], "error": str(data),
        })

out = os.path.join(SCRIPT_DIR, "premarket_order_results.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(f"\n结果已保存至 {out}")
