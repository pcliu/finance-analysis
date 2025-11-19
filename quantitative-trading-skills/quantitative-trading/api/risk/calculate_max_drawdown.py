"""
Calculate Maximum Drawdown and drawdown metrics.

Usage:
    from api.risk import calculate_max_drawdown
    from api.data_fetcher import fetch_stock_data_async
    
    data = await fetch_stock_data_async('AAPL', period='1y')
    returns = data['Returns'].dropna()
    metrics = calculate_max_drawdown(returns)
    print(f"Max Drawdown: {metrics['max_drawdown']:.2%}")
"""

import sys
import os
import pandas as pd
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'scripts'))

from risk_manager import RiskManager

_risk_manager = RiskManager()

def calculate_max_drawdown(returns: pd.Series):
    """
    Calculate Maximum Drawdown and comprehensive drawdown metrics.
    
    Args:
        returns: Series of returns
    
    Returns:
        dict: Drawdown metrics including max_drawdown, avg_drawdown, duration, etc.
    
    Example:
        metrics = calculate_max_drawdown(returns)
        # Extract only key metric
        summary = {
            'max_drawdown': metrics['max_drawdown'],
            'duration': metrics['max_drawdown_duration']
        }
        print(summary)
    """
    return _risk_manager.calculate_drawdown_metrics(returns)

