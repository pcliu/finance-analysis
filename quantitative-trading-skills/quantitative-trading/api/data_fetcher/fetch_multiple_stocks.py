"""
Fetch data for multiple stocks simultaneously.

Usage:
    from api.data_fetcher import fetch_multiple_stocks
    
    data_dict = fetch_multiple_stocks(['AAPL', 'GOOGL', 'MSFT'], period='1y')
    # Process and summarize before returning
    summary = {ticker: df['Close'].iloc[-1] for ticker, df in data_dict.items()}
    print(summary)
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'scripts'))

from data_fetcher import DataFetcher

_fetcher = DataFetcher()

async def fetch_multiple_stocks_async(
    tickers: list,
    start_date: str = None,
    end_date: str = None,
    period: str = '1y',
    provider: str = None,
    market: str = None,
):
    """
    Fetch data for multiple stocks.
    
    Args:
        tickers: List of ticker symbols
        start_date: Start date in 'YYYY-MM-DD' format (optional)
        end_date: End date in 'YYYY-MM-DD' format (optional)
        period: Period for data fetching
    
    Returns:
        dict: Dictionary with ticker as key and DataFrame as value
    
    Example:
        # Fetch multiple stocks
        data = await fetch_multiple_stocks_async(['AAPL', 'GOOGL'], period='6mo')
        
        # Extract only current prices
        prices = {t: df['Close'].iloc[-1] for t, df in data.items()}
        print(prices)
    """
    return _fetcher.fetch_multiple_stocks(tickers, start_date, end_date, period,
                                          provider=provider, market=market)

def fetch_multiple_stocks(tickers: list, start_date: str = None, end_date: str = None, period: str = '1y',
                          provider: str = None, market: str = None):
    """Synchronous version"""
    return _fetcher.fetch_multiple_stocks(tickers, start_date, end_date, period,
                                          provider=provider, market=market)
