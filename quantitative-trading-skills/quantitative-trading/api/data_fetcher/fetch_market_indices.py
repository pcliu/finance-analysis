"""
Fetch major market indices data.

Usage:
    from api.data_fetcher import fetch_market_indices
    
    indices = fetch_market_indices(['^GSPC', '^DJI'], period='1y')
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'scripts'))

from data_fetcher import DataFetcher

_fetcher = DataFetcher()

async def fetch_market_indices_async(indices: list = None, period: str = '1y',
                                     provider: str = None, market: str = None):
    """
    Fetch major market indices data.
    
    Args:
        indices: List of index symbols (default: ['^GSPC', '^DJI', '^IXIC', '^RUT'])
        period: Period for data fetching
    
    Returns:
        dict: Dictionary with index data
    
    Example:
        indices = await fetch_market_indices_async(['^GSPC'], period='6mo')
        sp500 = indices['^GSPC']
        print(f"S&P 500 current: ${sp500['Close'].iloc[-1]:.2f}")
    """
    return _fetcher.fetch_market_indices(indices, period, provider=provider, market=market)

def fetch_market_indices(indices: list = None, period: str = '1y',
                         provider: str = None, market: str = None):
    """Synchronous version"""
    return _fetcher.fetch_market_indices(indices, period, provider=provider, market=market)
