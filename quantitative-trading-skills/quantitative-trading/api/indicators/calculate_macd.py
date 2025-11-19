"""
Calculate MACD (Moving Average Convergence Divergence).

Usage:
    from api.indicators import calculate_macd
    from api.data_fetcher import fetch_stock_data_async
    
    data = await fetch_stock_data_async('AAPL', period='1y')
    macd = calculate_macd(data)
    print(f"MACD: {macd['MACD'].iloc[-1]:.2f}, Signal: {macd['Signal'].iloc[-1]:.2f}")
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'scripts'))

from indicators import TechnicalIndicators

_indicators = TechnicalIndicators()

def calculate_macd(data, fast: int = 12, slow: int = 26, signal: int = 9, column: str = 'Close'):
    """
    Calculate MACD (Moving Average Convergence Divergence).
    
    Args:
        data: DataFrame with price data
        fast: Fast EMA period (default: 12)
        slow: Slow EMA period (default: 26)
        signal: Signal line period (default: 9)
        column: Column to calculate on (default: 'Close')
    
    Returns:
        dict: {'MACD': Series, 'Signal': Series, 'Histogram': Series}
    
    Example:
        macd = calculate_macd(data)
        # Extract latest values only
        latest = {
            'macd': macd['MACD'].iloc[-1],
            'signal': macd['Signal'].iloc[-1],
            'histogram': macd['Histogram'].iloc[-1]
        }
        print(latest)
    """
    return _indicators.calculate_macd(data, fast, slow, signal, column)

