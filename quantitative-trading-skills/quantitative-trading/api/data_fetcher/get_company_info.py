"""
Get company information and fundamentals.

Usage:
    from api.data_fetcher import get_company_info
    
    info = get_company_info('AAPL')
    print(f"Company: {info['Name']}, Sector: {info['Sector']}")
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'scripts'))

from data_fetcher import DataFetcher

_fetcher = DataFetcher()

async def get_company_info_async(ticker: str, provider: str = None, market: str = None):
    """
    Get company information and fundamentals.
    
    Args:
        ticker: Stock ticker symbol
    
    Returns:
        dict: Company information including Name, Sector, Industry, Market Cap, P/E Ratio, etc.
    
    Example:
        info = await get_company_info_async('AAPL')
        print(f"{info['Name']} - {info['Sector']}")
    """
    return _fetcher.get_company_info(ticker, provider=provider, market=market)

def get_company_info(ticker: str, provider: str = None, market: str = None):
    """Synchronous version"""
    return _fetcher.get_company_info(ticker, provider=provider, market=market)


if __name__ == "__main__":
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(description='Get company information')
    parser.add_argument('ticker', type=str, help='Stock ticker symbol')
    
    args = parser.parse_args()
    
    try:
        info = get_company_info(args.ticker)
        if info:
            print(f"\nCompany Information for {args.ticker}:")
            print("=" * 50)
            for key, value in info.items():
                if value != 'N/A':
                    print(f"{key:20s}: {value}")
        else:
            print(f"Error: Could not fetch company info for {args.ticker}")
            sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
