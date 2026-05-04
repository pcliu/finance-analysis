import sys, os, json
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../../.claude/skills/moomoo-trading'))
sys.path.append(SKILL_DIR)

from dotenv import load_dotenv
load_dotenv(os.path.join(SCRIPT_DIR, '../../../../.env.local'))

from scripts import get_realtime_quote, get_order_list, make_serializable

# 1. 当前实时行情（盘前）
print("=== 当前实时行情 ===")
quotes = get_realtime_quote(['US.NVDA', 'US.IAU'])
print(json.dumps(make_serializable(quotes), ensure_ascii=False, indent=2))

# 2. 当前订单状态
print("\n=== 当前订单状态 ===")
orders = get_order_list(trading_env='REAL')
print(json.dumps(make_serializable(orders), ensure_ascii=False, indent=2))
