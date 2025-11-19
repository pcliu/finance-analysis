"""
Calculate Bollinger Bands.

Usage:
    from api.indicators import calculate_bollinger_bands
    from api.data_fetcher import fetch_stock_data_async
    
    data = await fetch_stock_data_async('AAPL', period='1y')
    bb = calculate_bollinger_bands(data)
    current_price = data['Close'].iloc[-1]
    
    if current_price > bb['Upper'].iloc[-1]:
        print("Price above upper band")
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'scripts'))

from indicators import TechnicalIndicators

_indicators = TechnicalIndicators()

def calculate_bollinger_bands(data, window: int = 20, num_std: float = 2, column: str = 'Close'):
    """
    Calculate Bollinger Bands.
    
    Args:
        data: DataFrame with price data
        window: Moving average window (default: 20)
        num_std: Number of standard deviations (default: 2)
        column: Column to calculate on (default: 'Close')
    
    Returns:
        dict: {'Middle': Series, 'Upper': Series, 'Lower': Series, 'Bandwidth': Series, 'Percent_B': Series}
    
    Example:
        bb = calculate_bollinger_bands(data)
        latest = {
            'upper': bb['Upper'].iloc[-1],
            'middle': bb['Middle'].iloc[-1],
            'lower': bb['Lower'].iloc[-1]
        }
        print(latest)
    """
    return _indicators.calculate_bollinger_bands(data, window, num_std, column)

