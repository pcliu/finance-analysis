"""
Calculate Value at Risk (VaR).

Usage:
    from api.risk import calculate_var
    from api.data_fetcher import fetch_stock_data_async
    
    data = await fetch_stock_data_async('AAPL', period='1y')
    returns = data['Returns'].dropna()
    var = calculate_var(returns, method='historical', confidence_level=0.95)
    print(f"VaR(95%): {var:.2%}")
"""

import sys
import os
import pandas as pd
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'scripts'))

from risk_manager import RiskManager

_risk_manager = RiskManager()

def calculate_var(returns: pd.Series, method: str = 'historical', confidence_level: float = 0.95):
    """
    Calculate Value at Risk (VaR).
    
    Args:
        returns: Series of returns
        method: 'historical', 'parametric', or 'monte_carlo'
        confidence_level: Confidence level (default: 0.95)
    
    Returns:
        float: VaR value
    
    Example:
        var = calculate_var(returns, 'historical', 0.95)
        print(f"VaR(95%): {var:.2%}")
    """
    return _risk_manager.calculate_var(returns, method, confidence_level)

