"""
Moving Average Crossover Strategy.

Buy when fast MA crosses above slow MA, sell when fast MA crosses below slow MA.

Usage:
    from api.strategies import moving_average_crossover
    from api.data_fetcher import fetch_stock_data_async
    
    data = await fetch_stock_data_async('AAPL', period='1y')
    signals = moving_average_crossover(data, fast_window=20, slow_window=50)
    # Filter only buy/sell signals
    buy_signals = signals[signals['Buy_Signal'] == True]
    print(f"Found {len(buy_signals)} buy signals")
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'scripts'))

from strategies import TradingStrategy

_strategy = TradingStrategy()

def moving_average_crossover(data, fast_window: int = 20, slow_window: int = 50):
    """
    Moving Average Crossover Strategy.
    
    Args:
        data: DataFrame with price data
        fast_window: Fast moving average window (default: 20)
        slow_window: Slow moving average window (default: 50)
    
    Returns:
        pd.DataFrame: Original data with added columns: MA_Fast, MA_Slow, Signal, Position, Buy_Signal, Sell_Signal
    
    Example:
        signals = moving_average_crossover(data)
        # Extract only signal dates
        buy_dates = signals[signals['Buy_Signal']].index
        sell_dates = signals[signals['Sell_Signal']].index
        print(f"Buy signals: {len(buy_dates)}, Sell signals: {len(sell_dates)}")
    """
    return _strategy.moving_average_crossover(data, fast_window, slow_window)

