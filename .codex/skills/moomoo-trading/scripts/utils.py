"""
utils.py — Shared Utilities for moomoo-trading skill

Market code conversion, enum resolution, JSON serialization.
"""

import numpy as np
import pandas as pd
from datetime import date, datetime
import moomoo as ft


# ── Market Code Conversion ────────────────────────────────────────────────────

def to_moomoo_code(ticker: str, market: str = None) -> str:
    """
    Convert a bare ticker to Moomoo format.

    Examples:
        to_moomoo_code('NVDA', 'US')  → 'US.NVDA'
        to_moomoo_code('700', 'HK')   → 'HK.00700'
        to_moomoo_code('D05', 'SG')   → 'SG.D05'
        to_moomoo_code('US.AAPL')     → 'US.AAPL' (already formatted)
    """
    ticker = ticker.strip().upper()
    if '.' in ticker:
        return ticker  # Already in Moomoo format

    if market is None:
        # Auto-detect: numeric-only → probably HK
        if ticker.isdigit():
            market = 'HK'
        else:
            market = 'US'

    market = market.upper()
    if market == 'HK' and ticker.isdigit():
        ticker = ticker.zfill(5)  # HK codes are 5 digits: 700 → 00700

    return f'{market}.{ticker}'


def parse_market_from_code(moomoo_code: str) -> str:
    """Extract market from Moomoo code. 'US.NVDA' → 'US'"""
    parts = moomoo_code.split('.')
    return parts[0].upper() if len(parts) >= 2 else 'US'


def strip_market_prefix(moomoo_code: str) -> str:
    """'US.NVDA' → 'NVDA'"""
    parts = moomoo_code.split('.', 1)
    return parts[1] if len(parts) == 2 else moomoo_code


# ── Enum Resolution ───────────────────────────────────────────────────────────

def resolve_trd_env(trading_env: str):
    """'SIMULATE' → ft.TrdEnv.SIMULATE, 'REAL' → ft.TrdEnv.REAL"""
    env_map = {
        'SIMULATE': ft.TrdEnv.SIMULATE,
        'SIM':      ft.TrdEnv.SIMULATE,
        'PAPER':    ft.TrdEnv.SIMULATE,
        'REAL':     ft.TrdEnv.REAL,
        'LIVE':     ft.TrdEnv.REAL,
    }
    env = env_map.get(str(trading_env).upper())
    if env is None:
        raise ValueError(f"trading_env must be 'SIMULATE' or 'REAL', got '{trading_env}'")
    return env


def resolve_trd_market(market: str):
    """'US' → ft.TrdMarket.US, etc."""
    market_map = {
        'US': ft.TrdMarket.US,
        'HK': ft.TrdMarket.HK,
        'SG': ft.TrdMarket.SG,
        'CN': ft.TrdMarket.CN,
    }
    m = market_map.get(str(market).upper())
    if m is None:
        raise ValueError(f"market must be one of US/HK/SG/CN, got '{market}'")
    return m


# ── JSON Serialization ────────────────────────────────────────────────────────

def make_serializable(obj):
    """
    Recursively convert objects to JSON-serializable types.
    Identical to quantitative-trading utils.make_serializable.
    """
    if isinstance(obj, (np.integer, int)):
        return int(obj)
    elif isinstance(obj, (np.floating, float)):
        return float(obj)
    elif isinstance(obj, (np.bool_, bool)):
        return bool(obj)
    elif isinstance(obj, np.ndarray):
        return make_serializable(obj.tolist())
    elif isinstance(obj, (pd.Series, pd.DataFrame)):
        return make_serializable(obj.to_dict())
    elif isinstance(obj, (datetime, date, pd.Timestamp)):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: make_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [make_serializable(item) for item in obj]
    elif obj is None:
        return None
    else:
        return str(obj)
