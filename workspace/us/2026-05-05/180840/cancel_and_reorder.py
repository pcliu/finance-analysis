import sys, os, json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../../.claude/skills/moomoo-trading'))
sys.path.append(SKILL_DIR)

from scripts import cancel_order, get_realtime_quote, make_serializable
import moomoo as ft
from dotenv import load_dotenv
load_dotenv(os.path.join(SCRIPT_DIR, '../../../../.env.local'))

import os as _os
host = _os.getenv('MOOMOO_HOST', '127.0.0.1')
port = int(_os.getenv('MOOMOO_PORT', '11111'))
trade_pwd = _os.getenv('MOOMOO_TRADE_PASSWORD', '')

# 原订单已在上次执行中取消，跳过取消步骤
print("=== 原订单已取消，直接重新下单 ===")

# ── 2. 获取最新报价 ────────────────────────────────────────
print("\n=== 最新实时报价 ===")
quotes = get_realtime_quote(['US.SLV', 'US.TSM'])
print(quotes[['code', 'last_price', 'update_time']].to_string())

slv_price = round(float(quotes[quotes['code'] == 'US.SLV']['last_price'].values[0]) + 0.05, 2)
tsm_price = round(float(quotes[quotes['code'] == 'US.TSM']['last_price'].values[0]) + 0.05, 2)

# ── 3. 重新下单（ENHANCED_LIMIT 支持盘前/盘后） ───────────────
print("\n=== 重新提交（ENHANCED_LIMIT 盘前订单）===")
ctx = ft.OpenSecTradeContext(filter_trdmarket=ft.TrdMarket.US, host=host, port=port)
ctx.unlock_trade(trade_pwd)

orders_result = []
for ticker, qty, price, label in [
    ('US.SLV', 10, slv_price, 'SLV'),
    ('US.TSM',  2, tsm_price, 'TSM'),
]:
    print(f"\n══════════════════════════════════════")
    print(f"  ORDER SUMMARY  [🔴 REAL MONEY]")
    print(f"══════════════════════════════════════")
    print(f"  Ticker:    {ticker}")
    print(f"  Direction: BUY")
    print(f"  Quantity:  {qty}")
    print(f"  Price:     {price} (ENHANCED_LIMIT / 盘前)")
    print(f"  Est. Cost: ~{price * qty:.2f} USD")
    print(f"══════════════════════════════════════")

    ret, data = ctx.place_order(
        price=price,
        qty=qty,
        code=ticker,
        trd_side=ft.TrdSide.BUY,
        order_type=ft.OrderType.NORMAL,  # 限价单，配合 fill_outside_rth=True 支持盘前
        trd_env=ft.TrdEnv.REAL,
        time_in_force=ft.TimeInForce.DAY,
        fill_outside_rth=True,
    )
    if ret == ft.RET_OK:
        order_id = data['order_id'].values[0] if hasattr(data, 'values') else data
        print(f"  ✅ 提交成功: order_id={order_id}")
        orders_result.append({'ticker': ticker, 'status': 'submitted', 'order_id': str(order_id), 'price': price, 'qty': qty})
    else:
        print(f"  ❌ 提交失败: {data}")
        orders_result.append({'ticker': ticker, 'status': 'failed', 'error': str(data)})

ctx.close()

# ── 4. 保存日志 ────────────────────────────────────────────
log_path = os.path.join(SCRIPT_DIR, 'orders_log.json')
with open(log_path, 'w') as f:
    json.dump(orders_result, f, ensure_ascii=False, indent=2)
print(f"\n记录已保存: {log_path}")
