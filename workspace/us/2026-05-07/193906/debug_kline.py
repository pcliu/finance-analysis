#!/usr/bin/env python3
import sys, os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../../.claude/skills/moomoo-trading'))
sys.path.insert(0, SKILL_DIR)
from scripts import get_kline_data, get_realtime_quote
import moomoo as ft

kline = get_kline_data('US.NVDA', ktype=ft.KLType.K_DAY, count=5)
print("Columns:", kline.columns.tolist())
print(kline.head(3))

quote = get_realtime_quote(['US.NVDA'])
print("\nQuote columns:", quote.columns.tolist())
print(quote.head(2))
