"""
connection.py — Moomoo OpenD Connection Manager

Handles connection lifecycle, health checks, and provides context managers
for both quote and trading API clients.
"""

import moomoo as ft
from contextlib import contextmanager


# ── Default connection parameters ───────────────────────────────────────────
OPEND_HOST = '127.0.0.1'
OPEND_PORT = 11111


class MoomooConnection:
    """
    Manages OpenD connections for both quote and trading operations.

    Usage (recommended — context manager):
        with MoomooConnection.quote_ctx() as ctx:
            ret, data = ctx.get_market_snapshot(['US.NVDA'])

        with MoomooConnection.trade_ctx() as ctx:
            ret, data = ctx.unlock_trade(password='...')
    """

    @staticmethod
    def check_health(host=OPEND_HOST, port=OPEND_PORT) -> dict:
        """
        Verify OpenD is reachable and return status info.

        Returns:
            dict with keys: connected (bool), message (str), version (str|None)
        """
        try:
            ctx = ft.OpenQuoteContext(host=host, port=port)
            ret, data = ctx.get_global_state()
            ctx.close()
            if ret == ft.RET_OK:
                return {'connected': True, 'message': 'OpenD reachable', 'data': data}
            else:
                return {'connected': False, 'message': f'OpenD error: {data}', 'data': None}
        except Exception as e:
            return {
                'connected': False,
                'message': (
                    f'Cannot connect to OpenD at {host}:{port}. '
                    f'Make sure OpenD is running. Error: {e}'
                ),
                'data': None
            }

    @staticmethod
    @contextmanager
    def quote_ctx(host=OPEND_HOST, port=OPEND_PORT):
        """Context manager for quote API. Auto-closes on exit."""
        ctx = ft.OpenQuoteContext(host=host, port=port)
        try:
            yield ctx
        finally:
            ctx.close()

    @staticmethod
    @contextmanager
    def trade_ctx(market=ft.TrdMarket.US, host=OPEND_HOST, port=OPEND_PORT):
        """
        Context manager for trading API.

        Args:
            market: ft.TrdMarket.US | ft.TrdMarket.HK | ft.TrdMarket.SG
        """
        ctx = ft.OpenSecTradeContext(
            filter_trdmarket=market,
            host=host,
            port=port,
            security_firm=ft.SecurityFirm.FUTUSECURITIES
        )
        try:
            yield ctx
        finally:
            ctx.close()


def require_opend(func):
    """
    Decorator: checks OpenD health before running the decorated function.
    Raises ConnectionError if OpenD is unreachable.
    """
    def wrapper(*args, **kwargs):
        status = MoomooConnection.check_health()
        if not status['connected']:
            raise ConnectionError(status['message'])
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper
