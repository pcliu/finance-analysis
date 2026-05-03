"""
Moomoo Trading Skill — Unified Exports

All public functions are importable directly from `scripts`.

Quick import pattern (from a workspace script):
    import sys, os
    SKILL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../.claude/skills/moomoo-trading'))
    sys.path.append(SKILL_DIR)
    from scripts import get_realtime_quote, get_kline_data, place_order, ...
"""

# Connection
from .connection import MoomooConnection, require_opend

# Data
from .data_fetcher import (
    get_realtime_quote,
    get_order_book,
    get_kline_data,
    get_multiple_klines,
    get_stock_basicinfo,
)

# Indicators (compatible with quantitative-trading)
from .indicators import (
    calculate_rsi,
    calculate_sma,
    calculate_ema,
    calculate_macd,
    calculate_bollinger_bands,
    calculate_atr,
    calculate_stochastic,
    calculate_all,
)

# Account
from .account import (
    get_account_info,
    get_positions,
    get_cash_info,
    print_account_summary,
)

# Orders
from .order_manager import (
    place_order,
    cancel_order,
    modify_order,
    cancel_all_orders,
    get_order_list,
    get_order_detail,
    save_order_log,
    order_log,
)

# Utils
from .utils import (
    to_moomoo_code,
    parse_market_from_code,
    strip_market_prefix,
    resolve_trd_env,
    resolve_trd_market,
    make_serializable,
)

__all__ = [
    # Connection
    'MoomooConnection', 'require_opend',
    # Data
    'get_realtime_quote', 'get_order_book', 'get_kline_data',
    'get_multiple_klines', 'get_stock_basicinfo',
    # Indicators
    'calculate_rsi', 'calculate_sma', 'calculate_ema', 'calculate_macd',
    'calculate_bollinger_bands', 'calculate_atr', 'calculate_stochastic',
    'calculate_all',
    # Account
    'get_account_info', 'get_positions', 'get_cash_info', 'print_account_summary',
    # Orders
    'place_order', 'cancel_order', 'modify_order', 'cancel_all_orders',
    'get_order_list', 'get_order_detail', 'save_order_log', 'order_log',
    # Utils
    'to_moomoo_code', 'parse_market_from_code', 'strip_market_prefix',
    'resolve_trd_env', 'resolve_trd_market', 'make_serializable',
]
