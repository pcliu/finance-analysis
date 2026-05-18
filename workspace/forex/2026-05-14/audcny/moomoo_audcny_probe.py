"""Probe AUDCNY forex code on Moomoo and fetch quote + K-line."""
import sys, os, json
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = '/Users/liupengcheng/Code/finance-analysis/.claude/skills/moomoo-trading'
sys.path.append(SKILL_DIR)

import moomoo as ft
from scripts.connection import MoomooConnection

candidates = [
    'FX.AUDCNY', 'FX.CNYAUD',
    'CC.AUDCNY', 'CC.CNYAUD',
    'AUDCNY', 'CNYAUD',
    'FX_AUDCNY', 'FX.AUDCNH',
    'CC.AUDCNH', 'CC.AUDUSD',
    'FX.AUDUSD',
]

quote_ctx = ft.OpenQuoteContext(host='127.0.0.1', port=11111)
print("== subscribe / get_market_snapshot probes ==")
for code in candidates:
    ret, data = quote_ctx.get_market_snapshot([code])
    print(f"{code:20s} ret={ret} data={ (data if ret!=0 else (data.iloc[0].to_dict() if hasattr(data,'iloc') and len(data) else data)) }"[:200])

print("\n== subscribe + history k-line probes ==")
for code in ['FX.AUDCNH', 'CC.AUDCNH', 'FX.AUDUSD']:
    ret, data, _ = quote_ctx.request_history_kline(code, ktype=ft.KLType.K_DAY, max_count=5)
    print(f"{code:15s} ret={ret} -> {data if ret!=0 else data.tail().to_dict('records')}"[:300])

quote_ctx.close()
