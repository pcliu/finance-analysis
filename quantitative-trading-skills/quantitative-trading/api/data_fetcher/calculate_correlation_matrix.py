"""
Calculate correlation matrix for multiple stocks.

Usage:
    from api.data_fetcher import calculate_correlation_matrix
    
    corr = calculate_correlation_matrix(['AAPL', 'GOOGL', 'MSFT'], period='1y')
    print(corr)
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'scripts'))

from data_fetcher import DataFetcher

_fetcher = DataFetcher()

async def calculate_correlation_matrix_async(tickers: list, period: str = '1y',
                                             provider: str = None, market: str = None):
    """
    Calculate correlation matrix for multiple stocks.
    
    Args:
        tickers: List of ticker symbols
        period: Period for data fetching
    
    Returns:
        pd.DataFrame: Correlation matrix
    
    Example:
        corr = await calculate_correlation_matrix_async(['AAPL', 'GOOGL', 'MSFT'])
        # Filter high correlations
        high_corr = corr[corr > 0.7]
        print(high_corr)
    """
    return _fetcher.calculate_correlation_matrix(tickers, period, provider=provider, market=market)

def calculate_correlation_matrix(tickers: list, period: str = '1y',
                                 provider: str = None, market: str = None):
    """Synchronous version"""
    return _fetcher.calculate_correlation_matrix(tickers, period, provider=provider, market=market)
