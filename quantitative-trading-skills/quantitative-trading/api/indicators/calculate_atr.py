"""
Calculate Average True Range (ATR).

Usage:
    from api.indicators import calculate_atr
    from api.data_fetcher import fetch_stock_data_async
    
    data = await fetch_stock_data_async('AAPL', period='1y')
    atr = calculate_atr(data, window=14)
    print(f"ATR: ${atr.iloc[-1]:.2f}")
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'scripts'))

from indicators import TechnicalIndicators

_indicators = TechnicalIndicators()

def calculate_atr(data, window: int = 14):
    """
    Calculate Average True Range (ATR).
    
    Args:
        data: DataFrame with High, Low, Close columns
        window: ATR window (default: 14)
    
    Returns:
        pd.Series: ATR values
    
    Example:
        atr = calculate_atr(data)
        current_atr = atr.iloc[-1]
        print(f"Current ATR: ${current_atr:.2f}")
    """
    return _indicators.calculate_atr(data, window)

