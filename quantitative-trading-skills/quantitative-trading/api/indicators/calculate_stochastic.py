"""
Calculate Stochastic Oscillator.

Usage:
    from api.indicators import calculate_stochastic
    from api.data_fetcher import fetch_stock_data_async
    
    data = await fetch_stock_data_async('AAPL', period='1y')
    stoch = calculate_stochastic(data)
    print(f"Stoch K: {stoch['K'].iloc[-1]:.2f}, D: {stoch['D'].iloc[-1]:.2f}")
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'scripts'))

from indicators import TechnicalIndicators

_indicators = TechnicalIndicators()

def calculate_stochastic(data, k_window: int = 14, d_window: int = 3):
    """
    Calculate Stochastic Oscillator.
    
    Args:
        data: DataFrame with High, Low, Close columns
        k_window: %K window (default: 14)
        d_window: %D window (default: 3)
    
    Returns:
        dict: {'K': Series, 'D': Series}
    
    Example:
        stoch = calculate_stochastic(data)
        latest = {
            'k': stoch['K'].iloc[-1],
            'd': stoch['D'].iloc[-1]
        }
        print(latest)
    """
    return _indicators.calculate_stochastic(data, k_window, d_window)

