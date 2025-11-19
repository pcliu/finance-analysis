"""
Calculate Relative Strength Index (RSI).

Usage:
    from api.indicators import calculate_rsi
    from api.data_fetcher import fetch_stock_data_async
    
    data = await fetch_stock_data_async('AAPL', period='1y')
    rsi = calculate_rsi(data, window=14)
    current_rsi = rsi.iloc[-1]
    
    if current_rsi > 70:
        print("Overbought")
    elif current_rsi < 30:
        print("Oversold")
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'scripts'))

from indicators import TechnicalIndicators

_indicators = TechnicalIndicators()

def calculate_rsi(data, window: int = 14, column: str = 'Close'):
    """
    Calculate Relative Strength Index.
    
    Args:
        data: DataFrame with price data
        window: RSI window (default: 14)
        column: Column to calculate on (default: 'Close')
    
    Returns:
        pd.Series: RSI values (0-100)
    
    Example:
        rsi = calculate_rsi(data)
        current = rsi.iloc[-1]
        # Only return signal, not full series
        signal = "Overbought" if current > 70 else "Oversold" if current < 30 else "Neutral"
        print(signal)
    """
    return _indicators.calculate_rsi(data, window, column)

