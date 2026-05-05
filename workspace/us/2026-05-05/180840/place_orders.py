import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../../.claude/skills/moomoo-trading'))
sys.path.append(SKILL_DIR)

from scripts import get_realtime_quote, place_order, make_serializable
import json

# 获取最新实时价
tickers = ['US.SLV', 'US.TSM']
quotes = get_realtime_quote(tickers)
print("\n=== 最新实时报价 ===")
print(quotes[['code', 'last_price', 'volume', 'update_time']].to_string())

# 用 last_price + 小缓冲确保限价单能成交
slv_last = float(quotes[quotes['code'] == 'US.SLV']['last_price'].values[0])
tsm_last = float(quotes[quotes['code'] == 'US.TSM']['last_price'].values[0])
slv_price = round(slv_last + 0.05, 2)
tsm_price = round(tsm_last + 0.05, 2)

print(f"\nSLV ask: {slv_price}")
print(f"TSM ask: {tsm_price}")

# 打印订单摘要
print("\n" + "="*60)
print("           完整订单摘要（待执行）")
print("="*60)
print(f"订单 1 | SLV | 买入 | 10 股 | 限价 {slv_price:.2f} USD")
print(f"       | 预估总金额: {slv_price * 10:.2f} USD")
print(f"订单 2 | TSM | 买入 | 2  股 | 限价 {tsm_price:.2f} USD")
print(f"       | 预估总金额: {tsm_price * 2:.2f} USD")
print(f"       合计预估: {slv_price * 10 + tsm_price * 2:.2f} USD")
print("="*60)

# 执行订单
orders_result = []

print("\n[1/2] 提交 SLV 订单...")
result_slv = place_order(
    ticker='US.SLV',
    direction='BUY',
    qty=10,
    price=slv_price,
    order_type='LIMIT',
    trading_env='REAL'
)
print(f"SLV 结果: {result_slv}")
orders_result.append({'ticker': 'US.SLV', 'result': make_serializable(result_slv)})

print("\n[2/2] 提交 TSM 订单...")
result_tsm = place_order(
    ticker='US.TSM',
    direction='BUY',
    qty=2,
    price=tsm_price,
    order_type='LIMIT',
    trading_env='REAL'
)
print(f"TSM 结果: {result_tsm}")
orders_result.append({'ticker': 'US.TSM', 'result': make_serializable(result_tsm)})

# 保存订单记录
out_path = os.path.join(SCRIPT_DIR, 'orders_log.json')
with open(out_path, 'w') as f:
    json.dump(orders_result, f, ensure_ascii=False, indent=2)
print(f"\n订单记录已保存: {out_path}")
