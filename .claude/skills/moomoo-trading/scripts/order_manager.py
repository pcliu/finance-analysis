"""
order_manager.py — Order Placement & Management

🔴 SAFETY CONTRACT:
  - Default mode is SIMULATE. Real trading requires trading_env='REAL'.
  - place_order() always prints a full order summary before execution.
  - Every order attempt is logged to order_log (list) for audit trail.
  - The caller (agent script) is responsible for confirming with the user
    before calling place_order() in REAL mode.
"""

import json
import os
from datetime import datetime
import moomoo as ft
from .connection import MoomooConnection, require_opend
from .utils import resolve_trd_env, resolve_trd_market, parse_market_from_code, make_serializable

# In-memory audit log for this session
order_log = []


def _log_order(action: str, details: dict):
    """Append an order event to the session audit log."""
    order_log.append({
        'timestamp': datetime.now().isoformat(),
        'action': action,
        **details
    })


def _print_order_summary(ticker, direction, qty, price, order_type, trading_env, estimated_cost):
    """Print a formatted order summary so the agent/user can verify before execution."""
    env_label = '🟡 SIMULATE' if trading_env == 'SIMULATE' else '🔴 REAL MONEY'
    print('\n' + '═' * 50)
    print(f'  ORDER SUMMARY  [{env_label}]')
    print('═' * 50)
    print(f'  Ticker:     {ticker}')
    print(f'  Direction:  {direction}')
    print(f'  Quantity:   {qty}')
    print(f'  Price:      {price} (type: {order_type})')
    print(f'  Est. Cost:  ~{estimated_cost:,.2f} USD')
    print('═' * 50)
    if trading_env == 'REAL':
        print('  ⚠️  THIS IS A REAL ORDER. Verify before proceeding.')
    print()


@require_opend
def place_order(
    ticker: str,
    direction: str,
    qty: int,
    price: float,
    order_type: str = 'LIMIT',
    trading_env: str = 'SIMULATE',
    trd_side: str = None,
) -> dict:
    """
    Place an order. Always prints summary. Defaults to SIMULATE mode.

    Args:
        ticker:       Moomoo code, e.g. 'US.NVDA'
        direction:    'BUY' or 'SELL'
        qty:          Number of shares (must be positive integer)
        price:        Limit price (ignored for MARKET orders)
        order_type:   'LIMIT' (default) | 'MARKET' | 'STOP' | 'STOP_LIMIT'
        trading_env:  'SIMULATE' (default) | 'REAL'

    Returns:
        dict with order_id, status, message, ticker, direction, qty, price, trading_env
    """
    if qty <= 0:
        raise ValueError(f'qty must be positive, got {qty}')
    if direction.upper() not in ('BUY', 'SELL'):
        raise ValueError(f'direction must be BUY or SELL, got {direction}')

    direction = direction.upper()
    estimated_cost = qty * price

    _print_order_summary(ticker, direction, qty, price, order_type, trading_env, estimated_cost)

    # Resolve enums
    env = resolve_trd_env(trading_env)
    market = parse_market_from_code(ticker)
    trd_market = resolve_trd_market(market)

    side_map = {'BUY': ft.TrdSide.BUY, 'SELL': ft.TrdSide.SELL}
    side = side_map[direction]

    order_type_map = {
        'LIMIT':      ft.OrderType.NORMAL,
        'MARKET':     ft.OrderType.MARKET,
        'STOP':       ft.OrderType.STOP,
        'STOP_LIMIT': ft.OrderType.STOP_LIMIT,
    }
    otype = order_type_map.get(order_type.upper(), ft.OrderType.NORMAL)

    # For market orders, price is irrelevant but API requires a value
    api_price = 0.0 if order_type.upper() == 'MARKET' else float(price)

    with MoomooConnection.trade_ctx(market=trd_market) as ctx:
        ret, data = ctx.place_order(
            price=api_price,
            qty=qty,
            code=ticker,
            trd_side=side,
            order_type=otype,
            trd_env=env
        )

    if ret == ft.RET_OK:
        order_id = data['order_id'].iloc[0] if not data.empty else 'unknown'
        result = {
            'success':     True,
            'order_id':    str(order_id),
            'status':      'submitted',
            'ticker':      ticker,
            'direction':   direction,
            'qty':         qty,
            'price':       price,
            'order_type':  order_type,
            'trading_env': trading_env,
            'message':     f'Order submitted successfully. order_id={order_id}',
        }
        print(f'  ✅ {result["message"]}')
    else:
        result = {
            'success':     False,
            'order_id':    None,
            'status':      'failed',
            'ticker':      ticker,
            'direction':   direction,
            'qty':         qty,
            'price':       price,
            'trading_env': trading_env,
            'message':     f'Order failed: {data}',
        }
        print(f'  ❌ {result["message"]}')

    _log_order('place_order', result)
    return result


