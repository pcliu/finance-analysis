"""
Calculate Exponential Moving Average (EMA).

Usage:
    from api.indicators import calculate_ema
    from api.data_fetcher import fetch_stock_data_async
    
    data = await fetch_stock_data_async('AAPL', period='1y')
    ema_12 = calculate_ema(data, span=12)
    print(f"EMA(12): ${ema_12.iloc[-1]:.2f}")
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'scripts'))

from indicators import TechnicalIndicators

_indicators = TechnicalIndicators()

def calculate_ema(data, span: int = 20, column: str = 'Close'):
    """
    Calculate Exponential Moving Average.
    
    Args:
        data: DataFrame with price data
        span: EMA span (default: 20)
        column: Column to calculate on (default: 'Close')
    
    Returns:
        pd.Series: EMA values
    
    Example:
        ema = calculate_ema(data, span=12)
        current_ema = ema.iloc[-1]
        print(f"Current EMA(12): ${current_ema:.2f}")
    """
    return _indicators.calculate_ema(data, span, column)

