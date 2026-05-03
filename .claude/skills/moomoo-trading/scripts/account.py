"""
account.py — Account & Position Management

Query account info, positions, and cash balance from Moomoo OpenD.
All functions default to SIMULATE (paper trading) mode.
"""

import pandas as pd
import moomoo as ft
from .connection import MoomooConnection, require_opend
from .utils import resolve_trd_env, resolve_trd_market


@require_opend
def get_account_info(trading_env: str = 'SIMULATE', market: str = 'US') -> dict:
    """
    Get account summary: total assets, cash, market value, buying power.

    Args:
        trading_env: 'SIMULATE' (default) or 'REAL'
        market:      'US', 'HK', or 'SG'

    Returns:
        dict with keys: total_assets, cash, market_val, frozen_cash,
                        available_funds, unrealized_pl, realized_pl, currency
    """
    env = resolve_trd_env(trading_env)
    trd_market = resolve_trd_market(market)

    with MoomooConnection.trade_ctx(market=trd_market) as ctx:
        ret, data = ctx.accinfo_query(trd_env=env, currency=ft.Currency.USD)
        if ret != ft.RET_OK:
            raise RuntimeError(f'accinfo_query failed: {data}')

    if data.empty:
        return {}

    row = data.iloc[0].to_dict()
    return {
        'total_assets':    row.get('total_assets', 0),
        'cash':            row.get('cash', 0),
        'market_val':      row.get('market_val', 0),
        'frozen_cash':     row.get('frozen_cash', 0),
        'available_funds': row.get('available_funds', 0),
        'unrealized_pl':   row.get('unrealized_pl', 0),
        'realized_pl':     row.get('realized_pl', 0),
        'currency':        row.get('currency', 'USD'),
        'trading_env':     trading_env,
    }


@require_opend
def get_positions(trading_env: str = 'SIMULATE', market: str = 'US', ticker: str = None) -> pd.DataFrame:
    """
    Get current holdings with P&L.

    Args:
        trading_env: 'SIMULATE' or 'REAL'
        market:      'US', 'HK', or 'SG'
        ticker:      Filter by specific Moomoo code (e.g. 'US.NVDA'), or None for all

    Returns:
        pd.DataFrame with columns:
            code, stock_name, qty, can_sell_qty, cost_price,
            market_val, nominal_price, pl_ratio, pl_val, currency
    """
    env = resolve_trd_env(trading_env)
    trd_market = resolve_trd_market(market)

    with MoomooConnection.trade_ctx(market=trd_market) as ctx:
        ret, data = ctx.position_list_query(
            code=ticker or '',
            trd_env=env
        )
        if ret != ft.RET_OK:
            raise RuntimeError(f'position_list_query failed: {data}')

    if data.empty:
        return pd.DataFrame()

    cols = [
        'code', 'stock_name', 'qty', 'can_sell_qty', 'cost_price',
        'market_val', 'nominal_price', 'pl_ratio', 'pl_val', 'currency'
    ]
    available = [c for c in cols if c in data.columns]
    return data[available].reset_index(drop=True)


@require_opend
def get_cash_info(trading_env: str = 'SIMULATE', market: str = 'US') -> dict:
    """
    Get cash balance breakdown (available, frozen, total).

    Returns:
        dict with cash, frozen_cash, available_funds, currency
    """
    info = get_account_info(trading_env=trading_env, market=market)
    return {
        'cash':            info.get('cash', 0),
        'frozen_cash':     info.get('frozen_cash', 0),
        'available_funds': info.get('available_funds', 0),
        'currency':        info.get('currency', 'USD'),
    }


def print_account_summary(trading_env: str = 'SIMULATE', market: str = 'US'):
    """
    Print a human-readable account + positions summary. Useful for quick inspection.
    """
    info = get_account_info(trading_env=trading_env, market=market)
    positions = get_positions(trading_env=trading_env, market=market)

    env_label = '🟡 SIMULATE' if trading_env == 'SIMULATE' else '🔴 REAL'
    print(f'\n═══ Account Summary ({env_label} | {market}) ═══')
    print(f"  Total Assets:    {info.get('currency','')} {info.get('total_assets', 0):,.2f}")
    print(f"  Market Value:    {info.get('currency','')} {info.get('market_val', 0):,.2f}")
    print(f"  Cash:            {info.get('currency','')} {info.get('cash', 0):,.2f}")
    print(f"  Available Funds: {info.get('currency','')} {info.get('available_funds', 0):,.2f}")
    print(f"  Unrealized P&L:  {info.get('currency','')} {info.get('unrealized_pl', 0):+,.2f}")

    if not positions.empty:
        print(f'\n  Holdings ({len(positions)} positions):')
        for _, row in positions.iterrows():
            pl_sign = '+' if row.get('pl_val', 0) >= 0 else ''
            print(
                f"    {row.get('code',''):15s} {row.get('stock_name',''):12s} "
                f"qty={int(row.get('qty',0)):6d}  "
                f"cost={row.get('cost_price',0):.2f}  "
                f"now={row.get('nominal_price',0):.2f}  "
                f"P&L={pl_sign}{row.get('pl_val',0):.2f} ({row.get('pl_ratio',0):.1%})"
            )
    else:
        print('\n  No open positions.')
    print()
