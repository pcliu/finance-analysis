"""
Fetch stock data for a given ticker symbol.

Usage:
    from api.data_fetcher import fetch_stock_data
    
    data = fetch_stock_data(ticker='AAPL', period='1y')
    # Filter recent data before returning to model
    recent = data[data.index > '2024-01-01']
    print(f"Current price: ${recent['Close'].iloc[-1]:.2f}")
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'scripts'))

from data_fetcher import DataFetcher

_fetcher = DataFetcher()

async def fetch_stock_data_async(
    ticker: str,
    start_date: str = None,
    end_date: str = None,
    period: str = '1y',
    provider: str = None,
    market: str = None,
):
    """
    Fetch stock data for a given ticker.
    
    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL')
        start_date: Start date in 'YYYY-MM-DD' format (optional)
        end_date: End date in 'YYYY-MM-DD' format (optional)
        period: Period if dates not specified ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max')
        provider: 'yfinance', 'tushare', or None for auto-detect
        market: Market hint (e.g., 'cn', 'hk') used for tushare mapping
    
    Returns:
        pd.DataFrame: Stock data with OHLCV and calculated fields (Returns, Volatility, etc.)
    
    Example:
        # Fetch 1 year of data
        data = await fetch_stock_data_async('AAPL', period='1y')
        
        # Filter to recent months only
        recent = data[data.index > '2024-01-01']
        print(f"Records: {len(recent)}, Current: ${recent['Close'].iloc[-1]:.2f}")
    """
    return _fetcher.fetch_stock_data(ticker, start_date, end_date, period, provider=provider, market=market)

def fetch_stock_data(ticker: str, start_date: str = None, end_date: str = None, period: str = '1y',
                     provider: str = None, market: str = None):
    """Synchronous version for immediate use"""
    return _fetcher.fetch_stock_data(ticker, start_date, end_date, period, provider=provider, market=market)


if __name__ == "__main__":
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(description='Fetch stock data')
    parser.add_argument('ticker', type=str, help='Stock ticker symbol')
    parser.add_argument('period', type=str, nargs='?', default='1y',
                       help='Period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max). Default: 1y')
    parser.add_argument('--start', type=str, help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end', type=str, help='End date (YYYY-MM-DD)')
    parser.add_argument('--rows', type=int, default=10, help='Number of rows to display')
    parser.add_argument('--provider', choices=['auto', 'yfinance', 'tushare'], default='auto',
                        help='Select data source (auto by default).')
    parser.add_argument('--market', type=str, help='Market hint (cn, hk, etc.) for tushare mapping')
    
    args = parser.parse_args()
    
    # Use period from positional argument if provided, otherwise from --period
    period = args.period
    
    try:
        data = fetch_stock_data(args.ticker, args.start, args.end, period,
                                provider=args.provider, market=args.market)
        if data is not None and not data.empty:
            print(f"\nStock Data for {args.ticker} ({period}):")
            print(f"Total records: {len(data)}")
            print(f"\nLatest {args.rows} records:")
            print(data.tail(args.rows))
            print(f"\nSummary:")
            print(f"  Current Price: ${data['Close'].iloc[-1]:.2f}")
            print(f"  Period High: ${data['High'].max():.2f}")
            print(f"  Period Low: ${data['Low'].min():.2f}")
            print(f"  Total Return: {(data['Close'].iloc[-1] / data['Close'].iloc[0] - 1) * 100:.2f}%")
        else:
            print(f"Error: Could not fetch data for {args.ticker}")
            sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
