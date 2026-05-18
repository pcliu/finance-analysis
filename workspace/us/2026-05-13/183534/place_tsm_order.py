"""
place_tsm_order.py — 买入 US.TSM 2 股，限价 $397.28，REAL 环境
"""
import sys, os, json
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../../.claude/skills/moomoo-trading'))
sys.path.insert(0, SKILL_DIR)

from dotenv import load_dotenv
load_dotenv(os.path.abspath(os.path.join(SCRIPT_DIR, '../../../../.env.local')))

from scripts import make_serializable
from scripts.connection import MoomooConnection
import moomoo as ft

TICKER   = 'US.TSM'
QTY      = 2
PRICE    = 397.28
TRD_ENV  = ft.TrdEnv.REAL
TRADE_PWD = os.environ.get('MOOMOO_TRADE_PASSWORD', '')

print("=" * 50)
print("  订单摘要（真实账户）")
print("=" * 50)
print(f"  标的:     {TICKER}")
print(f"  方向:     BUY")
print(f"  数量:     {QTY} 股")
print(f"  限价:     ${PRICE:.2f}")
print(f"  预估成本: ${PRICE * QTY:.2f}")
print(f"  时段:     fill_outside_rth=True (盘前/盘中/盘后)")
print(f"  环境:     REAL")
print("=" * 50)

with MoomooConnection.trade_ctx() as ctx:
    # 解锁交易密码
    ret, data = ctx.unlock_trade(password=TRADE_PWD, is_unlock=True)
    if ret != ft.RET_OK:
        print(f"解锁失败: {data}")
        sys.exit(1)
    print("交易密码解锁成功")

    ret, data = ctx.place_order(
        price=PRICE,
        qty=QTY,
        code=TICKER,
        trd_side=ft.TrdSide.BUY,
        order_type=ft.OrderType.NORMAL,
        trd_env=TRD_ENV,
        time_in_force=ft.TimeInForce.DAY,
        fill_outside_rth=True,
    )

if ret == ft.RET_OK:
    order_id = data['order_id'].values[0] if hasattr(data, 'columns') else str(data)
    print(f"\n✅ 下单成功！Order ID: {order_id}")
    result = {
        'status': 'success',
        'order_id': str(order_id),
        'ticker': TICKER,
        'side': 'BUY',
        'qty': QTY,
        'price': PRICE,
        'estimated_cost': PRICE * QTY,
        'time': datetime.now().isoformat(),
    }
else:
    print(f"\n❌ 下单失败: {data}")
    result = {'status': 'failed', 'error': str(data), 'time': datetime.now().isoformat()}

out_path = os.path.join(SCRIPT_DIR, 'tsm_order_result.json')
with open(out_path, 'w') as f:
    json.dump(make_serializable(result), f, indent=2)
print(f"结果已保存: {out_path}")
