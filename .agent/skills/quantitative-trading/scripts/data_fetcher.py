#!/usr/bin/env python3
"""
Data Fetcher Script for Quantitative Trading
Fetches and preprocesses market data using yfinance (global) and tushare (China/HK)
"""

import os
import sys
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, Tuple
import argparse
import warnings

warnings.filterwarnings('ignore')

# Ensure project root is importable for config modules
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

try:
    import tushare as ts
except ImportError:
    ts = None

try:
    from tushare_config import TUSHARE_TOKEN as _CONFIG_TUSHARE_TOKEN
except ImportError:
    _CONFIG_TUSHARE_TOKEN = None

PERIOD_LOOKBACK = {
    '1d': timedelta(days=1),
    '5d': timedelta(days=5),
    '1mo': timedelta(days=31),
    '3mo': timedelta(days=93),
    '6mo': timedelta(days=186),
    '1y': timedelta(days=365),
    '2y': timedelta(days=730),
    '5y': timedelta(days=1825),
    '10y': timedelta(days=3650),
    'ytd': timedelta(days=datetime.now().timetuple().tm_yday),
    'max': timedelta(days=3650),
}


class DataFetcher:
    def __init__(self, default_provider: str = 'auto', tushare_token: Optional[str] = None):
        self.data_cache = {}
        self.default_provider = default_provider
        self._tushare_token = tushare_token or os.getenv('TUSHARE_TOKEN') or _CONFIG_TUSHARE_TOKEN or '602a0859f5c2f2cf0c5382dd3035f016b8b0dc18fd10cdd3e912f3c5'
        self._tushare_client = None

    # ------------------------------------------------------------------
    # Provider helpers
    # ------------------------------------------------------------------
    def _resolve_provider(self, ticker: str, provider: Optional[str], market: Optional[str]) -> str:
        provider = (provider or self.default_provider or 'auto').lower()
        if provider in ('yfinance', 'yahoo'):
            return 'yfinance'
        if provider == 'tushare':
            return 'tushare'

        if market and market.lower() in ('cn', 'china', 'hk', 'hongkong', 'hong-kong'):
            return 'tushare'

        suffix = ticker.upper().split('.')[-1]
        if suffix in {'SS', 'SZ', 'SH', 'BJ', 'HK'}:
            return 'tushare'

        return 'yfinance'

    def _normalize_ts_code(self, ticker: str, market: Optional[str]) -> Optional[str]:
        ticker = ticker.upper()
        if '.' in ticker:
            base, suffix = ticker.split('.')
        else:
            base, suffix = ticker, ''

        # Shanghai codes: 6xxxxx (stocks), 5xxxxx (ETF/funds), 000xxx (indices), 9xxxxx
        if suffix in {'SS', 'SH'} or (not suffix and base.startswith(('6', '5', '9'))):
            return f"{base}.SH"
        # Shenzhen codes: 0xxxxx, 3xxxxx (stocks), 159xxx, 16xxxx, 18xxxx (ETF/LOF), 399xxx (indices)
        if suffix in {'SZ'} or (not suffix and base.startswith(('0', '2', '3', '4', '159', '16', '18'))):
            return f"{base}.SZ"
        if suffix in {'BJ'}:
            return f"{base}.BJ"
        if suffix == 'HK' or (market and market.lower() in ('hk', 'hongkong', 'hong-kong')):
            base = base.zfill(5) if base.isdigit() else base
            return f"{base}.HK"
        if suffix == 'CN':
            return f"{base}.SH"
        return None

    def _resolve_tushare_dates(self, start_date: Optional[str], end_date: Optional[str], period: str) -> Tuple[str, str]:
        def _parse(date_str: Optional[str]) -> Optional[datetime]:
            if not date_str:
                return None
            return datetime.strptime(date_str, '%Y-%m-%d')

        end_dt = _parse(end_date) or datetime.today()
        if start_date:
            start_dt = _parse(start_date)
        else:
            delta = PERIOD_LOOKBACK.get(period, timedelta(days=365))
            start_dt = end_dt - delta

        return start_dt.strftime('%Y%m%d'), end_dt.strftime('%Y%m%d')

    def _determine_asset_type(self, ts_code: str) -> str:
        """
        Determine asset type based on Tushare code conventions.
        Returns:
            'E': Stock (Equity)
            'I': Index
            'FD': Fund (ETF/LOF/Mutual)
            'FT': Future
            'O': Option
            'CB': Convertible Bond
        """
        if not ts_code:
            return 'E'
            
        # Extract code and suffix
        parts = ts_code.split('.')
        if len(parts) != 2:
            return 'E'
            
        code, suffix = parts[0], parts[1]
        
        # Index patterns
        # SH: 000xxx (e.g. 000001.SH), but 000xxx.SZ is stock
        # SZ: 399xxx (e.g. 399001.SZ)
        # CSI: 000xxx.CSI, 93xxxx.CSI
        # CIC: 000xxx.CIC
        if suffix == 'SH' and code.startswith('000'):
            return 'I'
        if suffix == 'SZ' and code.startswith('399'):
            return 'I'
        if suffix in ['CSI', 'CIC', 'SI', 'CI']:
            return 'I'
            
        # Fund patterns
        # SH: 5xxxxx (ETF/LOF)
        # SZ: 15xxxx, 16xxxx (ETF/LOF)
        # BJ: 
        if suffix == 'SH' and code.startswith(('5')):
            return 'FD'
        if suffix == 'SZ' and code.startswith(('15', '16', '18')):
            return 'FD'
            
        # Future/Option usually have different suffixes or lengths, 
        # but for now default to Equity for others (6xxxxx.SH, 0xxxxx.SZ, 3xxxxx.SZ, 8xxxxx.BJ, 4xxxxx.BJ)
        
        return 'E'

    def _ensure_tushare_client(self):
        if self._tushare_client is not None:
            return self._tushare_client
        if ts is None:
            raise ImportError("tushare is not installed. Run `pip install tushare` to enable China/HK market data.")
        token = self._tushare_token
        if not token:
            raise EnvironmentError("Set TUSHARE_TOKEN env var to use tushare (https://tushare.pro/register).")
        ts.set_token(token)
        self._tushare_client = ts.pro_api()
        return self._tushare_client

    def _augment_features(self, data: pd.DataFrame) -> pd.DataFrame:
        if data is None or data.empty:
            return data
        data['Returns'] = data['Close'].pct_change()
        data['Log_Returns'] = np.log(data['Close'] / data['Close'].shift(1))
        data['Volatility'] = data['Returns'].rolling(window=20).std() * np.sqrt(252)
        data['Cumulative_Returns'] = (1 + data['Returns']).cumprod()
        return data

    def _fetch_with_yfinance(self, ticker, start_date=None, end_date=None, period='1y'):
        if start_date and end_date:
            data = yf.download(ticker, start=start_date, end=end_date, auto_adjust=False)
        else:
            data = yf.download(ticker, period=period, auto_adjust=False)

        if data.empty:
            print(f"No data found for ticker {ticker}")
            return None

        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        return data

    def _fetch_with_tushare(self, ticker, start_date=None, end_date=None, period='1y', market: Optional[str] = None):
        ts_code = self._normalize_ts_code(ticker, market)
        if not ts_code:
            raise ValueError(f"Ticker {ticker} cannot be mapped to a tushare ts_code. Provide market hint via --market.")

        # Ensure client is initialized (needed for pro_bar internally if not passed, but we pass api)
        pro = self._ensure_tushare_client()
        start_dt, end_dt = self._resolve_tushare_dates(start_date, end_date, period)
        
        # Determine asset type
        asset_type = self._determine_asset_type(ts_code)

        try:
            # Use different API based on asset type
            if asset_type == 'FD':
                # Use fund_daily for ETF/LOF funds - more reliable for fund data
                raw = pro.fund_daily(
                    ts_code=ts_code,
                    start_date=start_dt,
                    end_date=end_dt,
                    fields='trade_date,open,high,low,close,pre_close,vol,amount'
                )
                volume_multiplier = 1  # fund_daily returns volume in shares already
            else:
                # Use pro_bar for stocks, indices, etc.
                adj = 'qfq' if asset_type == 'E' else None
                raw = ts.pro_bar(
                    ts_code=ts_code,
                    api=pro,
                    start_date=start_dt, 
                    end_date=end_dt,
                    asset=asset_type,
                    adj=adj
                )
                # pro_bar returns vol in lots (100 shares) for stocks/funds
                volume_multiplier = 100 if asset_type == 'E' else 1
            
            if raw is None or raw.empty:
                print(f"No tushare data found for {ts_code} (Asset: {asset_type})")
                return None
                
        except Exception as exc:
            print(f"Tushare error for {ts_code}: {exc}")
            return None

        raw['trade_date'] = pd.to_datetime(raw['trade_date'])
        raw.sort_values('trade_date', inplace=True)
        raw.set_index('trade_date', inplace=True)

        data = pd.DataFrame(index=raw.index)
        data['Open'] = raw['open'].astype(float)
        data['High'] = raw['high'].astype(float)
        data['Low'] = raw['low'].astype(float)
        data['Close'] = raw['close'].astype(float)
        
        # Use close as adjusted close (fund_daily doesn't have adj prices)
        data['Adj Close'] = raw['close'].astype(float)
        
        if 'pre_close' in raw.columns:
            data['Prev Close'] = raw['pre_close'].astype(float)
            
        if 'vol' in raw.columns:
            data['Volume'] = raw['vol'].astype(float) * volume_multiplier
        else:
            data['Volume'] = 0.0
            
        return data

    def _fetch_company_info_yfinance(self, ticker: str) -> dict:
        stock = yf.Ticker(ticker)
        info = stock.info
        return {
            'Name': info.get('longName', 'N/A'),
            'Sector': info.get('sector', 'N/A'),
            'Industry': info.get('industry', 'N/A'),
            'Market Cap': info.get('marketCap', 'N/A'),
            'P/E Ratio': info.get('forwardPE', 'N/A'),
            'Dividend Yield': info.get('dividendYield', 'N/A'),
            'Beta': info.get('beta', 'N/A'),
            'EPS': info.get('trailingEps', 'N/A'),
            'Revenue': info.get('totalRevenue', 'N/A'),
            'Debt to Equity': info.get('debtToEquity', 'N/A')
        }

    def _fetch_company_info_tushare(self, ticker: str, market: Optional[str]) -> dict:
        ts_code = self._normalize_ts_code(ticker, market)
        if not ts_code:
            print(f"Unable to derive tushare ts_code for {ticker}")
            return {}

        pro = self._ensure_tushare_client()

        info_df = None
        try:
            if ts_code.endswith('.HK'):
                info_df = pro.hk_basic(ts_code=ts_code)
            else:
                info_df = pro.stock_company(ts_code=ts_code)
                if info_df is None or info_df.empty:
                    info_df = pro.stock_basic(ts_code=ts_code,
                                              fields='ts_code,name,fullname,industry,market,exchange,list_date')
        except Exception as exc:
            print(f"Tushare company info error for {ts_code}: {exc}")
            return {}

        if info_df is None or info_df.empty:
            return {}

        info_row = info_df.iloc[0]

        metrics = {}
        try:
            daily = pro.daily_basic(ts_code=ts_code, limit=1)
            if daily is not None and not daily.empty:
                metrics = daily.iloc[0].to_dict()
        except Exception:
            metrics = {}

        total_mv = metrics.get('total_mv')
        if total_mv is not None:
            total_mv = float(total_mv) * 1e4  # tushare reports market cap in 10k units

        company_data = {
            'Name': info_row.get('fullname') or info_row.get('name') or 'N/A',
            'Sector': info_row.get('industry', 'N/A'),
            'Industry': info_row.get('industry', 'N/A'),
            'Market': info_row.get('market', 'N/A'),
            'Exchange': info_row.get('exchange', 'N/A'),
            'List Date': info_row.get('list_date', 'N/A'),
            'Market Cap': total_mv if total_mv is not None else 'N/A',
            'P/E Ratio': metrics.get('pe_ttm', 'N/A'),
            'P/B Ratio': metrics.get('pb', 'N/A'),
            'Dividend Yield': 'N/A',
            'Beta': 'N/A',
            'EPS': metrics.get('eps', 'N/A'),
            'Revenue': 'N/A',
            'Debt to Equity': 'N/A'
        }
        return company_data

    def fetch_stock_data(self, ticker, start_date=None, end_date=None, period='1y', provider: Optional[str] = None, market: Optional[str] = None):
        """
        Fetch stock data for a given ticker

        Args:
            ticker (str): Stock ticker symbol
            start_date (str): Start date in 'YYYY-MM-DD' format
            end_date (str): End date in 'YYYY-MM-DD' format
            period (str): Period if start_date and end_date not specified ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max')
            provider (str): 'yfinance', 'tushare', or 'auto'
            market (str): Market hint for provider resolution

        Returns:
            pd.DataFrame: Stock data with OHLCV
        """
        source = self._resolve_provider(ticker, provider, market)
        cache_key = f"{ticker}:{source}"

        try:
            if source == 'tushare':
                data = self._fetch_with_tushare(ticker, start_date, end_date, period, market)
            else:
                data = self._fetch_with_yfinance(ticker, start_date, end_date, period)
        except Exception as e:
            print(f"Error fetching data for {ticker} via {source}: {str(e)}")
            return None

        if data is None or data.empty:
            return None

        data = self._augment_features(data)
        self.data_cache[cache_key] = data
        return data

    def fetch_multiple_stocks(self, tickers, start_date=None, end_date=None, period='1y', provider: Optional[str] = None, market: Optional[str] = None):
        """
        Fetch data for multiple stocks

        Args:
            tickers (list): List of ticker symbols
            start_date (str): Start date in 'YYYY-MM-DD' format
            end_date (str): End date in 'YYYY-MM-DD' format
            period (str): Period for data fetching

        Returns:
            dict: Dictionary with ticker as key and DataFrame as value
        """
        data_dict = {}

        for ticker in tickers:
            print(f"Fetching data for {ticker}...")
            data = self.fetch_stock_data(ticker, start_date, end_date, period, provider=provider, market=market)
            if data is not None:
                data_dict[ticker] = data

        return data_dict

    def get_company_info(self, ticker, provider: Optional[str] = None, market: Optional[str] = None):
        """
        Get company information and fundamentals

        Args:
            ticker (str): Stock ticker symbol

        Returns:
            dict: Company information
        """
        try:
            source = self._resolve_provider(ticker, provider, market)
            if source == 'tushare':
                return self._fetch_company_info_tushare(ticker, market)
            return self._fetch_company_info_yfinance(ticker)

        except Exception as e:
            print(f"Error fetching company info for {ticker}: {str(e)}")
            return {}

    def fetch_market_indices(self, indices=None, period='1y', provider: Optional[str] = None, market: Optional[str] = None):
        """
        Fetch major market indices data

        Args:
            indices (list): List of index symbols
            period (str): Period for data fetching

        Returns:
            dict: Dictionary with index data
        """
        if indices is None:
            indices = ['^GSPC', '^DJI', '^IXIC', '^RUT']  # S&P 500, Dow Jones, NASDAQ, Russell 2000

        return self.fetch_multiple_stocks(indices, period=period, provider=provider, market=market)

    def get_sector_data(self, sector_tickers, period='1y'):
        """
        Fetch sector-specific data

        Args:
            sector_tickers (list): List of sector ETF tickers
            period (str): Period for data fetching

        Returns:
            dict: Sector data dictionary
        """
        return self.fetch_multiple_stocks(sector_tickers, period=period)

    def calculate_correlation_matrix(self, tickers, period='1y', provider: Optional[str] = None, market: Optional[str] = None):
        """
        Calculate correlation matrix for multiple stocks

        Args:
            tickers (list): List of ticker symbols
            period (str): Period for data fetching

        Returns:
            pd.DataFrame: Correlation matrix
        """
        data_dict = self.fetch_multiple_stocks(tickers, period=period, provider=provider, market=market)

        if not data_dict:
            return None

        # Extract close prices and calculate returns
        close_prices = pd.DataFrame()
        for ticker, data in data_dict.items():
            if data is not None and not data.empty:
                close_prices[ticker] = data['Close']

        # Calculate correlation of returns
        returns = close_prices.pct_change().dropna()
        correlation_matrix = returns.corr()

        return correlation_matrix

    def get_data_summary(self, ticker, period='1y', provider: Optional[str] = None, market: Optional[str] = None):
        """
        Get summary statistics for a stock

        Args:
            ticker (str): Stock ticker symbol
            period (str): Period for data fetching

        Returns:
            dict: Summary statistics
        """
        data = self.fetch_stock_data(ticker, period=period, provider=provider, market=market)

        if data is None or data.empty:
            return {}

        summary = {
            'Ticker': ticker,
            'Period': period,
            'Start Date': data.index[0].strftime('%Y-%m-%d'),
            'End Date': data.index[-1].strftime('%Y-%m-%d'),
            'Current Price': round(data['Close'][-1], 2),
            'Period High': round(data['High'].max(), 2),
            'Period Low': round(data['Low'].min(), 2),
            'Total Return (%)': round((data['Close'][-1] / data['Close'][0] - 1) * 100, 2),
            'Annualized Volatility (%)': round(data['Volatility'][-1] * 100, 2),
            'Max Drawdown (%)': round(((data['Close'] / data['Close'].cummax() - 1).min()) * 100, 2),
            'Sharpe Ratio': round((data['Returns'].mean() / data['Returns'].std()) * np.sqrt(252), 2) if data['Returns'].std() != 0 else 0
        }

        return summary


