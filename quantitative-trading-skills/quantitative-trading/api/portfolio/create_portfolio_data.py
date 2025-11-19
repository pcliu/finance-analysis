"""
Create portfolio data from multiple stocks.

Usage:
    from api.portfolio import create_portfolio_data
    
    portfolio = create_portfolio_data(['AAPL', 'GOOGL', 'MSFT'], period='1y')
    # Get only recent data
    recent = portfolio.tail(30)
    print(recent)
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'scripts'))

from portfolio_analyzer import PortfolioAnalyzer

_analyzer = PortfolioAnalyzer()

async def create_portfolio_data_async(tickers: list, period: str = '1y'):
    """
    Create portfolio data from multiple stocks.
    
    Args:
        tickers: List of ticker symbols
        period: Period for data fetching
    
    Returns:
        pd.DataFrame: Portfolio data with all tickers (aligned dates)
    
    Example:
        portfolio = await create_portfolio_data_async(['AAPL', 'GOOGL'], period='1y')
        # Calculate summary statistics
        summary = {
            'tickers': list(portfolio.columns),
            'dates': len(portfolio),
            'current_prices': portfolio.iloc[-1].to_dict()
        }
        print(summary)
    """
    return _analyzer.create_portfolio_data(tickers, period)

def create_portfolio_data(tickers: list, period: str = '1y'):
    """Synchronous version"""
    return _analyzer.create_portfolio_data(tickers, period)
