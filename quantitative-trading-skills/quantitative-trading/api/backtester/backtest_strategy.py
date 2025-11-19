"""
Backtest a trading strategy on historical data.

Usage:
    from api.backtester import backtest_strategy
    from api.data_fetcher import fetch_stock_data_async
    
    data = await fetch_stock_data_async('AAPL', period='2y')
    results = backtest_strategy(data, 'moving_average_crossover', {
        'fast_window': 20,
        'slow_window': 50
    })
    print(f"Total Return: {results['total_return']:.2f}%")
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'scripts'))

from backtester import Backtester

_backtester = Backtester()

def backtest_strategy(data, strategy_name: str, strategy_params: dict = None):
    """
    Backtest a trading strategy.
    
    Args:
        data: DataFrame with historical price data
        strategy_name: Name of strategy ('moving_average_crossover', 'rsi_mean_reversion', etc.)
        strategy_params: Dictionary of strategy parameters
    
    Returns:
        dict: Backtest results including total_return, sharpe_ratio, max_drawdown, etc.
    
    Example:
        results = backtest_strategy(data, 'moving_average_crossover', {'fast_window': 20, 'slow_window': 50})
        # Extract key metrics only
        summary = {
            'return': results['total_return'],
            'sharpe': results['sharpe_ratio'],
            'max_drawdown': results['max_drawdown']
        }
        print(summary)
    """
    return _backtester.backtest_strategy(data, strategy_name, strategy_params)