def main():
    parser = argparse.ArgumentParser(description='Fetch market data using yfinance (global) or tushare (CN/HK)')
    parser.add_argument('--ticker', '-t', type=str, help='Single ticker symbol')
    parser.add_argument('--tickers', type=str, help='Comma-separated list of tickers')
    parser.add_argument('--start', type=str, help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end', type=str, help='End date (YYYY-MM-DD)')
    parser.add_argument('--period', type=str, default='1y', help='Period (1y, 6mo, 3mo, etc.)')
    parser.add_argument('--provider', type=str, choices=['auto', 'yfinance', 'tushare'], default='auto',
                        help='Select data provider (default auto-detect).')
    parser.add_argument('--market', type=str, help='Market hint (cn, hk, us, etc.)')
    parser.add_argument('--info', action='store_true', help='Get company information')
    parser.add_argument('--indices', action='store_true', help='Fetch major market indices')
    parser.add_argument('--correlation', action='store_true', help='Calculate correlation matrix')
    parser.add_argument('--summary', action='store_true', help='Get data summary')

    args = parser.parse_args()

    fetcher = DataFetcher(default_provider=args.provider)

    if args.ticker:
        if args.info:
            info = fetcher.get_company_info(args.ticker, provider=args.provider, market=args.market)
            print(f"\nCompany Information for {args.ticker}:")
            for key, value in info.items():
                print(f"{key}: {value}")

        if args.summary:
            summary = fetcher.get_data_summary(args.ticker, args.period, provider=args.provider, market=args.market)
            print(f"\nData Summary for {args.ticker}:")
            for key, value in summary.items():
                print(f"{key}: {value}")

        data = fetcher.fetch_stock_data(args.ticker, args.start, args.end, args.period,
                                        provider=args.provider, market=args.market)
        if data is not None:
            print(f"\nData for {args.ticker}:")
            print(data.tail())

    elif args.tickers:
        ticker_list = [t.strip() for t in args.tickers.split(',')]

        if args.correlation:
            corr_matrix = fetcher.calculate_correlation_matrix(ticker_list, args.period,
                                                               provider=args.provider, market=args.market)
            if corr_matrix is not None:
                print(f"\nCorrelation Matrix:")
                print(corr_matrix.round(3))

        data_dict = fetcher.fetch_multiple_stocks(ticker_list, args.start, args.end, args.period,
                                                  provider=args.provider, market=args.market)
        print(f"\nFetched data for {len(data_dict)} tickers")

    elif args.indices:
        data_dict = fetcher.fetch_market_indices(period=args.period, provider=args.provider, market=args.market)
        print(f"\nFetched data for {len(data_dict)} indices")

    else:
        print("Please specify either --ticker or --tickers")
        print("Use --help for more options")


if __name__ == "__main__":
    main()
