#!/usr/bin/env python3
"""Place confirmed orders: IAU x8 @ 88.30, NVDA x5 @ 207.83"""
import sys, os, json
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../../.claude/skills/moomoo-trading'))
sys.path.insert(0, SKILL_DIR)

from scripts import place_order, make_serializable

ORDERS = [
    {'ticker': 'US.IAU',  'qty': 8,  'price': 88.30,  'direction': 'BUY'},
    {'ticker': 'US.NVDA', 'qty': 5,  'price': 207.83, 'direction': 'BUY'},
]

def main():
    results = []
    for o in ORDERS:
        print(f"\n{'='*50}")
        print(f"下单: {o['direction']} {o['ticker']} x{o['qty']} @ ${o['price']}")
        print(f"预估金额: ${o['qty'] * o['price']:.2f}")
        print(f"{'='*50}")
        try:
            result = place_order(
                ticker=o['ticker'],
                direction=o['direction'],
                qty=o['qty'],
                price=o['price'],
                order_type='LIMIT',
                trading_env='REAL',
            )
            print(f"结果: {result}")
            results.append({'order': o, 'result': make_serializable(result), 'status': 'ok', 'time': datetime.now().isoformat()})
        except Exception as e:
            print(f"错误: {e}")
            results.append({'order': o, 'error': str(e), 'status': 'error', 'time': datetime.now().isoformat()})

    out_path = os.path.join(SCRIPT_DIR, 'us_orders_log.json')
    with open(out_path, 'w') as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    print(f"\n订单日志已保存至 {out_path}")

if __name__ == '__main__':
    main()