@require_opend
def cancel_order(order_id: str, trading_env: str = 'SIMULATE', market: str = 'US') -> dict:
    """Cancel a pending order by order_id."""
    env = resolve_trd_env(trading_env)
    trd_market = resolve_trd_market(market)

    with MoomooConnection.trade_ctx(market=trd_market) as ctx:
        ret, data = ctx.modify_order(
            modify_order_op=ft.ModifyOrderOp.CANCEL,
            order_id=order_id,
            qty=0,
            price=0,
            trd_env=env
        )

    success = ret == ft.RET_OK
    result = {
        'success':   success,
        'order_id':  order_id,
        'action':    'cancel',
        'message':   'Cancelled' if success else f'Cancel failed: {data}',
        'trading_env': trading_env,
    }
    status_icon = '✅' if success else '❌'
    print(f'  {status_icon} cancel_order({order_id}): {result["message"]}')
    _log_order('cancel_order', result)
    return result


@require_opend
def modify_order(
    order_id: str,
    qty: int,
    price: float,
    trading_env: str = 'SIMULATE',
    market: str = 'US'
) -> dict:
    """Modify qty and/or price of a pending order."""
    env = resolve_trd_env(trading_env)
    trd_market = resolve_trd_market(market)

    with MoomooConnection.trade_ctx(market=trd_market) as ctx:
        ret, data = ctx.modify_order(
            modify_order_op=ft.ModifyOrderOp.NORMAL,
            order_id=order_id,
            qty=qty,
            price=float(price),
            trd_env=env
        )

    success = ret == ft.RET_OK
    result = {
        'success':   success,
        'order_id':  order_id,
        'new_qty':   qty,
        'new_price': price,
        'message':   'Modified' if success else f'Modify failed: {data}',
        'trading_env': trading_env,
    }
    _log_order('modify_order', result)
    return result


@require_opend
def cancel_all_orders(trading_env: str = 'SIMULATE', market: str = 'US') -> list:
    """Cancel all pending orders. Returns list of cancel results."""
    orders = get_order_list(trading_env=trading_env, market=market, status_filter=['SUBMITTING', 'SUBMITTED', 'PART_FILLED'])
    results = []
    for _, row in orders.iterrows():
        results.append(cancel_order(str(row['order_id']), trading_env=trading_env, market=market))
    return results


@require_opend
def get_order_list(
    trading_env: str = 'SIMULATE',
    market: str = 'US',
    status_filter: list = None
) -> 'pd.DataFrame':
    """
    Query order history.

    Args:
        status_filter: list of status strings to filter, e.g. ['SUBMITTED', 'FILLED']
                       None returns all orders.
    """
    import pandas as pd
    env = resolve_trd_env(trading_env)
    trd_market = resolve_trd_market(market)

    with MoomooConnection.trade_ctx(market=trd_market) as ctx:
        ret, data = ctx.order_list_query(trd_env=env)
        if ret != ft.RET_OK:
            raise RuntimeError(f'order_list_query failed: {data}')

    if data.empty:
        return pd.DataFrame()

    if status_filter:
        data = data[data['order_status'].isin(status_filter)]

    return data.reset_index(drop=True)


@require_opend
def get_order_detail(order_id: str, trading_env: str = 'SIMULATE', market: str = 'US') -> dict:
    """Get details for a specific order."""
    orders = get_order_list(trading_env=trading_env, market=market)
    if orders.empty:
        return {}
    match = orders[orders['order_id'].astype(str) == str(order_id)]
    if match.empty:
        return {}
    return match.iloc[0].to_dict()


def save_order_log(output_path: str):
    """Save the session order log to a JSON file for audit trail."""
    with open(output_path, 'w') as f:
        json.dump(make_serializable(order_log), f, indent=2, ensure_ascii=False)
    print(f'Order log saved to: {output_path}')
