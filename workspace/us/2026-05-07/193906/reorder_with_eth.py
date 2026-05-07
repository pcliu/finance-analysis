#!/usr/bin/env python3
"""Cancel wrong orders and re-place with fill_outside_rth=True."""
import sys, os, json
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../../.claude/skills/moomoo-trading'))
sys.path.insert(0, SKILL_DIR)

from scripts.connection import MoomooConnection
from scripts.utils import resolve_trd_env, parse_market_from_code, resolve_trd_market
from scripts import cancel_order as skill_cancel_order
import moomoo as ft

CANCEL_ORDER_IDS = [
    'FS1C7B521EA47A1000',  # IAU
    'FS1C7B521F45BA1000',  # NVDA
]

ORDERS = [
    {'ticker': 'US.IAU',  'qty': 8,  'price': 88.30,  'direction': ft.TrdSide.BUY},
    {'ticker': 'US.NVDA', 'qty': 5,  'price': 207.83, 'direction': ft.TrdSide.BUY},
]

def cancel_order(order_id):
    result = skill_cancel_order(order_id, trading_env='REAL', market='US')
    return result['success'], result

def place_with_eth(ticker, qty, price, direction):
    market = parse_market_from_code(ticker)
    trd_market = resolve_trd_market(market)
    env = resolve_trd_env('REAL')
    with MoomooConnection.trade_ctx(market=trd_market) as ctx:
        ret, data = ctx.place_order(
            price=float(price),
            qty=qty,
            code=ticker,
            trd_side=direction,
            order_type=ft.OrderType.NORMAL,
            trd_env=env,
            time_in_force=ft.TimeInForce.DAY,
            fill_outside_rth=True,
        )
    return ret, data

def main():
    log = []

    # Step 1: Cancel existing orders
    print("=== 取消原始订单 ===")
    for oid in CANCEL_ORDER_IDS:
        ret, data = cancel_order(oid)
        log.append({'action': 'cancel', 'order_id': oid, 'ret': ret, 'time': datetime.now().isoformat()})

    # Step 2: Re-place with fill_outside_rth=True
    print("\n=== 重新下单（fill_outside_rth=True） ===")
    for o in ORDERS:
        print(f"\n下单: {'BUY'} {o['ticker']} x{o['qty']} @ ${o['price']}")
        print(f"  fill_outside_rth=True, order_type=NORMAL(限价), trd_env=REAL")
        ret, data = place_with_eth(o['ticker'], o['qty'], o['price'], o['direction'])
        if ret == ft.RET_OK:
            order_id = data['order_id'].iloc[0] if not data.empty else 'unknown'
            print(f"  ✅ 提交成功 order_id={order_id}")
            log.append({
                'action': 'place', 'ticker': o['ticker'], 'qty': o['qty'],
                'price': o['price'], 'fill_outside_rth': True,
                'order_id': str(order_id), 'status': 'ok',
                'time': datetime.now().isoformat()
            })
        else:
            print(f"  ❌ 提交失败: {data}")
            log.append({
                'action': 'place', 'ticker': o['ticker'],
                'error': str(data), 'status': 'error',
                'time': datetime.now().isoformat()
            })

    out = os.path.join(SCRIPT_DIR, 'us_orders_log.json')
    with open(out, 'w') as f:
        json.dump(log, f, ensure_ascii=False, indent=2)
    print(f"\n日志已保存: {out}")

if __name__ == '__main__':
    main()
