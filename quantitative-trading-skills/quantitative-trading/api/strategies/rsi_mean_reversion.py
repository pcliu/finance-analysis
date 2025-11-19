"""
RSI Mean Reversion Strategy.

Buy when RSI crosses above oversold level, sell when RSI crosses below overbought level.

Usage:
    from api.strategies import rsi_mean_reversion
    from api.data_fetcher import fetch_stock_data_async
    
    data = await fetch_stock_data_async('AAPL', period='1y')
    signals = rsi_mean_reversion(data, oversold=30, overbought=70)
    buy_signals = signals[signals['Buy_Signal'] == True]
    print(f"Found {len(buy_signals)} buy signals")
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'scripts'))

from strategies import TradingStrategy

_strategy = TradingStrategy()

def rsi_mean_reversion(data, rsi_window: int = 14, oversold: float = 30, overbought: float = 70):
    """
    RSI Mean Reversion Strategy.
    
    Args:
        data: DataFrame with price data
        rsi_window: RSI calculation window (default: 14)
        oversold: Oversold threshold (default: 30)
        overbought: Overbought threshold (default: 70)
    
    Returns:
        pd.DataFrame: Original data with added columns: RSI, Signal, Position, Buy_Signal, Sell_Signal
    
    Example:
        signals = rsi_mean_reversion(data)
        # Extract signal summary
        summary = {
            'buy_signals': len(signals[signals['Buy_Signal']]),
            'sell_signals': len(signals[signals['Sell_Signal']]),
            'current_rsi': signals['RSI'].iloc[-1]
        }
        print(summary)
    """
    return _strategy.rsi_mean_reversion(data, rsi_window, oversold, overbought)

