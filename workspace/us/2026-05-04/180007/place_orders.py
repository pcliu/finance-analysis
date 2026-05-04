import sys, os, json
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../../.claude/skills/moomoo-trading'))
sys.path.append(SKILL_DIR)

from dotenv import load_dotenv
load_dotenv(os.path.join(SCRIPT_DIR, '../../../../.env.local'))

from scripts import place_order, make_serializable

orders_to_place = [
    {"ticker": "US.NVDA", "direction": "BUY", "qty": 5,  "price": 198.45},
    {"ticker": "US.IAU",  "direction": "BUY", "qty": 5,  "price": 86.72},
]

results = []
for o in orders_to_place:
    print(f"\n>>> Placing order: {o['direction']} {o['qty']} x {o['ticker']} @ ${o['price']}")
    try:
        result = place_order(
            ticker=o["ticker"],
            direction=o["direction"],
            qty=o["qty"],
            price=o["price"],
            order_type="LIMIT",
            trading_env="REAL",
        )
        print(f"    Result: {result}")
        results.append({"order": o, "result": make_serializable(result)})
    except Exception as e:
        print(f"    ERROR: {e}")
        results.append({"order": o, "error": str(e)})

out_path = os.path.join(SCRIPT_DIR, 'order_results.json')
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(f"\nOrder results saved to {out_path}")
