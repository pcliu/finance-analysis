"""
Get summary statistics for a stock.

Usage:
    from api.data_fetcher import get_data_summary
    
    summary = get_data_summary('AAPL', period='1y')
    print(summary)
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'scripts'))

from data_fetcher import DataFetcher

_fetcher = DataFetcher()

async def get_data_summary_async(ticker: str, period: str = '1y',
                                 provider: str = None, market: str = None):
    """
    Get summary statistics for a stock.
    
    Args:
        ticker: Stock ticker symbol
        period: Period for data fetching
    
    Returns:
        dict: Summary statistics including current price, returns, volatility, Sharpe ratio, etc.
    
    Example:
        summary = await get_data_summary_async('AAPL')
        print(f"Return: {summary['Total Return (%)']}%, Sharpe: {summary['Sharpe Ratio']}")
    """
    return _fetcher.get_data_summary(ticker, period, provider=provider, market=market)

def get_data_summary(ticker: str, period: str = '1y', provider: str = None, market: str = None):
    """Synchronous version"""
    return _fetcher.get_data_summary(ticker, period, provider=provider, market=market)
