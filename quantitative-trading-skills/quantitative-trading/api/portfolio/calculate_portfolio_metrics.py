"""
Calculate portfolio risk and return metrics.

Usage:
    from api.portfolio import calculate_portfolio_metrics, create_portfolio_data
    import numpy as np
    
    portfolio = await create_portfolio_data_async(['AAPL', 'GOOGL'], period='1y')
    returns = portfolio.pct_change().dropna()
    weights = np.array([0.6, 0.4])
    metrics = calculate_portfolio_metrics(returns, weights)
    print(f"Sharpe: {metrics['sharpe_ratio']:.2f}, Return: {metrics['expected_return']:.2%}")
"""

import sys
import os
import pandas as pd
import numpy as np
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'scripts'))

from portfolio_analyzer import PortfolioAnalyzer

_analyzer = PortfolioAnalyzer()

def calculate_portfolio_metrics(returns: pd.DataFrame, weights: np.ndarray = None):
    """
    Calculate portfolio risk and return metrics.
    
    Args:
        returns: DataFrame with asset returns
        weights: Portfolio weights (default: equal weights)
    
    Returns:
        dict: Portfolio metrics including sharpe_ratio, volatility, max_drawdown, etc.
    
    Example:
        metrics = calculate_portfolio_metrics(returns, weights)
        # Extract key metrics only
        summary = {
            'sharpe': metrics['sharpe_ratio'],
            'volatility': metrics['volatility'],
            'max_drawdown': metrics['max_drawdown']
        }
        print(summary)
    """
    return _analyzer.calculate_portfolio_metrics(returns, weights)

