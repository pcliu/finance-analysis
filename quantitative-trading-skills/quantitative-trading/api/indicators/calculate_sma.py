"""
Calculate Simple Moving Average (SMA).

Usage:
    from api.indicators import calculate_sma
    from api.data_fetcher import fetch_stock_data_async
    
    data = await fetch_stock_data_async('AAPL', period='1y')
    sma_20 = calculate_sma(data, window=20)
    print(f"SMA(20): ${sma_20.iloc[-1]:.2f}")
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'scripts'))

from indicators import TechnicalIndicators

_indicators = TechnicalIndicators()

def calculate_sma(data, window: int = 20, column: str = 'Close'):
    """
    Calculate Simple Moving Average.
    
    Args:
        data: DataFrame with price data
        window: Moving average window (default: 20)
        column: Column to calculate on (default: 'Close')
    
    Returns:
        pd.Series: SMA values
    
    Example:
        sma = calculate_sma(data, window=20)
        # Get latest value only
        current_sma = sma.iloc[-1]
        print(f"Current SMA(20): ${current_sma:.2f}")
    """
    return _indicators.calculate_sma(data, window, column)

