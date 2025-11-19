"""
Optimize portfolio weights for various objectives.

Usage:
    from api.portfolio import optimize_portfolio, create_portfolio_data
    
    portfolio = await create_portfolio_data_async(['AAPL', 'GOOGL', 'MSFT'], period='1y')
    returns = portfolio.pct_change().dropna()
    result = optimize_portfolio(returns, optimization_method='sharpe')
    print(f"Optimal weights: {result['optimal_weights']}")
"""

import sys
import os
import pandas as pd
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'scripts'))

from portfolio_analyzer import PortfolioAnalyzer

_analyzer = PortfolioAnalyzer()

def optimize_portfolio(returns: pd.DataFrame, optimization_method: str = 'sharpe', target_return: float = None):
    """
    Optimize portfolio weights.
    
    Args:
        returns: DataFrame with asset returns
        optimization_method: 'sharpe', 'min_volatility', 'target_return', 'risk_parity'
        target_return: Target return for target_return optimization
    
    Returns:
        dict: Optimization results with optimal_weights and metrics
    
    Example:
        result = optimize_portfolio(returns, 'sharpe')
        # Extract only key information
        summary = {
            'weights': dict(zip(returns.columns, result['optimal_weights'])),
            'sharpe': result['metrics']['sharpe_ratio'],
            'return': result['metrics']['expected_return']
        }
        print(summary)
    """
    return _analyzer.optimize_portfolio(returns, optimization_method, target_return)

