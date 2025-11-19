"""
Calculate Conditional Value at Risk (CVaR).

Usage:
    from api.risk import calculate_cvar
    from api.data_fetcher import fetch_stock_data_async
    
    data = await fetch_stock_data_async('AAPL', period='1y')
    returns = data['Returns'].dropna()
    cvar = calculate_cvar(returns, confidence_level=0.95)
    print(f"CVaR(95%): {cvar:.2%}")
"""

import sys
import os
import pandas as pd
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'scripts'))

from risk_manager import RiskManager

_risk_manager = RiskManager()

def calculate_cvar(returns: pd.Series, var: float = None, confidence_level: float = 0.95):
    """
    Calculate Conditional Value at Risk (CVaR).
    
    Args:
        returns: Series of returns
        var: VaR value (if None, will be calculated)
        confidence_level: Confidence level (default: 0.95)
    
    Returns:
        float: CVaR value
    
    Example:
        cvar = calculate_cvar(returns, confidence_level=0.95)
        print(f"CVaR(95%): {cvar:.2%}")
    """
    return _risk_manager.calculate_cvar(returns, var, confidence_level)

