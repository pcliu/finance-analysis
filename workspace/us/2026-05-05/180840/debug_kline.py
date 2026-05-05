import sys, os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../../.claude/skills/moomoo-trading'))
sys.path.append(SKILL_DIR)
from scripts import get_kline_data
import moomoo as ft

kline = get_kline_data('US.NVDA', ktype=ft.KLType.K_DAY, count=10)
print("Columns:", kline.columns.tolist())
print(kline.tail(3))
